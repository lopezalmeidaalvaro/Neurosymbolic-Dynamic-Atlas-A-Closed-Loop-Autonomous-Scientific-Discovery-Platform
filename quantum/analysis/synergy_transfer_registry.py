import json
from typing import List, Dict, Any

class SynergyTransferRegistry:
    """
    Registry that filters and preserves synergistic compositions suitable for transfer
    across different quantum domains based on strict synergy, novelty, and class criteria.
    """

    def __init__(self, novelty_threshold: float = 0.30, approved_classes: List[str] = None):
        self.novelty_threshold = novelty_threshold
        self.approved_classes = approved_classes or ["STATE_PREPARATION_EXTENSION"]
        self.registry = []

    def build_transfer_registry(
        self, scaffolds: List[Dict[str, Any]], pairwise_records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        self.registry = []
        
        # 1. Map pairwise records by composed representation for quick lookup of synergy details
        pairwise_map = {}
        for r in pairwise_records:
            rep = f"{r['pattern_a']}->{r['pattern_b']}"
            pairwise_map[rep] = r

        # 2. Filter candidates matching criteria
        for sc in scaffolds:
            rep = sc.get("representation", "")
            
            # Find synergy details
            pair_rec = pairwise_map.get(rep)
            if pair_rec:
                synergy = pair_rec["synergy_score"]
                interaction_type = pair_rec["interaction_type"]
                novelty = pair_rec["novelty"]
            else:
                # Fallback to scaffold properties
                synergy = sc.get("emergent_utility", 0.0)
                interaction_type = sc.get("interaction_type", "UNKNOWN")
                novelty = sc.get("scaffold_novelty", 0.5)

            # Filtering Criteria:
            # - synergy_score > 0
            # - novelty > novelty_threshold
            # - interaction_type in approved_classes
            if (
                synergy > 0.0
                and novelty >= self.novelty_threshold
                and interaction_type in self.approved_classes
            ):
                self.registry.append({
                    "representation": rep,
                    "sequence": sc.get("sequence", []),
                    "interaction_type": interaction_type,
                    "contexts": sc.get("context"),
                    "utility": sc.get("utility_scaffold", sc.get("mean_delta_score", 0.0)),
                    "confidence": sc.get("confidence_score", 0.1),
                    "novelty": novelty,
                    "synergy_score": synergy
                })

        # Save to synergy_transfer_registry.json
        with open("synergy_transfer_registry.json", "w", encoding="utf-8") as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)

        return self.registry
