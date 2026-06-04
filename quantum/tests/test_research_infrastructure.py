import os
import json
import pytest
import numpy as np
import torch
import tensorflow as tf

from quantum.simulation.cuquantum_backend import CuQuantumBackend
from quantum.simulation.simulation_manager import SimulationManager
from quantum.optimization.pyzx_optimizer import PyZXOptimizer
from quantum.noise.mitiq_backend import NoiseMitigationEngine
from quantum.qml.pennylane_models import HybridTransferPredictor, HybridSynergyPredictor, QuantumPINN
from quantum.qml.tfq_models import TFQTransferPredictor, TFQSynergyPredictor
from quantum.qml.torchquantum_models import TorchQuantumTransferPredictor, TorchQuantumSynergyPredictor
from quantum.graph.knowledge_graph_analyzer import KnowledgeGraphAnalyzer
from quantum.explainability.shap_analyzer import SHAPAnalyzer
from quantum.research.research_registry import ResearchRegistry

def test_cuquantum_backend():
    backend = CuQuantumBackend(use_gpu=False)
    circuit = {
        "qubits": 2,
        "gates": [{"type": "H", "qubits": [0]}, {"type": "CNOT", "qubits": [0, 1]}]
    }
    
    # Test statevector
    res_sv = backend.simulate_statevector(circuit)
    assert res_sv["success"] is True
    assert "emulated_statevector" in res_sv["result"]["simulation_type"]
    
    # Test tensor network
    res_tn = backend.simulate_tensor_network(circuit)
    assert res_tn["success"] is True
    assert "emulated_tensor_network" in res_tn["result"]["simulation_type"]
    
    # Test estimations
    assert backend.estimate_memory(5) > 0.0
    assert backend.estimate_memory(30) > 0.0
    assert backend.estimate_contraction_cost(circuit) > 0.0
    
    # Test high qubit memory protection
    circuit_high = {"qubits": 40, "gates": []}
    res_high = backend.simulate_tensor_network(circuit_high)
    assert res_high["success"] is True
    assert res_high["result"]["qubits"] == 40


def test_simulation_manager():
    manager = SimulationManager(use_gpu=False)
    assert manager.select_backend(5) == "STATEVECTOR_SIM"
    assert manager.select_backend(30) == "TENSOR_NETWORK_SIM"
    
    circuit = {
        "qubits": 3,
        "gates": [{"type": "H", "qubits": [0]}]
    }
    res = manager.run_simulation(circuit)
    assert res["success"] is True
    assert res["result"]["backend_selected"] == "STATEVECTOR_SIM"


def test_pyzx_optimizer():
    optimizer = PyZXOptimizer()
    
    # Test sequence optimization
    seq = ["H", "H", "CNOT", "X", "X"]
    opt_seq, metrics = optimizer.optimize_sequence(seq)
    assert opt_seq == ["CNOT"]
    assert metrics["gate_reduction"] == 4
    assert metrics["compression_ratio"] == 0.2
    
    # Test specific composed pattern simplification
    seq_synergy = ["H", "CNOT", "H", "CNOT"]
    opt_syn, _ = optimizer.optimize_sequence(seq_synergy)
    assert opt_syn == ["H", "CNOT"]
    
    # Test circuit dictionary optimization
    circuit = {
        "qubits": 2,
        "gates": [
            {"type": "H", "qubits": [0]},
            {"type": "H", "qubits": [0]},
            {"type": "CNOT", "qubits": [0, 1]},
            {"type": "CNOT", "qubits": [0, 1]}
        ]
    }
    opt_circuit, c_metrics = optimizer.optimize_circuit(circuit)
    assert len(opt_circuit["gates"]) == 0
    assert c_metrics["gate_reduction"] == 4
    
    rules = optimizer.extract_rewrite_rules()
    assert len(rules) > 0
    
    comp_metrics = optimizer.measure_compression(10, 5)
    assert comp_metrics["compression_ratio"] == 0.5


