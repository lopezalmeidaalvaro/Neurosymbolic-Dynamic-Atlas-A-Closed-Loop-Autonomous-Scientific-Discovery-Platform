from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, pairwise_distances

try:
    from physics.core.base_module import ScientificModule
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from core.base_module import ScientificModule


ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"


class BiasDetector(ScientificModule):
    """Facade for bias/leakage checks, reusing the validation audit stack."""

    reused_modules = [
        "physics/core/validation/strict_leakage_audit.py",
        "physics/core/validation/dataset_bias_elimination_audit.py",
        "physics/core/validation/causal_ablation_audit.py",
        "physics/feature_redundancy_analysis.py",
    ]

    def detect_data_leakage(self, X_train, X_test, threshold: float = 0.95) -> pd.DataFrame:
        X_train = _as_2d_array(X_train)
        X_test = _as_2d_array(X_test)
        if len(X_train) == 0 or len(X_test) == 0:
            return pd.DataFrame(columns=["test_index", "nearest_train_index", "cosine_similarity", "is_leakage"])
        distances = pairwise_distances(X_test, X_train, metric="cosine")
        similarities = 1.0 - distances
        nearest = np.argmax(similarities, axis=1)
        scores = similarities[np.arange(similarities.shape[0]), nearest]
        return pd.DataFrame(
            {
                "test_index": np.arange(len(X_test)),
                "nearest_train_index": nearest,
                "cosine_similarity": scores,
                "is_leakage": scores >= threshold,
            }
        )

    def detect_spurious_correlations(self, X, y, n_permutations: int = 1000) -> pd.DataFrame:
        X_arr = _as_2d_array(X)
        y_arr = np.asarray(y).ravel()
        feature_names = _feature_names(X, X_arr.shape[1])
        rows = []
        rng = np.random.default_rng(self.config_manager.get("physics.random_seed", 42))
        for idx, name in enumerate(feature_names):
            x = X_arr[:, idx]
            if np.std(x) == 0 or np.std(y_arr) == 0:
                corr, p_value = 0.0, 1.0
            else:
                corr, _ = stats.pearsonr(x, y_arr)
                permuted = []
                for _ in range(max(1, n_permutations)):
                    permuted_y = rng.permutation(y_arr)
                    perm_corr = stats.pearsonr(x, permuted_y)[0] if np.std(permuted_y) else 0.0
                    permuted.append(abs(perm_corr))
                p_value = (1.0 + sum(value >= abs(corr) for value in permuted)) / (len(permuted) + 1.0)
            bonferroni_alpha = 0.05 / max(1, X_arr.shape[1])
            rows.append(
                {
                    "feature": name,
                    "correlation": corr,
                    "p_value": p_value,
                    "is_significant": p_value < bonferroni_alpha,
                }
            )
        return pd.DataFrame(rows)

    def detect_overfitting(
        self,
        model,
        X_train,
        y_train,
        X_val,
        y_val,
        threshold: float = 0.05,
    ) -> dict[str, Any]:
        train_score = _score_model(model, X_train, y_train)
        val_score = _score_model(model, X_val, y_val)
        gap = train_score - val_score
        shap_stability = _estimate_shap_stability(model, X_train, X_val)
        return {
            "train_score": train_score,
            "validation_score": val_score,
            "generalization_gap": gap,
            "threshold": threshold,
            "is_overfit": bool(gap > threshold),
            "shap_stability": shap_stability,
        }

    def permutation_importance_test(self, model, X, y, n_repeats: int = 30) -> pd.DataFrame:
        result = permutation_importance(
            model,
            X,
            y,
            n_repeats=n_repeats,
            random_state=self.config_manager.get("physics.random_seed", 42),
        )
        feature_names = _feature_names(X, _as_2d_array(X).shape[1])
        stderr = result.importances_std / np.sqrt(max(1, n_repeats))
        return pd.DataFrame(
            {
                "feature": feature_names,
                "importance_mean": result.importances_mean,
                "importance_std": result.importances_std,
                "ci95_low": result.importances_mean - 1.96 * stderr,
                "ci95_high": result.importances_mean + 1.96 * stderr,
            }
        )

    def knockoff_filter(self, X, y, q: float = 0.1) -> pd.DataFrame:
        X_arr = _as_2d_array(X)
        y_arr = np.asarray(y).ravel()
        feature_names = _feature_names(X, X_arr.shape[1])
        rng = np.random.default_rng(self.config_manager.get("physics.random_seed", 42))
        knockoff = np.column_stack([rng.permutation(X_arr[:, idx]) for idx in range(X_arr.shape[1])])
        original_scores = np.array([abs(_safe_corr(X_arr[:, idx], y_arr)) for idx in range(X_arr.shape[1])])
        knockoff_scores = np.array([abs(_safe_corr(knockoff[:, idx], y_arr)) for idx in range(X_arr.shape[1])])
        statistics_w = original_scores - knockoff_scores
        positive = np.sort(np.unique(np.abs(statistics_w[statistics_w > 0])))
        threshold = np.inf
        for candidate in positive:
            false_discovery_ratio = (1 + np.sum(statistics_w <= -candidate)) / max(1, np.sum(statistics_w >= candidate))
            if false_discovery_ratio <= q:
                threshold = candidate
                break
        selected = statistics_w >= threshold
        return pd.DataFrame(
            {
                "feature": feature_names,
                "original_score": original_scores,
                "knockoff_score": knockoff_scores,
                "statistic_w": statistics_w,
                "selected": selected,
            }
        )

    def run(self, pipeline_results_dir: str | None = None, **kwargs: Any) -> dict[str, Any]:
        self.status = "running"
        X, y = self._load_or_demo_data(pipeline_results_dir)
        split = max(2, int(0.7 * len(X)))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        leakage = self.detect_data_leakage(X_train, X_test)
        correlations = self.detect_spurious_correlations(X, y, n_permutations=200)
        knockoffs = self.knockoff_filter(X, y)
        metrics = {
            "reused_modules": self.reused_modules,
            "samples": int(len(X)),
            "features": int(X.shape[1]),
            "leakage_hits": int(leakage["is_leakage"].sum()) if not leakage.empty else 0,
            "significant_spurious_correlations": int(correlations["is_significant"].sum()) if not correlations.empty else 0,
            "knockoff_selected_features": int(knockoffs["selected"].sum()) if not knockoffs.empty else 0,
            "pipeline_results_dir": pipeline_results_dir or "demo_synthetic",
        }
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        self.artifact_manager.save_csv("bias_leakage_scan.csv", leakage)
        self.artifact_manager.save_csv("bias_spurious_correlations.csv", correlations)
        self.artifact_manager.save_csv("bias_knockoff_filter.csv", knockoffs)
        report_path = self.log_result(metrics, "bias_report.md")
        return {"metrics": metrics, "report_path": report_path}

    def _load_or_demo_data(self, pipeline_results_dir: str | None) -> tuple[np.ndarray, np.ndarray]:
        if pipeline_results_dir:
            directory = Path(pipeline_results_dir)
            for csv_path in directory.glob("*.csv"):
                try:
                    frame = pd.read_csv(csv_path)
                except Exception:
                    continue
                numeric = frame.select_dtypes(include=[np.number])
                if numeric.shape[1] >= 2:
                    X = numeric.iloc[:, :-1].to_numpy()
                    y = numeric.iloc[:, -1].to_numpy()
                    return X, y
        rng = np.random.default_rng(self.config_manager.get("physics.random_seed", 42))
        X = rng.normal(size=(120, 5))
        y = 0.7 * X[:, 0] - 0.2 * X[:, 2] + rng.normal(scale=0.1, size=120)
        return X, y


