import os
import json
from typing import Dict, Any, List

class HypothesisGenerator:
    """
    Component D: Hypothesis Generator.
    Converts candidate laws into explanatory scientific hypotheses.
    """

    def __init__(self, input_path: str = "candidate_laws.json", output_path: str = "generated_hypotheses.json"):
        self.input_path = input_path
        self.output_path = output_path
        self.hypotheses: List[Dict[str, Any]] = []

    def load_laws(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.input_path):
            return []
        with open(self.input_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_hypotheses(self) -> List[Dict[str, Any]]:
        laws = self.load_laws()
        self.hypotheses = []
        
        # Mapping properties to hypotheses template
        templates = {
            "gate_entropy < 0.25": {
                "statement": "Low gate entropy improves transferability.",
                "rationale": "Circuits with highly regular or structured gate layouts (low entropy) minimize structural domain mismatch, facilitating knowledge reuse."
            },
            "stabilizer_overlap > 0.6": {
                "statement": "High stabilizer overlap improves composition synergy.",
                "rationale": "Strong overlapping of stabilizer states preserves quantum correlations and algebraic properties across composed layers."
            },
            "tensor_rank < 3": {
                "statement": "Low tensor network contraction rank improves scalability.",
                "rationale": "Low-rank tensor networks reduce simulation contraction cost and complexity, leading to faster execution."
            },
            "clifford_ratio > 0.7": {
                "statement": "High Clifford gate ratio enhances noise resilience.",
                "rationale": "Clifford-dominated circuits are structurally compatible with error mitigation and less prone to multi-qubit noise dispersion."
            },
            "betweenness_centrality > 0.25": {
                "statement": "High graph centrality predicts modular knowledge reuse.",
                "rationale": "Bridge motifs with high centralities connect disparate parts of the knowledge graph and represent reusable scaffolds."
            }
        }
        
        for idx, law in enumerate(laws):
            antecedents = law["antecedents"]
            consequent = law["consequent"]
            trend = law["trend"]
            
            # Match templates
            matched_statements = []
            matched_rationales = []
            for ant in antecedents:
                if ant in templates:
                    matched_statements.append(templates[ant]["statement"])
                    matched_rationales.append(templates[ant]["rationale"])
            
            if matched_statements:
                statement = " AND ".join(matched_statements)
                rationale = " ".join(matched_rationales)
            else:
                statement = f"Correlation of antecedents {antecedents} affects {consequent}."
                rationale = f"A combined physical interaction between {antecedents} causes {consequent} to {trend}."
                
            hyp_id = f"HYP_{idx+1:03d}"
            
            hypothesis = {
                "id": hyp_id,
                "law_id": law["id"],
                "statement": statement,
                "rationale": rationale,
                "target_metric": consequent,
                "confidence": law["precision"],
                "status": "PROPOSED"
            }
            self.hypotheses.append(hypothesis)
            
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.hypotheses, f, indent=2, ensure_ascii=False)
            
        print(f"Generated {len(self.hypotheses)} hypotheses and saved to: {self.output_path}")
        return self.hypotheses

if __name__ == "__main__":
    generator = HypothesisGenerator()
    generator.generate_hypotheses()
