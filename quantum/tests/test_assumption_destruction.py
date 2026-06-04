import os
import pytest
from quantum.scientific_reproduction.assumption_destruction import AssumptionDestructionEngine

def test_assumption_destruction():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    destruction = AssumptionDestructionEngine(root)
    res = destruction.run_destruction()
    
    assert res["status"] == "PASS"
    for domain, record in res["destruction_results"].items():
        assert "mae_baseline" in record
        assert "mae_no_gate" in record
        assert record["necessity_verified"] == "YES"
        
    report_path = os.path.join(root, "docs", "ASSUMPTION_DESTRUCTION_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