def test_noise_mitigation():
    engine = NoiseMitigationEngine(mitigation_method="ZNE")
    
    # Apply noise
    noisy_f = engine.apply_noise(1.0, 0.1, 10)
    assert noisy_f < 1.0
    
    # Mitigate noise
    assert engine.mitigate_noise(noisy_f, 0.1, 10, "ZNE") > noisy_f
    assert engine.mitigate_noise(noisy_f, 0.1, 10, "PEC") > noisy_f
    assert engine.mitigate_noise(noisy_f, 0.1, 10, "CDR") > noisy_f
    
    # Execute mitigated circuit
    circuit = {
        "qubits": 2,
        "gates": [{"type": "H", "qubits": [0]}, {"type": "CNOT", "qubits": [0, 1]}]
    }
    res = engine.execute_mitigated(circuit, 0.05)
    assert res["success"] is True
    assert res["mitigated_fidelity"] >= res["unmitigated_fidelity"]


def test_pennylane_models():
    np.random.seed(42)
    X = np.random.rand(10, 9)
    y_class = np.random.randint(0, 2, 10)
    y_reg = np.random.rand(10)
    
    # HybridTransferPredictor
    clf = HybridTransferPredictor(input_dim=9)
    clf.fit(X, y_class, epochs=2)
    probs = clf.predict_proba(X)
    preds = clf.predict(X)
    assert probs.shape == (10, 2)
    assert preds.shape == (10,)
    
    # HybridSynergyPredictor
    reg = HybridSynergyPredictor(input_dim=9)
    reg.fit(X, y_reg, epochs=2)
    preds_reg = reg.predict(X)
    assert preds_reg.shape == (10,)
    
    # QuantumPINN
    pinn = QuantumPINN(input_dim=9)
    # y_state represents a valid quantum statevector of 2 qubits (4 amplitudes)
    y_state = np.zeros((10, 4))
    y_state[:, 0] = 1.0
    pinn.fit(X, y_state, epochs=2)
    states = pinn.predict(X)
    assert states.shape == (10, 4)
    # Verify probability normalization constraint
    norms = np.linalg.norm(states, axis=1)
    for norm in norms:
        assert norm == pytest.approx(1.0, abs=1e-5)


def test_tfq_models():
    np.random.seed(42)
    X = np.random.rand(10, 9)
    y_class = np.random.randint(0, 2, 10)
    y_reg = np.random.rand(10)
    
    # TFQTransferPredictor
    clf = TFQTransferPredictor(input_dim=9)
    clf.fit(X, y_class, epochs=2)
    probs = clf.predict_proba(X)
    preds = clf.predict(X)
    assert probs.shape == (10, 2)
    assert preds.shape == (10,)
    
    # TFQSynergyPredictor
    reg = TFQSynergyPredictor(input_dim=9)
    reg.fit(X, y_reg, epochs=2)
    preds_reg = reg.predict(X)
    assert preds_reg.shape == (10,)


def test_torchquantum_models():
    np.random.seed(42)
    X = np.random.rand(10, 9)
    y_class = np.random.randint(0, 2, 10)
    y_reg = np.random.rand(10)
    
    # TorchQuantumTransferPredictor
    clf = TorchQuantumTransferPredictor(input_dim=9)
    clf.fit(X, y_class, epochs=2)
    probs = clf.predict_proba(X)
    preds = clf.predict(X)
    assert probs.shape == (10, 2)
    assert preds.shape == (10,)
    
    # TorchQuantumSynergyPredictor
    reg = TorchQuantumSynergyPredictor(input_dim=9)
    reg.fit(X, y_reg, epochs=2)
    preds_reg = reg.predict(X)
    assert preds_reg.shape == (10,)


def test_knowledge_graph_analyzer():
    mock_graph = {
        "nodes": {
            "A": {"type": "QuantumPattern", "attributes": {"frequency": 10}},
            "B": {"type": "QuantumPattern", "attributes": {"frequency": 5}},
            "C": {"type": "CompositeScaffold", "attributes": {"confidence": 0.8}}
        },
        "edges": [
            {"source": "C", "target": "A", "type": "composed_from"},
            {"source": "C", "target": "B", "type": "composed_from"}
        ]
    }
    
    analyzer = KnowledgeGraphAnalyzer(mock_graph)
    stats = analyzer.analyze()
    
    assert stats["node_count"] == 3
    assert stats["edge_count"] == 2
    assert "pagerank" in stats
    assert "betweenness_centrality" in stats
    assert "communities" in stats
    assert os.path.exists("knowledge_graph_statistics.json")
    assert os.path.exists("docs/GRAPH_ANALYTICS_REPORT.md")


