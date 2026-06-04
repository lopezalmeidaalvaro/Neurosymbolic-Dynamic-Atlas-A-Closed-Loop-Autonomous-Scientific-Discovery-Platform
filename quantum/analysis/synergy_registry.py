import json
from typing import List, Dict, Any

class SynergyRegistry:
    """
    Registers and saves scaffolds that exhibit genuine positive synergy and have high confidence.
    """

    def __init__(self, confidence_threshold: float = 0.15):
        self.confidence_threshold = confidence_threshold
        self.registry = []

    def register_synergistic_structures(self, scaffolds: List[Dict[str, Any]], pairwise_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.registry = []
        
        # 1. Map pairwise records by representation for quick lookup of synergy_score
        pairwise_map = {}
        for r in pairwise_records:
            rep = f"{r['pattern_a']}->{r['pattern_b']}"
            pairwise_map[rep] = r

        # 2. Filter scaffolds with positive synergy and sufficient confidence
        for sc in scaffolds:
            rep = sc.get("representation", "")
            conf = sc.get("confidence_score", 0.0)
            
            # Retrieve synergy details
            pair_rec = pairwise_map.get(rep)
            if pair_rec:
                synergy = pair_rec["synergy_score"]
                interaction_type = pair_rec["interaction_type"]
                novelty = pair_rec["novelty"]
            else:
                # Fallback if not found in pairwise records
                synergy = sc.get("emergent_utility", 0.0)
                interaction_type = sc.get("interaction_type", "UNKNOWN")
                novelty = sc.get("scaffold_novelty", 0.5)

            # Filter criteria: synergy_score > 0 and confidence > threshold
            if synergy > 0.0 and conf > self.confidence_threshold:
                self.registry.append({
                    "representation": rep,
                    "interaction_type": interaction_type,
                    "contexts": sc.get("context"),
                    "utility": sc.get("utility_scaffold", sc.get("mean_delta_score", 0.0)),
                    "confidence": conf,
                    "novelty": novelty,
                    "synergy_score": synergy
                })

        # Save to synergy_registry.json
        with open("synergy_registry.json", "w", encoding="utf-8") as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)

        return self.registry
