import os
import json
from typing import Dict, Any, List

class SymbolicLawGenerator:
    """
    Component C: Symbolic Law Generator.
    Converts association rules into human-readable scientific laws.
    """

    def __init__(self, input_path: str = "pattern_rules.json", output_path: str = "candidate_laws.json"):
        self.input_path = input_path
        self.output_path = output_path
        self.laws: List[Dict[str, Any]] = []

    def load_rules(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.input_path):
            return []
        with open(self.input_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_laws(self) -> List[Dict[str, Any]]:
        rules = self.load_rules()
        self.laws = []
        
        target_map = {
            "transferability_high": ("transferability", "increases"),
            "synergy_high": ("synergy", "increases"),
            "noise_resilience_high": ("noise_resilience", "increases"),
            "novelty_high": ("novelty", "increases"),
            "transferability_low": ("transferability", "decreases"),
            "synergy_low": ("synergy", "decreases"),
            "noise_resilience_low": ("noise_resilience", "decreases"),
            "novelty_low": ("novelty", "decreases")
        }
        
        for idx, rule in enumerate(rules):
            antecedents = rule["antecedent"]
            consequent_raw = rule["consequent"]
            
            # Map antecedent to expression
            antecedent_expr = " AND ".join(f"({ant})" for ant in antecedents)
            
            # Map consequent
            cons_field, cons_trend = target_map.get(consequent_raw, (consequent_raw.replace("_high", ""), "increases"))
            consequent_expr = f"{cons_field} {cons_trend}"
            
            law_rule_str = f"IF {antecedent_expr} THEN {consequent_expr}"
            
            # Formulate text description
            desc_parts = []
            for ant in antecedents:
                if "gate_entropy" in ant:
                    desc_parts.append("lower gate entropy")
                elif "stabilizer_overlap" in ant:
                    desc_parts.append("higher stabilizer overlap")
                elif "tensor_rank" in ant:
                    desc_parts.append("lower tensor network rank")
                elif "clifford_ratio" in ant:
                    desc_parts.append("higher Clifford gate ratio")
                elif "betweenness_centrality" in ant:
                    desc_parts.append("higher betweenness centrality")
                    
            ant_desc = " combined with ".join(desc_parts) if desc_parts else "particular structural properties"
            description = f"Rules indicate that {ant_desc} tends to cause an effect where {cons_field} {cons_trend}."
            
            law_id = f"LAW_{idx+1:03d}"
            
            law = {
                "id": law_id,
                "rule": law_rule_str,
                "description": description,
                "precision": rule["confidence"],
                "coverage": rule["support"],
                "lift": rule["lift"],
                "antecedents": antecedents,
                "consequent": cons_field,
                "trend": cons_trend,
                "status": "CANDIDATE"
            }
            self.laws.append(law)
            
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.laws, f, indent=2, ensure_ascii=False)
            
        print(f"Generated {len(self.laws)} candidate laws and saved to: {self.output_path}")
        return self.laws

if __name__ == "__main__":
    generator = SymbolicLawGenerator()
    generator.generate_laws()
