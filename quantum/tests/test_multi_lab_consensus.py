import os
import pytest
from quantum.scientific_reproduction.multi_lab_consensus import MultiLabConsensusEngine

def test_multi_lab_consensus():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    engine = MultiLabConsensusEngine(root)
    res = engine.calculate_consensus()
    
    assert res["status"] == "PASSED"
    assert res["consensus_score"] >= 0.90  # Must be > 90%
    
    report_path = os.path.join(root, "docs", "MULTI_LAB_CONSENSUS.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
