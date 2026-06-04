import os
import json
import sqlite3
import pytest
from quantum.theory.theory_memory import TheoryMemory
from quantum.hardware.hardware_runner import HardwareRunner
from quantum.hardware.theory_experiment_generator import TheoryExperimentGenerator
from quantum.hardware.preregistered_predictions import PreregisteredPredictions
from quantum.hardware.hardware_replication import HardwareReplication
from quantum.hardware.temporal_stability import TemporalStability
from quantum.hardware.calibration_audit import CalibrationAudit
from quantum.hardware.hardware_adversary import HardwareAdversary
from quantum.hardware.ood_hardware_validation import OodHardwareValidation
from quantum.hardware.physical_mechanism_validation import PhysicalMechanismValidation
from quantum.hardware.hardware_fdr_audit import HardwareFdrAudit
from quantum.hardware.hardware_theory_tournament import HardwareTheoryTournament
from quantum.hardware.reality_evolution import RealityEvolution
from quantum.hardware.external_reproduction import ExternalReproduction
from quantum.hardware.negative_results_repository import NegativeResultsRepository
from quantum.hardware.hardware_consensus import HardwareConsensus

@pytest.fixture
def setup_hardware_test_db():
    db_path = "test_hardware_memory.db"
    
    # Setup standard database with dummy theories and predictions
    memory = TheoryMemory(db_path=db_path)
    
    theory = {
        "id": "THEORY_001",
        "name": "Test Information Entropy Coherence",
        "laws_explained": ["LAW_001"],
        "mechanism_graph": {
            "nodes": [
                {"id": "gate_entropy", "type": "input"},
                {"id": "structural_coherence", "type": "latent"},
                {"id": "transferability", "type": "output"}
            ],
            "edges": [
                {"source": "gate_entropy", "target": "structural_coherence", "weight": -0.80},
                {"source": "structural_coherence", "target": "transferability", "weight": 0.85}
            ]
        },
        "assumptions": ["A1"],
        "predictions": ["PRED_001"],
        "confidence": 0.85,
        "status": "CANDIDATE"
    }
    
    prediction = {
        "id": "PRED_001",
        "originating_theory": "THEORY_001",
        "prediction_statement": "If gate_entropy decreases, then transferability increases.",
        "antecedents": ["gate_entropy < 0.25"],
        "consequent": "transferability",
        "trend": "increases",
        "effect_size": 0.35,
        "confidence": 0.88,
        "status": "UNCONFIRMED"
    }
    
    memory.save_theory(theory)
    memory.save_prediction(prediction)
    
    yield db_path
    
    # Cleanup files
    for path in [
        db_path
    ]:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass
    if os.path.exists("reproduce"):
        try:
            os.rmdir("reproduce")
        except Exception:
            pass

def test_hardware_db_extensions(setup_hardware_test_db):
    db_path = setup_hardware_test_db
    memory = TheoryMemory(db_path=db_path)
    
    # 1. Preregistered predictions test
    pred = {
        "id": "PRED_TEST",
        "expected_effect": 0.12,
        "expected_direction": "greater_than",
        "expected_confidence": 0.85,
        "timestamp": "2026-06-04T12:00:00Z",
        "hash": "abc123hash"
    }
    memory.save_preregistered_prediction(pred)
    loaded = memory.get_preregistered_prediction("PRED_TEST")
    assert loaded is not None
    assert loaded["hash"] == "abc123hash"
    
    # 2. Hardware executions test
    exec_data = {
        "id": "EXEC_TEST",
        "backend": "IBM",
        "device": "ibm_sherbrooke",
        "shots": 1000,
        "error_rate": 0.015,
        "calibration_state": "NOMINAL",
        "timestamp": "2026-06-04T12:00:00Z"
    }
    memory.save_hardware_execution(exec_data)
    all_execs = memory.get_all_hardware_executions()
    assert len(all_execs) == 1
    assert all_execs[0]["device"] == "ibm_sherbrooke"
    
    # 3. Negative results test
    neg = {
        "id": "NEG_TEST",
        "type": "theory",
        "target_id": "THEORY_002",
        "reason": "Failed replication rate",
        "timestamp": "2026-06-04T12:00:00Z"
    }
    memory.save_negative_result(neg)
    all_negs = memory.get_all_negative_results()
    assert len(all_negs) == 1
    assert all_negs[0]["target_id"] == "THEORY_002"

def test_hardware_execution_and_translation(setup_hardware_test_db):
    db_path = setup_hardware_test_db
    
    # Test Runner
    runner = HardwareRunner(db_path=db_path)
    res = runner.execute("ibm_sherbrooke", shots=1000, calibration_state="nominal")
    assert res["device"] == "ibm_sherbrooke"
    assert res["shots"] == 1000
    assert "error_rate" in res
    
    # Test Translation
    gen = TheoryExperimentGenerator(db_path=db_path)
    translated = gen.translate_predictions()
    assert len(translated) == 1
    assert translated[0]["consequent"] == "transferability"
    assert translated[0]["expected_effect"] == 0.28  # Scaled from 0.35 * 0.8
    
    # Test Pre-registration
    prereg = PreregisteredPredictions(db_path=db_path)
    prereg.register_predictions(translated)
    assert prereg.verify_registry(translated) is True
    
    # Verify modification error
    translated[0]["expected_effect"] = 0.99
    with pytest.raises(ValueError):
        prereg.register_predictions(translated)

