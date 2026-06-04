import hashlib
import json
import time
from typing import Dict, Any, List
from quantum.theory.theory_memory import TheoryMemory

class PreregisteredPredictions:
    """
    Component C: Pre-Registered Predictions.
    Cryptographically hashes and registers predictions prior to hardware runs.
    Enforces freeze rules to prevent post-hoc modifications.
    """

    def __init__(self, db_path: str = "theory_memory.db"):
        self.memory = TheoryMemory(db_path=db_path)

    def _compute_hash(self, pred: Dict[str, Any]) -> str:
        # Standardize representation to ensure stable hash
        payload = {
            "id": pred["id"],
            "prediction_statement": pred["prediction_statement"],
            "expected_effect": pred["expected_effect"],
            "expected_direction": pred["expected_direction"],
            "expected_confidence": pred["expected_confidence"]
        }
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

    def register_predictions(self, translated_predictions: List[Dict[str, Any]]) -> None:
        """
        Freezes predictions by hashing them and saving to preregistered_predictions database table.
        """
        for pred in translated_predictions:
            existing = self.memory.get_preregistered_prediction(pred["id"])
            current_hash = self._compute_hash(pred)
            
            if existing:
                # Enforce freeze rule: do not allow hash to change
                if existing["hash"] != current_hash:
                    raise ValueError(
                        f"CRITICAL: Cryptographic freeze violation! "
                        f"Pre-registered prediction {pred['id']} has been modified post-registration."
                    )
            else:
                # Register new prediction
                timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                pred_to_save = {
                    "id": pred["id"],
                    "expected_effect": pred["expected_effect"],
                    "expected_direction": pred["expected_direction"],
                    "expected_confidence": pred["expected_confidence"],
                    "timestamp": timestamp,
                    "hash": current_hash
                }
                self.memory.save_preregistered_prediction(pred_to_save)
                print(f"Pre-registered and froze prediction: {pred['id']} (Hash: {current_hash[:8]}...)")

    def verify_registry(self, translated_predictions: List[Dict[str, Any]]) -> bool:
        """
        Verifies that none of the translated predictions violate frozen registry hashes.
        """
        for pred in translated_predictions:
            existing = self.memory.get_preregistered_prediction(pred["id"])
            if not existing:
                print(f"Warning: Prediction {pred['id']} is not yet pre-registered.")
                return False
                
            current_hash = self._compute_hash(pred)
            if existing["hash"] != current_hash:
                print(f"Error: Hash mismatch for prediction {pred['id']}.")
                return False
                
        return True

if __name__ == "__main__":
    reg = PreregisteredPredictions()
    dummy = {
        "id": "PRED_TEST",
        "prediction_statement": "If entropy decreases, novelty increases",
        "expected_effect": 0.12,
        "expected_direction": "greater_than",
        "expected_confidence": 0.85
    }
    reg.register_predictions([dummy])
    print("Verification:", reg.verify_registry([dummy]))
