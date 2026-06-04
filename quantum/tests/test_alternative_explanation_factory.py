import os
import pytest
from quantum.scientific_reproduction.alternative_explanation_factory import AlternativeExplanationFactory

def test_alternative_explanation_factory():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    factory = AlternativeExplanationFactory(root)
    res = factory.run_factory()
    
    assert res["status"] == "PASS"
    for domain, record in res["comparison_records"].items():
        assert record["status"] == "RTHEORY_PREFERRED"
        
    report_path = os.path.join(root, "docs", "ALTERNATIVE_EXPLANATION_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
