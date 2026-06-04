import os
import pytest
from quantum.external_audit.red_team_reimplementation import RedTeamReimplementation

def test_red_team_reimplementation():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    reimpl = RedTeamReimplementation(root)
    res = reimpl.run_reimplementation()
    
    assert res["status"] == "PASSED"
    assert res["equivalence_rate"] >= 0.95  # Must be > 95%
    assert res["mean_deviation"] < 1e-4
    
    report_path = os.path.join(root, "docs", "RED_TEAM_REIMPLEMENTATION_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
