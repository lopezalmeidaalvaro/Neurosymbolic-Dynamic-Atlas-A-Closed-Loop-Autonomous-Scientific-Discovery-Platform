import os
import pytest
from quantum.novel_physics.experiment_designer import ExperimentDesigner

def test_experiment_designer():
    cases = [
        {"case_id": "IMP_001_00", "theory_id": "RTHEORY_001", "domain": "noise",
         "gate_error": 0.01, "readout_error": 0.02, "standard_prediction": 0.0,
         "rtheory_prediction": -0.05, "divergence": 0.05},
        {"case_id": "IMP_001_01", "theory_id": "RTHEORY_001", "domain": "noise",
         "gate_error": 0.015, "readout_error": 0.035, "standard_prediction": 0.0,
         "rtheory_prediction": -0.08, "divergence": 0.08},
    ]
    designer = ExperimentDesigner(cases)
    experiments = designer.design_experiments()
    assert len(experiments) == 1  # one per theory
    assert experiments[0]["expected_divergence"] == 0.08  # max divergence
    assert experiments[0]["required_shots"] >= 10000
    assert os.path.exists("docs/NOVEL_EXPERIMENTAL_DESIGN.md")
