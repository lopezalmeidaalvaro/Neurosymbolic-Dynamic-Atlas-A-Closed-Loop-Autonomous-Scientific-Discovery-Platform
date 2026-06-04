import os
import pytest
from quantum.novel_physics.alternative_explanation_audit import AlternativeExplanationAudit

def test_alternative_explanation_audit():
    # Simulate validation results with large observed gaps that exceed all conventional limits
    mock_validation = {
        "validation_results": {
            "IMP_001_00": {
                "theory_id": "RTHEORY_001",
                "domain": "quantum_hardware_noise",
                "gate_error": 0.01,
                "readout_error": 0.02,
                "observed_gap": -0.045,  # large enough to survive all conventional checks
                "mae_standard": 0.045,
                "mae_rtheory": 0.0003,
                "status": "VERIFIED"
            },
            "IMP_002_00": {
                "theory_id": "RTHEORY_002",
                "domain": "calibration_drift",
                "gate_error": 0.01,
                "readout_error": 0.025,
                "observed_gap": -0.038,
                "mae_standard": 0.038,
                "mae_rtheory": 0.0002,
                "status": "VERIFIED"
            }
        }
    }
    auditor = AlternativeExplanationAudit(mock_validation)
    results = auditor.audit_explanations()

    assert "elimination_rate" in results
    assert results["elimination_rate"] >= 0.70
    assert results["status"] == "PASSED"
    for case_id, rec in results["audit_records"].items():
        assert rec["status"] == "ELIMINATED_ALL_CONVENTIONAL"
    assert os.path.exists("docs/ALTERNATIVE_EXPLANATION_AUDIT.md")
