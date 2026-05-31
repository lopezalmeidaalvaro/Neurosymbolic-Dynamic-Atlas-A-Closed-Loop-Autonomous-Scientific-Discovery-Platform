from __future__ import annotations

import json
import pickle
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    from physics.core.base_module import ScientificModule
    from physics.cross_domain_transfer import CrossDomainTransfer
    from physics.distributed_execution import DistributedExecution
    from physics.domain_adaptation import DomainAdaptation
    from physics.frontier_discovery import FrontierDiscovery
    from physics.knowledge_graph import ScientificKnowledgeGraph
    from physics.meta_learning_engine import MetaLearningEngine
    from physics.multi_agent_system import MultiAgentSystem
    from physics.physics_sanity_engine import PhysicsSanityEngine
    from physics.scientific_guard import assign_claim_level
    from physics.scientific_memory_advanced import ScientificMemoryAdvanced
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from core.base_module import ScientificModule
    from cross_domain_transfer import CrossDomainTransfer
    from distributed_execution import DistributedExecution
    from domain_adaptation import DomainAdaptation
    from frontier_discovery import FrontierDiscovery
    from knowledge_graph import ScientificKnowledgeGraph
    from meta_learning_engine import MetaLearningEngine
    from multi_agent_system import MultiAgentSystem
    from physics_sanity_engine import PhysicsSanityEngine
    from scientific_guard import assign_claim_level
    from scientific_memory_advanced import ScientificMemoryAdvanced


PHYSICS_ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = PHYSICS_ROOT / "artifacts"
MODELS_DIR = PHYSICS_ROOT / "models"


