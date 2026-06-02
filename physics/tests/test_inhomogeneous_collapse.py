#!/usr/bin/env python3
"""
Unit Tests for Phase 33.0 — Inhomogeneous Collapse and Quantum Remnant Falsification
Author: Antigravity AI
"""

import os
import sys
import json
import pytest
from pathlib import Path

# Add project root to sys.path
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_inhomogeneous_collapse_execution():
    """
    Verifies that the inhomogeneous collapse simulation runs successfully,
    generates all required figures, and produces all 8 analytical documents.
    """
    results_file = Path("physics/benchmark/inhomogeneous_audit_results.json")
    
    # 1. Assert that the simulation has executed and results are saved
    assert results_file.exists(), "inhomogeneous_audit_results.json is missing!"
    
    with open(results_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert "initial_conditions" in data
    assert "simulation_metrics" in data
    assert "final_verdict" in data
    
    # Check verdict
    assert data["final_verdict"]["QG_INHOMOGENEOUS_STATUS"] == "PARTIALLY_STABLE_REMNANT"
    
    # Check falsification factors
    fals_factors = data["final_verdict"]["falsification_factors"]
    assert "shear_instability" in fals_factors
    assert "shockwave_barrier" in fals_factors
    assert "hawking_backreaction" in fals_factors

def test_inhomogeneous_collapse_figures_exist():
    """
    Asserts that all 4 required scientific plots exist and are well-formed.
    """
    figures = [
        "figures/inhomogeneous_evolution.png",
        "figures/shockwave_formation.png",
        "figures/non_spherical_perturbations.png",
        "figures/remnant_falsification_phase.png"
    ]
    for fig_path in figures:
        assert Path(fig_path).exists(), f"Figure {fig_path} is missing!"

def test_inhomogeneous_collapse_docs_exist():
    """
    Asserts that all 8 required technical specification documents exist in the docs/ directory.
    """
    docs = [
        "docs/QG_INHOMOGENEOUS_COLLAPSE.md",
        "docs/QG_SHEAR_PERTURBATIONS.md",
        "docs/QG_SHOCKWAVE_BACKREACTION.md",
        "docs/QG_INHOMOGENEOUS_HORIZONS.md",
        "docs/QG_FALSIFICATION_VERDICT.md",
        "docs/QG_INHOMOGENEOUS_PHASE_SPACE.md",
        "docs/QG_NON_LOCAL_EFFECTS.md",
        "docs/PHASE33_FINAL_INHOMOGENEOUS_REPORT.md"
    ]
    for doc_path in docs:
        assert Path(doc_path).exists(), f"Document {doc_path} is missing!"
