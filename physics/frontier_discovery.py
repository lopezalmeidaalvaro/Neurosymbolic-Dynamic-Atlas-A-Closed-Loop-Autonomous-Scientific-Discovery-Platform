from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

import numpy as np

try:
    from physics.core.base_module import ScientificModule
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
    from knowledge_graph import ScientificKnowledgeGraph
    from meta_learning_engine import MetaLearningEngine
    from multi_agent_system import MultiAgentSystem
    from physics_sanity_engine import PhysicsSanityEngine
    from scientific_guard import assign_claim_level
    from scientific_memory_advanced import ScientificMemoryAdvanced


ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"


class FrontierDiscovery(ScientificModule):
    """Traceable frontier candidate generator over authorized sources only."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sanity = PhysicsSanityEngine()
        self.memory = ScientificMemoryAdvanced()
        self.meta = MetaLearningEngine()
        self.warnings: list[str] = []

    def compute_novelty_score(self, hypothesis_text: str, existing_texts: list[str]) -> float:
        if not existing_texts:
            return 1.0
        query = self.memory.embed_text(hypothesis_text)
        sims = [self._cosine(query, self.memory.embed_text(text)) for text in existing_texts if text]
        return float(1.0 - max(sims or [0.0]))

    def compute_consistency_score(self, candidate: dict[str, Any]) -> float:
        result = self.sanity.validate_hypothesis(candidate)
        return float(result.get("score", 0.0))

    def compute_empirical_utility_score(self, candidate: dict[str, Any]) -> float:
        text = json.dumps(candidate, default=str).lower()
        data_score = 0.4 if any(token in text for token in ["dataset", "data", "experiment", "telemetry", "benchmark"]) else 0.15
        testability = 0.35 if any(token in text for token in ["falsification", "mse", "p_value", "threshold", ">"]) else 0.1
        cost = 0.25 if "low_cost" in text or "simulation" in text else 0.15
        return float(min(1.0, data_score + testability + cost))

    def explore_frontier(self, domain: str = "multi", n_iterations: int = 100) -> list[dict[str, Any]]:
        kg = ScientificKnowledgeGraph()
        source_candidates = []
        existing_texts = []
        source_candidates.extend(self._from_knowledge_graph(kg))
        existing_texts.extend([item["hypothesis"] for item in source_candidates])
        source_candidates.extend(self._from_memory_contradictions(kg))
        source_candidates.extend(self._from_experiment_registry())
        source_candidates.extend(self._from_multi_agent(domain))
        kg.close()
        if not source_candidates:
            self.warnings.append("No authorized source produced candidates; no disconnected hypotheses generated.")
            return []
        evaluated = []
        for candidate in source_candidates[: max(1, n_iterations)]:
            candidate = self._normalize_candidate(candidate, domain)
            novelty = self.compute_novelty_score(candidate["hypothesis"], existing_texts)
            consistency = self.compute_consistency_score(candidate)
            utility = self.compute_empirical_utility_score(candidate)
            claim = assign_claim_level(candidate["hypothesis"], candidate.get("source", "authorized source"))
            candidate.update(
                {
                    "novelty_score": novelty,
                    "consistency_score": consistency,
                    "physics_sanity_score": consistency,
                    "empirical_utility_score": utility,
                    "claim_level": claim,
                    "frontier_score": novelty * consistency * utility,
                }
            )
            evaluated.append(candidate)
        ranked = sorted(evaluated, key=lambda item: item["frontier_score"], reverse=True)[:10]
        self.artifact_manager.save_json("frontier_candidates.json", ranked)
        self._cache_umap(ranked)
        return ranked

    def human_expert_flag(self, candidate: dict[str, Any]) -> dict[str, Any]:
        return {"requires_human_review": True, "reason": "placeholder for expert frontier review", "candidate_id": candidate.get("id")}

    def run(self, domain: str = "multi", n_iterations: int = 100, **kwargs: Any) -> dict[str, Any]:
        self.status = "running"
        candidates = self.explore_frontier(domain, n_iterations)
        metrics = {
            "domain": domain,
            "iterations_requested": n_iterations,
            "candidates_ranked": len(candidates),
            "top_frontier_score": candidates[0]["frontier_score"] if candidates else 0.0,
            "warnings": self.warnings,
        }
        self.experiment_registry.register(
            module=self.module_name,
            params={"system": domain, "n_iterations": n_iterations},
            results=metrics,
            status="completed" if candidates else "warning",
        )
        report_path = self.log_result(metrics, "frontier_report.md")
        return {"metrics": metrics, "report_path": report_path, "candidates": candidates}

    def _from_knowledge_graph(self, kg: ScientificKnowledgeGraph) -> list[dict[str, Any]]:
        candidates = []
        try:
            for node in kg.get_all_hypotheses():
                props = dict(node)
                text = props.get("text") or props.get("hypothesis")
                if text:
                    candidates.append({"id": props.get("id"), "hypothesis": f"Refine existing KG hypothesis: {text}", "source": "knowledge_graph"})
        except Exception as exc:
            self.warnings.append(f"knowledge_graph_degraded: {exc}")
        return candidates

    def _from_memory_contradictions(self, kg: ScientificKnowledgeGraph) -> list[dict[str, Any]]:
        candidates = []
        try:
            contradiction_probe = self.memory.detect_contradictions(
                kg,
                {"id": "frontier_probe", "hypothesis": "Existing validated hypothesis may be contradicted by recent evidence."},
                threshold=0.95,
            )
            for item in contradiction_probe:
                candidates.append(
                    {
                        "id": f"resolve_{item['source']}_{item['target']}",
                        "hypothesis": f"Resolve contradiction between {item['source']} and {item['target']} with a crucial experiment.",
                        "source": "scientific_memory_contradiction",
                    }
                )
        except Exception as exc:
            self.warnings.append(f"scientific_memory_degraded: {exc}")
        return candidates

    def _from_experiment_registry(self) -> list[dict[str, Any]]:
        db_path = Path(self.experiment_registry.storage_path)
        candidates = []
        if not db_path.exists():
            return candidates
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute("SELECT * FROM experiments ORDER BY timestamp DESC LIMIT 50").fetchall()
            for row in rows:
                results = json.loads(row["results_json"] or "{}")
                module = row["module"]
                candidates.append(
                    {
                        "id": f"registry_{row['id'][:8]}",
                        "hypothesis": (
                            f"Follow up {module} result from registered experiment {row['id'][:8]} "
                            f"with falsification criterion p_value < 0.05 and dataset benchmark."
                        ),
                        "source": "experiment_registry",
                        "historical_results": results,
                    }
                )
        except Exception as exc:
            self.warnings.append(f"experiment_registry_degraded: {exc}")
        return candidates

    def _from_multi_agent(self, domain: str) -> list[dict[str, Any]]:
        try:
            debate = MultiAgentSystem().run_scientific_debate(domain if domain != "multi" else "lorenz", "Identify the next falsifiable frontier test.", n_rounds=2)
            proposal = debate["rounds"][0]["payload"]
            return [
                {
                    "id": "multi_agent_proposal",
                    "hypothesis": proposal.get("hypothesis", ""),
                    "equation": proposal.get("equation", "dx = v"),
                    "variables": proposal.get("variables", ["x", "v"]),
                    "source": "multi_agent_system",
                }
            ]
        except Exception as exc:
            self.warnings.append(f"multi_agent_degraded: {exc}")
            return []

    def _normalize_candidate(self, candidate: dict[str, Any], domain: str) -> dict[str, Any]:
        normalized = dict(candidate)
        normalized.setdefault("id", f"candidate_{abs(hash(normalized.get('hypothesis', ''))) % 10**8}")
        normalized.setdefault("equation", "dx = v")
        normalized.setdefault("variables", ["x", "v"])
        normalized.setdefault("falsification_test", "p_value < 0.05")
        normalized.setdefault("confidence_prior", 0.25)
        normalized.setdefault("system_type", domain if domain != "multi" else "unknown")
        normalized.setdefault("variable_ranges", {var: (-1.0, 1.0) for var in normalized["variables"][:3]})
        return normalized

    def _cache_umap(self, candidates: list[dict[str, Any]]) -> str:
        if not candidates:
            coords = np.empty((0, 2))
        else:
            vectors = np.vstack([self.memory.embed_text(item["hypothesis"]) for item in candidates])
            try:
                import umap

                coords = umap.UMAP(n_components=2, random_state=self.config_manager.get("physics.random_seed", 42)).fit_transform(vectors)
            except Exception:
                coords = vectors[:, :2] if vectors.shape[1] >= 2 else np.column_stack([vectors[:, 0], np.zeros(len(vectors))])
        output = ARTIFACTS_DIR / "frontier_umap.npy"
        np.save(output, coords)
        return str(output)

    @staticmethod
    def _cosine(a: np.ndarray, b: np.ndarray) -> float:
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        return 0.0 if denom == 0 else float(np.dot(a, b) / denom)


if __name__ == "__main__":
    print(json.dumps(FrontierDiscovery().run(), indent=2, default=str))
