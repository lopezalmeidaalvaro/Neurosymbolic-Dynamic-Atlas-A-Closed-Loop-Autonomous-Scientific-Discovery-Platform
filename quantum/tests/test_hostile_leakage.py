import os
import pytest
from quantum.external_audit.hostile_leakage_audit import HostileLeakageAudit

def test_hostile_leakage():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    auditor = HostileLeakageAudit(root)
    res = auditor.run_leakage_audit()
    
    assert res["status"] == "PASSED"
    assert res["leakage_score"] < 0.01  # Must be < 1%
    assert res["device_overlap"] == 0.0
    
    report_path = os.path.join(root, "docs", "HOSTILE_LEAKAGE_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
