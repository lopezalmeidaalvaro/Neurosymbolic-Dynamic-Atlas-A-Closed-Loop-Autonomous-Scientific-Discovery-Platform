import pytest
from quantum.knowledge.pattern_valuation import PatternValuationEngine

class MockMemory:
    def __init__(self, patterns, causal_records, knowledge_graph):
        self.store = {
            "quantum:distillation:patterns": patterns,
            "quantum:distillation:causal_records": causal_records,
            "quantum:distillation:knowledge_graph": knowledge_graph
        }

    def query_patterns(self):
        return self.store["quantum:distillation:patterns"]

    def retrieve(self, key):
        return self.store.get(key)

    def get_knowledge_graph(self):
        return self.store["quantum:distillation:knowledge_graph"]

def test_pattern_valuation_engine_logic():
    # 1. Mock patterns
    patterns = [
        {
            "pattern_id": "pat_1",
            "sequence": ["H(q0)", "CNOT(q0,q1)"],
            "frequency": 8,
            "avg_score": 0.5,
            "type": "entanglement_motif",
            "representation": "H(q0)->CNOT(q0,q1)"
        },
        {
            "pattern_id": "pat_2",
            "sequence": ["X(q0)", "X(q0)"],
            "frequency": 3,
            "avg_score": 0.2,
            "type": "repeated_subsequence",
            "representation": "X(q0)->X(q0)"
        },
        {
            "pattern_id": "pat_3",
            "sequence": ["H", "CNOT"],
            "frequency": 12,
            "avg_score": 0.9,
            "type": "repeated_subsequence",
            "representation": "H->CNOT"
        }
    ]

    # 2. Mock causal records
    causal_records = [
        {"pattern": "H(q0)->CNOT(q0,q1)", "delta_score": -0.15, "survival_status": False},
        {"pattern": "H(q0)->CNOT(q0,q1)", "delta_score": -0.25, "survival_status": False},
        {"pattern": "H->CNOT", "delta_score": 0.1, "survival_status": True},
        {"pattern": "H->CNOT", "delta_score": 0.2, "survival_status": True}
    ]

    # 3. Mock knowledge graph
    knowledge_graph = {
        "nodes": {
            # Pattern Nodes
            "pattern_pat_1": {"type": "Pattern", "attributes": {"sequence": ["H(q0)", "CNOT(q0,q1)"], "type": "entanglement_motif"}},
            "pattern_pat_2": {"type": "Pattern", "attributes": {"sequence": ["X(q0)", "X(q0)"], "type": "repeated_subsequence"}},
            "pattern_pat_3": {"type": "Pattern", "attributes": {"sequence": ["H", "CNOT"], "type": "repeated_subsequence"}},
            
            # Circuit Nodes
            "circ_1": {"type": "Circuit", "attributes": {"raw": True, "score": 0.45, "fidelity": 0.5}},
            "circ_2": {"type": "Circuit", "attributes": {"raw": True, "score": 0.95, "fidelity": 0.99}},
            "circ_3": {"type": "Circuit", "attributes": {"raw": True, "score": 0.98, "fidelity": 1.0}},
            "circ_4": {"type": "Circuit", "attributes": {"raw": False}} # Canonical, should be skipped
        },
        "edges": [
            # contains_pattern edges
            {"source": "circ_1", "target": "pattern_pat_1", "type": "contains_pattern"},
            {"source": "circ_2", "target": "pattern_pat_1", "type": "contains_pattern"},
            {"source": "circ_3", "target": "pattern_pat_3", "type": "contains_pattern"},
            {"source": "circ_4", "target": "pattern_pat_3", "type": "contains_pattern"}
        ]
    }

    memory = MockMemory(patterns, causal_records, knowledge_graph)
    engine = PatternValuationEngine(memory)
    evaluated = engine.evaluate_patterns()

    assert len(evaluated) == 3

    # Assert metrics for pat_1 ("H(q0)->CNOT(q0,q1)")
    p1 = evaluated["H(q0)->CNOT(q0,q1)"]
    assert p1["frequency"] == 8
    # raw circuits 1 and 2 contain pat_1. Scores: 0.45, 0.95. Mean = 0.70.
    assert pytest.approx(p1["mean_score"]) == 0.70
    # Fidelities: 0.5, 0.99. Mean = 0.745.
    assert pytest.approx(p1["mean_fidelity"]) == 0.745
    # Causal records: 2 records, both survival_status=False. Survival prob = 0.0.
    assert p1["survival_probability"] == 0.0
    # Convergence probability: 1 out of 2 raw circuits has fidelity >= 0.99 (circ_2). P_conv = 0.5.
    assert pytest.approx(p1["P_convergence"]) == 0.5
    # Causal delta scores: -0.15, -0.25. Mean = -0.20.
    assert pytest.approx(p1["mean_delta_score"]) == -0.20
    # Since mean_delta_score < 0 and survival_prob == 0, it's TOXIC.
    assert p1["category"] == "TOXIC"

    # Assert category for pat_2 ("X(q0)->X(q0)")
    p2 = evaluated["X(q0)->X(q0)"]
    # Contains redundant adjacent gates on same qubit, should be classified as NOISE/JUNK
    assert p2["category"] == "NOISE/JUNK"

    # Assert metrics for pat_3 ("H->CNOT")
    p3 = evaluated["H->CNOT"]
    assert p3["frequency"] == 12
    # Only circ_3 is a raw circuit containing pat_3. Score = 0.98, Fidelity = 1.0.
    assert pytest.approx(p3["mean_score"]) == 0.98
    assert pytest.approx(p3["mean_fidelity"]) == 1.0
    # Causal records: 2 records, both survival_status=True. Survival prob = 1.0.
    assert p3["survival_probability"] == 1.0
    # Convergence probability: 1 out of 1 raw circuit has fidelity >= 0.99. P_conv = 1.0.
    assert pytest.approx(p3["P_convergence"]) == 1.0
    # Causal delta scores: 0.1, 0.2. Mean = 0.15.
    assert pytest.approx(p3["mean_delta_score"]) == 0.15
    # Since mean_delta_score > 0, it's HIGH_VALUE.
    assert p3["category"] == "HIGH_VALUE"
