import os
import pytest
from quantum.validation.run_independent_reproduction import run_independent_reproduction_pipeline

def test_independent_reproduction_pipeline_orchestration():
    verdict = run_independent_reproduction_pipeline()
    assert verdict in (
        "SCIENTIFICALLY_REPRODUCIBLE_THEORY",
        "INDEPENDENTLY_REPRODUCIBLE_THEORY",
        "REPRODUCIBLE_THEORY",
        "FAILED_REPRODUCTION"
    )
    
    # Assert that all 8 mandatory documentation reports are created and exist
    reports = [
        "docs/RTHEORY_001_EXPORT.md",
        "docs/LOCKED_PREDICTIONS.md",
        "docs/REPRODUCTION_TOURNAMENT.md",
        "docs/CROSS_LAB_REPRODUCTION.md",
        "docs/LEAKAGE_AUDIT.md",
        "docs/EXTERNAL_REIMPLEMENTATION_REPORT.md",
        "docs/INDEPENDENT_REPRODUCTION_REPORT.md",
        "docs/FINAL_REPRODUCTION_VERDICT.md"
    ]
    
    for report_path in reports:
        assert os.path.exists(report_path), f"Mandatory report {report_path} was not generated!"
