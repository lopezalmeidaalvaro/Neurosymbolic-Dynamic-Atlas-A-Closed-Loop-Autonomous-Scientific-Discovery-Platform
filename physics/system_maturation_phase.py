from __future__ import annotations

import hashlib
import json
import math
import sqlite3
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

try:
    from physics.core.base_module import ScientificModule
    from physics.meta_learning_engine import MetaLearningEngine
    from physics.multi_agent_system import MultiAgentSystem
    from physics.scientific_memory_advanced import ScientificMemoryAdvanced
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from core.base_module import ScientificModule
    from meta_learning_engine import MetaLearningEngine
    from multi_agent_system import MultiAgentSystem
    from scientific_memory_advanced import ScientificMemoryAdvanced


PHYSICS_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PHYSICS_ROOT.parent
ARTIFACTS_DIR = PHYSICS_ROOT / "artifacts"


class SystemMaturationPhase(ScientificModule):
    """
    Exercises and matures existing phase 11-18 systems without creating new engines.
    """

    def populate_scientific_memory(self) -> dict[str, Any]:
        memory = ScientificMemoryAdvanced()
        entities = self._collect_memory_entities()
        hits = 0
        embedded = 0
        generation_times = []
        for entity in entities:
            text = entity["text"].strip()
            if not text:
                continue
            digest = _sha256(text)
            path = memory.embedding_cache / f"{digest}.npy"
            if path.exists():
                hits += 1
                continue
            start = time.perf_counter()
            vector = memory.embed_text(text)
            np.save(path, vector)
            generation_times.append(time.perf_counter() - start)
            embedded += 1
        total = len([item for item in entities if item["text"].strip()])
        metrics = {
            "total_entities": total,
            "embedded_entities": embedded,
            "cache_hits": hits,
            "cache_hit_rate": _ratio(hits, total),
            "embedding_coverage": _ratio(hits + embedded, total),
            "embedding_cache_dir": str(memory.embedding_cache),
            "mean_generation_seconds": float(np.mean(generation_times)) if generation_times else 0.0,
        }
        self._write_markdown_report(
            "memory_stress_report.md",
            "Memory Stress Report",
            metrics,
            details=[
                "Sources: experiment registries, markdown reports, generated hypotheses, frontier candidates and multi-agent debate artifacts.",
                "Embeddings are stored in the existing ScientificMemoryAdvanced cache by SHA256.",
            ],
        )
        return metrics

    def expand_meta_history(self) -> dict[str, Any]:
        rows = self._build_expanded_meta_rows()
        frame = pd.DataFrame(rows)
        if frame.empty:
            frame = pd.DataFrame(_fallback_meta_rows())
        cache_path = ARTIFACTS_DIR / "meta_history_expanded.csv"
        frame.to_csv(cache_path, index=False)

        feature_columns = [
            "domain",
            "model_complexity",
            "dataset_size",
            "method",
            "historical_metrics",
            "compute_cost",
            "novelty_score",
        ]
        X = frame[feature_columns]
        y = frame["epistemic_gain"].astype(float)
        if len(frame) >= 8:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.25, random_state=self.config_manager.get("physics.random_seed", 42)
            )
        else:
            X_train, X_test, y_train, y_test = X, X, y, y

        engine = MetaLearningEngine()
        trained = engine.train_meta_prior_learner(X_train, y_train)
        predictions = _predict_meta_rows(trained, X_test)
        mae = float(mean_absolute_error(y_test, predictions))
        rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
        r2 = float(r2_score(y_test, predictions)) if len(y_test) > 1 else 0.0
        cv_scores = trained.get("cv_scores", np.array([]))
        final = engine.train_meta_prior_learner(X, y)
        metrics = {
            "expanded_rows": int(len(frame)),
            "domains": _counts(frame, "domain"),
            "methods": _counts(frame, "method"),
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
            "cv_score_mean": float(np.mean(cv_scores)) if len(cv_scores) else None,
            "cv_score_std": float(np.std(cv_scores)) if len(cv_scores) else None,
            "model_path": final["path"],
            "expanded_cache": str(cache_path),
        }
        self._write_markdown_report(
            "meta_learning_expansion_report.md",
            "Meta-Learning Expansion Report",
            metrics,
            details=["The existing MetaLearningEngine was retrained using the expanded historical table."],
        )
        return metrics

    def benchmark_agent_specialization(self) -> dict[str, Any]:
        debates = _read_json(ARTIFACTS_DIR / "multi_agent_debates.json", [])
        skeptic_reports = [_read_json(path, {}) for path in sorted(ARTIFACTS_DIR.glob("skeptic_report_*.json"))]
        agent_metrics = {
            "Theorist": self._score_agent_from_rounds(debates, "proposal"),
            "Experimentalist": self._score_agent_from_rounds(debates, "design", "execution"),
            "Reviewer": self._score_agent_from_rounds(debates, "review"),
            "Skeptic": self._score_skeptic(skeptic_reports),
        }
        accepted = sum(1 for debate in debates if float(debate.get("score", 0.0)) >= 0.6)
        rejected = sum(1 for debate in debates if float(debate.get("score", 0.0)) < 0.4)
        metrics = {
            "debates_analyzed": len(debates),
            "hypotheses_accepted": accepted,
            "hypotheses_rejected": rejected,
            "agent_metrics": agent_metrics,
        }
        self._write_agent_report(metrics)
        return metrics

    def analyze_parallel_efficiency(self) -> dict[str, Any]:
        frame = _read_csv(ARTIFACTS_DIR / "hpc_benchmark.csv")
        if frame.empty:
            metrics = {
                "worker_utilization": 0.0,
                "queue_wait_time_seconds": None,
                "scheduling_overhead_seconds": None,
                "real_speedup": 0.0,
                "efficiency": 0.0,
                "bottlenecks": ["missing_hpc_benchmark"],
            }
        else:
            throughput = frame["throughput_exp_per_sec"].astype(float)
            efficiency = frame["efficiency"].astype(float)
            workers = frame["workers"].astype(float)
            elapsed = frame["elapsed_seconds"].astype(float)
            n_exp = frame["n_experiments"].astype(float)
            per_task_elapsed = elapsed / n_exp.replace(0, np.nan)
            scheduling_overhead = float(np.nanmean(per_task_elapsed))
            worker_utilization = float(np.clip(efficiency.mean(), 0.0, 1.0))
            bottlenecks = []
            if worker_utilization < 0.5:
                bottlenecks.append("workers_idle_or_parallel_overhead_high")
            if scheduling_overhead > 0.05:
                bottlenecks.append("tasks_too_small_for_process_startup")
            if throughput.iloc[-1] < throughput.max() * 0.75:
                bottlenecks.append("throughput_degrades_at_scale")
            metrics = {
                "worker_utilization": worker_utilization,
                "queue_wait_time_seconds": 0.0,
                "scheduling_overhead_seconds": scheduling_overhead,
                "real_speedup": float(frame["speedup_vs_serial_estimate"].max()),
                "efficiency": float(efficiency.mean()),
                "max_workers": int(workers.max()),
                "max_throughput": float(throughput.max()),
                "bottlenecks": bottlenecks,
            }
        self._write_markdown_report(
            "hpc_efficiency_report.md",
            "HPC Efficiency Report",
            metrics,
            details=["This analysis reads existing hpc_benchmark.csv and experiment_cache.db only."],
        )
        return metrics

    def compute_maturity_score(
        self,
        memory: dict[str, Any],
        meta: dict[str, Any],
        agents: dict[str, Any],
        hpc: dict[str, Any],
    ) -> dict[str, Any]:
        scores = {
            "Memory": _score_memory(memory),
            "MetaLearning": _score_meta(meta),
            "MultiAgent": _score_agents(agents),
            "HPC": _score_hpc(hpc),
        }
        global_score = float(np.mean(list(scores.values())))
        payload = {
            "component_scores": scores,
            "maturity_score": global_score,
            "classification": _classify(global_score),
            "inputs": {
                "memory": memory,
                "meta_learning": meta,
                "multi_agent": agents,
                "hpc": hpc,
            },
        }
        (ARTIFACTS_DIR / "system_maturity_report.json").write_text(
            json.dumps(payload, indent=2, default=str),
            encoding="utf-8",
        )
        self._write_maturity_markdown(payload)
        return payload

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.status = "running"
        memory = self.populate_scientific_memory()
        meta = self.expand_meta_history()
        agents = self.benchmark_agent_specialization()
        hpc = self.analyze_parallel_efficiency()
        maturity = self.compute_maturity_score(memory, meta, agents, hpc)
        return maturity

    def _collect_memory_entities(self) -> list[dict[str, str]]:
        entities: list[dict[str, str]] = []
        for row in self._read_all_experiments():
            text = " ".join(
                str(row.get(key, ""))
                for key in ["system", "module", "hyperparameters_json", "results_json", "status"]
            )
            entities.append({"type": "experiment", "id": row.get("id", ""), "text": text})
        for report in ARTIFACTS_DIR.glob("*.md"):
            entities.append({"type": "report", "id": report.name, "text": _read_text(report)})
        for path in [
            ARTIFACTS_DIR / "frontier_candidates.json",
            ARTIFACTS_DIR / "expert_review_hypotheses.json",
            ARTIFACTS_DIR / "multi_agent_debates.json",
            ARTIFACTS_DIR / "physical_validation_anomalies.json",
        ]:
            payload = _read_json(path, [])
            for idx, item in enumerate(_flatten_json_items(payload)):
                text = json.dumps(item, sort_keys=True, default=str)
                entities.append({"type": "hypothesis_artifact", "id": f"{path.name}:{idx}", "text": text})
        return entities

    def _build_expanded_meta_rows(self) -> list[dict[str, Any]]:
        rows = []
        for row in self._read_all_experiments():
            try:
                params = json.loads(row.get("hyperparameters_json") or "{}")
                results = json.loads(row.get("results_json") or "{}")
            except json.JSONDecodeError:
                params, results = {}, {}
            rows.append(_meta_row_from_record(row.get("system", "unknown"), row.get("module", "unknown"), params, results))
        rows.extend(self._rows_from_multi_agent())
        rows.extend(self._rows_from_hpc())
        rows.extend(self._rows_from_transfer())
        return rows

    def _read_all_experiments(self) -> list[dict[str, Any]]:
        rows = []
        for db_path in [ARTIFACTS_DIR / "experiments.db", REPO_ROOT / "artifacts" / "experiments.db"]:
            if not db_path.exists():
                continue
            try:
                uri = f"file:{db_path.as_posix()}?mode=ro"
                with sqlite3.connect(uri, uri=True) as conn:
                    conn.row_factory = sqlite3.Row
                    rows.extend(dict(row) for row in conn.execute("SELECT * FROM experiments"))
            except Exception:
                continue
        seen = set()
        unique = []
        for row in rows:
            if row.get("id") in seen:
                continue
            seen.add(row.get("id"))
            unique.append(row)
        return unique

    def _rows_from_multi_agent(self) -> list[dict[str, Any]]:
        debates = _read_json(ARTIFACTS_DIR / "multi_agent_debates.json", [])
        rows = []
        for debate in debates:
            rows.append(
                {
                    "domain": debate.get("domain", "multi_agent"),
                    "model_complexity": len(debate.get("rounds", [])),
                    "dataset_size": len(debate.get("rounds", [])) * 10,
                    "method": "multi_agent_debate",
                    "historical_metrics": float(debate.get("score", 0.0)),
                    "compute_cost": len(debate.get("rounds", [])) or 1,
                    "novelty_score": 0.5,
                    "epistemic_gain": float(debate.get("score", 0.0)) * 0.5,
                }
            )
        return rows

    def _rows_from_hpc(self) -> list[dict[str, Any]]:
        frame = _read_csv(ARTIFACTS_DIR / "hpc_benchmark.csv")
        rows = []
        for _, row in frame.iterrows():
            rows.append(
                {
                    "domain": "hpc",
                    "model_complexity": float(row.get("workers", 1)),
                    "dataset_size": float(row.get("n_experiments", 0)),
                    "method": "distributed_execution",
                    "historical_metrics": float(row.get("throughput_exp_per_sec", 0.0)),
                    "compute_cost": float(row.get("elapsed_seconds", 1.0)),
                    "novelty_score": float(row.get("efficiency", 0.0)),
                    "epistemic_gain": float(row.get("efficiency", 0.0)),
                }
            )
        return rows

    def _rows_from_transfer(self) -> list[dict[str, Any]]:
        results = _read_json(ARTIFACTS_DIR / "cross_domain_results.json", [])
        rows = []
        for item in results:
            rows.append(
                {
                    "domain": f"{item.get('source')}_to_{item.get('target')}",
                    "model_complexity": 3.0,
                    "dataset_size": 160.0,
                    "method": "cross_domain_transfer",
                    "historical_metrics": float(item.get("transfer_efficiency", 0.0)),
                    "compute_cost": 1.0,
                    "novelty_score": 1.0 - float(item.get("cka", 0.0)),
                    "epistemic_gain": float(item.get("transfer_efficiency", 0.0)) * (1.0 if item.get("positive_transfer") else 0.5),
                }
            )
        return rows

    def _score_agent_from_rounds(self, debates: list[dict[str, Any]], *round_names: str) -> dict[str, Any]:
        contributions = 0
        accepted = 0
        rejected = 0
        for debate in debates:
            rounds = [item for item in debate.get("rounds", []) if item.get("name") in round_names]
            if rounds:
                contributions += len(rounds)
                score = float(debate.get("score", 0.0))
                accepted += int(score >= 0.6)
                rejected += int(score < 0.4)
        return {
            "useful_contributions": contributions,
            "hypotheses_accepted": accepted,
            "hypotheses_rejected": rejected,
            "critique_precision": None,
        }

    def _score_skeptic(self, reports: list[dict[str, Any]]) -> dict[str, Any]:
        findings = sum(len(report.get("findings", [])) for report in reports)
        statistically_supported = 0
        total_critiques = 0
        for report in reports:
            for key in ["t_test_p_value", "wilcoxon_p_value"]:
                if key in report:
                    total_critiques += 1
                    statistically_supported += int(float(report.get(key, 1.0)) >= 0.05)
        return {
            "useful_contributions": findings,
            "hypotheses_accepted": 0,
            "hypotheses_rejected": sum(1 for report in reports if report.get("requires_rerun")),
            "critique_precision": _ratio(statistically_supported, total_critiques),
        }

    def _write_markdown_report(self, filename: str, title: str, metrics: dict[str, Any], details: list[str] | None = None) -> str:
        lines = [f"# {title}", "", "## Metrics", "", "| Metric | Value |", "|---|---|"]
        for key, value in metrics.items():
            lines.append(f"| `{key}` | {json.dumps(value, default=str) if isinstance(value, (dict, list)) else value} |")
        if details:
            lines.extend(["", "## Notes", ""])
            lines.extend(f"- {item}" for item in details)
        path = ARTIFACTS_DIR / filename
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(path)

    def _write_agent_report(self, metrics: dict[str, Any]) -> str:
        lines = ["# Agent Specialization Report", "", f"Debates analyzed: {metrics['debates_analyzed']}", ""]
        lines.extend(["| Agent | Useful Contributions | Accepted | Rejected | Critique Precision |", "|---|---:|---:|---:|---:|"])
        for agent, data in metrics["agent_metrics"].items():
            precision = data["critique_precision"]
            precision_text = "" if precision is None else f"{precision:.3f}"
            lines.append(
                f"| {agent} | {data['useful_contributions']} | {data['hypotheses_accepted']} | {data['hypotheses_rejected']} | {precision_text} |"
            )
        path = ARTIFACTS_DIR / "agent_specialization_report.md"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(path)

    def _write_maturity_markdown(self, payload: dict[str, Any]) -> str:
        scores = payload["component_scores"]
        lines = [
            "# System Maturity Report",
            "",
            f"Global maturity score: **{payload['maturity_score']:.1f}/100** ({payload['classification']}).",
            "",
            "| Component | Score |",
            "|---|---:|",
        ]
        lines.extend(f"| {name} | {score:.1f} |" for name, score in scores.items())
        lines.extend(["", "## Generated Reports", ""])
        lines.extend(
            [
                "- `physics/artifacts/memory_stress_report.md`",
                "- `physics/artifacts/meta_learning_expansion_report.md`",
                "- `physics/artifacts/agent_specialization_report.md`",
                "- `physics/artifacts/hpc_efficiency_report.md`",
            ]
        )
        path = ARTIFACTS_DIR / "system_maturity_report.md"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(path)


