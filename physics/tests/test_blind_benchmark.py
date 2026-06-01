#!/usr/bin/env python3
"""
Unit Tests for Fase 28.5 - Blind Benchmark Revisado
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import pytest
import json
from pathlib import Path

# Add project root to sys.path to enable absolute imports
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from physics.benchmark.isolated_environment import create_isolated_benchmark_environment
from physics.benchmark.benchmark_scorer import BenchmarkScorer

def test_blind_benchmark_isolation_integrity():
    """
    Tests that create_isolated_benchmark_environment prunes all forbidden nodes
    and generates benchmark_environment_report.json.
    """
    env_report = create_isolated_benchmark_environment()
    
    # 1. Assert contamination self-audits are clean
    assert env_report["memory_contamination"] is False
    assert env_report["kg_contamination"] is False
    assert env_report["status"] == "fully_isolated"
    
    # 2. Check that the report file exists
    report_file = Path("physics/benchmark/benchmark_environment_report.json")
    assert report_file.exists()
    
    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["memory_contamination"] is False
    assert data["kg_contamination"] is False

def test_blind_benchmark_scoring_integrity():
    """
    Tests that the BenchmarkScorer correctly parses mock/discovered equations,
    generates matplotlib comparative charts, and outputs global scores in [0, 100].
    """
    scorer = BenchmarkScorer()
    
    results_mock = {
        "problem_A": {"best_equation": "b(r) = 0.5*(0.5/r)**2"},
        "problem_B": {"best_equation": "f(r) = 0.5*(1.0-tanh(10.0*(r-0.5)))"},
        "problem_C": {"best_equation": "r**3/(r**3+1.5)"}
    }
    
    res_path = Path("physics/benchmark/temp_test_results.json")
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump(results_mock, f)
        
    env_mock = {"memory_contamination": False, "kg_contamination": False}
    env_path = Path("physics/benchmark/temp_test_env.json")
    with open(env_path, "w", encoding="utf-8") as f:
        json.dump(env_mock, f)
        
    try:
        # Run scoring
        scores = scorer.score_benchmark(str(res_path), str(env_path))
        
        # 3. Assert scores are bounded correctly
        assert 0.0 <= scores["problem_score_A"] <= 100.0
        assert 0.0 <= scores["problem_score_B"] <= 100.0
        assert 0.0 <= scores["problem_score_C"] <= 100.0
        assert 0.0 <= scores["global_score"] <= 100.0
        assert scores["classification"] in ["EXCELLENT", "GOOD", "INSUFFICIENT", "SUSPICIOUS"]
        
        # 4. Verify plot files exist on disk
        img_dir = Path("physics/benchmark/equations_comparison")
        assert (img_dir / "A_comparison.png").exists()
        assert (img_dir / "B_comparison.png").exists()
        assert (img_dir / "C_comparison.png").exists()
        
        # 5. Verify score json output
        scores_file = Path("physics/benchmark/benchmark_scores.json")
        assert scores_file.exists()
        
    finally:
        # Clean up temporary test files
        if res_path.exists(): os.remove(res_path)
        if env_path.exists(): os.remove(env_path)
