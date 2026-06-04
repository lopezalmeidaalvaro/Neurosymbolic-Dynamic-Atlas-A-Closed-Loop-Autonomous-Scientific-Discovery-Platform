import pytest
import os
import json
from quantum.analysis.transferability_features import TransferabilityFeatureEngine
from quantum.analysis.transferability_predictor import TransferabilityPredictor

def test_feature_engine_computations():
    engine = TransferabilityFeatureEngine()
    
    # Test case 1: Same task and same qubits (Bell -> Bell)
    src_context = {"task_name": "bell_state", "qubit_count": 2}
    tgt_context = {"task_name": "bell_state", "qubit_count": 2}
    features = engine.compute_features(
        scaffold_rep="H->CNOT",
        sequence=["H", "CNOT"],
        source_context=src_context,
        target_context=tgt_context
    )
    
    assert features["topology_similarity"] == 1.0
    assert features["qubit_count_difference"] == 0.0
    assert features["entanglement_overlap"] == 1.0
    assert features["state_preparation_overlap"] == 1.0
    assert features["circuit_depth_difference"] == 0.0
    assert features["gate_distribution_distance"] == 0.1
    assert features["context_distance"] == 0.0
    assert features["scaffold_complexity"] == 2.0
    assert features["interaction_frequency"] == 5.0

    # Test case 2: Different tasks (Bell -> GHZ, qubits 2 -> 3)
    src_context = {"task_name": "bell_state", "qubit_count": 2}
    tgt_context = {"task_name": "ghz_state", "qubit_count": 3}
    features = engine.compute_features(
        scaffold_rep="H->CNOT",
        sequence=["H", "CNOT"],
        source_context=src_context,
        target_context=tgt_context
    )
    
    # topology_similarity = 1.0 - (1 / 3) = 2/3 = 0.6667
    assert features["topology_similarity"] == pytest.approx(0.6667, abs=1e-4)
    assert features["qubit_count_difference"] == 1.0
    assert features["entanglement_overlap"] == 1.0
    assert features["state_preparation_overlap"] == 1.0
    # context_distance = 1.0 - 0.6667 + 0.5 = 0.8333
    assert features["context_distance"] == pytest.approx(0.8333, abs=1e-4)

    # Test case 3: Variational target (Bell -> Variational, different gate distribution)
    tgt_context_var = {"task_name": "variational_ansatz", "qubit_count": 2}
    features_var = engine.compute_features(
        scaffold_rep="H->CNOT",
        sequence=["H", "CNOT"],
        source_context=src_context,
        target_context=tgt_context_var
    )
    assert features_var["gate_distribution_distance"] == 0.8


def test_predictor_analysis_low_data():
    predictor = TransferabilityPredictor()
    
    # Low data should trigger dummy results to avoid classifier training error
    records = [
        {"transfer_utility": 0.1, "transfer_success": 1.0, "source_domain": "bell", "target_domain": "ghz"}
    ]
    results = predictor.analyze_transferability(records)
    
    assert results["status"] == "SUCCESS"
    assert results["metrics"]["ROC-AUC"] == 0.5
    assert len(results["rules"]) > 0
    assert len(results["taxonomy"]) == 1
    assert os.path.exists("transferability_rules.json")
    assert os.path.exists("transferability_taxonomy.json")


def test_predictor_analysis_high_data():
    predictor = TransferabilityPredictor()
    
    # Sufficient data with class variance to train sklearn classifiers (at least 6 samples, both classes)
    records = []
    # 5 successful transfers
    for i in range(5):
        records.append({
            "source_domain": "bell_state",
            "target_domain": "ghz_state",
            "interaction_type": "STATE_PREPARATION_EXTENSION",
            "transfer_utility": 0.1,
            "transfer_success": 1.0,
            "topology_similarity": 0.8,
            "qubit_count_difference": 1.0,
            "entanglement_overlap": 1.0,
            "state_preparation_overlap": 1.0,
            "circuit_depth_difference": 2.0,
            "gate_distribution_distance": 0.1,
            "context_distance": 0.2,
            "scaffold_complexity": 4.0,
            "interaction_frequency": 5.0,
            "synergy_retention": 0.5
        })
    # 5 failed transfers
    for i in range(5):
        records.append({
            "source_domain": "bell_state",
            "target_domain": "variational_ansatz",
            "interaction_type": "STATE_PREPARATION_EXTENSION",
            "transfer_utility": -0.1,
            "transfer_success": 0.0,
            "topology_similarity": 0.3,
            "qubit_count_difference": 4.0,
            "entanglement_overlap": 0.5,
            "state_preparation_overlap": 0.5,
            "circuit_depth_difference": 4.0,
            "gate_distribution_distance": 0.8,
            "context_distance": 0.7,
            "scaffold_complexity": 8.0,
            "interaction_frequency": 1.0,
            "synergy_retention": 0.0
        })
        
    results = predictor.analyze_transferability(records)
    
    assert results["status"] == "SUCCESS"
    assert "metrics" in results
    assert "ROC-AUC" in results["metrics"]
    assert "causal_ablation" in results
    assert len(results["causal_ablation"]) == 9
    assert len(results["rules"]) > 0
    assert len(results["taxonomy"]) == 10
    
    # Check that rule files are generated and contain correct structure
    assert os.path.exists("transferability_rules.json")
    assert os.path.exists("transferability_taxonomy.json")
    
    with open("transferability_rules.json", "r", encoding="utf-8") as f:
        rules_data = json.load(f)
        assert len(rules_data) >= 2
        assert "rule" in rules_data[0]
        assert "precision" in rules_data[0]
        
    with open("transferability_taxonomy.json", "r", encoding="utf-8") as f:
        taxonomy_data = json.load(f)
        assert len(taxonomy_data) == 10
        assert "label" in taxonomy_data[0]
        assert taxonomy_data[0]["label"] in {"NON_TRANSFERABLE", "LOCALLY_TRANSFERABLE", "DOMAIN_TRANSFERABLE", "HIGHLY_TRANSFERABLE"}
