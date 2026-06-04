import os
import pytest
from quantum.novel_physics.impossible_prediction_generator import ImpossiblePredictionGenerator

def test_impossible_predictions():
    theories = [
        {"theory_id": "RTHEORY_001", "domain": "quantum_hardware_noise",
         "equation": "Gap = -1.4907 * E_gate + -1.5060 * E_readout + -0.0021"},
        {"theory_id": "RTHEORY_002", "domain": "calibration_drift",
         "equation": "Gap = -1.8500 * E_gate + -1.2500 * E_readout + -0.0050"},
    ]
    ipg = ImpossiblePredictionGenerator(theories)
    cases = ipg.generate_impossible_predictions()
    assert len(cases) == 6  # 2 theories * 3 sweeps
    for c in cases:
        assert c["standard_prediction"] == 0.0
        assert c["divergence"] > 0.0
        assert c["rtheory_prediction"] != 0.0
    assert os.path.exists("docs/IMPOSSIBLE_PREDICTIONS.md")
