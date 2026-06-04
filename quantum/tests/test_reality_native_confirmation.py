import os
import json
import sqlite3
import pytest
import numpy as np

from quantum.reality_native.reality_native_confirmation import RealityNativeConfirmationEngine
from quantum.validation.run_reality_native_confirmation import run_confirmation_pipeline

@pytest.fixture
def temp_reality_db(tmp_path):
    reality_db = str(tmp_path / "test_reality_native_confirmation.db")
    
    # Pre-populate the database with the discovered law table and dummy rule
    conn = sqlite3.connect(reality_db)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discovered_laws (
            id TEXT PRIMARY KEY,
            equation TEXT,
            confidence REAL,
            complexity REAL,
            supporting_observations TEXT,
            cross_platform_support TEXT
        )
    """)
    cursor.execute("""
        INSERT INTO discovered_laws (id, equation, confidence, complexity, supporting_observations, cross_platform_support)
        VALUES ('RLAW_001', 'Gap = 2.4500 * E_gate + 1.1200 * E_readout + 0.0100', 1.0, 1.0, '[]', '{"vendors": ["IBM"], "paradigms": ["Superconducting"]}')
    """)
    conn.commit()
    conn.close()
    
    return reality_db

def test_reality_native_confirmation_flow(temp_reality_db):
    engine = RealityNativeConfirmationEngine(reality_db_path=temp_reality_db)
    
    # 1. Test Dataset Generation & Independence
    confirmation_data = engine.generate_independent_dataset()
    assert len(confirmation_data) == 4
    
    # Verify different backends and no overlap with original training list
    discovery_devices = {"ibm_sherbrooke", "ionq_aria", "rigetti_aspen", "quantinuum_h1"}
    confirmation_devices = {run["device"] for run in confirmation_data}
    assert len(discovery_devices.intersection(confirmation_devices)) == 0
    
    # 2. Test Tournament Evaluator
    results = engine.run_tournament(confirmation_data)
    
    assert "SIM_THEORY" in results
    assert "RTHEORY_001" in results
    
    rn = results["RTHEORY_001"]
    sim = results["SIM_THEORY"]
    
    # Assert error measurements are computed directly
    assert rn["MAE"] < sim["MAE"]
    assert rn["RMSE"] < sim["RMSE"]
    assert rn["MedianAbsoluteError"] < sim["MedianAbsoluteError"]
    assert rn["ReplicationRate"] == 1.0 # Due to low measurement noise (std=0.0003)
    assert rn["ImprovementPercent"] >= 15.0
    
    # 3. Test Adversarial Re-Evaluation Audits
    adv = engine.run_adversarial_reevaluation(confirmation_data, results)
    
    assert adv["leakage_audit"] == "PASSED"
    assert adv["overfit_audit"] == "PASSED"
    assert adv["counterfactual_audit"] == "PASSED"
    assert adv["vendor_ablation_audit"] == "PASSED"
    assert adv["technology_ablation_audit"] == "PASSED"
    assert adv["all_passed"]

def test_run_confirmation_orchestrator():
    # Run the main confirmation runner pipeline and verify it finishes successfully
    verdict = run_confirmation_pipeline()
    assert verdict == "CONFIRMED_REALITY_NATIVE_THEORY"
    
    # Verify report files were generated
    assert os.path.exists("docs/REALITY_NATIVE_CONFIRMATION_REPORT.md")
    assert os.path.exists("docs/THEORY_TOURNAMENT_CONFIRMATION.md")
    assert os.path.exists("docs/INDEPENDENT_PREDICTION_AUDIT.md")
    assert os.path.exists("docs/FINAL_EPISTEMIC_VERDICT.md")
