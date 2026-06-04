import os
import pytest
from quantum.external_audit.external_hardware_challenge import ExternalHardwareChallenge

def test_external_hardware():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    challenge = ExternalHardwareChallenge(root)
    res = challenge.run_hardware_challenge()
    
    assert res["status"] == "PASSED"
    assert res["replication_rate"] >= 0.90  # Must be > 90%
    
    report_path = os.path.join(root, "docs", "EXTERNAL_HARDWARE_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
