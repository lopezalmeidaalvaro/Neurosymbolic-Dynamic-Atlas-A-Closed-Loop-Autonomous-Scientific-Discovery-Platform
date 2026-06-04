import os
import pytest
from quantum.reality_native.cross_lab_simulation import CrossLabSimulationEngine

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

def test_cross_lab_simulation_flow(mock_validation_data, tmp_path):
    # Create a temp export file to ensure reconstruction uses mock values
    export_file = tmp_path / "RTHEORY_001_EXPORT.md"
    export_file.write_text("""
# Independent Theory Specification — RTHEORY_001
## 4. Parameter Specification
- **a (Gate Error Coefficient)**: `-1.5000`
- **b (Readout Error Coefficient)**: `-1.5000`
- **c (Intrinsic Calibration Offset)**: `-0.0020`
""", encoding="utf-8")

    engine = CrossLabSimulationEngine(export_path=str(export_file))
    results = engine.run_cross_lab_validation(mock_validation_data)
    
    assert "lab_a" in results
    assert "lab_b" in results
    assert "lab_c" in results
    assert "pairwise_agreements" in results
    assert "mean_agreement" in results
    
    # Since they all read the same specification file, the agreement should be 1.0 (100%)
    assert results["mean_agreement"] == 1.0
    assert results["pairwise_agreements"]["Lab_A_vs_Lab_B"] == 1.0
    
    # Report file checks
    assert os.path.exists("docs/CROSS_LAB_REPRODUCTION.md")
