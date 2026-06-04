import os
import pytest
from quantum.external_audit.external_epistemic_verdict import ExternalEpistemicVerdict

def test_external_verdict():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    verdict_engine = ExternalEpistemicVerdict(root)
    
    # Simulate a set of results that meet all success criteria
    metrics = {
        "leakage_score": 0.0,
        "checksum_integrity": True,
        "red_team_equivalence": 1.0,
        "double_blind_agreement": 0.99,
        "external_hardware_replication": 1.0,
        "adversarial_tournament_win_rate": 1.0,
        "independent_physics_survival": 1.0,
        "external_review_score": 94.5,
        "meta_reproduction_rate": 1.0
    }
    
    verdict = verdict_engine.evaluate_verdict(metrics)
    assert verdict == "EXTERNALLY_AUDITED_NEW_PHYSICS_CANDIDATE"
    
    report_path = os.path.join(root, "docs", "FINAL_EXTERNAL_AUDIT_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
