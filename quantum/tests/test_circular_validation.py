import os
import pytest
from quantum.external_audit.circular_validation_audit import CircularValidationAudit

def test_circular_validation():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    auditor = CircularValidationAudit(root)
    res = auditor.audit_circular_validation()
    
    assert res["status"] == "PASSED"
    assert res["self_referential_scoring"] is False
    assert res["recursive_validation"] is False
    assert res["metric_reuse"] is False
    
    report_path = os.path.join(root, "docs", "CIRCULAR_VALIDATION_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
