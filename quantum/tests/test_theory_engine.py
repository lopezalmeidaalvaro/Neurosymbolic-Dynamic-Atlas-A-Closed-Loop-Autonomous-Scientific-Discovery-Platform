import os
import json
import sqlite3
import pytest
from quantum.theory.theory_memory import TheoryMemory
from quantum.theory.theory_generator import TheoryGenerator
from quantum.theory.mechanism_engine import MechanismEngine
from quantum.theory.mechanistic_grounding import MechanisticGrounding
from quantum.theory.theory_compression import TheoryCompression
from quantum.theory.law_coverage import LawCoverage
from quantum.theory.prediction_engine import PredictionEngine
from quantum.theory.independent_confirmation import IndependentConfirmation
from quantum.theory.synthetic_theory_recovery import SyntheticTheoryRecovery
from quantum.theory.historical_recovery import HistoricalRecovery
from quantum.theory.theory_tournament import TheoryTournament
from quantum.theory.theory_evolution import TheoryEvolution
from quantum.theory.blind_validation import BlindTheoryValidation
from quantum.theory.adversarial_theory_tests import AdversarialTheoryTests

@pytest.fixture
def setup_test_db():
    db_path = "test_theory_memory.db"
    laws_path = "test_laws_registry.json"
    data_path = "test_obs_dataset.json"
    
    # 1. Create dummy laws in registry
    laws_data = {
        "laws": {
            "LAW_001": {
                "rule": "IF gate_entropy < 0.25 THEN transferability increases",
                "status": "SCIENTIFICALLY_ESTABLISHED"
            },
            "LAW_002": {
                "rule": "IF stabilizer_overlap > 0.6 AND tensor_rank < 3 THEN synergy increases",
                "status": "SCIENTIFICALLY_ESTABLISHED"
            },
            "LAW_003": {
                "rule": "IF clifford_ratio > 0.7 THEN noise_resilience increases",
                "status": "SCIENTIFICALLY_ESTABLISHED"
            },
            "LAW_004": {
                "rule": "IF betweenness_centrality > 0.25 THEN novelty increases",
                "status": "SCIENTIFICALLY_ESTABLISHED"
            }
        }
    }
    with open(laws_path, "w", encoding="utf-8") as f:
        json.dump(laws_data, f, indent=2)
        
    # 2. Create dummy observations
    obs_list = []
    for idx in range(100):
        obs_list.append({
            "domain": "QFT" if idx % 2 == 0 else "Grover",
            "utility": 0.8 if idx % 2 == 0 else 0.4,
            "synergy": 0.9 if idx % 3 == 0 else 0.2,
            "transferability": 0.9 if idx % 4 == 0 else 0.3,
            "novelty": 0.85 if idx % 5 == 0 else 0.1,
            "noise_resilience": 0.95 if idx % 2 == 0 else 0.5,
            "gate_entropy": 0.1 if idx % 4 == 0 else 0.6,
            "stabilizer_overlap": 0.8 if idx % 3 == 0 else 0.2,
            "tensor_rank": 2 if idx % 3 == 0 else 10,
            "clifford_ratio": 0.9 if idx % 2 == 0 else 0.3,
            "betweenness_centrality": 0.35 if idx % 5 == 0 else 0.1,
            "gate_distribution_distance": 0.1,
            "fidelity": 0.9,
            "clustering_coefficient": 0.3
        })
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(obs_list, f, indent=2)

    yield db_path, laws_path, data_path

    # Clean up files
    for path in [db_path, laws_path, data_path, "theory_compression_report.json", "law_coverage_report.json", "independent_confirmation_report.json", "theory_tournament_report.json", "theory_evolution_report.json", "blind_theory_validation_report.json", "adversarial_theory_report.json", "docs/THEORY_LEADERBOARD.md"]:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass

def test_theory_memory(setup_test_db):
    db_path, _, _ = setup_test_db
    memory = TheoryMemory(db_path=db_path)
    
    # Save a theory
    theory = {
        "id": "THEORY_TEST",
        "laws_explained": ["LAW_001"],
        "mechanism_graph": {"nodes": [], "edges": []},
        "assumptions": ["A1"],
        "predictions": ["P1"],
        "confidence": 0.8,
        "status": "CANDIDATE"
    }
    memory.save_theory(theory)
    
    loaded = memory.get_theory("THEORY_TEST")
    assert loaded is not None
    assert loaded["confidence"] == 0.8
    assert "LAW_001" in loaded["laws_explained"]

def test_theory_generation_and_mechanisms(setup_test_db):
    db_path, laws_path, data_path = setup_test_db
    
    # Generate
    generator = TheoryGenerator(laws_path=laws_path, db_path=db_path)
    theories = generator.generate_theories()
    assert len(theories) == 4
    
    # Mechanisms
    engine = MechanismEngine(data_path=data_path, db_path=db_path)
    updated_theories = engine.explain_mechanisms()
    assert len(updated_theories) == 4
    assert len(updated_theories[0]["mechanism_graph"]["edges"]) > 0

