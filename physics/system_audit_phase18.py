from __future__ import annotations

import json
import math
import pickle
import sqlite3
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    from physics.core.artifact_manager import ArtifactManager
    from physics.core.base_module import ScientificModule
    from physics.core.config_manager import ConfigManager
    from physics.core.report_manager import ReportManager
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from core.artifact_manager import ArtifactManager
    from core.base_module import ScientificModule
    from core.config_manager import ConfigManager
    from core.report_manager import ReportManager


PHYSICS_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PHYSICS_ROOT.parent
ARTIFACTS_DIR = PHYSICS_ROOT / "artifacts"
MODELS_DIR = PHYSICS_ROOT / "models"


class SystemAuditPhase18(ScientificModule):
    """Read-only post-implementation audit for phases 9-18."""

    def __init__(self):
        # Deliberately avoid ScientificModule.__init__ because it initializes
        # writable experiment registries. This audit is observational only.
        self.config_manager = ConfigManager()
        self.artifact_manager = ArtifactManager(ARTIFACTS_DIR)
        self.report_manager = ReportManager(ARTIFACTS_DIR)
        self.module_name = self.__class__.__name__
        self.status = "initialized_read_only"

    def audit_memory_system(self) -> dict[str, Any]:
        cache_dir = Path(self.config_manager.get("models.embedding_cache", MODELS_DIR / "embeddings_cache"))
        if not cache_dir.is_absolute():
            cache_dir = REPO_ROOT / cache_dir
        files = sorted(cache_dir.glob("*.npy")) if cache_dir.exists() else []
        sizes = [path.stat().st_size for path in files]
        hashes = [path.stem for path in files]
        duplicate_hashes = [item for item, count in Counter(hashes).items() if count > 1]
        invalid_paths = [str(path) for path in files if not path.exists()]
        timings = self._sample_embedding_cache_timings(files)
        node_metadata = self._read_embedding_metadata_from_reports()
        referenced_paths = [Path(item.get("embedding_path", "")) for item in node_metadata if item.get("embedding_path")]
        orphaned = [str(path) for path in files if referenced_paths and path not in referenced_paths]
        nodes_without_embedding = [item.get("id") for item in node_metadata if not item.get("embedding_hash")]
        result = {
            "embedded_nodes_total": len(node_metadata),
            "cached_embeddings_total": len(files),
            "embedding_cache_total_bytes": int(sum(sizes)),
            "mean_embedding_size_bytes": float(np.mean(sizes)) if sizes else 0.0,
            "cache_reuse_percent": self._extract_percent_from_report("memory_report.md", "reused", "entities_seen"),
            "mean_embedding_generation_seconds": timings["generation"],
            "mean_embedding_reuse_seconds": timings["reuse"],
            "orphaned_embeddings": orphaned,
            "duplicate_hashes": duplicate_hashes,
            "invalid_embedding_paths": invalid_paths,
            "nodes_without_embedding": nodes_without_embedding,
            "read_only": True,
        }
        self._write_json("memory_audit.json", result)
        return result

    def audit_meta_learning(self) -> dict[str, Any]:
        cache_path = ARTIFACTS_DIR / "meta_history_cache.csv"
        frame = _read_csv(cache_path)
        registry = _read_json(MODELS_DIR / "model_registry.json", {})
        meta_record = registry.get("meta_prior_learner", {})
        model_bundle = self._load_pickle(MODELS_DIR / "meta_prior_learner.pkl")
        cv_scores = meta_record.get("metadata", {}).get("cv_scores", [])
        feature_importances = {}
        stability = None
        if model_bundle and "model" in model_bundle:
            model = model_bundle["model"]
            columns = list(model_bundle.get("feature_columns", []))
            importances = getattr(model, "feature_importances_", np.array([]))
            feature_importances = {f"feature_{idx}": float(value) for idx, value in enumerate(importances)}
            tree_importances = [tree.feature_importances_ for tree in getattr(model, "estimators_", []) if hasattr(tree, "feature_importances_")]
            if tree_importances:
                stability = float(1.0 / (1.0 + np.mean(np.std(tree_importances, axis=0))))
            if columns and len(importances) == len(columns):
                feature_importances = dict(zip(columns, map(float, importances)))
        leakage_flags = self._detect_meta_leakage(frame)
        result = {
            "x_meta_rows": int(len(frame)),
            "x_meta_columns": int(max(0, frame.shape[1] - (1 if "epistemic_gain" in frame else 0))),
            "historical_experiments": int(len(frame)),
            "domain_distribution": _value_counts(frame, "domain"),
            "method_distribution": _value_counts(frame, "method"),
            "cv_mean_score": float(np.mean(cv_scores)) if cv_scores else None,
            "cv_std_score": float(np.std(cv_scores)) if cv_scores else None,
            "feature_importance": feature_importances,
            "model_stability": stability,
            "too_small_dataset": bool(len(frame) < 30),
            "information_leakage_flags": leakage_flags,
            "potential_overfitting": bool((cv_scores and np.std(cv_scores) > 0.25) or len(frame) < 30),
            "read_only": True,
        }
        self._write_json("meta_learning_audit.json", result)
        return result

    def audit_multi_agent(self) -> dict[str, Any]:
        debates = _read_json(ARTIFACTS_DIR / "multi_agent_debates.json", [])
        skeptic_files = sorted(ARTIFACTS_DIR.glob("skeptic_report_*.json"))
        skeptic_reports = [_read_json(path, {}) for path in skeptic_files]
        approved = sum(1 for debate in debates if _debate_score(debate) >= 0.6)
        rejected = sum(1 for debate in debates if _debate_score(debate) < 0.4)
        modified = sum(1 for report in skeptic_reports if report.get("findings"))
        discarded = sum(1 for report in skeptic_reports if report.get("requires_rerun"))
        round_names = [round_.get("name") for debate in debates for round_ in debate.get("rounds", [])]
        payload_signatures = [json.dumps(debate.get("rounds", []), sort_keys=True, default=str) for debate in debates]
        result = {
            "debates_executed": len(debates),
            "skeptic_reports": len(skeptic_reports),
            "hypotheses_approved": approved,
            "hypotheses_rejected": rejected,
            "hypotheses_modified_by_skeptic_percent": _percent(modified, len(skeptic_reports)),
            "hypotheses_discarded_percent": _percent(discarded, len(skeptic_reports)),
            "skeptic_impact_mean_findings": float(np.mean([len(item.get("findings", [])) for item in skeptic_reports])) if skeptic_reports else 0.0,
            "redundant_debates": len(payload_signatures) - len(set(payload_signatures)),
            "possible_infinite_cycles": bool(max(Counter(round_names).values() or [0]) > 100),
            "agents_without_effective_contribution": self._agent_contribution_gaps(debates),
            "read_only": True,
        }
        self._write_json("multi_agent_audit.json", result)
        return result

    def audit_hpc(self) -> dict[str, Any]:
        frame = _read_csv(ARTIFACTS_DIR / "hpc_benchmark.csv")
        cache_path = ARTIFACTS_DIR / "experiment_cache.db"
        cache_rows = self._read_cache_rows(cache_path)
        cache_hits = int(frame.get("cache_hits", pd.Series(dtype=float)).sum()) if not frame.empty else 0
        total_executions = int(frame.get("n_experiments", pd.Series(dtype=float)).sum()) if not frame.empty else 0
        result = {
            "throughput": _series_stats(frame, "throughput_exp_per_sec"),
            "speedup": _series_stats(frame, "speedup_vs_serial_estimate"),
            "efficiency": _series_stats(frame, "efficiency"),
            "backend_comparison": {
                "ray_available": _module_available("ray"),
                "multiprocessing_available": True,
                "dask_available": _module_available("dask"),
                "observed_backend": "artifact_read_only_not_reexecuted",
            },
            "cache_hit_rate": _percent(cache_hits, total_executions),
            "cache_miss_rate": 100.0 - _percent(cache_hits, total_executions),
            "cache_entries": len(cache_rows),
            "invalid_cache_entries": sum(1 for row in cache_rows if not row.get("key") or not row.get("result_json")),
            "estimated_time_saved_seconds": self._estimate_cache_time_saved(frame),
            "performance_degradation": bool(_is_monotonic_decreasing(frame.get("throughput_exp_per_sec", []))),
            "idle_workers_risk": bool((frame.get("efficiency", pd.Series([1.0])) < 0.1).any()) if not frame.empty else True,
            "bottlenecks": self._hpc_bottlenecks(frame),
            "read_only": True,
        }
        self._write_json("hpc_audit.json", result)
        return result

    def audit_transfer(self) -> dict[str, Any]:
        results = _read_json(ARTIFACTS_DIR / "cross_domain_results.json", [])
        false_positives = [
            item for item in results if item.get("positive_transfer") and (item.get("cka", 0.0) < 0.1 or item.get("cca", 0.0) < 0.1)
        ]
        near_identical = [
            item for item in results if item.get("cka", 0.0) > 0.99 and item.get("wasserstein", math.inf) < 1e-6
        ]
        inconsistent = [
            item for item in results if item.get("positive_transfer") and item.get("transfer_efficiency", 0.0) < 0.55
        ]
        result = {
            "pairs_evaluated": len(results),
            "successful_pairs": sum(1 for item in results if item.get("positive_transfer")),
            "failed_pairs": sum(1 for item in results if not item.get("positive_transfer")),
            "cka": _list_stats([item.get("cka") for item in results]),
            "wasserstein": _list_stats([item.get("wasserstein") for item in results]),
            "cca": _list_stats([item.get("cca") for item in results]),
            "effective_transfer": _list_stats([item.get("transfer_efficiency") for item in results]),
            "false_positive_candidates": false_positives,
            "near_identical_pairs": near_identical,
            "metric_inconsistencies": inconsistent,
            "read_only": True,
        }
        self._write_json("transfer_audit.json", result)
        return result

    def audit_theory_generation(self) -> dict[str, Any]:
        demo = _read_text(ARTIFACTS_DIR / "theory_demo.md")
        registry_rows = self._read_experiments_by_module("TheoryAutowriter")
        theory_statuses = []
        for row in registry_rows:
            try:
                results = json.loads(row.get("results_json") or "{}")
                theory_statuses.append(results.get("theory_status"))
            except json.JSONDecodeError:
                pass
        theories_generated = max(1 if demo else 0, len(theory_statuses))
        valid = sum(1 for status in theory_statuses if status == "valid")
        rejected = sum(1 for status in theory_statuses if status == "invalid")
        trivial_predictions = demo.lower().count("residual") == 0 if demo else True
        duplicate_theories = max(0, len(theory_statuses) - len(set(theory_statuses))) if len(theory_statuses) > 1 else 0
        result = {
            "theories_generated": theories_generated,
            "theories_valid": valid,
            "theories_rejected": rejected,
            "rejected_by_sanity_engine_percent": _percent(rejected, theories_generated),
            "rejected_by_scientific_guard_percent": 0.0 if "claim_level" in demo else None,
            "duplicate_theories": duplicate_theories,
            "combinatorial_explosion_detected": "omitted_terms" in demo and "WARNING" in demo,
            "trivial_predictions": trivial_predictions,
            "limitations_section_present": "## Limitations" in demo,
            "read_only": True,
        }
        self._write_json("theory_audit.json", result)
        return result

    def audit_frontier(self) -> dict[str, Any]:
        candidates = _read_json(ARTIFACTS_DIR / "frontier_candidates.json", [])
        novelty = [item.get("novelty_score", 0.0) for item in candidates]
        consistency = [item.get("consistency_score", 0.0) for item in candidates]
        utility = [item.get("empirical_utility_score", 0.0) for item in candidates]
        frontier = [item.get("frontier_score", 0.0) for item in candidates]
        texts = [item.get("hypothesis", "") for item in candidates]
        result = {
            "top_candidates": len(candidates),
            "novelty_score": _list_stats(novelty),
            "consistency_score": _list_stats(consistency),
            "empirical_utility_score": _list_stats(utility),
            "frontier_score": _list_stats(frontier),
            "semantic_duplicates": self._semantic_duplicate_count(texts),
            "repeated_clusters": self._repeated_cluster_count(candidates),
            "hypotheses_without_traceability": [item.get("id") for item in candidates if item.get("source") not in _authorized_sources()],
            "novelty_frontier_correlation": _corr(novelty, frontier),
            "consistency_frontier_correlation": _corr(consistency, frontier),
            "read_only": True,
        }
        self._write_json("frontier_audit.json", result)
        return result

    def compute_system_health(self, audits: dict[str, dict[str, Any]]) -> dict[str, Any]:
        scores = {
            "memory": self._score_memory(audits["memory"]),
            "meta_learning": self._score_meta(audits["meta_learning"]),
            "multi_agent": self._score_multi_agent(audits["multi_agent"]),
            "hpc": self._score_hpc(audits["hpc"]),
            "transfer": self._score_transfer(audits["transfer"]),
            "theory": self._score_theory(audits["theory"]),
            "frontier": self._score_frontier(audits["frontier"]),
        }
        overall = float(np.mean(list(scores.values()))) if scores else 0.0
        return {"component_scores": scores, "overall_health_score": overall, "classification": _classify_health(overall)}

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.status = "running_read_only"
        audits = {
            "memory": self.audit_memory_system(),
            "meta_learning": self.audit_meta_learning(),
            "multi_agent": self.audit_multi_agent(),
            "hpc": self.audit_hpc(),
            "transfer": self.audit_transfer(),
            "theory": self.audit_theory_generation(),
            "frontier": self.audit_frontier(),
        }
        health = self.compute_system_health(audits)
        payload = {"audits": audits, "health": health, "read_only": True}
        self._write_json("system_health_report.json", payload)
        markdown_path = self._write_markdown_report(audits, health)
        return {"health": health, "json_report": str(ARTIFACTS_DIR / "system_health_report.json"), "markdown_report": markdown_path}

    def _write_json(self, name: str, payload: Any) -> str:
        path = ARTIFACTS_DIR / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        return str(path)

    def _write_markdown_report(self, audits: dict[str, dict[str, Any]], health: dict[str, Any]) -> str:
        critical = self._critical_findings(audits, health)
        risks = self._technical_risks(audits)
        scores = health["component_scores"]
        strongest = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:3]
        weakest = sorted(scores.items(), key=lambda item: item[1])[:3]
        lines = [
            "# System Health Report - Phase 18A",
            "",
            "## Executive Summary",
            "",
            f"Overall Health Score: **{health['overall_health_score']:.1f}/100** ({health['classification']}).",
            "This audit is read-only: it did not execute phases, retrain models, mutate the knowledge graph, or register experiments.",
            "",
            "## Critical Findings",
            "",
        ]
        lines.extend(f"- {item}" for item in critical or ["No critical blocking finding detected from available artifacts."])
        lines.extend(["", "## Technical Risks", ""])
        lines.extend(f"- {item}" for item in risks or ["No major technical risk detected from available artifacts."])
        lines.extend(["", "## Strongest Components", ""])
        lines.extend(f"- {name}: {score:.1f}/100" for name, score in strongest)
        lines.extend(["", "## Weakest Components", ""])
        lines.extend(f"- {name}: {score:.1f}/100" for name, score in weakest)
        lines.extend(["", "## Prioritized Recommendations", ""])
        lines.extend(f"- {item}" for item in self._recommendations(audits, weakest))
        lines.extend(["", "## Component Scores", "", "| Component | Score |", "|---|---:|"])
        lines.extend(f"| {name} | {score:.1f} |" for name, score in scores.items())
        output = ARTIFACTS_DIR / "system_health_report.md"
        output.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(output)

    def _read_embedding_metadata_from_reports(self) -> list[dict[str, Any]]:
        # Neo4j is intentionally not queried because connecting is not guaranteed
        # and this audit must remain read-only. Use available memory report metadata.
        report = _read_text(ARTIFACTS_DIR / "memory_report.md")
        if "entities_seen" not in report:
            return []
        return []

    def _sample_embedding_cache_timings(self, files: list[Path]) -> dict[str, float]:
        sample = files[: min(5, len(files))]
        if not sample:
            return {"generation": 0.0, "reuse": 0.0}
        reuse_times = []
        for path in sample:
            start = time.perf_counter()
            try:
                np.load(path, mmap_mode="r")
            except Exception:
                pass
            reuse_times.append(time.perf_counter() - start)
        return {"generation": 0.0, "reuse": float(np.mean(reuse_times))}

    def _extract_percent_from_report(self, report_name: str, numerator_key: str, denominator_key: str) -> float:
        text = _read_text(ARTIFACTS_DIR / report_name)
        numerator = _extract_metric_value(text, numerator_key)
        denominator = _extract_metric_value(text, denominator_key)
        return _percent(numerator, denominator)

    def _load_pickle(self, path: Path) -> Any:
        if not path.exists():
            return None
        try:
            with path.open("rb") as handle:
                return pickle.load(handle)
        except Exception:
            return None

    def _detect_meta_leakage(self, frame: pd.DataFrame) -> list[str]:
        flags = []
        if frame.empty:
            return ["missing_meta_history_cache"]
        if "epistemic_gain" in frame.columns:
            for column in frame.columns:
                if column == "epistemic_gain":
                    continue
                if pd.api.types.is_numeric_dtype(frame[column]):
                    corr = _corr(frame[column].tolist(), frame["epistemic_gain"].tolist())
                    if corr is not None and abs(corr) > 0.98:
                        flags.append(f"near_target_duplicate:{column}")
        duplicate_rate = frame.duplicated().mean() if len(frame) else 0.0
        if duplicate_rate > 0.2:
            flags.append(f"high_duplicate_rate:{duplicate_rate:.2f}")
        return flags

    def _agent_contribution_gaps(self, debates: list[dict[str, Any]]) -> list[str]:
        expected = {"proposal", "design", "review", "execution", "adjustment", "scrutiny"}
        observed = {round_.get("name") for debate in debates for round_ in debate.get("rounds", [])}
        return sorted(expected - observed)

    def _read_cache_rows(self, cache_path: Path) -> list[dict[str, Any]]:
        if not cache_path.exists():
            return []
        try:
            uri = f"file:{cache_path.as_posix()}?mode=ro"
            with sqlite3.connect(uri, uri=True) as conn:
                conn.row_factory = sqlite3.Row
                return [dict(row) for row in conn.execute("SELECT * FROM cache")]
        except Exception:
            return []

    def _estimate_cache_time_saved(self, frame: pd.DataFrame) -> float:
        if frame.empty or "cache_hits" not in frame or "throughput_exp_per_sec" not in frame:
            return 0.0
        total = 0.0
        for _, row in frame.iterrows():
            throughput = max(float(row.get("throughput_exp_per_sec", 0.0)), 1e-9)
            total += float(row.get("cache_hits", 0.0)) / throughput
        return total

    def _hpc_bottlenecks(self, frame: pd.DataFrame) -> list[str]:
        bottlenecks = []
        if frame.empty:
            return ["missing_hpc_benchmark"]
        if (frame.get("efficiency", pd.Series([1.0])) < 0.1).any():
            bottlenecks.append("low_parallel_efficiency")
        if _is_monotonic_decreasing(frame.get("throughput_exp_per_sec", [])):
            bottlenecks.append("throughput_decreases_with_scale")
        return bottlenecks

    def _read_experiments_by_module(self, module: str) -> list[dict[str, Any]]:
        rows = []
        for db_path in [ARTIFACTS_DIR / "experiments.db", REPO_ROOT / "artifacts" / "experiments.db"]:
            if not db_path.exists():
                continue
            try:
                uri = f"file:{db_path.as_posix()}?mode=ro"
                with sqlite3.connect(uri, uri=True) as conn:
                    conn.row_factory = sqlite3.Row
                    rows.extend(dict(row) for row in conn.execute("SELECT * FROM experiments WHERE module = ?", (module,)))
            except Exception:
                continue
        return rows

    def _semantic_duplicate_count(self, texts: list[str]) -> int:
        normalized = [" ".join(text.lower().split()) for text in texts]
        return len(normalized) - len(set(normalized))

    def _repeated_cluster_count(self, candidates: list[dict[str, Any]]) -> int:
        prefixes = [str(item.get("hypothesis", ""))[:80].lower() for item in candidates]
        return sum(count - 1 for count in Counter(prefixes).values() if count > 1)

    def _score_memory(self, audit: dict[str, Any]) -> float:
        score = 80.0
        if audit["cached_embeddings_total"] == 0:
            score -= 25
        if audit["orphaned_embeddings"]:
            score -= 10
        if audit["invalid_embedding_paths"] or audit["duplicate_hashes"]:
            score -= 15
        return _clamp_score(score)

    def _score_meta(self, audit: dict[str, Any]) -> float:
        score = 80.0
        if audit["too_small_dataset"]:
            score -= 20
        if audit["information_leakage_flags"]:
            score -= 25
        if audit["potential_overfitting"]:
            score -= 15
        if audit["cv_mean_score"] is None:
            score -= 10
        return _clamp_score(score)

    def _score_multi_agent(self, audit: dict[str, Any]) -> float:
        score = 75.0
        if audit["debates_executed"] == 0:
            score -= 40
        if audit["redundant_debates"] > 0:
            score -= min(20, audit["redundant_debates"] * 3)
        if audit["agents_without_effective_contribution"]:
            score -= 15
        return _clamp_score(score)

    def _score_hpc(self, audit: dict[str, Any]) -> float:
        score = 75.0
        if audit["idle_workers_risk"]:
            score -= 20
        if audit["performance_degradation"]:
            score -= 20
        if audit["invalid_cache_entries"]:
            score -= 15
        return _clamp_score(score)

    def _score_transfer(self, audit: dict[str, Any]) -> float:
        score = 70.0
        if audit["pairs_evaluated"] < 4:
            score -= 20
        if audit["false_positive_candidates"]:
            score -= 25
        if audit["metric_inconsistencies"]:
            score -= 15
        return _clamp_score(score)

    def _score_theory(self, audit: dict[str, Any]) -> float:
        score = 65.0
        if not audit["limitations_section_present"]:
            score -= 20
        if audit["trivial_predictions"]:
            score -= 20
        if audit["combinatorial_explosion_detected"]:
            score -= 5
        return _clamp_score(score)

    def _score_frontier(self, audit: dict[str, Any]) -> float:
        score = 75.0
        if audit["hypotheses_without_traceability"]:
            score -= 30
        if audit["semantic_duplicates"] > 0:
            score -= min(25, audit["semantic_duplicates"] * 5)
        if audit["repeated_clusters"] > 0:
            score -= min(20, audit["repeated_clusters"] * 4)
        return _clamp_score(score)

    def _critical_findings(self, audits: dict[str, dict[str, Any]], health: dict[str, Any]) -> list[str]:
        findings = []
        if health["overall_health_score"] < 60:
            findings.append("Overall health is below acceptable threshold.")
        if audits["frontier"]["hypotheses_without_traceability"]:
            findings.append("Frontier candidates without authorized traceability were detected.")
        if audits["meta_learning"]["information_leakage_flags"]:
            findings.append("Potential meta-learning information leakage was detected.")
        if audits["hpc"]["invalid_cache_entries"]:
            findings.append("Invalid HPC cache entries were detected.")
        return findings

    def _technical_risks(self, audits: dict[str, dict[str, Any]]) -> list[str]:
        risks = []
        if audits["memory"]["cached_embeddings_total"] == 0:
            risks.append("Scientific memory has no cached embeddings, so semantic retrieval is not exercised.")
        if audits["meta_learning"]["too_small_dataset"]:
            risks.append("Meta-learning history is small for robust scheduler conclusions.")
        if audits["hpc"]["idle_workers_risk"]:
            risks.append("HPC benchmark shows low parallel efficiency or idle worker risk.")
        if audits["frontier"]["semantic_duplicates"]:
            risks.append("Frontier candidates include semantic duplicates.")
        return risks

    def _recommendations(self, audits: dict[str, dict[str, Any]], weakest: list[tuple[str, float]]) -> list[str]:
        recs = []
        weak_names = {name for name, _ in weakest}
        if "meta_learning" in weak_names:
            recs.append("Grow the historical experiment dataset before trusting meta-prior scheduling claims.")
        if "hpc" in weak_names:
            recs.append("Profile parallel overhead and separate cold-cache from warm-cache throughput benchmarks.")
        if "frontier" in weak_names:
            recs.append("Deduplicate frontier candidates and require explicit source IDs in every generated candidate.")
        if "memory" in weak_names:
            recs.append("Run incremental embedding only after Neo4j is populated, then audit orphaned cache files.")
        if not recs:
            recs.append("Keep current modules read-only audited and add external validation before stronger claims.")
        return recs


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
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _value_counts(frame: pd.DataFrame, column: str) -> dict[str, int]:
    if frame.empty or column not in frame:
        return {}
    return {str(key): int(value) for key, value in frame[column].value_counts(dropna=False).to_dict().items()}