def test_hardware_validation_pipelines(setup_hardware_test_db):
    db_path = setup_hardware_test_db
    
    # Translate & Pre-register first
    gen = TheoryExperimentGenerator(db_path=db_path)
    translated = gen.translate_predictions()
    prereg = PreregisteredPredictions(db_path=db_path)
    prereg.register_predictions(translated)
    
    # 1. Replication Testing
    replication = HardwareReplication(db_path=db_path)
    rep_reports = replication.run_replication(translated)
    assert len(rep_reports) == 1
    assert rep_reports[0]["replication_rate"] >= 0.0
    
    # 2. Temporal stability Testing
    temporal = TemporalStability(db_path=db_path)
    temp_reports = temporal.run_temporal_audit(translated, device_name="ibm_sherbrooke")
    assert len(temp_reports) == 1
    assert "temporal_stability_score" in temp_reports[0]
    
    # 3. Calibration robustness testing
    calibration = CalibrationAudit(db_path=db_path)
    cal_reports = calibration.run_calibration_audit(translated, device_name="ibm_sherbrooke")
    assert len(cal_reports) == 1
    assert "robustness_coefficient" in cal_reports[0]
    
    # 4. Adversarial testing
    adversary = HardwareAdversary(db_path=db_path)
    adv_reports = adversary.run_adversarial_tests(translated, device_name="ibm_sherbrooke")
    assert len(adv_reports) == 1
    assert "adversarial_survival_rate" in adv_reports[0]
    
    # 5. OOD validation
    ood = OodHardwareValidation(db_path=db_path)
    ood_reports = ood.run_ood_validation(translated)
    assert len(ood_reports) == 1
    assert "ood_transfer_score" in ood_reports[0]

def test_mechanistic_fdr_and_evolution(setup_hardware_test_db):
    db_path = setup_hardware_test_db
    
    # Setup
    gen = TheoryExperimentGenerator(db_path=db_path)
    translated = gen.translate_predictions()
    prereg = PreregisteredPredictions(db_path=db_path)
    prereg.register_predictions(translated)
    
    replication = HardwareReplication(db_path=db_path)
    rep_reports = replication.run_replication(translated)
    temporal = TemporalStability(db_path=db_path)
    temp_reports = temporal.run_temporal_audit(translated, device_name="ibm_sherbrooke")
    calibration = CalibrationAudit(db_path=db_path)
    cal_reports = calibration.run_calibration_audit(translated, device_name="ibm_sherbrooke")
    adversary = HardwareAdversary(db_path=db_path)
    adv_reports = adversary.run_adversarial_tests(translated, device_name="ibm_sherbrooke")
    ood = OodHardwareValidation(db_path=db_path)
    ood_reports = ood.run_ood_validation(translated)
    
    # 1. Physical Mechanism Validation
    mechanism = PhysicalMechanismValidation(db_path=db_path)
    mech_reports = mechanism.run_mechanism_audit()
    assert len(mech_reports) == 1
    assert mech_reports[0]["status"] == "PASSED"
    
    # 2. FDR Controls
    fdr = HardwareFdrAudit(db_path=db_path)
    fdr_report = fdr.run_fdr_audit(rep_reports)
    assert fdr_report["total_tested"] == 1
    assert fdr_report["fdr_rate"] < 0.05
    
    # 3. Tournament Ranking
    tournament = HardwareTheoryTournament(db_path=db_path)
    standings = tournament.run_tournament(
        replication_reports=rep_reports,
        temporal_reports=temp_reports,
        calibration_reports=cal_reports,
        adversarial_reports=adv_reports,
        ood_reports=ood_reports,
        mechanism_reports=mech_reports,
        fdr_report=fdr_report
    )
    assert len(standings) == 1
    assert standings[0]["tournament_score"] > 0
    
    # 4. Evolution
    evolution = RealityEvolution(db_path=db_path)
    evo_records = evolution.evolve_theories(standings, temp_reports)
    assert len(evo_records) == 1
    assert evo_records[0]["new_status"] in ["HARDWARE_SUPPORTED_THEORY", "PARTIALLY_TRANSFERRED_THEORY", "RETIRED"]
    
    # 5. External reproduction package
    reproduction = ExternalReproduction(db_path=db_path)
    reprod_report = reproduction.package_reproduction_suite(translated)
    assert reprod_report["reproduction_script_packaged"] == "YES"
    
    # 6. Consensus calculations
    consensus = HardwareConsensus(db_path=db_path)
    consensus_report = consensus.calculate_consensus(
        replication_reports=rep_reports,
        temporal_reports=temp_reports,
        ood_reports=ood_reports,
        external_report=reprod_report,
        fdr_report=fdr_report
    )
    assert consensus_report["global_hardware_confidence_score"] > 0
    assert consensus_report["final_allowed_verdict"] in [
        "HARDWARE_SUPPORTED_THEORY", "PARTIALLY_TRANSFERRED_THEORY",
        "SIMULATION_ONLY_THEORY", "THEORY_RETRACTED"
    ]
