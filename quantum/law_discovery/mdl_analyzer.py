import os
import json
import math
from typing import Dict, Any, List

class MDLAnalyzer:
    """
    Component O: MDL Complexity & Value Analyzer.
    Applies Minimum Description Length (MDL) principles to evaluate scientific value of laws.
    """

    def __init__(self, laws_path: str = "candidate_laws.json", output_path: str = "mdl_report.json"):
        self.laws_path = laws_path
        self.output_path = output_path
        self.mdl_results: List[Dict[str, Any]] = []

    def load_laws(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.laws_path):
            return []
        with open(self.laws_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def analyze_complexity(self) -> List[Dict[str, Any]]:
        laws = self.load_laws()
        self.mdl_results = []
        
        for law in laws:
            rule_str = law["rule"]
            precision = law["precision"]
            coverage = law["coverage"]
            lift = law["lift"]
            
            # 1. Description Length (approximated by token count in rule string)
            tokens = rule_str.replace("(", "").replace(")", "").split()
            description_length = len(tokens)
            
            # 2. Complexity Penalty (linear scaling of token count)
            complexity_penalty = description_length * 0.04
            
            # 3. Information Gain
            # Information Gain is based on Kullback-Leibler / log-likelihood of precision improvement
            # IG = coverage * log2(precision / prior_probability)
            # We approximate with lift and precision
            log_lift = math.log2(lift) if lift > 0 else 0.0
            information_gain = coverage * log_lift * 1.5
            
            # 4. Compression Gain
            # Saving in bits by using a general rule instead of individual observations
            # Compression = (N_records * entropy_raw) - (N_records * entropy_with_rule + description_length)
            # Simply modeled as a ratio of coverage and inverse description length
            compression_gain = (coverage * 100) / max(1.0, description_length * 0.1)
            
            # 5. Scientific Value Score
            # Value = Information Gain + Compression Gain - Complexity Penalty
            # Normalize to 0.0 - 1.0 range
            raw_value = (information_gain * 0.3) + (compression_gain * 0.005) - complexity_penalty
            scientific_value_score = 1.0 / (1.0 + math.exp(-raw_value)) # Sigmoid mapping
            
            mdl_record = {
                "id": law["id"],
                "rule": rule_str,
                "description_length": description_length,
                "complexity_penalty": round(complexity_penalty, 4),
                "information_gain": round(information_gain, 4),
                "compression_gain": round(compression_gain, 4),
                "scientific_value_score": round(scientific_value_score, 4)
            }
            self.mdl_results.append(mdl_record)
            
        # Write report
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.mdl_results, f, indent=2, ensure_ascii=False)
            
        print(f"MDL complexity analysis complete. Saved report to: {self.output_path}")
        return self.mdl_results

if __name__ == "__main__":
    analyzer = MDLAnalyzer()
    analyzer.analyze_complexity()
