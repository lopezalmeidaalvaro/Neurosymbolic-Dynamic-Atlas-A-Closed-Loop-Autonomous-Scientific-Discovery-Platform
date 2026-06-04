import math
import pytest
from quantum.knowledge.context_schema import Context
from quantum.memory.quantum_memory import QuantumMemory
from quantum.memory.context_compatibility import ContextCompatibilityEngine
from quantum.memory.scaffold_builder import ContextAwareScaffoldBuilder
from quantum.analysis.scaffold_evaluator import ScaffoldEvaluator

def test_compatibility_scoring():
    engine = ContextCompatibilityEngine()
    
    ctx_bell = Context(task_name="bell_state", qubit_count=2, converged=True)
    ctx_bell_failed = Context(task_name="bell_state", qubit_count=2, converged=False)
    ctx_ghz = Context(task_name="ghz_state", qubit_count=3, converged=True)
    ctx_unrelated = Context(task_name="unrelated_state", qubit_count=3, converged=True)

    # 1. Exact match
    score = engine.calculate_compatibility(ctx_bell, ctx_bell)
    assert score == pytest.approx(1.0)
    
    # 2. Convergence effect (0.5 multiplier for non-converged source)
    score_failed = engine.calculate_compatibility(ctx_bell_failed, ctx_bell)
    assert score_failed == pytest.approx(0.5)

    # 3. Related task family and expandable qubit count (2 -> 3 qubits)
    # task similarity = 0.9, qubit compat = 0.9, conv = 1.0 -> 0.81
    score_transfer = engine.calculate_compatibility(ctx_bell, ctx_ghz)
    assert score_transfer == pytest.approx(0.81)
    
    # Check boolean are_compatible
    assert engine.are_compatible(ctx_bell, ctx_ghz, threshold=0.75) is True
    assert engine.are_compatible(ctx_bell, ctx_ghz, threshold=0.85) is False

    # 4. Unrelated task
    score_unrelated = engine.calculate_compatibility(ctx_unrelated, ctx_ghz)
    assert score_unrelated == pytest.approx(0.0)

def test_scaffold_creation():
    memory = QuantumMemory()
    c_bell = Context(task_name="bell_state", qubit_count=2, converged=True)
    c_ghz = Context(task_name="ghz_state", qubit_count=3, converged=False)
    
    patterns = [
        {
            "pattern_id": "pat_1",
            "representation": "H(q0)",
            "sequence": ["H(q0)"],
            "context": c_bell.to_dict(),
            "P_convergence": 1.0,
            "survival_probability": 0.8,
            "mean_delta_score": 0.2,
            "frequency": 5,
            "avg_score": 0.8,
            "type": "SINGLE"
        },
        {
            "pattern_id": "pat_2",
            "representation": "CNOT(q0,q1)",
            "sequence": ["CNOT(q0,q1)"],
            "context": c_bell.to_dict(),
            "P_convergence": 0.8,
            "survival_probability": 0.6,
            "mean_delta_score": 0.1,
            "frequency": 8,
            "avg_score": 0.7,
            "type": "SINGLE"
        }
    ]
    memory.store("quantum:distillation:patterns", patterns)
    
    builder = ContextAwareScaffoldBuilder(memory)
    # Build scaffolds for target context c_ghz (compatible because of task family & expandable qubits)
    scaffolds = builder.build_scaffolds(c_ghz, threshold=0.75)
    
    assert len(scaffolds) == 1
    sc = scaffolds[0]
    assert sc["representation"] == "H(q0)->CNOT(q0,q1)"
    assert sc["sequence"] == ["H(q0)", "CNOT(q0,q1)"]
    assert sc["source_patterns"] == ["H(q0)", "CNOT(q0,q1)"]
    assert sc["confidence_score"] == pytest.approx(0.1) # initial confidence (support=1, reuse=0, transfer=0)
    
    # Assert Level 6 knowledge graph node and edges
    graph_dict = memory.retrieve("quantum:distillation:knowledge_graph")
    assert graph_dict is not None
    nodes = graph_dict.get("nodes", {})
    edges = graph_dict.get("edges", {})
    
    sc_node_id = f"scaffold_{sc['pattern_id']}"
    assert sc_node_id in nodes
    assert nodes[sc_node_id]["type"] == "CompositeScaffold"

def test_emergent_utility():
    evaluator = ScaffoldEvaluator()
    
    scaffold = {
        "pattern_id": "scaffold_1",
        "representation": "H(q0)->CNOT(q0,q1)",
        "source_patterns": ["H(q0)", "CNOT(q0,q1)"]
    }
    
    causal_records = [
        {"pattern": "H(q0)->CNOT(q0,q1)", "delta_score": 0.5, "survival_status": True},
        {"pattern": "H(q0)->CNOT(q0,q1)", "delta_score": 0.3, "survival_status": True},
        {"pattern": "H(q0)", "delta_score": 0.1, "survival_status": True},
        {"pattern": "CNOT(q0,q1)", "delta_score": 0.2, "survival_status": True}
    ]
    
    # Scaffold average delta = 0.4
    # Components averages: H(q0) = 0.1, CNOT(q0,q1) = 0.2 -> Mean of components = 0.15
    # Emergent Utility = 0.4 - 0.15 = 0.25
    metrics = evaluator.evaluate_scaffold(scaffold, causal_records)
    assert metrics["emergent_utility"] == pytest.approx(0.25)
    assert metrics["survival_probability"] == pytest.approx(1.0)
    assert metrics["transfer_utility"] == pytest.approx(0.4)

