import os
import pytest
from quantum.external_audit.external_review_panel import ExternalReviewPanel

def test_external_panel():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    panel = ExternalReviewPanel(root)
    
    # test evaluation with valid scores
    metrics = {
        "leakage_score": 0.0,
        "checksum_integrity": 1.0,
        "red_team_equivalence": 1.0,
        "double_blind_agreement": 0.99,
        "external_hardware_replication": 1.0,
        "independent_physics_survival": 1.0
    }
    res = panel.evaluate_panel(metrics)
    
    assert res["status"] == "PASSED"
    assert res["panel_score"] >= 80.0  # Must be > 80%
    
    report_path = os.path.join(root, "docs", "EXTERNAL_PANEL_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
