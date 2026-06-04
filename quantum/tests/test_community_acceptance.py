import os
import pytest
from quantum.scientific_reproduction.community_acceptance import CommunityAcceptanceSimulator

def test_community_acceptance():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    sim = CommunityAcceptanceSimulator(root)
    
    metrics = {
        "leakage_score": 0.0,
        "quality_grade": "VERY_HIGH",
        "consensus_score": 1.0,
        "readiness_score": 1.0
    }
    res = sim.simulate_peer_review(metrics)
    
    assert res["status"] == "PASSED"
    assert res["reject_count"] == 0  # Rejections must be 0
    assert res["accept_count"] + res["minor_revisions_count"] >= 4
    
    report_path = os.path.join(root, "docs", "COMMUNITY_ACCEPTANCE_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