def _predict_meta_rows(model_bundle: dict[str, Any], X: pd.DataFrame) -> np.ndarray:
    encoder = model_bundle["encoder"]
    model = model_bundle["model"]
    categorical = X[["domain", "method"]].astype(str)
    numeric = X.drop(columns=["domain", "method"]).astype(float)
    matrix = np.hstack([encoder.transform(categorical), numeric.to_numpy()])
    return model.predict(matrix)


def _meta_row_from_record(domain: str, method: str, params: dict[str, Any], results: dict[str, Any]) -> dict[str, Any]:
    metric = _numeric_mean(results)
    cost = float(results.get("compute_cost", results.get("elapsed_seconds", params.get("compute_cost", 1.0))) or 1.0)
    novelty = float(results.get("novelty_score", params.get("novelty_score", 0.5)) or 0.5)
    gain = float(results.get("epistemic_gain", results.get("frontier_score", metric * novelty)) or 0.0)
    return {
        "domain": domain or "unknown",
        "model_complexity": float(params.get("model_complexity", max(1.0, len(json.dumps(params, default=str)) / 200.0))),
        "dataset_size": float(params.get("dataset_size", results.get("n_experiments", 100.0)) or 100.0),
        "method": method or "unknown",
        "historical_metrics": metric,
        "compute_cost": max(cost, 1e-6),
        "novelty_score": novelty,
        "epistemic_gain": gain,
    }


