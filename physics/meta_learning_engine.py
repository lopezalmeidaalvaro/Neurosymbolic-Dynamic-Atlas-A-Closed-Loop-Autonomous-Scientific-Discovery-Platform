from __future__ import annotations

import json
import pickle
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import ttest_ind
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import OneHotEncoder

try:
    from physics.core.base_module import ScientificModule
    from physics.core.model_registry import ModelRegistry
    from physics.knowledge_graph import ScientificKnowledgeGraph
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from core.base_module import ScientificModule
    from core.model_registry import ModelRegistry
    from knowledge_graph import ScientificKnowledgeGraph


PHYSICS_ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = PHYSICS_ROOT / "artifacts"
MODELS_DIR = PHYSICS_ROOT / "models"


class MetaLearningEngine(ScientificModule):
    """Meta-prior learner and experiment scheduler over existing experiment history."""

    feature_columns = [
        "domain",
        "model_complexity",
        "dataset_size",
        "method",
        "historical_metrics",
        "compute_cost",
        "novelty_score",
    ]

    def build_experiment_history_dataset(self, knowledge_graph: ScientificKnowledgeGraph) -> tuple[pd.DataFrame, pd.Series]:
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        cache_path = ARTIFACTS_DIR / "meta_history_cache.csv"
        meta_path = ARTIFACTS_DIR / "meta_history_cache.meta.json"
        records = self._records_from_graph(knowledge_graph)
        if not records:
            records = self._records_from_experiment_registry()
        signature = _records_signature(records)
        if cache_path.exists() and meta_path.exists():
            try:
                metadata = json.loads(meta_path.read_text(encoding="utf-8"))
                if metadata.get("signature") == signature:
                    cached = pd.read_csv(cache_path)
                    return cached[self.feature_columns], cached["epistemic_gain"]
            except Exception:
                pass
        frame = pd.DataFrame(records or _demo_history())
        for column in self.feature_columns + ["epistemic_gain"]:
            if column not in frame:
                frame[column] = 0.0 if column != "method" and column != "domain" else "unknown"
        frame.to_csv(cache_path, index=False)
        meta_path.write_text(json.dumps({"signature": signature, "rows": len(frame)}, indent=2), encoding="utf-8")
        return frame[self.feature_columns], frame["epistemic_gain"]

    def train_meta_prior_learner(self, X_meta: pd.DataFrame, y_meta: pd.Series) -> dict[str, Any]:
        try:
            encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        except TypeError:
            encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)
        categorical = X_meta[["domain", "method"]].astype(str)
        numeric = X_meta.drop(columns=["domain", "method"]).astype(float)
        encoded = encoder.fit_transform(categorical)
        X = np.hstack([encoded, numeric.to_numpy()])
        model = RandomForestRegressor(n_estimators=100, random_state=self.config_manager.get("physics.random_seed", 42))
        cv = min(5, len(X))
        cv_scores = cross_val_score(model, X, y_meta, cv=cv) if cv >= 2 else np.array([])
        model.fit(X, y_meta)
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        model_path = MODELS_DIR / "meta_prior_learner.pkl"
        with model_path.open("wb") as handle:
            pickle.dump({"model": model, "encoder": encoder, "feature_columns": self.feature_columns}, handle)
        ModelRegistry().register("meta_prior_learner", model_path, metadata={"cv_scores": cv_scores.tolist()})
        return {"model": model, "encoder": encoder, "cv_scores": cv_scores, "path": str(model_path)}

    def predict_experiment_value(self, meta_model: dict[str, Any], context: dict[str, Any]) -> dict[str, float]:
        frame = pd.DataFrame([{column: context.get(column, 0.0) for column in self.feature_columns}])
        X = _transform_context(meta_model, frame)
        trees = np.array([tree.predict(X)[0] for tree in meta_model["model"].estimators_])
        mean = float(np.mean(trees))
        uncertainty = float(np.std(trees))
        return {
            "predicted_gain": mean,
            "uncertainty": uncertainty,
            "ci_low": mean - 1.96 * uncertainty,
            "ci_high": mean + 1.96 * uncertainty,
        }

    def benchmark_scheduler(self, domain: str, n_experiments: int = 50) -> dict[str, Any]:
        kg = ScientificKnowledgeGraph()
        X_meta, y_meta = self.build_experiment_history_dataset(kg)
        kg.close()
        meta_model = self.train_meta_prior_learner(X_meta, y_meta)
        scheduler = ExperimentScheduler(self, meta_model)
        rng = np.random.default_rng(self.config_manager.get("physics.random_seed", 42))
        scheduler_scores = []
        random_scores = []
        records = []
        for idx in range(n_experiments):
            candidates = [_candidate(domain, rng, idx, j) for j in range(8)]
            chosen = scheduler.select_next_experiment(candidates)
            random_chosen = candidates[int(rng.integers(0, len(candidates)))]
            scheduler_gain = _realized_gain(chosen, rng)
            random_gain = _realized_gain(random_chosen, rng)
            scheduler_scores.append(scheduler_gain)
            random_scores.append(random_gain)
            records.append({"trial": idx, "scheduler_gain": scheduler_gain, "random_gain": random_gain})
        t_stat, p_value = ttest_ind(scheduler_scores, random_scores, equal_var=False)
        result = {
            "domain": domain,
            "n_experiments": n_experiments,
            "scheduler_mean_gain": float(np.mean(scheduler_scores)),
            "random_mean_gain": float(np.mean(random_scores)),
            "t_stat": float(t_stat),
            "p_value": float(p_value),
            "significant": bool(p_value < 0.05),
            "model_path": meta_model["path"],
        }
        self.artifact_manager.save_csv("meta_learning_benchmark.csv", pd.DataFrame(records))
        self.experiment_registry.register(
            module=self.module_name,
            params={"system": domain, "n_experiments": n_experiments},
            results=result,
            status="completed",
        )
        self.report_manager.generate_phase_report("Meta Learning Benchmark", result, "meta_learning_benchmark.md")
        return result

    def run(self, domain: str = "lorenz", n_experiments: int = 50, **kwargs: Any) -> dict[str, Any]:
        self.status = "running"
        metrics = self.benchmark_scheduler(domain, n_experiments)
        report_path = self.log_result(metrics, "meta_learning_report.md")
        return {"metrics": metrics, "report_path": report_path}

    def _records_from_graph(self, knowledge_graph: ScientificKnowledgeGraph) -> list[dict[str, Any]]:
        records = []
        for row in knowledge_graph.get_experiment_records():
            ex = row.get("experiment", {})
            dataset = row.get("dataset", {})
            hyp = row.get("hypothesis", {})
            eval_props = row.get("evaluation", {})
            records.append(
                {
                    "domain": dataset.get("domain") or ex.get("dataset_name") or "unknown",
                    "model_complexity": _complexity(ex),
                    "dataset_size": float(dataset.get("n_samples") or 0),
                    "method": ex.get("method") or "unknown",
                    "historical_metrics": _metric_scalar(ex),
                    "compute_cost": float(ex.get("compute_cost") or 1.0),
                    "novelty_score": float(hyp.get("novelty_score") or 0.5),
                    "epistemic_gain": float(ex.get("epistemic_gain") or eval_props.get("epistemic_gain") or 0.1),
                }
            )
        return records

    def _records_from_experiment_registry(self) -> list[dict[str, Any]]:
        db_path = Path(self.experiment_registry.storage_path)
        if not db_path.exists():
            return []
        records = []
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            for row in conn.execute("SELECT * FROM experiments"):
                try:
                    params = json.loads(row["hyperparameters_json"] or "{}")
                    results = json.loads(row["results_json"] or "{}")
                except json.JSONDecodeError:
                    params, results = {}, {}
                records.append(
                    {
                        "domain": row["system"] or params.get("domain", "unknown"),
                        "model_complexity": float(params.get("model_complexity", 1.0)),
                        "dataset_size": float(params.get("dataset_size", 100.0)),
                        "method": row["module"] or params.get("method", "unknown"),
                        "historical_metrics": _numeric_mean(results),
                        "compute_cost": float(results.get("compute_cost", params.get("compute_cost", 1.0))),
                        "novelty_score": float(results.get("novelty_score", 0.5)),
                        "epistemic_gain": float(results.get("epistemic_gain", results.get("score", 0.1))),
                    }
                )
        return records


