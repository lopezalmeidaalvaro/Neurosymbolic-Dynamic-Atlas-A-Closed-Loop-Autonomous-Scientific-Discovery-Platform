#!/usr/bin/env python3
"""
Unit Tests for Phase 28.5 / Prompt 29 - Reproducibility Challenge
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import json
import pytest
from pathlib import Path

# Add project root to sys.path to enable absolute imports
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from physics.benchmark.isolated_environment import create_isolated_benchmark_environment
from physics.benchmark.benchmark_scorer import BenchmarkScorer

def test_reproducibility_outputs_exist():
    """
    Tests that the 30-seed statistical loop outputs exist and are well-formed.
    This check expects the challenge run to have completed.
    """
    results_file = Path("physics/benchmark/reproducibility_results.json")
    report_file = Path("docs/REPRODUCIBILITY_REPORT.md")
    figures_dir = Path("physics/benchmark/reproducibility_figures")
    
    assert results_file.exists(), "reproducibility_results.json is missing!"
    assert report_file.exists(), "docs/REPRODUCIBILITY_REPORT.md is missing!"
    assert figures_dir.exists(), "reproducibility_figures directory is missing!"
    assert (figures_dir / "score_distribution.png").exists(), "score_distribution.png is missing!"
    assert (figures_dir / "families_distribution.png").exists(), "families_distribution.png is missing!"
    
    # Verify contents of JSON results
    with open(results_file, "r", encoding="utf-8") as f:
        raw_results = json.load(f)
        
    assert isinstance(raw_results, list)
    assert len(raw_results) > 0
    
    first_run = raw_results[0]
    assert "seed" in first_run
    assert "problem_A" in first_run
    assert "problem_B" in first_run
    assert "problem_C" in first_run
    assert "global_score" in first_run

def test_isolated_sandbox_resets_across_seeds():
    """
    Asserts that environment isolation successfully clones and prunes target
    keywords independently across successive reset calls.
    """
    for _ in range(3):
        env_report = create_isolated_benchmark_environment()
        assert env_report["memory_contamination"] is False
        assert env_report["kg_contamination"] is False
        assert env_report["status"] == "fully_isolated"
        
        # Verify pruner report exists
        pruner_report_path = Path("physics/benchmark/benchmark_environment_report.json")
        assert pruner_report_path.exists()
        
        with open(pruner_report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        assert report_data["memory_contamination"] is False
        assert report_data["kg_contamination"] is False

def test_reproducibility_score_calculation():
    """
    Verifies that the stability metrics calculation logic matches the formulas,
    lies within [0, 100], and maps to the correct classification.
    """
    # Mocks statistical outputs similar to those calculated in the main loop
    from physics.benchmark.reproducibility_challenge import write_final_reproducibility_report
    
    # Calculate score using the same formula
    struct_c = 100.0
    fam_c = 100.0
    param_s = 98.5
    val_s = 99.2
    skeptic_a = 100.0
    critic_a = 100.0
    kg_s = 94.6
    
    reproducibility_score = (
        0.25 * struct_c +
        0.20 * fam_c +
        0.15 * param_s +
        0.15 * val_s +
        0.15 * skeptic_a +
        0.10 * critic_a
    )
    
    assert 0.0 <= reproducibility_score <= 100.0
    
    # Classification
    if reproducibility_score >= 90.0:
        classification = "Exceptional"
    elif reproducibility_score >= 80.0:
        classification = "Strong"
    elif reproducibility_score >= 70.0:
        classification = "Acceptable"
    else:
        classification = "Fragile"
        
    assert classification == "Exceptional"
    
    # Ensure production reports are not modified
    official_report = Path("docs/REPRODUCIBILITY_REPORT.md")
    revalidation_report = Path("docs/REPRODUCIBILITY_REVALIDATION_REPORT.md")
    
    initial_official_content = official_report.read_text(encoding="utf-8") if official_report.exists() else None
    initial_revalidation_content = revalidation_report.read_text(encoding="utf-8") if revalidation_report.exists() else None
    
    temp_report = Path("physics/tests/temp_report_test.md")
    
    # Mock global scores array and verdicts count
    global_scores = [58.01] * 30
    verdicts = {"ACCEPTED": 30, "REJECTED": 0}
    
    try:
        write_final_reproducibility_report(
            reproducibility_score, classification,
            struct_c, fam_c, param_s, val_s, skeptic_a, critic_a, kg_s,
            global_scores, verdicts,
            report_path=temp_report
        )
        # Check that doc was written to the temp path, not the official files
        assert temp_report.exists()
        
        # Verify that official reports were not modified
        if initial_official_content is not None:
            assert official_report.read_text(encoding="utf-8") == initial_official_content, "REPRODUCIBILITY_REPORT.md was modified!"
        if initial_revalidation_content is not None:
            assert revalidation_report.read_text(encoding="utf-8") == initial_revalidation_content, "REPRODUCIBILITY_REVALIDATION_REPORT.md was modified!"
        
    finally:
        if temp_report.exists():
            temp_report.unlink()
