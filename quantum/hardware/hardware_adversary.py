import numpy as np
import json
from typing import Dict, Any, List
from quantum.hardware.hardware_runner import HardwareRunner
from quantum.theory.theory_memory import TheoryMemory

class HardwareAdversary:
    """
    Component G: Adversarial Hardware Tests.
    Generates adverse conditions (depth expansion, randomized transpilation,
    noise injection) to stress-test and potentially destroy theories.
    """

    ADVERSARIAL_MODELS = {
        "transpilation_jitter": 1.25,  # 25% noise overhead from random mapping
        "depth_expansion": 1.60,       # 60% noise overhead from circuit inflation
        "noise_injection": 2.20        # 120% noise injection
    }

    def __init__(self, db_path: str = "theory_memory.db"):
        self.runner = HardwareRunner(db_path=db_path)
        self.memory = TheoryMemory(db_path=db_path)

    def run_adversarial_tests(self, preregistered_preds: List[Dict[str, Any]], device_name: str = "ibm_sherbrooke") -> List[Dict[str, Any]]:
        """
        Evaluates predictions under adversarial hardware environments.
        """
        results = []
        all_db_preds = {p["id"]: p for p in self.memory.get_all_predictions()}

        for prereg in preregistered_preds:
            p_id = prereg["id"]
            db_pred = all_db_preds.get(p_id, {})
            sim_effect = db_pred.get("effect_size", 0.35)
            
            adv_replication_rates = {}
            np.random.seed(303)

            # Test nominal baseline first
            exec_log = self.runner.execute(device_name, shots=1000, calibration_state="nominal")
            base_err = exec_log["error_rate"]
            
            # Baseline replication
            success_base = sum(
                1 for _ in range(100)
                if (sim_effect - (base_err * 1.5) + np.random.normal(0, 0.02)) >= prereg["expected_effect"]
            ) / 100.0
            adv_replication_rates["baseline"] = success_base

            # Test adversarial scenarios
            total_adversarial_reps = 0
            successful_adversarial_reps = 0

            for model_name, scale in self.ADVERSARIAL_MODELS.items():
                exec_log = self.runner.execute(device_name, shots=1000, calibration_state="nominal", noise_scale=scale)
                err_rate = exec_log["error_rate"]
                
                trials = 50
                success_count = 0
                for _ in range(trials):
                    obs_effect = sim_effect - (err_rate * 1.5) + np.random.normal(0, 0.02)
                    
                    is_success = False
                    if prereg["expected_direction"] == "greater_than" and obs_effect >= prereg["expected_effect"]:
                        is_success = True
                    elif prereg["expected_direction"] == "less_than" and obs_effect <= prereg["expected_effect"]:
                        is_success = True
                        
                    if is_success:
                        success_count += 1
                        successful_adversarial_reps += 1
                    total_adversarial_reps += 1
                    
                adv_replication_rates[model_name] = success_count / trials

            # Compute adversarial survival rate
            survival_rate = successful_adversarial_reps / total_adversarial_reps if total_adversarial_reps > 0 else 0.0
            
            results.append({
                "id": p_id,
                "device": device_name,
                "replication_rates": adv_replication_rates,
                "adversarial_survival_rate": round(survival_rate, 4),
                "status": "PASSED" if survival_rate >= 0.75 else "FAILED"
            })

        with open("hardware_adversary_report.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        return results

if __name__ == "__main__":
    adv = HardwareAdversary()
    dummy = [{
        "id": "PRED_001",
        "expected_effect": 0.12,
        "expected_direction": "greater_than",
        "expected_confidence": 0.85
    }]
    print(adv.run_adversarial_tests(dummy))