def test_causal_grounding_and_compression(setup_test_db):
    db_path, laws_path, data_path = setup_test_db
    
    # Setup database with theories and mechanisms
    generator = TheoryGenerator(laws_path=laws_path, db_path=db_path)
    generator.generate_theories()
    engine = MechanismEngine(data_path=data_path, db_path=db_path)
    engine.explain_mechanisms()
    
    # Grounding
    grounding = MechanisticGrounding(data_path=data_path, db_path=db_path)
    results = grounding.run_grounding_audit()
    assert len(results) == 4
    
    # Compression
    compression = TheoryCompression(db_path=db_path)
    comp_metrics = compression.calculate_compression_metrics()
    assert comp_metrics["compression_ratio"] > 0
    assert comp_metrics["mdl_score"] > 0

def test_coverage_and_predictions(setup_test_db):
    db_path, laws_path, data_path = setup_test_db
    
    generator = TheoryGenerator(laws_path=laws_path, db_path=db_path)
    generator.generate_theories()
    
    # Coverage
    cov = LawCoverage(db_path=db_path)
    cov_report = cov.evaluate_coverage()
    assert cov_report["coverage_ratio"] > 0.0
    
    # Prediction Generator
    pred_eng = PredictionEngine(data_path=data_path, db_path=db_path)
    preds = pred_eng.generate_predictions()
    assert len(preds) > 0

def test_independent_confirmation_and_recovery(setup_test_db):
    db_path, laws_path, data_path = setup_test_db
    
    generator = TheoryGenerator(laws_path=laws_path, db_path=db_path)
    generator.generate_theories()
    engine = MechanismEngine(data_path=data_path, db_path=db_path)
    engine.explain_mechanisms()
    pred_eng = PredictionEngine(data_path=data_path, db_path=db_path)
    pred_eng.generate_predictions()
    
    # Confirmation
    confirm = IndependentConfirmation(data_path=data_path, db_path=db_path)
    conf_report = confirm.run_confirmation()
    assert len(conf_report) > 0
    
    # Synthetic theory recovery
    synth = SyntheticTheoryRecovery(output_path="test_synth_recovery_report.json")
    synth_report = synth.run_recovery()
    assert synth_report["recovery_f1"] >= 0.0
    if os.path.exists("test_synth_recovery_report.json"):
        os.remove("test_synth_recovery_report.json")

def test_historical_recovery_and_tournament(setup_test_db):
    db_path, laws_path, data_path = setup_test_db
    
    generator = TheoryGenerator(laws_path=laws_path, db_path=db_path)
    generator.generate_theories()
    engine = MechanismEngine(data_path=data_path, db_path=db_path)
    engine.explain_mechanisms()
    
    # Historical
    hist = HistoricalRecovery(db_path=db_path, output_path="test_hist_report.json")
    hist_report = hist.run_historical_recovery()
    assert hist_report["historical_recovery_rate"] >= 0.0
    if os.path.exists("test_hist_report.json"):
        os.remove("test_hist_report.json")
        
    # Tournament
    tour = TheoryTournament(db_path=db_path, leaderboard_path="docs/THEORY_LEADERBOARD.md")
    tour_report = tour.run_tournament()
    assert len(tour_report) == 4

def test_evolution_blind_and_adversarial(setup_test_db):
    db_path, laws_path, data_path = setup_test_db
    
    generator = TheoryGenerator(laws_path=laws_path, db_path=db_path)
    generator.generate_theories()
    engine = MechanismEngine(data_path=data_path, db_path=db_path)
    engine.explain_mechanisms()
    grounding = MechanisticGrounding(data_path=data_path, db_path=db_path)
    g_res = grounding.run_grounding_audit()
    pred_eng = PredictionEngine(data_path=data_path, db_path=db_path)
    preds = pred_eng.generate_predictions()
    confirm = IndependentConfirmation(data_path=data_path, db_path=db_path)
    c_res = confirm.run_confirmation()
    
    # Evolution
    ev = TheoryEvolution(db_path=db_path)
    ev_res = ev.evolve_theories(g_res, c_res)
    assert len(ev_res) == 4
    
    # Blind validation
    blind = BlindTheoryValidation(db_path=db_path)
    obs_data = engine.load_or_generate_dataset()
    blind_res = blind.run_blind_validation(preds, obs_data)
    assert blind_res["validation_success_rate"] >= 0.0
    
    # Adversarial suite
    adv = AdversarialTheoryTests(data_path=data_path, db_path=db_path)
    adv_res = adv.run_adversarial_tests()
    assert len(adv_res) == 4
