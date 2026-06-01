#!/usr/bin/env python3
"""
Unit Tests for ReproducibilityVerification Module
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import pytest
from pathlib import Path

# Add project root to sys.path to enable absolute imports
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from physics.reproducibility_verification import ReproducibilityVerification

def test_reproducibility_verification_execution():
    """
    Tests that the ReproducibilityVerification module can be instantiated
    and executed successfully, generating all necessary artifact files.
    """
    verifier = ReproducibilityVerification()
    
    # 1. Assert initial state is correct
    assert verifier.status == "initialized"
    
    # 2. Run the reproducibility audit
    result = verifier.run()
    
    # 3. Assert execution completed cleanly
    assert verifier.status == "completed"
    assert "metrics" in result
    assert "report_path" in result
    
    metrics = result["metrics"]
    
    # 4. Verify score boundaries and indices
    assert 0.0 <= metrics["DiscoveryReproducibility"] <= 100.0
    assert 0.0 <= metrics["SeedRobustness"] <= 100.0
    assert 0.0 <= metrics["SubsamplingRobustness"] <= 100.0
    assert 0.0 <= metrics["NoiseRobustness"] <= 100.0
    assert 0.0 <= metrics["EpistemicConsistency"] <= 100.0
    assert 0.0 <= metrics["ReproducibilityIndex"] <= 100.0
    
    # 5. Verify correct classification
    assert metrics["Classification"] in ["EXCELLENT", "GOOD", "ACCEPTABLE", "WEAK", "CRITICAL"]
    
    # 6. Verify that files are persisted to disk
    artifacts_dir = Path(verifier.artifacts_dir)
    metrics_file = artifacts_dir / "reproducibility_metrics.json"
    summary_file = artifacts_dir / "reproducibility_summary.json"
    report_file = artifacts_dir / "reproducibility_report.md"
    
    assert metrics_file.exists()
    assert summary_file.exists()
    assert report_file.exists()
    
    # Verify content format inside metrics
    with open(metrics_file, "r", encoding="utf-8") as f:
        import json
        metrics_data = json.load(f)
    assert "ReproducibilityIndex" in metrics_data
    assert "Classification" in metrics_data