@dataclass
class ExperimentScheduler:
    engine: MetaLearningEngine
    meta_model: dict[str, Any]
    epsilon: float = 0.1

    def select_next_experiment(self, candidates: list[dict[str, Any]]) -> dict[str, Any]:
        rng = np.random.default_rng(self.engine.config_manager.get("physics.random_seed", 42))
        if rng.random() < self.epsilon:
            return candidates[int(rng.integers(0, len(candidates)))]
        scored = []
        for candidate in candidates:
            prediction = self.engine.predict_experiment_value(self.meta_model, candidate)
            cost = max(float(candidate.get("compute_cost", 1.0)), 1e-9)
            scored.append((prediction["predicted_gain"] / cost, candidate))
        return max(scored, key=lambda item: item[0])[1]


def _transform_context(meta_model: dict[str, Any], frame: pd.DataFrame) -> np.ndarray:
    categorical = frame[["domain", "method"]].astype(str)
    numeric = frame.drop(columns=["domain", "method"]).astype(float)
    return np.hstack([meta_model["encoder"].transform(categorical), numeric.to_numpy()])


def _records_signature(records: list[dict[str, Any]]) -> str:
    import hashlib

    payload = json.dumps(records, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _demo_history() -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    rows = []
    for idx in range(20):
        complexity = rng.uniform(0.5, 4.0)
        size = rng.integers(80, 1000)
        novelty = rng.uniform(0.1, 1.0)
        cost = rng.uniform(0.5, 10.0)
        gain = 0.25 * novelty + 0.15 * np.log1p(size) / 7.0 - 0.03 * cost + rng.normal(0, 0.03)
        rows.append(
            {
                "domain": ["lorenz", "rossler", "duffing"][idx % 3],
                "model_complexity": complexity,
                "dataset_size": size,
                "method": ["neural_ode", "pinn", "symbolic"][idx % 3],
                "historical_metrics": rng.uniform(0.3, 0.95),
                "compute_cost": cost,
                "novelty_score": novelty,
                "epistemic_gain": gain,
            }
        )
    return rows


def _candidate(domain: str, rng: np.random.Generator, idx: int, variant: int) -> dict[str, Any]:
    return {
        "id": f"{domain}_{idx}_{variant}",
        "domain": domain,
        "model_complexity": float(rng.uniform(0.5, 5.0)),
        "dataset_size": float(rng.integers(50, 1500)),
        "method": ["neural_ode", "pinn", "symbolic", "domain_adaptation"][variant % 4],
        "historical_metrics": float(rng.uniform(0.2, 0.95)),
        "compute_cost": float(rng.uniform(0.5, 12.0)),
        "novelty_score": float(rng.uniform(0.05, 1.0)),
    }


def _realized_gain(candidate: dict[str, Any], rng: np.random.Generator) -> float:
    return float(
        0.35 * candidate["novelty_score"]
        + 0.20 * candidate["historical_metrics"]
        + 0.10 * np.log1p(candidate["dataset_size"]) / 8.0
        - 0.04 * candidate["compute_cost"]
        + rng.normal(0.0, 0.04)
    )


def _complexity(experiment: dict[str, Any]) -> float:
    text = json.dumps(experiment, default=str)
    return float(min(10.0, max(1.0, len(text) / 300.0)))


def _metric_scalar(experiment: dict[str, Any]) -> float:
    return _numeric_mean(experiment)


def _numeric_mean(data: dict[str, Any]) -> float:
    values = []
    for value in data.values():
        if isinstance(value, (int, float)) and np.isfinite(value):
            values.append(float(value))
    return float(np.mean(values)) if values else 0.0


if __name__ == "__main__":
    print(json.dumps(MetaLearningEngine().run(), indent=2, default=str))
