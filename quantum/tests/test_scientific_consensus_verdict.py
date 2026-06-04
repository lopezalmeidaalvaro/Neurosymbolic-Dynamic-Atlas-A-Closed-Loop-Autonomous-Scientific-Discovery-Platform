import os
import pytest
from quantum.scientific_reproduction.scientific_consensus_verdict import ScientificConsensusVerdict

def test_scientific_consensus_verdict():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    engine = ScientificConsensusVerdict(root)
    
    # 1. Test full pass -> COMMUNITY_READY_NEW_PHYSICS_CANDIDATE
    res_full = {
        "consensus_score": 1.0,
        "quality_grade": "VERY_HIGH",
        "reject_count": 0,
        "readiness_score": 1.0
    }
    verdict_full = engine.evaluate_verdict(res_full)
    assert verdict_full == "COMMUNITY_READY_NEW_PHYSICS_CANDIDATE"
    
    # 2. Test 3 passes -> STRONG_NEW_PHYSICS_CANDIDATE
    res_partial = {
        "consensus_score": 0.85, # fails
        "quality_grade": "VERY_HIGH", # passes
        "reject_count": 0, # passes
        "readiness_score": 0.95 # passes
    }
    verdict_partial = engine.evaluate_verdict(res_partial)
    assert verdict_partial == "STRONG_NEW_PHYSICS_CANDIDATE"
    
    report_path = os.path.join(root, "docs", "FINAL_SCIENTIFIC_VERDICT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
