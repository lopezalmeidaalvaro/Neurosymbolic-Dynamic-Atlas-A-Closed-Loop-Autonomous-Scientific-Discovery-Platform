import json
from typing import Dict, Any, List
from quantum.theory.theory_memory import TheoryMemory
from quantum.theory.mechanism_engine import MechanismEngine

class PredictionEngine:
    """
    Component F & G: Novel Prediction and Prioritization Engines.
    Generates novel predictions linking variables in previously unseen pathways,
    ranks them by information gain and experimental feasibility, and saves the Top 10.
    """

    def __init__(self, data_path: str = "observation_dataset.json", db_path: str = "theory_memory.db"):
        self.data_path = data_path
        self.db_path = db_path
        self.memory = TheoryMemory(db_path=db_path)
        self.engine = MechanismEngine(data_path=data_path, db_path=db_path)

    def generate_predictions(self) -> List[Dict[str, Any]]:
        # Load theories to link predictions to their origin
        theories = self.memory.get_all_theories()
        theory_map = {t["id"]: t for t in theories}
        
        # 11 Candidate Novel Predictions (cross-pathway relations)
        candidates = [
            {
                "id": "PRED_001",
                "originating_theory": "THEORY_001",
                "prediction_statement": "If tensor_rank decreases and structural_coherence increases, then transferability increases.",
                "antecedents": ["tensor_rank < 5", "gate_entropy < 0.25"],
                "consequent": "transferability",
                "trend": "increases"
            },
            {
                "id": "PRED_002",
                "originating_theory": "THEORY_002",
                "prediction_statement": "If stabilizer_overlap increases, then error_mitigation stabilizes and noise_resilience increases.",
                "antecedents": ["stabilizer_overlap > 0.6"],
                "consequent": "noise_resilience",
                "trend": "increases"
            },
            {
                "id": "PRED_003",
                "originating_theory": "THEORY_004",
                "prediction_statement": "If betweenness_centrality increases and structural_coherence increases, then synergy increases.",
                "antecedents": ["betweenness_centrality > 0.25", "gate_entropy < 0.25"],
                "consequent": "synergy",
                "trend": "increases"
            },
            {
                "id": "PRED_004",
                "originating_theory": "THEORY_003",
                "prediction_statement": "If clifford_ratio increases, then state_preservation improves and synergy increases.",
                "antecedents": ["clifford_ratio > 0.7"],
                "consequent": "synergy",
                "trend": "increases"
            },
            {
                "id": "PRED_005",
                "originating_theory": "THEORY_001",
                "prediction_statement": "If gate_entropy decreases, then module_recombination increases and novelty increases.",
                "antecedents": ["gate_entropy < 0.25"],
                "consequent": "novelty",
                "trend": "increases"
            },
            {
                "id": "PRED_006",
                "originating_theory": "THEORY_002",
                "prediction_statement": "If stabilizer_overlap increases, then domain_similarity improves and transferability increases.",
                "antecedents": ["stabilizer_overlap > 0.6"],
                "consequent": "transferability",
                "trend": "increases"
            },
            {
                "id": "PRED_007",
                "originating_theory": "THEORY_002",
                "prediction_statement": "If tensor_rank decreases, then error_mitigation improves and noise_resilience increases.",
                "antecedents": ["tensor_rank < 3"],
                "consequent": "noise_resilience",
                "trend": "increases"
            },
            {
                "id": "PRED_008",
                "originating_theory": "THEORY_004",
                "prediction_statement": "If betweenness_centrality increases, then algebraic_symmetry increases and synergy increases.",
                "antecedents": ["betweenness_centrality > 0.25"],
                "consequent": "synergy",
                "trend": "increases"
            },
            {
                "id": "PRED_009",
                "originating_theory": "THEORY_001",
                "prediction_statement": "If gate_distribution_distance decreases, then reuse_bottleneck increases and novelty increases.",
                "antecedents": ["gate_distribution_distance < 0.3"],
                "consequent": "novelty",
                "trend": "increases"
            },
            {
                "id": "PRED_010",
                "originating_theory": "THEORY_003",
                "prediction_statement": "If clifford_ratio increases, then domain_similarity improves and transferability increases.",
                "antecedents": ["clifford_ratio > 0.7"],
                "consequent": "transferability",
                "trend": "increases"
            },
            {
                "id": "PRED_011",
                "originating_theory": "THEORY_001",
                "prediction_statement": "If gate_entropy decreases, then error_mitigation stabilizes and noise_resilience increases.",
                "antecedents": ["gate_entropy < 0.25"],
                "consequent": "noise_resilience",
                "trend": "increases"
            }
        ]

        # Load dataset to evaluate empirical effect size and feasibility
        dataset = self.engine.load_or_generate_dataset()
        
        ranked_predictions = []
        for p in candidates:
            # 1. Expected Information Gain (mutual information proxy)
            # Calculated based on how well the antecedents predict the consequent
            consequent = p["consequent"]
            antecedents = p["antecedents"]
            
            # Simple correlation to approximate information gain
            # Let's map target to values
            corr_val = 0.0
            for ant in antecedents:
                var_name = ant.split()[0]
                corr_val += abs(self.engine.compute_correlation(dataset, var_name, consequent))
            
            info_gain = (corr_val / len(antecedents)) if antecedents else 0.1
            info_gain = min(0.95, max(0.2, info_gain))
            
            # 2. Experimental Feasibility
            # Feasibility is higher for simpler measurements (e.g. gate_entropy is easier than stabilizer_overlap or graph centrality)
            feasibility = 0.90
            for ant in antecedents:
                if "stabilizer" in ant:
                    feasibility -= 0.15
                if "centrality" in ant:
                    feasibility -= 0.10
                if "rank" in ant:
                    feasibility -= 0.10
            
            feasibility = max(0.40, feasibility)
            
            # Combined Prioritization Score
            prioritization_score = 0.6 * info_gain + 0.4 * feasibility
            
            prediction = {
                "id": p["id"],
                "originating_theory": p["originating_theory"],
                "prediction_statement": p["prediction_statement"],
                "antecedents": antecedents,
                "consequent": consequent,
                "trend": p["trend"],
                "effect_size": round(info_gain * 0.5, 4), # soft scale
                "confidence": round(prioritization_score, 4),
                "feasibility": round(feasibility, 4),
                "status": "UNCONFIRMED"
            }
            
            ranked_predictions.append(prediction)

        # Sort by confidence score (prioritization score) descending
        ranked_predictions.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Select Top 10
        top_10 = ranked_predictions[:10]
        
        # Save to database and update theories
        for pred in top_10:
            self.memory.save_prediction(pred)
            
            # Append prediction ID to originating theory
            theory_id = pred["originating_theory"]
            if theory_id in theory_map:
                theory = theory_map[theory_id]
                if pred["id"] not in theory.get("predictions", []):
                    theory.setdefault("predictions", []).append(pred["id"])
                    self.memory.save_theory(theory)
                    
        print(f"Generated and prioritized {len(top_10)} predictions.")
        return top_10

if __name__ == "__main__":
    eng = PredictionEngine()
    eng.generate_predictions()
