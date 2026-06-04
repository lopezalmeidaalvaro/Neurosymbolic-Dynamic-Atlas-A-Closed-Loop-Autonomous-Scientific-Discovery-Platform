import statistics
from typing import List, Dict, Any

class ScaffoldEvaluator:
    """
    Evaluates fitness, survival, and emergent utility of composed scaffolds compared to components.
    """

    def calculate_emergent_utility(self, scaffold: Dict[str, Any], causal_records: List[Dict[str, Any]]) -> float:
        """
        Computes Emergent Utility = Scaffold Delta Score - Mean(Component Delta Scores)
        """
        # 1. Get delta scores for the scaffold
        sc_rep = scaffold.get("representation")
        sc_id = scaffold.get("pattern_id")
        
        sc_records = []
        for r in causal_records:
            r_pat = r.get("pattern")
            r_id = r.get("pattern_id")
            if (r_pat == sc_rep or r_id == sc_id) and r.get("delta_score") is not None:
                sc_records.append(r["delta_score"])
                
        sc_delta_score = statistics.mean(sc_records) if sc_records else 0.0
        
        # 2. Get delta scores for each component
        comp_reps = scaffold.get("source_patterns", [])
        comp_deltas = []
        
        for comp in comp_reps:
            comp_records = []
            for r in causal_records:
                r_pat = r.get("pattern")
                if r_pat == comp and r.get("delta_score") is not None:
                    comp_records.append(r["delta_score"])
            comp_deltas.append(statistics.mean(comp_records) if comp_records else 0.0)
            
        mean_comp_delta = statistics.mean(comp_deltas) if comp_deltas else 0.0
        
        return round(sc_delta_score - mean_comp_delta, 4)

    def evaluate_scaffold(self, scaffold: Dict[str, Any], causal_records: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Evaluates and returns comprehensive metrics for a scaffold.
        """
        sc_rep = scaffold.get("representation")
        sc_id = scaffold.get("pattern_id")
        
        matching = [r for r in causal_records if r.get("pattern") == sc_rep or r.get("pattern_id") == sc_id]
        total_injections = len(matching)
        
        if total_injections == 0:
            return {
                "fitness": 0.0,
                "survival_probability": 0.0,
                "transfer_utility": 0.0,
                "emergent_utility": 0.0
            }
            
        survived = sum(1 for r in matching if r.get("survival_status", False))
        survival_prob = survived / total_injections
        
        deltas = [r.get("delta_score") for r in matching if r.get("delta_score") is not None]
        avg_delta = statistics.mean(deltas) if deltas else 0.0
        
        emergent_ut = self.calculate_emergent_utility(scaffold, causal_records)
        
        # Fitness can be defined as mean delta score plus survival probability
        fitness = avg_delta + survival_prob
        
        return {
            "fitness": round(fitness, 4),
            "survival_probability": round(survival_prob, 4),
            "transfer_utility": round(avg_delta, 4),
            "emergent_utility": emergent_ut
        }
