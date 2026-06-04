import math
import pytest
from typing import Dict, Any, List
from quantum.knowledge.representation_analyzer import RepresentationAnalyzer

def test_is_subsequence():
    """Validates the sequence matching helper method."""
    assert RepresentationAnalyzer.is_subsequence(["A", "B"], ["A", "B", "C"])
    assert RepresentationAnalyzer.is_subsequence(["B", "C"], ["A", "B", "C"])
    assert not RepresentationAnalyzer.is_subsequence(["A", "C"], ["A", "B", "C"])
    assert RepresentationAnalyzer.is_subsequence(["A"], ["A"])
    assert not RepresentationAnalyzer.is_subsequence(["A", "B", "C"], ["A", "B"])

def test_get_gate_repr():
    """Validates serialization of gates into canonical strings."""
    analyzer = RepresentationAnalyzer()
    gate_h = {"type": "H", "qubits": [0]}
    gate_cnot = {"type": "CNOT", "qubits": [0, 1]}
    assert analyzer.get_gate_repr(gate_h) == "H(q0)"
    assert analyzer.get_gate_repr(gate_cnot) == "CNOT(q0,q1)"

def test_circuit_contains():
    """Validates the logic for determining if a circuit contains a pattern at different levels."""
    analyzer = RepresentationAnalyzer()
    circuit = {
        "qubits": [0, 1],
        "task": "bell_state",
        "converged": True,
        "gates": [
            {"type": "H", "qubits": [0]},
            {"type": "CNOT", "qubits": [0, 1]}
        ]
    }

    # Level 1 Raw Patterns
    assert analyzer.circuit_contains(circuit, "LEVEL_1_RAW_PATTERN", "H(q0)")
    assert analyzer.circuit_contains(circuit, "LEVEL_1_RAW_PATTERN", "CNOT(q0,q1)")
    assert not analyzer.circuit_contains(circuit, "LEVEL_1_RAW_PATTERN", "X(q0)")

    # Level 2 Motifs (length <= 2)
    assert analyzer.circuit_contains(circuit, "LEVEL_2_MOTIF", "H->CNOT")
    assert analyzer.circuit_contains(circuit, "LEVEL_2_MOTIF", "H")
    assert not analyzer.circuit_contains(circuit, "LEVEL_2_MOTIF", "X->CNOT")

    # Level 4 Scaffold
    assert analyzer.circuit_contains(circuit, "LEVEL_4_SCAFFOLD", "Bell Scaffold")
    assert not analyzer.circuit_contains(circuit, "LEVEL_4_SCAFFOLD", "GHZ Scaffold")

    # Level 5 Context-Aware
    rep_context_converged = "Pattern: H->CNOT | Context: bell_state | 2 qubits | Converged"
    rep_context_failed = "Pattern: H->CNOT | Context: bell_state | 2 qubits | Failed"
    rep_context_diff_task = "Pattern: H->CNOT | Context: ghz_state | 2 qubits | Converged"

    assert analyzer.circuit_contains(circuit, "LEVEL_5_CONTEXT_AWARE", rep_context_converged)
    assert not analyzer.circuit_contains(circuit, "LEVEL_5_CONTEXT_AWARE", rep_context_failed)
    assert not analyzer.circuit_contains(circuit, "LEVEL_5_CONTEXT_AWARE", rep_context_diff_task)

def test_does_record_match():
    """Validates that causal records are correctly mapped to representations."""
    analyzer = RepresentationAnalyzer()
    record = {
        "pattern": "H(q0)->CNOT(q0,q1)",
        "survival_status": True,
        "delta_score": 0.25
    }

    # Level 1
    assert analyzer.does_record_match(record, "LEVEL_1_RAW_PATTERN", "H(q0)")
    assert analyzer.does_record_match(record, "LEVEL_1_RAW_PATTERN", "CNOT(q0,q1)")
    assert not analyzer.does_record_match(record, "LEVEL_1_RAW_PATTERN", "X(q0)")

    # Level 2
    assert analyzer.does_record_match(record, "LEVEL_2_MOTIF", "H->CNOT")
    assert not analyzer.does_record_match(record, "LEVEL_2_MOTIF", "X->CNOT")

    # Level 4 Scaffold
    assert analyzer.does_record_match(record, "LEVEL_4_SCAFFOLD", "Bell Scaffold")

    # Level 5 Context-Aware
    # For records, context task is assumed to be "ghz_state" and qubits "3" (standard transfer target)
    # The record survived, so its status is "Converged"
    rep_record_match = "Pattern: H->CNOT | Context: ghz_state | 3 qubits | Converged"
    rep_record_no_match = "Pattern: H->CNOT | Context: ghz_state | 3 qubits | Failed"

    assert analyzer.does_record_match(record, "LEVEL_5_CONTEXT_AWARE", rep_record_match)
    assert not analyzer.does_record_match(record, "LEVEL_5_CONTEXT_AWARE", rep_record_no_match)

