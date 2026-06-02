from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

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


try:
    from core.abstractions.base_memory import BaseMemory
except ImportError:
    from abc import ABC, abstractmethod
    class BaseMemory(ABC):
        @abstractmethod
        def store(self, *args, **kwargs):
            pass
        @abstractmethod
        def retrieve(self, *args, **kwargs):
            pass

class ScientificMemoryAdvanced(ScientificModule, BaseMemory):
    """Incremental semantic memory layer on top of the existing Neo4j graph."""

    def store(self, *args, **kwargs):
        pass

    def retrieve(self, *args, **kwargs):
        return []

    _embedding_backend = None
    _tokenizer = None
    _model = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cache_default = PHYSICS_ROOT / "models" / "embeddings_cache"
        self.embedding_cache = Path(self.config_manager.get("models.embedding_cache", cache_default))
        if not self.embedding_cache.is_absolute():
            self.embedding_cache = PHYSICS_ROOT.parent / self.embedding_cache
        self.embedding_cache.mkdir(parents=True, exist_ok=True)
        self.model_name = self.config_manager.get("models.scientific_embedding_model") or self.config_manager.get(
            "models.scibert_model", "allenai/scibert_scivocab_uncased"
        )
        ModelRegistry().register(
            "scientific_embedding_backend",
            self.embedding_cache,
            metadata={"model_name": self.model_name, "storage": "sha256 .npy cache"},
        )

    def embed_scientific_entities(self, knowledge_graph: ScientificKnowledgeGraph) -> dict[str, Any]:
        entities = knowledge_graph.get_scientific_entities()
        processed = 0
        reused = 0
        for entity in entities:
            text = _entity_text(entity)
            digest = _sha256(text)
            path = self.embedding_cache / f"{digest}.npy"
            if path.exists() and entity.get("properties", {}).get("embedding_hash") == digest:
                reused += 1
            else:
                vector = self.embed_text(text)
                np.save(path, vector)
                processed += 1
            knowledge_graph.update_entity_embedding_metadata(
                entity["label"],
                entity["id"],
                digest,
                str(path),
                metadata={"model": self.model_name, "dim": int(np.load(path).shape[0])},
            )
        return {"entities_seen": len(entities), "embedded_or_updated": processed, "reused": reused}

    def embed_text(self, text: str) -> np.ndarray:
        backend = self._load_embedding_backend()
        if backend == "transformers":
            return self._embed_transformers(text)
        return _hash_embedding(text)

    def detect_contradictions(
        self,
        knowledge_graph: ScientificKnowledgeGraph,
        new_hypothesis: dict[str, Any] | str,
        threshold: float = 0.9,
    ) -> list[dict[str, Any]]:
        hypothesis_id = new_hypothesis.get("id", "new_hypothesis") if isinstance(new_hypothesis, dict) else "new_hypothesis"
        text = new_hypothesis.get("text") or new_hypothesis.get("hypothesis") if isinstance(new_hypothesis, dict) else str(new_hypothesis)
        query_vec = self.embed_text(text)
        contradictions = []
        for entity in knowledge_graph.get_scientific_entities():
            if entity["label"] != "Hypothesis" or entity["id"] == hypothesis_id:
                continue
            props = entity.get("properties", {})
            emb_path = props.get("embedding_path")
            if not emb_path or not Path(emb_path).exists():
                continue
            score = _cosine(query_vec, np.load(emb_path))
            if score >= threshold and _opposite_polarity(text, props.get("text", "")):
                evidence = f"semantic_similarity={score:.3f}; opposite_polarity=true"
                knowledge_graph.create_hypothesis(hypothesis_id, text, confidence=0.5, state="pending")
                knowledge_graph.relate_hypotheses_contradiction(hypothesis_id, entity["id"], evidence=evidence, score=score)
                experiment_id = f"crucial_{hypothesis_id}_{entity['id']}".replace(" ", "_")[:120]
                knowledge_graph.create_experiment(
                    experiment_id,
                    description=f"Crucial experiment to resolve contradiction: {hypothesis_id} vs {entity['id']}",
                    dataset_name="pending",
                    method="crucial_contradiction_test",
                )
                self.experiment_registry.register(
                    module=self.module_name,
                    params={"system": "scientific_memory", "hypothesis": hypothesis_id, "contradicts": entity["id"]},
                    results={"similarity": score, "crucial_experiment": experiment_id},
                    status="registered",
                )
                contradictions.append({"source": hypothesis_id, "target": entity["id"], "score": score, "experiment_id": experiment_id})
        return contradictions

    def build_knowledge_evolution_graph(
        self,
        knowledge_graph: ScientificKnowledgeGraph,
        root_hypothesis_id: str,
    ):
        import networkx as nx

        graph = nx.DiGraph()
        for edge in knowledge_graph.get_knowledge_evolution_edges(root_hypothesis_id):
            graph.add_edge(edge["source"], edge["target"], type=edge["type"], **edge.get("properties", {}))
        if root_hypothesis_id and root_hypothesis_id not in graph:
            graph.add_node(root_hypothesis_id)
        return graph

    def visualize_knowledge_evolution(self, root_hypothesis_id: str, output_path: str | Path):
        import matplotlib.pyplot as plt
        import networkx as nx

        kg = ScientificKnowledgeGraph()
        graph = self.build_knowledge_evolution_graph(kg, root_hypothesis_id)
        colors = {"REFINES": "#2563eb", "DERIVES": "#059669", "CONTRADICTS": "#dc2626"}
        edge_colors = [colors.get(data.get("type"), "#64748b") for _, _, data in graph.edges(data=True)]
        pos = nx.spring_layout(graph, seed=self.config_manager.get("physics.random_seed", 42)) if graph.nodes else {}
        plt.figure(figsize=(9, 6))
        nx.draw_networkx_nodes(graph, pos, node_color="#f8fafc", edgecolors="#0f172a", node_size=1200)
        nx.draw_networkx_labels(graph, pos, font_size=8)
        nx.draw_networkx_edges(graph, pos, edge_color=edge_colors, arrows=True)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(output, dpi=160)
        plt.close()
        kg.close()
        return str(output)

    def query_by_similarity(self, knowledge_graph: ScientificKnowledgeGraph, query_text: str, top_k: int = 5) -> list[dict[str, Any]]:
        query_vec = self.embed_text(query_text)
        scored = []
        for entity in knowledge_graph.get_scientific_entities():
            path = entity.get("properties", {}).get("embedding_path")
            if path and Path(path).exists():
                scored.append(
                    {
                        "id": entity["id"],
                        "label": entity["label"],
                        "score": _cosine(query_vec, np.load(path)),
                        "text": _entity_text(entity)[:240],
                    }
                )
        return sorted(scored, key=lambda item: item["score"], reverse=True)[:top_k]

    def run(self, new_hypothesis: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        self.status = "running"
        kg = ScientificKnowledgeGraph()
        embed_stats = self.embed_scientific_entities(kg)
        contradictions = []
        if new_hypothesis:
            contradictions = self.detect_contradictions(kg, new_hypothesis)
        metrics = {
            **embed_stats,
            "contradictions_detected": len(contradictions),
            "embedding_model": self.model_name,
            "cache_dir": str(self.embedding_cache),
            "neo4j_connected": kg.connected,
        }
        kg.close()
        report_path = self.log_result(metrics, "memory_report.md")
        return {"metrics": metrics, "report_path": report_path, "contradictions": contradictions}

    def _load_embedding_backend(self) -> str:
        if ScientificMemoryAdvanced._embedding_backend is not None:
            return ScientificMemoryAdvanced._embedding_backend
        try:
            import torch
            from transformers import AutoModel, AutoTokenizer

            ScientificMemoryAdvanced._tokenizer = AutoTokenizer.from_pretrained(self.model_name, local_files_only=True)
            ScientificMemoryAdvanced._model = AutoModel.from_pretrained(self.model_name, local_files_only=True)
            ScientificMemoryAdvanced._model.eval()
            ScientificMemoryAdvanced._torch = torch
            ScientificMemoryAdvanced._embedding_backend = "transformers"
        except Exception:
            ScientificMemoryAdvanced._embedding_backend = "hash"
        return ScientificMemoryAdvanced._embedding_backend

    def _embed_transformers(self, text: str) -> np.ndarray:
        tokenizer = ScientificMemoryAdvanced._tokenizer
        model = ScientificMemoryAdvanced._model
        torch = ScientificMemoryAdvanced._torch
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            output = model(**inputs)
        return output.last_hidden_state.mean(dim=1).squeeze(0).cpu().numpy().astype(np.float32)


def _entity_text(entity: dict[str, Any]) -> str:
    props = entity.get("properties", {})
    fields = [
        props.get("text"),
        props.get("latex"),
        props.get("sympy_str"),
        props.get("description"),
        props.get("name"),
        props.get("method"),
        props.get("dataset_name"),
    ]
    return " ".join(str(value) for value in fields if value)


def _sha256(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _hash_embedding(text: str, dim: int = 384) -> np.ndarray:
    tokens = [token.strip(".,;:()[]{}").lower() for token in str(text).split() if token.strip()]
    vector = np.zeros(dim, dtype=np.float32)
    for token in tokens or ["empty"]:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "little") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[idx] += sign
    norm = np.linalg.norm(vector)
    return vector / norm if norm else vector


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    n = min(a.shape[0], b.shape[0])
    a = a[:n]
    b = b[:n]
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return 0.0 if denom == 0 else float(np.dot(a, b) / denom)


def _opposite_polarity(left: str, right: str) -> bool:
    neg = {"not", "no", "never", "reject", "decrease", "negative", "false", "invalid"}
    pos = {"increase", "positive", "true", "valid", "supports", "confirmed", "validated"}
    left_words = set(str(left).lower().split())
    right_words = set(str(right).lower().split())
    return bool((left_words & neg and right_words & pos) or (left_words & pos and right_words & neg))


if __name__ == "__main__":
    print(json.dumps(ScientificMemoryAdvanced().run(), indent=2, default=str))
