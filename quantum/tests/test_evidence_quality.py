import os
import pytest
from quantum.scientific_reproduction.evidence_quality_engine import EvidenceQualityEngine

def test_evidence_quality():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    engine = EvidenceQualityEngine(root)
    
    # Test valid input matching full criteria
    res = engine.score_evidence({
        "checksum_integrity": True,
        "consensus_score": 1.0,
        "reproduction_rate": 1.0
    })
    
    assert res["status"] == "PASSED"
    assert res["quality_grade"] in ("VERY_HIGH", "HIGH")
    
    report_path = os.path.join(root, "docs", "EVIDENCE_QUALITY_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