def test_entropy_computation():
    """Validates conditional entropy and information gain math."""
    analyzer = RepresentationAnalyzer()
    
    # Standard binary entropy checks
    assert pytest.approx(analyzer.compute_entropy(0.5)) == 1.0
    assert pytest.approx(analyzer.compute_entropy(0.0)) == 0.0
    assert pytest.approx(analyzer.compute_entropy(1.0)) == 0.0
    
    # 8 evaluations: 4 converged, 4 failed. Baseline entropy = 1.0
    # Let's say representation R is present in 4 of them.
    # Case A: R perfectly predicts convergence (e.g. converged = True when R is present, False when absent)
    # H(Y|X) = 0.5 * H(1.0) + 0.5 * H(0.0) = 0.0. Info gain = 1.0 - 0.0 = 1.0.
    evals = [
        {"circuit": {"gates": [{"type": "H", "qubits": [0]}]}, "converged": True, "task": "t1", "qubits": 1, "fidelity": 1.0},
        {"circuit": {"gates": [{"type": "H", "qubits": [0]}]}, "converged": True, "task": "t1", "qubits": 1, "fidelity": 1.0},
        {"circuit": {"gates": [{"type": "H", "qubits": [0]}]}, "converged": True, "task": "t1", "qubits": 1, "fidelity": 1.0},
        {"circuit": {"gates": [{"type": "H", "qubits": [0]}]}, "converged": True, "task": "t1", "qubits": 1, "fidelity": 1.0},
        {"circuit": {"gates": []}, "converged": False, "task": "t1", "qubits": 1, "fidelity": 0.0},
        {"circuit": {"gates": []}, "converged": False, "task": "t1", "qubits": 1, "fidelity": 0.0},
        {"circuit": {"gates": []}, "converged": False, "task": "t1", "qubits": 1, "fidelity": 0.0},
        {"circuit": {"gates": []}, "converged": False, "task": "t1", "qubits": 1, "fidelity": 0.0},
    ]
    
    ig = analyzer.compute_information_gain("H(q0)", "LEVEL_1_RAW_PATTERN", evals)
    assert pytest.approx(ig) == 1.0

def test_full_analysis():
    """Validates the complete analyze pipeline with mock evaluations and causal records."""
    analyzer = RepresentationAnalyzer()
    
    historical_evals = [
        {
            "circuit": {
                "qubits": [0, 1],
                "gates": [
                    {"type": "H", "qubits": [0]},
                    {"type": "CNOT", "qubits": [0, 1]}
                ]
            },
            "fidelity": 0.99,
            "converged": True,
            "task": "bell_state",
            "qubits": 2
        },
        {
            "circuit": {
                "qubits": [0, 1, 2],
                "gates": [
                    {"type": "H", "qubits": [0]},
                    {"type": "CNOT", "qubits": [0, 1]},
                    {"type": "CNOT", "qubits": [1, 2]}
                ]
            },
            "fidelity": 0.25,
            "converged": False,
            "task": "ghz_state",
            "qubits": 3
        }
    ]
    
    causal_records = [
        {
            "pattern": "H(q0)->CNOT(q0,q1)",
            "survival_status": False,
            "delta_score": -0.25
        }
    ]
    
    results = analyzer.analyze(historical_evals, causal_records)
    
    # Check that we have results for all 5 levels
    for lvl in ["LEVEL_1_RAW_PATTERN", "LEVEL_2_MOTIF", "LEVEL_3_EXTENDED_MOTIF", "LEVEL_4_SCAFFOLD", "LEVEL_5_CONTEXT_AWARE"]:
        assert lvl in results
        assert isinstance(results[lvl], list)
        if results[lvl]:
            first = results[lvl][0]
            assert "representation" in first
            assert "frequency" in first
            assert "mean_fidelity" in first
            assert "P_convergence" in first
            assert "survival_probability" in first
            assert "mean_delta_score" in first
            assert "transfer_success_rate" in first
            assert "information_gain" in first
