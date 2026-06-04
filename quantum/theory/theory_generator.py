import os
import json
from typing import Dict, Any, List
from quantum.theory.theory_memory import TheoryMemory

class TheoryGenerator:
    """
    Component A: Theory Candidate Generation Engine.
    Generates candidate theories explaining multiple laws simultaneously.
    """

    def __init__(self, laws_path: str = "law_status_registry.json", db_path: str = "theory_memory.db"):
        self.laws_path = laws_path
        self.db_path = db_path
        self.memory = TheoryMemory(db_path=db_path)

    def load_laws(self) -> Dict[str, Any]:
        if not os.path.exists(self.laws_path):
            # Check accepted_laws.json as fallback
            fallback = "accepted_laws.json"
            if os.path.exists(fallback):
                with open(fallback, "r", encoding="utf-8") as f:
                    laws_list = json.load(f)
                    return {law["id"]: law for law in laws_list}
            return {}
        with open(self.laws_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("laws", {})

    def generate_theories(self) -> List[Dict[str, Any]]:
        laws = self.load_laws()
        if not laws:
            print("No laws found to explain.")
            return []

        # Unify laws into 4 thematic theories
        theories_def = [
            {
                "id": "THEORY_001",
                "name": "Information Entropy and Representation Coherence Theory",
                "theme": "entropy_transferability",
                "assumptions": [
                    "Low gate entropy corresponds to higher structural regularity in circuit layers.",
                    "Coherent circuit structures minimize the representation gap between transfer source and target."
                ],
                "confidence": 0.88,
                "status": "CANDIDATE"
            },
            {
                "id": "THEORY_002",
                "name": "Stabilizer Symmetry Conservation and Emergent Synergy Theory",
                "theme": "stabilizer_synergy",
                "assumptions": [
                    "Sufficient stabilizer overlap ensures conservation of algebraic symmetries in concatenated states.",
                    "Low tensor network rank restricts accumulation of node contraction errors during composition."
                ],
                "confidence": 0.85,
                "status": "CANDIDATE"
            },
            {
                "id": "THEORY_003",
                "name": "Clifford Algebraic Noise Resilience Theory",
                "theme": "clifford_resilience",
                "assumptions": [
                    "High Clifford ratio is structurally compatible with stabilizer-based error correction codes.",
                    "Classical simulator tractability of Clifford sub-circuits facilitates high-fidelity zero-noise extrapolation."
                ],
                "confidence": 0.86,
                "status": "CANDIDATE"
            },
            {
                "id": "THEORY_004",
                "name": "Topology Centrality and Recombinatorial Novelty Theory",
                "theme": "centrality_novelty",
                "assumptions": [
                    "High betweenness centrality indicates structural bottleneck states connecting independent circuit modules.",
                    "Central topological pattern reuse increases structural variety and combinations, driving overall novelty."
                ],
                "confidence": 0.82,
                "status": "CANDIDATE"
            }
        ]

        generated_theories = []
        for t_def in theories_def:
            # Gather which laws this theory explains
            laws_explained = []
            theme = t_def["theme"]
            for law_id, law_data in laws.items():
                rule = law_data.get("rule", "").lower()
                if theme == "entropy_transferability" and "entropy" in rule and "transfer" in rule:
                    laws_explained.append(law_id)
                elif theme == "stabilizer_synergy" and ("stabilizer" in rule or "rank" in rule) and "synergy" in rule:
                    laws_explained.append(law_id)
                elif theme == "clifford_resilience" and "clifford" in rule and "resilience" in rule:
                    laws_explained.append(law_id)
                elif theme == "centrality_novelty" and "centrality" in rule and "novelty" in rule:
                    laws_explained.append(law_id)

            # Build the theory dictionary
            theory = {
                "id": t_def["id"],
                "name": t_def["name"],
                "laws_explained": laws_explained,
                "mechanism_graph": {}, # will be populated by mechanism engine
                "assumptions": t_def["assumptions"],
                "predictions": [], # will be populated by prediction engine
                "confidence": t_def["confidence"],
                "status": t_def["status"]
            }
            
            # Save to database
            self.memory.save_theory(theory)
            generated_theories.append(theory)

        print(f"Generated {len(generated_theories)} candidate theories and saved to database.")
        return generated_theories

if __name__ == "__main__":
    gen = TheoryGenerator()
    gen.generate_theories()
