from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

try:
    from physics.core.base_module import ScientificModule
    from physics.neurosymbolic.audit import linear_cka
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from core.base_module import ScientificModule
    from neurosymbolic.audit import linear_cka


PHYSICS_ROOT = Path(__file__).resolve().parent
REAL_DATA_DIR = PHYSICS_ROOT / "data" / "real"


class DomainAdaptation(ScientificModule):
    """Coordinator for reality-gap and transfer checks."""

    reused_modules = [
        "physics/neurosymbolic/audit.py",
        "physics/robustness_audit.py",
        "physics/core/empirical/mit_bih_bifurcated_audit.py",
        "physics/core/empirical/causal_continuity_audit.py",
        "physics/train_ecg_models.py",
        "physics/train_all_architectures_ptbxl.py",
    ]

    def measure_reality_gap(
        self,
        synthetic_data,
        real_data,
        feature_extractor: Callable[[Any], Any] | None = None,
    ) -> dict[str, Any]:
        synthetic_features = _features(synthetic_data, feature_extractor)
        real_features = _features(real_data, feature_extractor)
        n = min(len(synthetic_features), len(real_features))
        if n == 0:
            return {"summary": pd.DataFrame(), "global_score": 0.0, "cka": 0.0, "wasserstein_mean": np.inf}
        synthetic_features = synthetic_features[:n]
        real_features = real_features[:n]
        cka = float(linear_cka(synthetic_features, real_features))
        distances = []
        rows = []
        for idx in range(min(synthetic_features.shape[1], real_features.shape[1])):
            dist = float(wasserstein_distance(synthetic_features[:, idx], real_features[:, idx]))
            distances.append(dist)
            rows.append({"feature": f"feature_{idx}", "wasserstein_distance": dist})
        wasserstein_mean = float(np.mean(distances)) if distances else np.inf
        normalized_distance = 1.0 / (1.0 + wasserstein_mean)
        global_score = float(0.5 * cka + 0.5 * normalized_distance)
        return {
            "summary": pd.DataFrame(rows),
            "global_score": global_score,
            "cka": cka,
            "wasserstein_mean": wasserstein_mean,
        }

    def train_domain_adaptation(self, source, target, method: str = "transfer") -> dict[str, Any]:
        source_x, source_y = _split_xy(source)
        target_x, target_y = _split_xy(target)
        method = method.lower()
        if method not in {"transfer", "joint", "calibrate"}:
            raise ValueError("method must be one of transfer, joint, calibrate")
        scaler = StandardScaler()
        if method == "joint" and len(target_x):
            train_x = np.vstack([source_x, target_x])
            train_y = np.concatenate([source_y, target_y])
        else:
            train_x, train_y = source_x, source_y
        train_x = scaler.fit_transform(train_x)
        model = Ridge(alpha=1.0)
        model.fit(train_x, train_y)
        calibration = None
        if method in {"transfer", "calibrate"} and len(target_x) > 2:
            pred = model.predict(scaler.transform(target_x))
            calibration = float(np.mean(target_y - pred))
        checkpoints = sorted((PHYSICS_ROOT / "models").glob("*.pth")) + sorted((PHYSICS_ROOT / "models" / "ptbxl").glob("*.pth"))
        return {
            "model": model,
            "scaler": scaler,
            "method": method,
            "calibration_offset": calibration,
            "existing_checkpoints_seen": [str(path) for path in checkpoints[:10]],
        }

    def validate_transfer_performance(self, model_bundle, real_test, baseline_synthetic) -> dict[str, float]:
        model = model_bundle["model"] if isinstance(model_bundle, dict) else model_bundle
        scaler = model_bundle.get("scaler") if isinstance(model_bundle, dict) else None
        real_x, real_y = _split_xy(real_test)
        base_x, base_y = _split_xy(baseline_synthetic)
        if scaler is not None:
            real_x = scaler.transform(real_x)
            base_x = scaler.transform(base_x)
        real_score = float(r2_score(real_y, model.predict(real_x)))
        baseline_score = float(r2_score(base_y, model.predict(base_x)))
        retained = real_score / baseline_score if abs(baseline_score) > 1e-12 else 0.0
        return {"real_score": real_score, "baseline_score": baseline_score, "retained_fraction": retained}

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.status = "running"
        datasets = list(REAL_DATA_DIR.glob("*_pipeline.csv"))
        rng = np.random.default_rng(self.config_manager.get("physics.random_seed", 42))
        synthetic = pd.DataFrame(rng.normal(size=(120, 6)))
        domain_results = []
        for dataset_path in datasets:
            real = pd.read_csv(dataset_path)
            gap = self.measure_reality_gap(synthetic, real)
            domain_results.append(
                {
                    "dataset": str(dataset_path),
                    "global_score": gap["global_score"],
                    "cka": gap["cka"],
                    "wasserstein_mean": gap["wasserstein_mean"],
                }
            )
        domains_above_80 = sum(1 for item in domain_results if item["global_score"] >= 0.8)
        milestone_met = domains_above_80 >= 3
        metrics = {
            "datasets_found": len(datasets),
            "domains_above_80_percent": domains_above_80,
            "milestone_met": milestone_met,
            "reused_modules": self.reused_modules,
        }
        self.artifact_manager.save_json("domain_adaptation_results.json", domain_results)
        report_path = self.log_result(metrics, "domain_adaptation_report.md")
        return {"metrics": metrics, "report_path": report_path, "results": domain_results}


def _features(data, extractor: Callable[[Any], Any] | None = None) -> np.ndarray:
    if extractor is not None:
        data = extractor(data)
    if isinstance(data, pd.DataFrame):
        arr = data.select_dtypes(include=[np.number]).to_numpy()
    else:
        arr = np.asarray(data, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    return np.nan_to_num(arr.astype(float), nan=0.0, posinf=0.0, neginf=0.0)


def _split_xy(data) -> tuple[np.ndarray, np.ndarray]:
    arr = _features(data)
    if arr.shape[1] == 1:
        y = arr[:, 0]
        x = np.arange(len(y), dtype=float).reshape(-1, 1)
    else:
        x = arr[:, :-1]
        y = arr[:, -1]
    return x, y


if __name__ == "__main__":
    print(json.dumps(DomainAdaptation().run(), indent=2, default=str))
