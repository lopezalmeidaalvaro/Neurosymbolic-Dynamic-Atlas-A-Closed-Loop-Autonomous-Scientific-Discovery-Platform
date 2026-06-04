import os
import pytest
from quantum.external_audit.adversarial_model_tournament import AdversarialModelTournament

def test_adversarial_tournament():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    tournament = AdversarialModelTournament(root)
    res = tournament.run_tournament()
    
    assert res["status"] == "PASSED"
    assert res["win_rate"] >= 0.75  # Must be > 75%
    
    report_path = os.path.join(root, "docs", "ADVERSARIAL_TOURNAMENT_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