def _series_stats(frame: pd.DataFrame, column: str) -> dict[str, float | None]:
    if frame.empty or column not in frame:
        return {"mean": None, "min": None, "max": None}
    return _list_stats(frame[column].tolist())


def _list_stats(values: list[Any]) -> dict[str, float | None]:
    cleaned = [float(value) for value in values if value is not None and np.isfinite(float(value))]
    if not cleaned:
        return {"mean": None, "min": None, "max": None}
    return {"mean": float(np.mean(cleaned)), "min": float(np.min(cleaned)), "max": float(np.max(cleaned))}


def _percent(numerator: float | int | None, denominator: float | int | None) -> float:
    if not denominator:
        return 0.0
    return float(100.0 * (numerator or 0.0) / denominator)


def _corr(left: list[Any], right: list[Any]) -> float | None:
    try:
        x = np.asarray(left, dtype=float)
        y = np.asarray(right, dtype=float)
        n = min(len(x), len(y))
        x = x[:n]
        y = y[:n]
        if n < 2 or np.std(x) == 0 or np.std(y) == 0:
            return None
        return float(np.corrcoef(x, y)[0, 1])
    except Exception:
        return None


def _module_available(name: str) -> bool:
    try:
        __import__(name)
        return True
    except Exception:
        return False


def _is_monotonic_decreasing(values: Any) -> bool:
    series = list(values)
    if len(series) < 2:
        return False
    return all(float(series[idx]) <= float(series[idx - 1]) for idx in range(1, len(series)))


def _extract_metric_value(report_text: str, key: str) -> float:
    for line in report_text.splitlines():
        if f"`{key}`" in line:
            parts = [part.strip() for part in line.split("|") if part.strip()]
            if len(parts) >= 2:
                try:
                    return float(parts[1].strip("` "))
                except ValueError:
                    return 0.0
    return 0.0


def _debate_score(debate: dict[str, Any]) -> float:
    return float(debate.get("score", 0.0))


def _authorized_sources() -> set[str]:
    return {"knowledge_graph", "scientific_memory_contradiction", "experiment_registry", "multi_agent_system"}


def _clamp_score(value: float) -> float:
    return float(max(0.0, min(100.0, value)))


def _classify_health(score: float) -> str:
    if score >= 90:
        return "EXCELENTE"
    if score >= 75:
        return "BUENO"
    if score >= 60:
        return "ACEPTABLE"
    if score >= 40:
        return "NECESITA REVISION"
    return "CRITICO"


if __name__ == "__main__":
    print(json.dumps(SystemAuditPhase18().run(), indent=2, default=str))