def test_shap_analyzer():
    from sklearn.ensemble import RandomForestClassifier
    X = np.random.rand(20, 9)
    y = np.random.randint(0, 2, 20)
    model = RandomForestClassifier(n_estimators=5, random_state=42)
    model.fit(X, y)
    
    features = [f"feat_{i}" for i in range(9)]
    analyzer = SHAPAnalyzer(model, features)
    results = analyzer.analyze(X)
    
    assert len(results["shap_importance"]) == 9
    assert "audit" in results
    assert "feature_leakage_detected" in results["audit"]
    assert os.path.exists("shap_importance.json")
    assert os.path.exists("docs/SHAP_AUDIT_REPORT.md")


def test_research_registry():
    filename = "test_registry.json"
    if os.path.exists(filename):
        os.remove(filename)
        
    registry = ResearchRegistry(filename)
    registry.register_run("emergence", {"metric": 0.5})
    
    assert len(registry.get_runs("emergence")) == 1
    assert registry.get_runs("emergence")[0]["metric"] == 0.5
    
    # Load registry back
    new_reg = ResearchRegistry(filename)
    assert len(new_reg.get_runs("emergence")) == 1
    
    if os.path.exists(filename):
        os.remove(filename)


def test_dataset_integrity_auditor(tmp_path):
    from quantum.analysis.dataset_integrity_auditor import DatasetIntegrityAuditor
    # Create mock dataset
    mock_data = [
        {
            "topology_similarity": 1.0, "qubit_count_difference": 0.0, "entanglement_overlap": 1.0,
            "state_preparation_overlap": 1.0, "circuit_depth_difference": 2.0, "gate_distribution_distance": 0.1,
            "context_distance": 0.5, "scaffold_complexity": 4.0, "interaction_frequency": 5.0,
            "transfer_success": 1.0
        },
        {
            "topology_similarity": 1.0, "qubit_count_difference": 0.0, "entanglement_overlap": 1.0,
            "state_preparation_overlap": 1.0, "circuit_depth_difference": 2.0, "gate_distribution_distance": 0.1,
            "context_distance": 0.5, "scaffold_complexity": 4.0, "interaction_frequency": 5.0,
            "transfer_success": 1.0
        },  # Duplicate
        {
            "topology_similarity": 0.5, "qubit_count_difference": 1.0, "entanglement_overlap": 0.5,
            "state_preparation_overlap": 0.5, "circuit_depth_difference": 4.0, "gate_distribution_distance": 0.8,
            "context_distance": 0.8, "scaffold_complexity": 4.0, "interaction_frequency": 6.0,
            "transfer_success": 0.0
        }
    ]
    file_path = tmp_path / "test_integrity.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)
        
    auditor = DatasetIntegrityAuditor(dataset_path=str(file_path))
    report = auditor.run_audit()
    
    assert report["dataset_size"] == 3
    assert report["duplicate_count"] == 1
    assert report["duplicate_ratio"] == pytest.approx(1.0 / 3.0)
    assert "label_leakage" in report


def test_imbalance_calibration_audit(tmp_path, monkeypatch):
    from quantum.benchmarks.imbalance_audit import run_imbalance_calibration_audit
    mock_data = []
    # Create balanced classes but with feature correlations
    for i in range(100):
        mock_data.append({
            "topology_similarity": 0.8 if i % 2 == 0 else 0.2,
            "qubit_count_difference": 0.0 if i % 2 == 0 else 1.0,
            "entanglement_overlap": 1.0 if i % 2 == 0 else 0.5,
            "state_preparation_overlap": 1.0 if i % 2 == 0 else 0.5,
            "circuit_depth_difference": 2.0,
            "gate_distribution_distance": 0.1 if i % 2 == 0 else 0.8,
            "context_distance": 0.5,
            "scaffold_complexity": 4.0,
            "interaction_frequency": 5.0,
            "transfer_success": 1.0 if i % 2 == 0 else 0.0
        })
    
    file_path = tmp_path / "test_imbalance.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)
        
    # Patch dataset load in the script
    monkeypatch.setattr("quantum.benchmarks.imbalance_audit.os.path.exists", lambda path: True)
    
    original_open = open
    def mock_open(*args, **kwargs):
        path_str = str(args[0])
        if "transferability_dataset.json" in path_str:
            return original_open(file_path, "r", encoding="utf-8")
        return original_open(*args, **kwargs)
    monkeypatch.setattr("builtins.open", mock_open)
    
    results = run_imbalance_calibration_audit()
    assert "imbalance_metrics" in results
    assert "calibration_metrics" in results
    assert "ROC_AUC" in results["imbalance_metrics"]
    assert "Expected_Calibration_Error" in results["calibration_metrics"]


