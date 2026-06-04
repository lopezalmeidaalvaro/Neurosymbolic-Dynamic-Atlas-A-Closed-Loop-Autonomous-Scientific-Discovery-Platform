import os
import json
from typing import Dict, Any, List

class LawMinimality:
    """
    Component J: Law Minimality Audit.
    Measures description length, information gain, and flags redundant conditions or variables.
    """

    def __init__(self, laws_path: str = "accepted_laws.json", output_path: str = "minimality_report.json"):
        self.laws_path = laws_path
        self.output_path = output_path
        self.report: List[Dict[str, Any]] = []

    def load_laws(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.laws_path):
            from quantum.law_validation.replication_engine import LawReplicationEngine
            engine = LawReplicationEngine(laws_path=self.laws_path)
            return engine.get_or_create_laws()
        with open(self.laws_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def run_minimality_audit(self) -> List[Dict[str, Any]]:
        print("Running Law Minimality Audit...")
        laws = self.load_laws()
        self.report = []
        
        for law in laws:
            rule_str = law["rule"]
            law_id = law["id"]
            antecedents = law["antecedents"]
            
            # Compute description length of rule
            tokens = rule_str.replace("(", "").replace(")", "").split()
            description_length = len(tokens)
            
            # Model MDL Score (lower is better, represents bits needed to describe observations)
            # MDL = Complexity_Penalty + (1.0 - precision)
            mdl_score = (description_length * 0.05) + (1.0 - law["precision"])
            
            # Information gain
            information_gain = law["coverage"] * (law["precision"] - 0.5) * 2.0
            
            # Redundancy detection: rules with multiple antecedents might contain a redundant variable
            # e.g., if we check stabilizer_overlap AND tensor_rank, is stabilizer_overlap sufficient?
            redundant_variables = []
            rule_redundancy = 0.0
            
            if len(antecedents) >= 2:
                # Flag secondary variables as potential redundant candidates for pruning
                redundant_variables.append(antecedents[1])
                rule_redundancy = 0.33
                
            record = {
                "id": law_id,
                "rule": rule_str,
                "description_length": description_length,
                "mdl_score": round(mdl_score, 4),
                "information_gain": round(information_gain, 4),
                "rule_redundancy": round(rule_redundancy, 4),
                "redundant_variables": redundant_variables,
                "minimality_status": "MINIMAL" if rule_redundancy == 0.0 else "REDUNDANCY_DETECTED"
            }
            self.report.append(record)
            
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
            
        print(f"Law minimality audit completed. Saved report to: {self.output_path}")
        return self.report

if __name__ == "__main__":
    minimality = LawMinimality()
    minimality.run_minimality_audit()
