import os
import math
import pytest
from quantum.evolution.population_manager import QuantumPopulationManager
from quantum.sandbox.qiskit_quantum_sandbox import QiskitQuantumSandbox
from quantum.critics.quantum_critic import QuantumCritic
from quantum.memory.quantum_memory import QuantumMemory
from quantum.evolution.evolution_engine import EvolutionEngine
from core.observability.dashboard import KnowledgeDashboard

def test_evolution_engine_causal_instrumentation():
    # Setup pop manager, sandbox, critic, memory
    population_manager = QuantumPopulationManager(
        qubits=2,
        population_size=5,
        max_gates=8,
        seed=10,
    )
    memory = QuantumMemory()
    
    # Store a pattern to trigger injection
    patterns = [
        {
            "pattern_id": "pat_cnot",
            "sequence": ["H(q0)", "CNOT(q0,q1)"],
            "frequency": 10,
            "avg_score": 0.95,
            "type": "entanglement_motif",
            "representation": "H(q0)->CNOT(q0,q1)"
        }
    ]
    memory.store("quantum:distillation:patterns", patterns)
    
    engine = EvolutionEngine(
        population_manager=population_manager,
        sandbox=QiskitQuantumSandbox(),
        critic=QuantumCritic(alpha=0.01, beta=0.001),
        target_state=[1.0, 0, 0, 0],
        memory=memory,
        elitism=1,
        pattern_injection_rate=1.0, # Attempt injection 100% of the time
    )
    
    # Run 1 generation to trigger mutate with pattern injection and evaluate it
    report = engine.evolve_generation()
    
    # 1. Verify pattern attempts, selections, and injections
    assert engine.pattern_injection_attempts > 0
    assert engine.patterns_selected_from_memory > 0
    
    # 2. Verify that injected pattern records are created and populated
    records = engine.injected_patterns_records
    
    # Run a second generation to ensure pending injections of Gen 0 are processed/logged
    report_2 = engine.evolve_generation()
    
    # Now records must be populated with Gen 0 outcomes
    assert len(engine.injected_patterns_records) > 0
    
    for r in engine.injected_patterns_records:
        assert "pattern_id" in r
        assert "pattern" in r
        assert "pre_mutation_score" in r
        assert "child_hash" in r
        assert "post_mutation_score" in r
        assert "delta_score" in r
        assert "survival_status" in r
        assert r["pre_mutation_score"] is not None
        assert r["post_mutation_score"] is not None
        assert r["delta_score"] == r["post_mutation_score"] - r["pre_mutation_score"]

def test_dashboard_causal_aggregation():
    class MockMemory:
        def __init__(self):
            self.store = {
                "quantum:distillation:patterns": [
                    {"pattern_id": "pat_1", "sequence": ["H", "CNOT"], "frequency": 10, "avg_score": 0.95, "representation": "H->CNOT"}
                ],
                "quantum:distillation:metrics_history": [
                    {
                        "pattern_injection_attempts": 10,
                        "patterns_injected": 8,
                        "patterns_survived": 4,
                        "patterns_improved_score": 3,
                        "patterns_selected_from_memory": 9
                    }
                ],
                "quantum:distillation:causal_records": [
                    {"pattern": "H->CNOT", "delta_score": 0.1},
                    {"pattern": "H->CNOT", "delta_score": 0.2},
                    {"pattern": "H->CNOT", "delta_score": -0.05}
                ]
            }
            
        def query_patterns(self):
            return self.store["quantum:distillation:patterns"]
            
        def retrieve(self, key):
            return self.store.get(key)
            
    memory = MockMemory()
    dashboard = KnowledgeDashboard(memory=memory)
    
    metrics = dashboard.generate_report(
        json_output_path="test_causal_metrics.json",
        report_output_path="test_causal_report.md"
    )
    
    # Cleanup generated test files
    if os.path.exists("test_causal_metrics.json"):
        os.remove("test_causal_metrics.json")
    if os.path.exists("test_causal_report.md"):
        os.remove("test_causal_report.md")
        
    kr = metrics["knowledge_reuse"]
    assert kr["injection_attempts"] == 10
    assert kr["injected_patterns"] == 8
    assert kr["patterns_survived"] == 4
    assert kr["patterns_improved_score"] == 3
    assert kr["selected_from_memory"] == 9
    assert kr["injection_success_rate"] == 0.8
    assert kr["survival_rate"] == 0.5
    assert kr["improvement_rate"] == 0.375
    
    ca = metrics["causal_audit"]
    assert len(ca["motif_ranking"]) == 1
    ranking = ca["motif_ranking"][0]
    assert ranking["pattern"] == "H->CNOT"
    assert ranking["count"] == 3
    assert pytest.approx(ranking["mean_delta_score"]) == 0.0833  # (0.1 + 0.2 - 0.05) / 3
    assert pytest.approx(ranking["median_delta_score"]) == 0.1