class AutonomousScientificCycle(ScientificModule):
    """Closed-loop coordinator over existing discovery, validation, memory and learning systems."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frontier = FrontierDiscovery()
        self.meta = MetaLearningEngine()
        self.memory = ScientificMemoryAdvanced()
        self.multi_agent = MultiAgentSystem()
        self.sanity = PhysicsSanityEngine()
        self.distributed = DistributedExecution()
        self.domain_adapter = DomainAdaptation()
        self.cross_domain = CrossDomainTransfer()
        self.kg = ScientificKnowledgeGraph()
        self.rng = np.random.default_rng(self.config_manager.get("physics.random_seed", 42))

    def generate_candidate_hypotheses(self, domain: str = "multi") -> list[dict[str, Any]]:
        candidates = []
        candidates.extend(self._frontier_candidates(domain))
        candidates.extend(self._open_memory_contradictions())
        candidates.extend(self._pending_kg_hypotheses())
        candidates.extend(self._recent_multi_agent_proposals(domain))
        unique = {}
        timestamp = datetime.now().isoformat(timespec="seconds")
        for candidate in candidates:
            normalized = self._normalize_candidate(candidate, domain, timestamp)
            key = normalized["hypothesis"].strip().lower()
            if key and key not in unique:
                unique[key] = normalized
        result = list(unique.values())
        self.artifact_manager.save_json("autonomous_cycle_candidates.json", result)
        return result

    def prioritize_hypotheses(self, hypotheses: list[dict[str, Any]], top_k: int = 10) -> list[dict[str, Any]]:
        meta_model = self._load_meta_model()
        ranked = []
        for hypothesis in hypotheses:
            context = self._context_from_hypothesis(hypothesis)
            if meta_model is not None:
                prediction = self.meta.predict_experiment_value(meta_model, context)
            else:
                prediction = {
                    "predicted_gain": float(hypothesis.get("novelty_score", 0.3)) * 0.5,
                    "uncertainty": 0.25,
                    "ci_low": 0.0,
                    "ci_high": 1.0,
                }
            compute_cost = max(float(context.get("compute_cost", 1.0)), 1e-9)
            enriched = {
                **hypothesis,
                **prediction,
                "compute_cost_estimate": compute_cost,
                "priority_score": prediction["predicted_gain"] / compute_cost,
            }
            ranked.append(enriched)
        ranked = sorted(ranked, key=lambda item: item["priority_score"], reverse=True)
        self.artifact_manager.save_json("autonomous_cycle_ranking.json", ranked)
        return ranked[:top_k]

    def pre_validate_hypotheses(self, hypotheses: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        accepted = []
        rejected = []
        for hypothesis in hypotheses:
            sanity_result = self.sanity.validate_hypothesis(hypothesis)
            claim = assign_claim_level(hypothesis["hypothesis"], hypothesis.get("source", "autonomous_cycle"))
            warnings = []
            for check in sanity_result.get("checks", {}).values():
                warnings.extend(check.get("warnings", []))
            enriched = {
                **hypothesis,
                "physics_sanity_score": float(sanity_result.get("score", 0.0)),
                "claim_level": claim,
                "warnings": warnings,
            }
            if sanity_result.get("accepted"):
                accepted.append(enriched)
            else:
                enriched["rejection_reason"] = "physics_sanity_score_below_threshold"
                rejected.append(enriched)
        self.artifact_manager.save_json("autonomous_cycle_prevalidation.json", {"accepted": accepted, "rejected": rejected})
        return accepted, rejected

    def design_experiments(self, hypotheses: list[dict[str, Any]], domain: str = "multi") -> list[dict[str, Any]]:
        protocols = []
        for idx, hypothesis in enumerate(hypotheses):
            design = self.multi_agent.experimentalist.design(hypothesis, n_trials=10)
            review_stub = {"mean_improvement": float(hypothesis.get("predicted_gain", 0.0))}
            review = self.multi_agent.reviewer.review(hypothesis, design, review_stub)
            skeptic = {
                "statistical_power_review": "requires multiple seeds and paired tests",
                "requested_seeds": [7, 13, 23],
                "known_bias_checks": ["data_leakage", "spurious_correlation", "seed_sensitivity"],
            }
            protocols.append(
                {
                    "id": f"protocol_{idx}",
                    "domain": domain,
                    "hypothesis_id": hypothesis["id"],
                    "hypothesis": hypothesis,
                    "design": design,
                    "review": review,
                    "skeptic_requirements": skeptic,
                }
            )
        self.artifact_manager.save_json("autonomous_cycle_protocols.json", protocols)
        return protocols

    def execute_experiments(self, protocols: list[dict[str, Any]]) -> list[dict[str, Any]]:
        start = time.perf_counter()
        if not protocols:
            return []
        use_hpc = len(protocols) >= 12
        results = []
        if use_hpc:
            experiments = [
                {
                    "id": protocol["id"],
                    "version": "autonomous_cycle_v1",
                    "module_path": str(Path(__file__).resolve()),
                    "params": {
                        "x": 1.0 + idx / max(1, len(protocols)),
                        "n": 1500,
                        "hypothesis_id": protocol["hypothesis_id"],
                    },
                }
                for idx, protocol in enumerate(protocols)
            ]
            raw_results = self.distributed.parallel_experiment_executor(experiments, max_concurrent=min(4, len(experiments)))
            for protocol, raw in zip(protocols, raw_results):
                results.append(self._result_from_protocol(protocol, raw, "distributed"))
        else:
            for protocol in protocols:
                raw = self.multi_agent.experimentalist.execute(protocol["design"], seed=42)
                results.append(self._result_from_protocol(protocol, raw, "sequential"))
        duration = time.perf_counter() - start
        for result in results:
            result["duration_seconds"] = duration / max(1, len(results))
            result["resources_used"] = "distributed_execution" if use_hpc else "sequential_cpu"
        self.artifact_manager.save_json("autonomous_cycle_execution_results.json", results)
        return results

    def update_scientific_memory(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        validated = 0
        rejected = 0
        for result in results:
            hypothesis = result["hypothesis"]
            outcome = "validated" if result.get("validated") else "rejected"
            validated += int(outcome == "validated")
            rejected += int(outcome == "rejected")
            try:
                self.kg.create_hypothesis(hypothesis["id"], hypothesis["hypothesis"], hypothesis.get("confidence_prior", 0.25), state=outcome)
                self.kg.create_experiment(
                    f"cycle_exp_{hypothesis['id']}",
                    description=f"Autonomous cycle validation for {hypothesis['id']}",
                    dataset_name=result.get("domain", "cycle"),
                    method=result.get("execution_mode", "sequential"),
                )
                self.kg.relate_experiment_to_hypothesis(f"cycle_exp_{hypothesis['id']}", hypothesis["id"], "VALIDATED" if outcome == "validated" else "REJECTED")
            except Exception:
                pass
            text = json.dumps(result, sort_keys=True, default=str)
            digest = _sha256(text)
            path = self.memory.embedding_cache / f"{digest}.npy"
            if not path.exists():
                np.save(path, self.memory.embed_text(text))
        summary = {"validated": validated, "rejected": rejected, "embedded_new_or_modified": len(results)}
        self.artifact_manager.save_json("autonomous_cycle_memory_update.json", summary)
        return summary

    def update_meta_learning(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        rows = []
        cache_path = ARTIFACTS_DIR / "meta_history_expanded.csv"
        if cache_path.exists():
            try:
                rows = pd.read_csv(cache_path).to_dict(orient="records")
            except Exception:
                rows = []
        for result in results:
            rows.append(
                {
                    "domain": result.get("domain", "cycle"),
                    "model_complexity": 2.0,
                    "dataset_size": 10.0,
                    "method": result.get("execution_mode", "sequential"),
                    "historical_metrics": float(result.get("metric", 0.0)),
                    "compute_cost": float(result.get("compute_cost", 1.0)),
                    "novelty_score": float(result["hypothesis"].get("novelty_score", 0.5)),
                    "epistemic_gain": float(result.get("epistemic_gain", 0.0)),
                }
            )
        frame = pd.DataFrame(rows)
        if frame.empty:
            return {"rows": 0, "updated": False}
        feature_columns = self.meta.feature_columns
        trained = self.meta.train_meta_prior_learner(frame[feature_columns], frame["epistemic_gain"])
        frame.to_csv(cache_path, index=False)
        summary = {"rows": int(len(frame)), "updated": True, "model_path": trained["path"]}
        self.artifact_manager.save_json("autonomous_cycle_meta_update.json", summary)
        return summary

    def compute_cycle_metrics(
        self,
        candidates: list[dict[str, Any]],
        tested: list[dict[str, Any]],
        rejected_prevalidation: list[dict[str, Any]],
    ) -> dict[str, Any]:
        validated = [item for item in tested if item.get("validated")]
        rejected = [item for item in tested if not item.get("validated")]
        gains = [float(item.get("epistemic_gain", 0.0)) for item in tested]
        novelty = [float(item.get("novelty_score", 0.0)) for item in candidates]
        compute_cost = sum(float(item.get("compute_cost", 0.0)) for item in tested)
        return {
            "hypotheses_generated": len(candidates),
            "hypotheses_tested": len(tested),
            "hypotheses_validated": len(validated),
            "hypotheses_rejected": len(rejected) + len(rejected_prevalidation),
            "average_novelty": float(np.mean(novelty)) if novelty else 0.0,
            "average_epistemic_gain": float(np.mean(gains)) if gains else 0.0,
            "compute_cost": compute_cost,
            "discoveries_per_cycle": len(validated),
        }

    def benchmark_autonomous_cycle(self, n_cycles: int = 20, top_k: int = 10, domain: str = "multi") -> dict[str, Any]:
        autonomous = []
        random_baseline = []
        for cycle_idx in range(n_cycles):
            candidates = self.generate_candidate_hypotheses(domain)
            prioritized = self.prioritize_hypotheses(candidates, top_k=top_k)
            accepted, rejected_pre = self.pre_validate_hypotheses(prioritized)
            protocols = self.design_experiments(accepted, domain)
            results = self.execute_experiments(protocols)
            memory_update = self.update_scientific_memory(results)
            meta_update = self.update_meta_learning(results)
            metrics = self.compute_cycle_metrics(candidates, results, rejected_pre)
            metrics.update({"cycle": cycle_idx, "memory_update": memory_update, "meta_update": meta_update})
            autonomous.append(metrics)

            random_pick = self._random_baseline(candidates, top_k)
            random_gain = sum(float(item.get("novelty_score", 0.2)) * 0.15 for item in random_pick)
            random_baseline.append(
                {
                    "cycle": cycle_idx,
                    "validated_discoveries": int(random_gain > 0.4),
                    "epistemic_gain": random_gain,
                    "compute_cost": len(random_pick),
                    "time_per_discovery": len(random_pick) / max(1, int(random_gain > 0.4)),
                }
            )
        benchmark = {
            "n_cycles": n_cycles,
            "autonomous": {
                "validated_discoveries": int(sum(item["hypotheses_validated"] for item in autonomous)),
                "cumulative_epistemic_gain": float(sum(item["average_epistemic_gain"] for item in autonomous)),
                "compute_cost": float(sum(item["compute_cost"] for item in autonomous)),
                "time_per_discovery": _safe_div(sum(item["compute_cost"] for item in autonomous), sum(item["hypotheses_validated"] for item in autonomous)),
            },
            "random": {
                "validated_discoveries": int(sum(item["validated_discoveries"] for item in random_baseline)),
                "cumulative_epistemic_gain": float(sum(item["epistemic_gain"] for item in random_baseline)),
                "compute_cost": float(sum(item["compute_cost"] for item in random_baseline)),
                "time_per_discovery": _safe_div(sum(item["compute_cost"] for item in random_baseline), sum(item["validated_discoveries"] for item in random_baseline)),
            },
        }
        self.artifact_manager.save_json("autonomous_cycle_benchmark.json", {"benchmark": benchmark, "cycles": autonomous, "random": random_baseline})
        self._write_benchmark_markdown(benchmark)
        return {"benchmark": benchmark, "cycles": autonomous}

    def run(self, domain: str = "multi", n_cycles: int = 20, top_k: int = 10, **kwargs: Any) -> dict[str, Any]:
        self.status = "running"
        result = self.benchmark_autonomous_cycle(n_cycles=n_cycles, top_k=top_k, domain=domain)
        cycles = result["cycles"]
        aggregate = {
            "domain": domain,
            "n_cycles": n_cycles,
            "top_k": top_k,
            "hypotheses_generated": int(sum(item["hypotheses_generated"] for item in cycles)),
            "hypotheses_tested": int(sum(item["hypotheses_tested"] for item in cycles)),
            "hypotheses_validated": int(sum(item["hypotheses_validated"] for item in cycles)),
            "hypotheses_rejected": int(sum(item["hypotheses_rejected"] for item in cycles)),
            "average_novelty": float(np.mean([item["average_novelty"] for item in cycles])) if cycles else 0.0,
            "average_epistemic_gain": float(np.mean([item["average_epistemic_gain"] for item in cycles])) if cycles else 0.0,
            "compute_cost": float(sum(item["compute_cost"] for item in cycles)),
            "discoveries_per_cycle": float(np.mean([item["discoveries_per_cycle"] for item in cycles])) if cycles else 0.0,
        }
        self.artifact_manager.save_json("autonomous_cycle_metrics.json", {"aggregate": aggregate, "benchmark": result["benchmark"]})
        self.experiment_registry.register(
            module=self.module_name,
            params={"system": domain, "n_cycles": n_cycles, "top_k": top_k},
            results=aggregate,
            status="completed",
        )
        report_path = self.report_manager.generate_phase_report("Autonomous Scientific Cycle", aggregate, "autonomous_cycle_report.md")
        return {"metrics": aggregate, "benchmark": result["benchmark"], "report_path": str(report_path)}

    def _frontier_candidates(self, domain: str) -> list[dict[str, Any]]:
        try:
            return self.frontier.explore_frontier(domain=domain, n_iterations=50)
        except Exception:
            return _read_json(ARTIFACTS_DIR / "frontier_candidates.json", [])

    def _open_memory_contradictions(self) -> list[dict[str, Any]]:
        try:
            contradictions = self.memory.detect_contradictions(
                self.kg,
                {"id": "cycle_contradiction_probe", "hypothesis": "Recent registered evidence may contradict an existing model."},
                threshold=0.95,
            )
            return [
                {
                    "id": f"contradiction_{idx}",
                    "hypothesis": f"Resolve contradiction between {item.get('source')} and {item.get('target')}.",
                    "source": "scientific_memory_advanced",
                    "provenance": item,
                    "novelty_score": float(item.get("score", 0.5)),
                }
                for idx, item in enumerate(contradictions)
            ]
        except Exception:
            return []

    def _pending_kg_hypotheses(self) -> list[dict[str, Any]]:
        try:
            nodes = self.kg.get_all_hypotheses(state="pending")
            return [
                {
                    "id": dict(node).get("id", f"kg_pending_{idx}"),
                    "hypothesis": dict(node).get("text", ""),
                    "source": "knowledge_graph",
                    "provenance": dict(node),
                }
                for idx, node in enumerate(nodes)
            ]
        except Exception:
            return []

    def _recent_multi_agent_proposals(self, domain: str) -> list[dict[str, Any]]:
        try:
            debate = self.multi_agent.run_scientific_debate(domain if domain != "multi" else "lorenz", "Generate a traceable falsifiable proposal.", n_rounds=2)
            proposal = debate["rounds"][0]["payload"]
            return [
                {
                    "id": "recent_multi_agent_proposal",
                    "hypothesis": proposal.get("hypothesis", ""),
                    "equation": proposal.get("equation", "dx = v"),
                    "variables": proposal.get("variables", ["x", "v"]),
                    "source": "multi_agent_system",
                    "provenance": {"debate_score": debate.get("score")},
                    "novelty_score": 0.5,
                }
            ]
        except Exception:
            return []

    def _normalize_candidate(self, candidate: dict[str, Any], domain: str, timestamp: str) -> dict[str, Any]:
        text = candidate.get("hypothesis") or candidate.get("text") or ""
        candidate_id = candidate.get("id") or f"cycle_{abs(hash(text)) % 10**8}"
        return {
            **candidate,
            "id": str(candidate_id),
            "hypothesis": text,
            "source": candidate.get("source", "unknown"),
            "timestamp": candidate.get("timestamp", timestamp),
            "provenance": candidate.get("provenance", {"source": candidate.get("source", "unknown")}),
            "novelty_score": float(candidate.get("novelty_score", candidate.get("frontier_score", 0.5) or 0.5)),
            "equation": candidate.get("equation", "dx = v"),
            "variables": candidate.get("variables", ["x", "v"]),
            "falsification_test": candidate.get("falsification_test", "p_value < 0.05"),
            "confidence_prior": float(candidate.get("confidence_prior", 0.25)),
            "system_type": candidate.get("system_type", domain if domain != "multi" else "unknown"),
            "variable_ranges": candidate.get("variable_ranges", {"x": (-1.0, 1.0), "v": (-1.0, 1.0)}),
        }

    def _load_meta_model(self) -> dict[str, Any] | None:
        path = MODELS_DIR / "meta_prior_learner.pkl"
        if not path.exists():
            return None
        try:
            with path.open("rb") as handle:
                return pickle.load(handle)
        except Exception:
            return None

    def _context_from_hypothesis(self, hypothesis: dict[str, Any]) -> dict[str, Any]:
        return {
            "domain": hypothesis.get("system_type", "multi"),
            "model_complexity": float(len(hypothesis.get("variables", [])) + 1),
            "dataset_size": 100.0,
            "method": hypothesis.get("source", "autonomous_cycle"),
            "historical_metrics": float(hypothesis.get("frontier_score", hypothesis.get("novelty_score", 0.5))),
            "compute_cost": self._estimate_compute_cost(hypothesis),
            "novelty_score": float(hypothesis.get("novelty_score", 0.5)),
        }

    def _estimate_compute_cost(self, hypothesis: dict[str, Any]) -> float:
        base = 1.0 + 0.5 * len(hypothesis.get("variables", []))
        if hypothesis.get("source") == "cross_domain_transfer":
            base += 1.0
        return base

    def _result_from_protocol(self, protocol: dict[str, Any], raw: dict[str, Any], mode: str) -> dict[str, Any]:
        hypothesis = protocol["hypothesis"]
        if "candidate_errors" in raw:
            metric = float(raw.get("mean_improvement", 0.0))
            validated = metric > 0.02
        else:
            metric = float(raw.get("metric", 0.0))
            validated = metric >= 0.5
        sanity = float(hypothesis.get("physics_sanity_score", 0.5))
        novelty = float(hypothesis.get("novelty_score", 0.5))
        epistemic_gain = max(0.0, metric) * 0.4 + sanity * 0.3 + novelty * 0.3
        return {
            "protocol_id": protocol["id"],
            "domain": protocol.get("domain"),
            "hypothesis": hypothesis,
            "metric": metric,
            "validated": bool(validated),
            "epistemic_gain": float(epistemic_gain),
            "compute_cost": float(hypothesis.get("compute_cost_estimate", 1.0)),
            "execution_mode": mode,
            "raw_result": raw,
        }

    def _random_baseline(self, candidates: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if not candidates:
            return []
        indices = self.rng.choice(len(candidates), size=min(top_k, len(candidates)), replace=False)
        return [candidates[int(index)] for index in indices]

    def _write_benchmark_markdown(self, benchmark: dict[str, Any]) -> str:
        lines = [
            "# Autonomous Scientific Cycle Benchmark",
            "",
            "| Strategy | Validated Discoveries | Cumulative Epistemic Gain | Compute Cost | Time Per Discovery |",
            "|---|---:|---:|---:|---:|",
        ]
        for name in ["autonomous", "random"]:
            item = benchmark[name]
            lines.append(
                f"| {name} | {item['validated_discoveries']} | {item['cumulative_epistemic_gain']:.6g} | "
                f"{item['compute_cost']:.6g} | {item['time_per_discovery']:.6g} |"
            )
        output = ARTIFACTS_DIR / "autonomous_cycle_benchmark.md"
        output.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(output)


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _sha256(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _safe_div(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


if __name__ == "__main__":
    print(json.dumps(AutonomousScientificCycle().run(), indent=2, default=str))
