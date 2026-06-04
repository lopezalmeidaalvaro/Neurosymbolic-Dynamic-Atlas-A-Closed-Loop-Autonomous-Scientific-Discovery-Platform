import statistics
from typing import List, Dict, Any, Optional

class CounterfactualScaffoldEvaluator:
    """
    Evaluates Emergent Utility using the max individual component utility as a counterfactual baseline.
    """

    def __init__(self, memory: Any):
        self.memory = memory

    def evaluate_scaffold(self, scaffold: Dict[str, Any], causal_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluates a single scaffold, calculating its utility, its components' utilities,
        and its counterfactual emergent utility.
        """
        sc_rep = scaffold.get("representation")
        sc_id = scaffold.get("pattern_id")

        # 1. Calculate utility_scaffold (mean delta score of the scaffold in causal records)
        sc_records = []
        for r in causal_records:
            r_pat = r.get("pattern")
            r_id = r.get("pattern_id")
            if (r_pat == sc_rep or r_id == sc_id) and r.get("delta_score") is not None:
                sc_records.append(r["delta_score"])

        utility_scaffold = statistics.mean(sc_records) if sc_records else 0.0

        # 2. Get delta scores for each component individually
        comp_reps = scaffold.get("source_patterns", [])
        comp_utilities = []

        for comp in comp_reps:
            comp_records = []
            for r in causal_records:
                r_pat = r.get("pattern")
                if r_pat == comp and r.get("delta_score") is not None:
                    comp_records.append(r["delta_score"])
            comp_utilities.append(statistics.mean(comp_records) if comp_records else 0.0)

        # 3. Use the best component utility as counterfactual baseline
        max_component_utility = max(comp_utilities) if comp_utilities else 0.0

        # 4. Calculate Emergent Utility
        emergent_utility = utility_scaffold - max_component_utility

        # 5. Classify emergence
        if emergent_utility > 0:
            emergence_class = "EMERGENT"
        elif emergent_utility == 0:
            emergence_class = "NEUTRAL"
        else:
            emergence_class = "REDUNDANT"

        # Calculate survival probability for the scaffold
        matching = [r for r in causal_records if r.get("pattern") == sc_rep or r.get("pattern_id") == sc_id]
        total_injections = len(matching)
        if total_injections > 0:
            survived = sum(1 for r in matching if r.get("survival_status", False))
            survival_prob = survived / total_injections
        else:
            survival_prob = 0.0

        return {
            "utility_scaffold": round(utility_scaffold, 4),
            "max_component_utility": round(max_component_utility, 4),
            "emergent_utility": round(emergent_utility, 4),
            "emergence_class": emergence_class,
            "survival_probability": round(survival_prob, 4),
            "fitness": round(utility_scaffold + survival_prob, 4)
        }

    def evaluate_all_scaffolds(self) -> List[Dict[str, Any]]:
        """
        Evaluates all scaffolds currently stored in memory, updates their fields,
        and saves them back to memory.
        """
        scaffolds = self.memory.query_scaffolds()
        causal_records = self.memory.retrieve("quantum:distillation:causal_records") or []

        updated_scaffolds = []
        for sc in scaffolds:
            metrics = self.evaluate_scaffold(sc, causal_records)
            sc.update(metrics)
            updated_scaffolds.append(sc)

        self.memory.store("quantum:distillation:scaffolds", updated_scaffolds)
        return updated_scaffolds
