import os
import pytest
from quantum.external_audit.double_blind_reproduction import DoubleBlindReproduction

def test_double_blind():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    db = DoubleBlindReproduction(root)
    res = db.run_double_blind()
    
    assert res["status"] == "PASSED"
    assert res["prediction_agreement"] >= 0.90  # Must be > 90%
    assert res["classification_agreement"] >= 0.90
    
    report_path = os.path.join(root, "docs", "DOUBLE_BLIND_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
