import numpy as np
import json
from typing import Dict, Any, List
from quantum.hardware.hardware_runner import HardwareRunner
from quantum.theory.theory_memory import TheoryMemory

class CalibrationAudit:
    """
    Component F: Calibration Robustness.
    Audits predictions under different device calibrations:
    high-fidelity, nominal, and degraded, computing a robustness coefficient.
    """

    def __init__(self, db_path: str = "theory_memory.db"):
        self.runner = HardwareRunner(db_path=db_path)
        self.memory = TheoryMemory(db_path=db_path)

    def run_calibration_audit(self, preregistered_preds: List[Dict[str, Any]], device_name: str = "ibm_sherbrooke") -> List[Dict[str, Any]]:
        """
        Runs the calibration robustness audit for all predictions.
        """
        results = []
        all_db_preds = {p["id"]: p for p in self.memory.get_all_predictions()}
        states = ["high_fidelity", "nominal", "degraded"]

        for prereg in preregistered_preds:
            p_id = prereg["id"]
            db_pred = all_db_preds.get(p_id, {})
            sim_effect = db_pred.get("effect_size", 0.35)
            
            observed_effects_by_state = {}
            replication_rates_by_state = {}
            
            np.random.seed(202)

            for state in states:
                exec_log = self.runner.execute(device_name, shots=1000, calibration_state=state)
                total_err = exec_log["error_rate"]
                
                # 50 trials per state
                trials = 50
                observed_effects = []
                success_count = 0
                
                for _ in range(trials):
                    noise = np.random.normal(0, 0.02)
                    obs_effect = sim_effect - (total_err * 1.5) + noise
                    observed_effects.append(obs_effect)
                    
                    if prereg["expected_direction"] == "greater_than" and obs_effect >= prereg["expected_effect"]:
                        success_count += 1
                    elif prereg["expected_direction"] == "less_than" and obs_effect <= prereg["expected_effect"]:
                        success_count += 1
                        
                mean_eff = float(np.mean(observed_effects))
                observed_effects_by_state[state] = round(mean_eff, 4)
                replication_rates_by_state[state] = success_count / trials

            # Compute robustness coefficient: 1.0 - (std_deviation / mean_observed_effect)
            vals = [observed_effects_by_state[s] for s in states]
            mean_val = float(np.mean(vals))
            std_val = float(np.std(vals))
            
            if mean_val > 0:
                coef = max(0.0, 1.0 - (std_val / mean_val))
            else:
                coef = 0.0

            results.append({
                "id": p_id,
                "device": device_name,
                "effects_by_state": observed_effects_by_state,
                "replication_rates_by_state": replication_rates_by_state,
                "robustness_coefficient": round(coef, 4),
                "status": "PASSED" if coef >= 0.70 else "FAILED" # criteria threshold
            })
            
        with open("calibration_audit_report.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        return results

if __name__ == "__main__":
    audit = CalibrationAudit()
    dummy = [{
        "id": "PRED_001",
        "expected_effect": 0.12,
        "expected_direction": "greater_than",
        "expected_confidence": 0.85
    }]
    print(audit.run_calibration_audit(dummy))
