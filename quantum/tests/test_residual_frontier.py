import os
import pytest
from quantum.novel_physics.residual_frontier_engine import ResidualFrontierEngine

def test_residual_frontier():
    engine = ResidualFrontierEngine()
    observations = [
        {"id": "R1", "device": "d1", "vendor": "IBM", "paradigm": "SC",
         "gate_error": 0.01, "readout_error": 0.02, "observed_gap": -0.045},
        {"id": "R2", "device": "d2", "vendor": "IonQ", "paradigm": "IT",
         "gate_error": 0.005, "readout_error": 0.01, "observed_gap": -0.020},
    ]
    residuals = engine.discover_residuals(observations)
    assert len(residuals) == 2
    # Standard prediction is 0.0, so residual == observed_gap
    assert residuals[0]["residual_gap"] == pytest.approx(-0.045, abs=1e-5)
    assert residuals[1]["residual_gap"] == pytest.approx(-0.020, abs=1e-5)
    assert os.path.exists("docs/RESIDUAL_FRONTIER_REPORT.md")
