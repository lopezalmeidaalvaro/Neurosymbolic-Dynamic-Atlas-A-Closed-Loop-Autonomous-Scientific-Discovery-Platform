import pytest
from quantum.analysis.interaction_classifier import InteractionClassifier
from quantum.analysis.novelty_metrics import NoveltyMetrics
from quantum.analysis.scaffold_counterfactual_evaluator import CounterfactualScaffoldEvaluator
from quantum.analysis.pairwise_synergy_audit import PairwiseSynergyAuditor
from quantum.analysis.synergy_predictor import SynergyPredictor

def test_interaction_classifier():
    classifier = InteractionClassifier()
    
    # 1. State Preparation Extension (H followed by CNOT)
    seq_state = ["H(q0)", "CNOT(q0,q1)"]
    assert classifier.classify_sequence(seq_state) == "STATE_PREPARATION_EXTENSION"

    # 2. Parameter Preparation (rotation followed by CNOT)
    seq_param_prep = ["RX(q0)", "CNOT(q0,q1)"]
    assert classifier.classify_sequence(seq_param_prep) == "PARAMETER_PREPARATION"

    # 3. Parameter Refinement (successive rotations on same qubit)
    seq_refine = ["RX(q0)", "RY(q0)"]
    assert classifier.classify_sequence(seq_refine) == "PARAMETER_REFINEMENT"

    # 4. Symmetry Extension (symmetric sequence)
    seq_sym = ["H(q0)", "CNOT(q0,q1)", "H(q0)"]
    assert classifier.classify_sequence(seq_sym) == "SYMMETRY_EXTENSION"

    # 5. Entangling Chain (multiple CNOTs on disjoint qubits)
    seq_chain = ["CNOT(q0,q1)", "CNOT(q2,q3)"]
    assert classifier.classify_sequence(seq_chain) == "ENTANGLING_CHAIN"

    # 6. Control Reuse (CNOTs sharing qubits)
    seq_reuse = ["CNOT(q0,q1)", "CNOT(q1,q2)"]
    assert classifier.classify_sequence(seq_reuse) == "CONTROL_REUSE"


def test_improved_novelty_metrics():
    class MockMemory:
        def __init__(self):
            self.scaffolds = [
                {
                    "representation": "H(q0)->CNOT(q0,q1)",
                    "sequence": ["H(q0)", "CNOT(q0,q1)"],
                    "context": {"task_name": "bell_state", "qubit_count": 2},
                    "survival_probability": 0.8,
                    "confidence_score": 0.5
                },
                {
                    "representation": "H(q0)->CNOT(q0,q1)",
                    "sequence": ["H(q0)", "CNOT(q0,q1)"],
                    "context": {"task_name": "bell_state", "qubit_count": 2},
                    "survival_probability": 0.8,
                    "confidence_score": 0.5
                },
                {
                    "representation": "X(q0)->Y(q1)",
                    "sequence": ["X(q0)", "Y(q1)"],
                    "context": {"task_name": "ghz_state", "qubit_count": 3},
                    "survival_probability": 0.2,
                    "confidence_score": 0.1
                }
            ]

        def query_scaffolds(self):
            return self.scaffolds

        def store(self, key, val):
            pass

    mem = MockMemory()
    metric = NoveltyMetrics(mem)
    results = metric.compute_novelty_for_all()
    
    assert len(results) == 3
    # Same sequence, context, topo, and causal history -> 100% similarity -> 0.0 novelty (TRIVIAL)
    assert results[0]["scaffold_novelty"] == pytest.approx(0.0)
    assert results[0]["novelty_class"] == "TRIVIAL"
    
    # Completely different scaffold -> high novelty
    assert results[2]["scaffold_novelty"] > 0.5
    assert results[2]["novelty_class"] in ("NOVEL", "HIGHLY_NOVEL")


def test_pairwise_synergy_and_predictor():
    class MockMemory:
        def __init__(self):
            self.patterns = [
                {
                    "pattern_id": "pat_1",
                    "representation": "H(q0)",
                    "sequence": ["H(q0)"],
                    "context": {"task_name": "bell_state", "qubit_count": 2, "converged": True},
                    "frequency": 10,
                    "mean_delta_score": 0.2,
                    "confidence_score": 0.8
                },
                {
                    "pattern_id": "pat_2",
                    "representation": "CNOT(q0,q1)",
                    "sequence": ["CNOT(q0,q1)"],
                    "context": {"task_name": "bell_state", "qubit_count": 2, "converged": True},
                    "frequency": 12,
                    "mean_delta_score": 0.3,
                    "confidence_score": 0.9
                }
            ]
            self.scaffolds = [
                {
                    "pattern_id": "scaffold_1",
                    "representation": "H(q0)->CNOT(q0,q1)",
                    "sequence": ["H(q0)", "CNOT(q0,q1)"],
                    "context": {"task_name": "ghz_state", "qubit_count": 3},
                    "survival_probability": 0.5,
                    "confidence_score": 0.5
                }
            ]
            self.current_context = type('obj', (object,), {"task_name": "ghz_state", "qubit_count": 3, "converged": False, "to_dict": lambda s: {}})()

        def retrieve(self, key):
            if key == "quantum:distillation:patterns":
                return self.patterns
            return None

        def query_scaffolds(self):
            return self.scaffolds

        def store(self, key, val):
            pass

    causal_records = [
        {"pattern": "H(q0)", "delta_score": 0.2, "survival_status": True},
        {"pattern": "CNOT(q0,q1)", "delta_score": 0.3, "survival_status": True},
        {"pattern": "H(q0)->CNOT(q0,q1)", "delta_score": 0.6, "survival_status": True}  # Utility = 0.6
    ]

    mem = MockMemory()
    auditor = PairwiseSynergyAuditor(mem)
    records = auditor.audit_pairwise_interactions(causal_records)
    
    assert len(records) == 1
    rec = records[0]
    # Component max utility = 0.3, pair utility = 0.6 -> Synergy score = 0.3
    assert rec["synergy_score"] == pytest.approx(0.3)
    assert rec["interaction_type"] == "STATE_PREPARATION_EXTENSION"

    # Test predictor
    predictor = SynergyPredictor()
    pred_res = predictor.analyze_synergy(records, mem)
    assert pred_res["status"] == "SUCCESS"
    assert len(pred_res["ranking"]) > 0
