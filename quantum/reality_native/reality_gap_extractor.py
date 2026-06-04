import os
import json
import sqlite3
from typing import Dict, Any, List
from quantum.theory.theory_memory import TheoryMemory
from quantum.reality_native.reality_native_memory import RealityNativeMemory

class RealityGapExtractor:
    """
    Phase 3B-A: Reality Gap Extraction.
    Computes Observed - Predicted across physical performance indicators
    and stores results in the GAP_DATABASE (reality_native.db).
    """

    def __init__(
        self,
        db_path: str = "theory_memory.db",
        reality_db_path: str = "reality_native.db"
    ):
        self.memory = TheoryMemory(db_path=db_path)
        self.reality_mem = RealityNativeMemory(db_path=reality_db_path)

    def extract_reality_gaps(
        self,
        rep_report_path: str = "hardware_replication_report.json"
    ) -> List[Dict[str, Any]]:
        
        with open(rep_report_path, "r", encoding="utf-8") as f:
            rep_data = json.load(f)

        predictions = self.memory.get_all_predictions()
        pred_map = {p["id"]: p for p in predictions}
        
        extracted_gaps = []
        counter = 0

        # Mapping predictions to physical metrics
        metric_mapping = {
            "PRED_001": "scaling_efficiency",
            "PRED_002": "noise_accumulation",
            "PRED_003": "entanglement_retention",
            "PRED_004": "error_correction_efficacy",
            "PRED_005": "error_correction_efficacy",
            "PRED_007": "noise_accumulation",
            "PRED_008": "entanglement_retention",
            "PRED_009": "scaling_efficiency",
            "PRED_010": "scaling_efficiency",
            "PRED_011": "noise_accumulation"
        }

        for item in rep_data:
            p_id = item["id"]
            if p_id not in pred_map:
                continue
            
            # Simulated predicted effect size
            predicted_val = pred_map[p_id]["effect_size"]
            metric = metric_mapping.get(p_id, "fidelity")

            # Extract gaps across all device runs
            for dev_name, dev_info in item.get("device_details", {}).items():
                observed_val = dev_info["mean_effect"]
                gap = observed_val - predicted_val
                
                gap_id = f"GAP_{p_id}_{dev_name.upper()}"
                
                gap_record = {
                    "id": gap_id,
                    "prediction_id": p_id,
                    "device": dev_name,
                    "metric": metric,
                    "observed": round(observed_val, 4),
                    "predicted": round(predicted_val, 4),
                    "gap": round(gap, 4)
                }
                
                self.reality_mem.save_reality_gap(gap_record)
                extracted_gaps.append(gap_record)
                counter += 1

        print(f"Extracted {counter} reality gaps and saved to GAP_DATABASE (reality_native.db)")
        return extracted_gaps

if __name__ == "__main__":
    ext = RealityGapExtractor()
    print("Gaps compiled size:", len(ext.extract_reality_gaps()))
