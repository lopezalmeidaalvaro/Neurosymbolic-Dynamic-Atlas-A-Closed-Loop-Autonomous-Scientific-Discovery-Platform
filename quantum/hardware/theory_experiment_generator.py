import json
from typing import Dict, Any, List
from quantum.theory.theory_memory import TheoryMemory

class TheoryExperimentGenerator:
    """
    Component B: Theory-to-Experiment Translator.
    Converts qualitative predictions from simulations into quantitative,
    experimentally falsifiable predictions with numerical thresholds.
    """

    EFFECT_THRESHOLDS = {
        "transferability": 0.12,  # Must increase/decrease by at least 12.0%
        "synergy": 0.10,          # 10.0%
        "novelty": 0.15,          # 15.0%
        "noise_resilience": 0.08  # 8.0%
    }

    def __init__(self, db_path: str = "theory_memory.db"):
        self.memory = TheoryMemory(db_path=db_path)

    def translate_predictions(self) -> List[Dict[str, Any]]:
        """
        Translates simulation predictions into quantitative experimental predictions.
        """
        predictions = self.memory.get_all_predictions()
        translated = []

        for pred in predictions:
            consequent = pred["consequent"]
            trend = pred["trend"]
            
            # Look up standard quantitative requirement or scale from historical simulation effect size
            pct_effect = self.EFFECT_THRESHOLDS.get(consequent, 0.10)
            
            # Scale effect size expectation slightly based on simulation effect size
            if pred.get("effect_size"):
                # Use a combined metric: at least 80% of simulated effect, but capped to realistic margins
                scaled_effect = max(pct_effect, round(pred["effect_size"] * 0.8, 4))
            else:
                scaled_effect = pct_effect
                
            direction = "greater_than" if trend == "increases" else "less_than"
            
            # Format the rigorous quantitative statement
            quant_statement = (
                f"If {', '.join(pred['antecedents'])}, then {consequent} "
                f"will show an effect size {direction} {scaled_effect:.2%}"
            )
            
            translated.append({
                "id": pred["id"],
                "originating_theory": pred["originating_theory"],
                "prediction_statement": quant_statement,
                "consequent": consequent,
                "trend": trend,
                "expected_effect": scaled_effect,
                "expected_direction": direction,
                "expected_confidence": max(0.70, round(pred.get("confidence", 0.85), 4))
            })
            
        return translated

if __name__ == "__main__":
    gen = TheoryExperimentGenerator()
    for t_pred in gen.translate_predictions():
        print(t_pred["id"], "->", t_pred["prediction_statement"])
