import os
import pytest
from quantum.scientific_reproduction.publication_readiness import PublicationReadinessAudit

def test_publication_readiness():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    audit = PublicationReadinessAudit(root)
    
    check_status = {
        "reproducibility": True,
        "traceability": True,
        "robustness": True,
        "interpretability": True,
        "falsifiability": True,
        "experimental_evidence": True,
        "alternative_explanations": True,
        "limitations_disclosed": True
    }
    res = audit.run_readiness_audit(check_status)
    
    assert res["status"] == "PASSED"
    assert res["readiness_score"] >= 0.90  # Must be > 90%
    
    report_path = os.path.join(root, "docs", "PUBLICATION_READINESS_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
