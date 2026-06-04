import os
import pytest
from quantum.scientific_reproduction.independent_reanalysis import IndependentReanalysis

def test_independent_reanalysis():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    reanalysis = IndependentReanalysis(root)
    res = reanalysis.run_reanalysis()
    
    assert res["status"] == "PASS"
    for domain, record in res["reanalysis_records"].items():
        assert record["statistician_match"] == "PASS"
        assert record["physicist_validation"] == "PASS"
        assert record["engineer_status"] == "PASS"
        assert record["skeptic_status"] == "PASS"
        
    report_path = os.path.join(root, "docs", "INDEPENDENT_REANALYSIS_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
