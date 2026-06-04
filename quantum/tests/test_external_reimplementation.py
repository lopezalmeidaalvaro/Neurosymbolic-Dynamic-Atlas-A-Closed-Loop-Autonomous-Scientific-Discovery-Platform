import os
import pytest
from quantum.reality_native.external_reimplementation_challenge import ExternalReimplementationChallenge

@pytest.fixture
def mock_validation_data():
    return [
        {
            "id": "RUN_000",
            "device": "superconducting_odin",
            "gate_error": 0.005,
            "readout_error": 0.010,
            "predicted_sim": 0.3694,
            "observed": 0.3551
        },
        {
            "id": "RUN_001",
            "device": "superconducting_freya",
            "gate_error": 0.003,
            "readout_error": 0.008,
            "predicted_sim": 0.3694,
            "observed": 0.3601
        }
    ]

def test_external_reimplementation_flow(mock_validation_data, tmp_path):
    export_file = tmp_path / "RTHEORY_001_EXPORT.md"
    export_file.write_text("""
# Independent Theory Specification — RTHEORY_001
## 4. Parameter Specification
- **a (Gate Error Coefficient)**: `-1.5000`
- **b (Readout Error Coefficient)**: `-1.5000`
- **c (Intrinsic Calibration Offset)**: `-0.0020`
""", encoding="utf-8")

    engine = ExternalReimplementationChallenge(export_path=str(export_file))
    results = engine.run_challenge(mock_validation_data)
    
    assert "prediction_equivalence" in results
    assert "mae_difference" in results
    assert "calibration_difference" in results
    assert "decision_agreement" in results
    assert "status" in results
    
    # Check that predictions are perfectly equivalent (since they are generated from same equations & coefficients)
    assert results["prediction_equivalence"] == 1.0
    assert results["mae_difference"] == 0.0
    assert results["decision_agreement"] == 1.0
    assert results["status"] == "PASSED"
    
    # Check output files
    assert os.path.exists("external_predictor.py")
    assert os.path.exists("docs/EXTERNAL_REIMPLEMENTATION_REPORT.md")
