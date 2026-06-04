import os
import pytest
from quantum.validation.run_novel_physics import run_novel_physics_program

def test_novel_physics_pipeline():
    """End-to-end pipeline test for Phase 4 New Physics Discovery Program."""
    verdict = run_novel_physics_program()

    # The pipeline must reach the strongest verdict
    assert verdict == "INDEPENDENTLY_REPLICATED_NEW_PHYSICS_CANDIDATE"

    # Verify all mandatory reports were generated
    mandatory_reports = [
        "docs/RESIDUAL_FRONTIER_REPORT.md",
        "docs/NOVEL_EFFECT_REPORT.md",
        "docs/IMPOSSIBLE_PREDICTIONS.md",
        "docs/NOVEL_EXPERIMENTAL_DESIGN.md",
        "docs/NOVEL_PREDICTION_LOCK.md",
        "docs/NOVEL_PHYSICS_VALIDATION.md",
        "docs/ALTERNATIVE_EXPLANATION_AUDIT.md",
        "docs/NOVEL_PHYSICS_IMPACT.md",
        "docs/FINAL_NOVEL_PHYSICS_VERDICT.md",
    ]

    for report in mandatory_reports:
        assert os.path.exists(report), f"Report {report} should be generated"
        assert os.path.getsize(report) > 0, f"Report {report} should not be empty"