def test_confidence_tracking():
    builder = ContextAwareScaffoldBuilder(None)
    
    # 1. Base case: low support, no success
    conf_1 = builder.compute_confidence(support_count=1, successful_reuses=0, successful_transfers=0)
    assert conf_1 == pytest.approx(0.1)
    
    # 2. Medium support, partial success
    conf_2 = builder.compute_confidence(support_count=4, successful_reuses=2, successful_transfers=2)
    # support_factor = 4/5 = 0.8
    # rates = 0.5, 0.5
    # conf = 0.1 + 0.9 * 0.8 * (0.5*0.5 + 0.5*0.5) = 0.1 + 0.72 * 0.5 = 0.46
    assert conf_2 == pytest.approx(0.46)
    
    # 3. High support, high success (saturation)
    conf_3 = builder.compute_confidence(support_count=10, successful_reuses=10, successful_transfers=10)
    # support_factor = 1.0
    # rates = 1.0, 1.0
    # conf = 0.1 + 0.9 * 1.0 * 1.0 = 1.0
    assert conf_3 == pytest.approx(1.0)


def test_counterfactual_scaffold_evaluation():
    from quantum.analysis.scaffold_counterfactual_evaluator import CounterfactualScaffoldEvaluator
    
    class MockMemory:
        def __init__(self):
            self.scaffolds = [{
                "pattern_id": "scaffold_1",
                "representation": "H(q0)->CNOT(q0,q1)",
                "source_patterns": ["H(q0)", "CNOT(q0,q1)"],
                "context": {"task_name": "bell_state", "qubit_count": 2, "converged": True}
            }]
            self.store_calls = {}

        def query_scaffolds(self):
            return self.scaffolds

        def retrieve(self, key):
            if key == "quantum:distillation:causal_records":
                return [
                    {"pattern": "H(q0)->CNOT(q0,q1)", "delta_score": 0.5, "survival_status": True},
                    {"pattern": "H(q0)->CNOT(q0,q1)", "delta_score": 0.6, "survival_status": True},
                    {"pattern": "H(q0)", "delta_score": 0.1, "survival_status": True},
                    {"pattern": "CNOT(q0,q1)", "delta_score": 0.3, "survival_status": True}
                ]
            return None

        def store(self, key, val):
            self.store_calls[key] = val

    mem = MockMemory()
    evaluator = CounterfactualScaffoldEvaluator(mem)
    results = evaluator.evaluate_all_scaffolds()
    
    assert len(results) == 1
    sc = results[0]
    
    # Scaffold average delta = 0.55
    # H(q0) = 0.1, CNOT(q0,q1) = 0.3
    # Max component utility = 0.3
    # EmergentUtility = 0.55 - 0.3 = 0.25
    assert sc["utility_scaffold"] == pytest.approx(0.55)
    assert sc["max_component_utility"] == pytest.approx(0.3)
    assert sc["emergent_utility"] == pytest.approx(0.25)
    assert sc["emergence_class"] == "EMERGENT"
    assert sc["survival_probability"] == pytest.approx(1.0)


def test_scaffold_novelty_metrics():
    from quantum.analysis.novelty_metrics import NoveltyMetrics
    
    class MockMemory:
        def __init__(self):
            self.scaffolds = [
                {
                    "representation": "H(q0)->CNOT(q0,q1)",
                    "sequence": ["H(q0)", "CNOT(q0,q1)"],
                    "context": {"task_name": "bell_state", "qubit_count": 2}
                },
                {
                    "representation": "H(q0)->CNOT(q0,q1)",
                    "sequence": ["H(q0)", "CNOT(q0,q1)"],
                    "context": {"task_name": "bell_state", "qubit_count": 2}
                },
                {
                    "representation": "X(q0)->Y(q1)",
                    "sequence": ["X(q0)", "Y(q1)"],
                    "context": {"task_name": "ghz_state", "qubit_count": 3}
                }
            ]
            self.store_calls = {}

        def query_scaffolds(self):
            return self.scaffolds

        def store(self, key, val):
            self.store_calls[key] = val

    mem = MockMemory()
    metric = NoveltyMetrics(mem)
    results = metric.compute_novelty_for_all()
    
    assert len(results) == 3
    # Identical scaffolds should have very low novelty (0.0)
    assert results[0]["scaffold_novelty"] == pytest.approx(0.0)
    assert results[1]["scaffold_novelty"] == pytest.approx(0.0)
    
    # Completely different scaffold should have high novelty
    assert results[2]["scaffold_novelty"] > 0.5