def _as_2d_array(data) -> np.ndarray:
    if hasattr(data, "select_dtypes"):
        arr = data.select_dtypes(include=[np.number]).to_numpy()
    else:
        arr = np.asarray(data, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    return np.nan_to_num(arr.astype(float), nan=0.0, posinf=0.0, neginf=0.0)


def _feature_names(data, n_features: int) -> list[str]:
    if hasattr(data, "columns"):
        return [str(col) for col in data.select_dtypes(include=[np.number]).columns]
    return [f"feature_{idx}" for idx in range(n_features)]


def _safe_corr(x, y) -> float:
    if np.std(x) == 0 or np.std(y) == 0:
        return 0.0
    return float(stats.pearsonr(x, y)[0])


def _score_model(model, X, y) -> float:
    if hasattr(model, "score"):
        return float(model.score(X, y))
    if hasattr(model, "predict"):
        pred = model.predict(X)
        if set(np.unique(y)).issubset({0, 1}) or len(np.unique(y)) < 20:
            return float(accuracy_score(y, pred))
        return float(1.0 - np.mean((np.asarray(pred) - np.asarray(y)) ** 2))
    raise ValueError("model must expose score() or predict()")


def _estimate_shap_stability(model, X_train, X_val) -> float | None:
    try:
        import shap

        explainer = shap.Explainer(model, _as_2d_array(X_train))
        train_values = np.abs(explainer(_as_2d_array(X_train)).values).mean(axis=0)
        val_values = np.abs(explainer(_as_2d_array(X_val)).values).mean(axis=0)
    except Exception:
        if not hasattr(model, "feature_importances_"):
            return _load_existing_shap_stability()
        train_values = np.asarray(model.feature_importances_, dtype=float)
        val_values = train_values
    if np.std(train_values) == 0 or np.std(val_values) == 0:
        return 1.0
    return float(np.corrcoef(train_values.ravel(), val_values.ravel())[0, 1])


def _load_existing_shap_stability() -> float | None:
    shap_path = ARTIFACTS_DIR / "feature_importance_shap.json"
    mi_path = ARTIFACTS_DIR / "feature_importance_mi.json"
    if not shap_path.exists() or not mi_path.exists():
        return None
    try:
        shap_data = json.loads(shap_path.read_text(encoding="utf-8"))
        mi_data = json.loads(mi_path.read_text(encoding="utf-8"))
        shap_values = np.array(list(shap_data.values()), dtype=float)
        mi_values = np.array(list(mi_data.values()), dtype=float)
        if len(shap_values) != len(mi_values) or np.std(shap_values) == 0 or np.std(mi_values) == 0:
            return None
        return float(np.corrcoef(shap_values, mi_values)[0, 1])
    except Exception:
        return None


if __name__ == "__main__":
    result = BiasDetector().run()
    print(json.dumps(result, indent=2))