def test_explainability_audit(tmp_path, monkeypatch):
    from quantum.benchmarks.explainability_audit import run_explainability_audit
    mock_data = []
    for i in range(100):
        mock_data.append({
            "topology_similarity": 0.8 if i % 2 == 0 else 0.2,
            "qubit_count_difference": 0.0 if i % 2 == 0 else 1.0,
            "entanglement_overlap": 1.0 if i % 2 == 0 else 0.5,
            "state_preparation_overlap": 1.0 if i % 2 == 0 else 0.5,
            "circuit_depth_difference": 2.0,
            "gate_distribution_distance": 0.1 if i % 2 == 0 else 0.8,
            "context_distance": 0.5,
            "scaffold_complexity": 4.0,
            "interaction_frequency": 5.0,
            "transfer_success": 1.0 if i % 2 == 0 else 0.0
        })
    
    file_path = tmp_path / "test_explainability.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)
        
    monkeypatch.setattr("quantum.benchmarks.explainability_audit.os.path.exists", lambda path: True)
    
    original_open = open
    def mock_open(*args, **kwargs):
        path_str = str(args[0])
        if "transferability_dataset.json" in path_str:
            return original_open(file_path, "r", encoding="utf-8")
        if "consistency_audit_report.json" in path_str or "docs" in path_str or "shap_importance.json" in path_str:
            return original_open(os.devnull, "w")
        return original_open(*args, **kwargs)
    monkeypatch.setattr("builtins.open", mock_open)
    
    report = run_explainability_audit()
    assert "shap_importance" in report
    assert "permutation_importance" in report
    assert "ablation_importance" in report
    assert "consistency" in report


def test_reproducibility_suite(tmp_path, monkeypatch):
    from quantum.benchmarks.reproducibility_suite import run_reproducibility_suite
    mock_data = []
    for i in range(100):
        mock_data.append({
            "topology_similarity": 0.8 if i % 2 == 0 else 0.2,
            "qubit_count_difference": 0.0 if i % 2 == 0 else 1.0,
            "entanglement_overlap": 1.0 if i % 2 == 0 else 0.5,
            "state_preparation_overlap": 1.0 if i % 2 == 0 else 0.5,
            "circuit_depth_difference": 2.0,
            "gate_distribution_distance": 0.1 if i % 2 == 0 else 0.8,
            "context_distance": 0.5,
            "scaffold_complexity": 4.0,
            "interaction_frequency": 5.0,
            "transfer_success": 1.0 if i % 2 == 0 else 0.0
        })
    
    file_path = tmp_path / "test_reproducibility.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)
        
    monkeypatch.setattr("quantum.benchmarks.reproducibility_suite.os.path.exists", lambda path: True)
    
    original_open = open
    def mock_open(*args, **kwargs):
        path_str = str(args[0])
        if "transferability_dataset.json" in path_str:
            return original_open(file_path, "r", encoding="utf-8")
        if "reproducibility_report.json" in path_str or "docs" in path_str:
            return original_open(os.devnull, "w")
        return original_open(*args, **kwargs)
    monkeypatch.setattr("builtins.open", mock_open)
    
    results = run_reproducibility_suite()
    assert results["runs"] == 50
    assert "metrics" in results
    assert "feature_importances" in results


def test_graph_scale_audit():
    from quantum.benchmarks.benchmark_research_infrastructure import build_large_knowledge_graph
    from quantum.graph.knowledge_graph_analyzer import KnowledgeGraphAnalyzer
    
    mock_graph = build_large_knowledge_graph()
    num_nodes = len(mock_graph["nodes"])
    assert num_nodes >= 1000
    
    analyzer = KnowledgeGraphAnalyzer(mock_graph)
    stats = analyzer.analyze()
    assert stats["node_count"] == num_nodes
    assert "community_count" in stats
    assert "modularity" in stats
