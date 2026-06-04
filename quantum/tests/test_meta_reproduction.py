import os
import pytest
from quantum.external_audit.meta_reproduction_engine import MetaReproductionEngine

def test_meta_reproduction():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    meta = MetaReproductionEngine(root)
    res = meta.run_meta_analysis()
    
    assert res["status"] == "PASSED"
    assert res["meta_reproduction_rate"] >= 0.90  # Must be > 90%
    
    report_path = os.path.join(root, "docs", "META_REPRODUCTION_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