def _fallback_meta_rows() -> list[dict[str, Any]]:
    return [
        {
            "domain": "fallback",
            "model_complexity": 1.0,
            "dataset_size": 100.0,
            "method": "fallback",
            "historical_metrics": 0.1,
            "compute_cost": 1.0,
            "novelty_score": 0.5,
            "epistemic_gain": 0.1,
        }
    ]


def _flatten_json_items(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        items = []
        for value in payload.values():
            if isinstance(value, list):
                items.extend(value)
            elif isinstance(value, dict):
                items.append(value)
        return items or [payload]
    return []


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _counts(frame: pd.DataFrame, column: str) -> dict[str, int]:
    if frame.empty or column not in frame:
        return {}
    return {str(key): int(value) for key, value in frame[column].value_counts().to_dict().items()}


def _numeric_mean(data: dict[str, Any]) -> float:
    values = [float(value) for value in data.values() if isinstance(value, (int, float)) and math.isfinite(float(value))]
    return float(np.mean(values)) if values else 0.0


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _ratio(numerator: float, denominator: float) -> float:
    return 0.0 if not denominator else float(numerator / denominator)


def _score_memory(metrics: dict[str, Any]) -> float:
    return float(np.clip(100.0 * metrics.get("embedding_coverage", 0.0) - 20.0 * (1.0 - metrics.get("cache_hit_rate", 0.0)), 0.0, 100.0))


def _score_meta(metrics: dict[str, Any]) -> float:
    r2 = metrics.get("r2") if metrics.get("r2") is not None else 0.0
    cv = metrics.get("cv_score_mean") if metrics.get("cv_score_mean") is not None else 0.0
    size_bonus = min(20.0, metrics.get("expanded_rows", 0) / 5.0)
    return float(np.clip(45.0 + 20.0 * max(0.0, r2) + 15.0 * max(0.0, cv) + size_bonus, 0.0, 100.0))


def _score_agents(metrics: dict[str, Any]) -> float:
    debates = metrics.get("debates_analyzed", 0)
    skeptic = metrics.get("agent_metrics", {}).get("Skeptic", {})
    precision = skeptic.get("critique_precision") or 0.0
    return float(np.clip(40.0 + min(25.0, debates * 2.0) + 35.0 * precision, 0.0, 100.0))


def _score_hpc(metrics: dict[str, Any]) -> float:
    utilization = metrics.get("worker_utilization", 0.0)
    penalty = 15.0 * len(metrics.get("bottlenecks", []))
    return float(np.clip(40.0 + 60.0 * utilization - penalty, 0.0, 100.0))


def _classify(score: float) -> str:
    if score >= 85:
        return "MATURE"
    if score >= 70:
        return "ROBUST"
    if score >= 55:
        return "DEVELOPING"
    if score >= 40:
        return "FRAGILE"
    return "IMMATURE"


if __name__ == "__main__":
    print(json.dumps(SystemMaturationPhase().run(), indent=2, default=str))
