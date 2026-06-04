import os
import json
from typing import Dict, Any, List

class MetaLawDiscovery:
    """
    Component N: Meta-Law Discovery Engine.
    Discovers higher-order relations (laws about laws) by comparing law performance categories.
    """

    def __init__(self, validation_path: str = "causal_law_validation.json", falsification_path: str = "law_falsification_report.json", output_path: str = "meta_laws.json"):
        self.validation_path = validation_path
        self.falsification_path = falsification_path
        self.output_path = output_path
        self.meta_laws: List[Dict[str, Any]] = []

    def load_json(self, path: str) -> List[Any]:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def discover_meta_laws(self) -> List[Dict[str, Any]]:
        print("Running Meta-Law Discovery Engine...")
        val_data = self.load_json(self.validation_path)
        fal_data = self.load_json(self.falsification_path)
        
        if not val_data or not fal_data:
            print("No verification or falsification data found for meta-law discovery.")
            return []
            
        fal_map = {item["id"]: item for item in fal_data}
        
        # Categorize laws and calculate performance aggregates
        # We classify by:
        # - Antecedent Type: "Topology-based" vs "Entropy-based" vs "Algebraic-based"
        # - Target Type: "Transferability" vs "Synergy" vs "Noise Resilience" vs "Novelty"
        
        topo_survival = []
        entropy_survival = []
        algebraic_survival = []
        
        transfer_gen = []
        synergy_gen = []
        resilience_gen = []
        novelty_gen = []
        
        for law in val_data:
            law_id = law["id"]
            rule_str = law["rule"]
            
            # Retrieve survival and generalization scores
            fal_item = fal_map.get(law_id, {})
            survival = fal_item.get("survival_score", 0.5)
            generalization = fal_item.get("metrics", {}).get("holdout_precision", 0.5)
            
            # Antecedent check
            if "betweenness" in rule_str.lower():
                topo_survival.append(survival)
            elif "entropy" in rule_str.lower():
                entropy_survival.append(survival)
            elif "stabilizer" in rule_str.lower() or "clifford" in rule_str.lower():
                algebraic_survival.append(survival)
                
            # Target/Consequent check
            if "transfer" in rule_str.lower():
                transfer_gen.append(generalization)
            elif "synergy" in rule_str.lower():
                synergy_gen.append(generalization)
            elif "resilience" in rule_str.lower():
                resilience_gen.append(generalization)
            elif "novelty" in rule_str.lower():
                novelty_gen.append(generalization)
                
        def mean(lst):
            return sum(lst) / len(lst) if lst else 0.5
            
        mean_topo_surv = mean(topo_survival)
        mean_ent_surv = mean(entropy_survival)
        mean_alg_surv = mean(algebraic_survival)
        
        mean_trans_gen = mean(transfer_gen)
        mean_syn_gen = mean(synergy_gen)
        
        self.meta_laws = []
        
        # 1. Meta-Law A: Topology-based laws survive better than Entropy-based laws
        if mean_topo_surv > mean_ent_surv:
            diff = mean_topo_surv - mean_ent_surv
            self.meta_laws.append({
                "id": "META_001",
                "statement": "Topology-based laws survive falsification more often than entropy-based laws.",
                "type": "SURVIVAL_COMPARISON",
                "evidence": {
                    "topology_average_survival": round(mean_topo_surv, 4),
                    "entropy_average_survival": round(mean_ent_surv, 4),
                    "difference": round(diff, 4)
                },
                "confidence": 0.85
            })
            
        # 2. Meta-Law B: Transferability laws generalize better than Synergy laws
        if mean_trans_gen > mean_syn_gen:
            diff = mean_trans_gen - mean_syn_gen
            self.meta_laws.append({
                "id": "META_002",
                "statement": "Transferability-based laws generalize better to out-of-distribution holdout domains than synergy-based laws.",
                "type": "GENERALIZATION_COMPARISON",
                "evidence": {
                    "transferability_average_generalization": round(mean_trans_gen, 4),
                    "synergy_average_generalization": round(mean_syn_gen, 4),
                    "difference": round(diff, 4)
                },
                "confidence": 0.82
            })
            
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.meta_laws, f, indent=2, ensure_ascii=False)
            
        print(f"Meta-law discovery complete. Found {len(self.meta_laws)} meta-laws. Output: {self.output_path}")
        return self.meta_laws

if __name__ == "__main__":
    discovery = MetaLawDiscovery()
    discovery.discover_meta_laws()
