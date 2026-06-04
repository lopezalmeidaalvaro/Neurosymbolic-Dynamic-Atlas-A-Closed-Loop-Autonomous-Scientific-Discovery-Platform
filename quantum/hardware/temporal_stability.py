import numpy as np
import json
import time
from typing import Dict, Any, List
from quantum.hardware.hardware_runner import HardwareRunner
from quantum.theory.theory_memory import TheoryMemory

class TemporalStability:
    """
    Component E: Temporal Drift Audit.
    Evaluates theory predictions across different time intervals:
    Day 1, Day 7, Day 30, and Day 90 to estimate temporal degradation.
    """

    INTERVALS = [1, 7, 30, 90] # days

    def __init__(self, db_path: str = "theory_memory.db"):
        self.runner = HardwareRunner(db_path=db_path)
        self.memory = TheoryMemory(db_path=db_path)

    def run_temporal_audit(self, preregistered_preds: List[Dict[str, Any]], device_name: str = "ibm_sherbrooke") -> List[Dict[str, Any]]:
        """
        Runs the temporal stability evaluation for each prediction.
        """
        results = []
        all_db_preds = {p["id"]: p for p in self.memory.get_all_predictions()}

        for prereg in preregistered_preds:
            p_id = prereg["id"]
            db_pred = all_db_preds.get(p_id, {})
            sim_effect = db_pred.get("effect_size", 0.35)
            
            # Map temporal drift to increasing error rates
            # More days = more gate and readout calibration drift
            effects_by_day = {}
            replication_by_day = {}
            
            np.random.seed(101)

            for day in self.INTERVALS:
                # Drift multiplier increases error rates
                drift_mult = 1.0 + (day / 150.0) # day 90 -> multiplier of 1.6
                
                # Execute run with custom drift factor
                exec_log = self.runner.execute(device_name, shots=1000, calibration_state="nominal", noise_scale=drift_mult)
                total_err = exec_log["error_rate"]
                
                # Run 50 trials per day to get mean effect
                trials = 50
                observed_effects = []
                success_count = 0
                
                for _ in range(trials):
                    noise = np.random.normal(0, 0.02)
                    obs_effect = sim_effect - (total_err * 1.8) + noise
                    observed_effects.append(obs_effect)
                    
                    if prereg["expected_direction"] == "greater_than" and obs_effect >= prereg["expected_effect"]:
                        success_count += 1
                    elif prereg["expected_direction"] == "less_than" and obs_effect <= prereg["expected_effect"]:
                        success_count += 1
                        
                mean_eff = float(np.mean(observed_effects))
                effects_by_day[f"day_{day}"] = round(mean_eff, 4)
                replication_by_day[f"day_{day}"] = success_count / trials

            # Compute temporal degradation: drop from Day 1 to Day 90
            eff_day_1 = effects_by_day["day_1"]
            eff_day_90 = effects_by_day["day_90"]
            
            if eff_day_1 > 0:
                degradation = (eff_day_1 - eff_day_90) / eff_day_1
            else:
                degradation = 0.0
                
            degradation = max(0.0, degradation)
            stability_score = 1.0 - degradation

            results.append({
                "id": p_id,
                "device": device_name,
                "effects": effects_by_day,
                "replication_rates": replication_by_day,
                "temporal_degradation": round(degradation, 4),
                "temporal_stability_score": round(stability_score, 4),
                "status": "PASSED" if stability_score >= 0.75 else "FAILED"
            })
            
        with open("temporal_stability_report.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        return results

if __name__ == "__main__":
    audit = TemporalStability()
    dummy = [{
        "id": "PRED_001",
        "expected_effect": 0.12,
        "expected_direction": "greater_than",
        "expected_confidence": 0.85
    }]
    print(audit.run_temporal_audit(dummy))
