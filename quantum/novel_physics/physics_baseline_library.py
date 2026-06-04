import numpy as np
from typing import Dict, Any, List
from quantum.novel_physics.standard_physics_models import StandardPhysicsModel

class PhysicsBaselineLibrary:
    """
    Phase 4A: Serves standard physical baseline predictions for quantum device observations.
    """

    def __init__(self):
        self.model = StandardPhysicsModel()

    def get_baseline_predictions(self, data_records: List[Dict[str, Any]]) -> List[float]:
        predictions = []
        for r in data_records:
            ge = r.get("gate_error", 0.0)
            re = r.get("readout_error", 0.0)
            pred = self.model.predict_gap(ge, re)
            predictions.append(pred)
        return predictions

    def get_calibration_baseline(self, gate_errors: List[float], readout_errors: List[float]) -> List[float]:
        ge_arr = np.array(gate_errors)
        re_arr = np.array(readout_errors)
        return list(self.model.predict_calibration_curve(ge_arr, re_arr))
