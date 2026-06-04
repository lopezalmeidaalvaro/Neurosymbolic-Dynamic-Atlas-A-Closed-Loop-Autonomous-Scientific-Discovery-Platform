import difflib
from typing import List, Dict, Any, Optional
from quantum.memory.context_compatibility import ContextCompatibilityEngine

class NoveltyMetrics:
    """
    Computes a novelty score for scaffolds relative to other scaffolds in memory.
    """

    def __init__(self, memory: Any):
        self.memory = memory
        self.compatibility_engine = ContextCompatibilityEngine()

    def calculate_similarity(self, sc1: Dict[str, Any], sc2: Dict[str, Any]) -> float:
        """
        Calculates similarity between two scaffolds based on sequence (40%), topology (30%),
        context (20%), and causal history (10%).
        """
        # 1. Gate sequence similarity (40%)
        seq1 = sc1.get("sequence", [])
        seq2 = sc2.get("sequence", [])
        if not seq1 or not seq2:
            seq_sim = 0.0
        else:
            seq_sim = difflib.SequenceMatcher(None, seq1, seq2).ratio()

        # 2. Topology similarity (qubit count) (30%)
        ctx1 = sc1.get("context", {})
        ctx2 = sc2.get("context", {})
        q1 = ctx1.get("qubit_count", 0) if isinstance(ctx1, dict) else getattr(ctx1, "qubit_count", 0)
        q2 = ctx2.get("qubit_count", 0) if isinstance(ctx2, dict) else getattr(ctx2, "qubit_count", 0)

        if q1 == q2:
            topo_sim = 1.0
        elif abs(q1 - q2) <= 1:
            topo_sim = 0.5
        else:
            topo_sim = 0.0

        # 3. Context similarity (20%)
        task1 = ctx1.get("task_name") if isinstance(ctx1, dict) else getattr(ctx1, "task_name", "")
        task2 = ctx2.get("task_name") if isinstance(ctx2, dict) else getattr(ctx2, "task_name", "")
        
        if task1 == task2:
            context_sim = 1.0
        elif (task1, task2) in self.compatibility_engine.task_family_scores or (task2, task1) in self.compatibility_engine.task_family_scores:
            context_sim = 0.9
        else:
            context_sim = 0.0

        # 4. Causal history similarity (10%)
        surv1 = sc1.get("survival_probability", 0.0)
        surv2 = sc2.get("survival_probability", 0.0)
        conf1 = sc1.get("confidence_score", 0.1)
        conf2 = sc2.get("confidence_score", 0.1)

        causal_sim = 1.0 - (abs(surv1 - surv2) * 0.5 + abs(conf1 - conf2) * 0.5)
        causal_sim = max(0.0, min(1.0, causal_sim))

        return 0.4 * seq_sim + 0.3 * topo_sim + 0.2 * context_sim + 0.1 * causal_sim

    def classify_novelty(self, novelty: float) -> str:
        """
        Classifies the novelty score.
        """
        if novelty < 0.15:
            return "TRIVIAL"
        elif novelty < 0.4:
            return "VARIANT"
        elif novelty < 0.7:
            return "NOVEL"
        else:
            return "HIGHLY_NOVEL"

    def compute_novelty_for_all(self) -> List[Dict[str, Any]]:
        """
        Calculates and registers scaffold_novelty and novelty_class for all scaffolds in memory.
        """
        scaffolds = self.memory.query_scaffolds()
        if not scaffolds:
            return []

        if len(scaffolds) == 1:
            scaffolds[0]["scaffold_novelty"] = 1.0
            scaffolds[0]["novelty_class"] = "HIGHLY_NOVEL"
            self.memory.store("quantum:distillation:scaffolds", scaffolds)
            return scaffolds

        updated_scaffolds = []
        for i, sc1 in enumerate(scaffolds):
            max_sim = 0.0
            for j, sc2 in enumerate(scaffolds):
                if i == j:
                    continue
                sim = self.calculate_similarity(sc1, sc2)
                if sim > max_sim:
                    max_sim = sim
            
            novelty = round(1.0 - max_sim, 4)
            sc1["scaffold_novelty"] = novelty
            sc1["novelty_class"] = self.classify_novelty(novelty)
            updated_scaffolds.append(sc1)

        self.memory.store("quantum:distillation:scaffolds", updated_scaffolds)
        return updated_scaffolds
