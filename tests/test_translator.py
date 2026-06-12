import sys
from datetime import datetime, timezone
from pathlib import Path
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mathematics.ir_core.quantum_ir import QuantumEquivalenceIR, GateNode, GateType
from mathematics.ir_core.proof_ir import ProofGoalIR
from mathematics.translator.exceptions import NoMatchingRuleError
from mathematics.translator.rules import DoubleHadamardRule
from mathematics.translator.registry import RuleRegistry
from mathematics.translator.mapper import QuantumEquivalenceTranslator


def test_double_hadamard_rule_matches():
    """Verify DoubleHadamardRule pattern matching."""
    rule = DoubleHadamardRule()

    # Valid case: 2 H gates on qubit 0, empty RHS
    valid_ir = QuantumEquivalenceIR(
        motif_id="valid_h_h",
        source_system="test",
        created_at=datetime.now(timezone.utc),
        lhs=[
            GateNode(gate_type=GateType.H, qubits=[0]),
            GateNode(gate_type=GateType.H, qubits=[0]),
        ],
        rhs=[],
        assumptions=[],
    )
    assert rule.matches(valid_ir) is True

    # Invalid case 1: Different qubits
    diff_qubits_ir = QuantumEquivalenceIR(
        motif_id="diff_qubits",
        source_system="test",
        created_at=datetime.now(timezone.utc),
        lhs=[
            GateNode(gate_type=GateType.H, qubits=[0]),
            GateNode(gate_type=GateType.H, qubits=[1]),
        ],
        rhs=[],
        assumptions=[],
    )
    assert rule.matches(diff_qubits_ir) is False

    # Invalid case 2: Different gate type
    wrong_type_ir = QuantumEquivalenceIR(
        motif_id="wrong_type",
        source_system="test",
        created_at=datetime.now(timezone.utc),
        lhs=[
            GateNode(gate_type=GateType.H, qubits=[0]),
            GateNode(gate_type=GateType.X, qubits=[0]),
        ],
        rhs=[],
        assumptions=[],
    )
    assert rule.matches(wrong_type_ir) is False

    # Invalid case 3: Non-empty RHS
    non_empty_rhs_ir = QuantumEquivalenceIR(
        motif_id="non_empty_rhs",
        source_system="test",
        created_at=datetime.now(timezone.utc),
        lhs=[
            GateNode(gate_type=GateType.H, qubits=[0]),
            GateNode(gate_type=GateType.H, qubits=[0]),
        ],
        rhs=[GateNode(gate_type=GateType.I if hasattr(GateType, "I") else GateType.X, qubits=[0])],  # type: ignore
        assumptions=[],
    )
    assert rule.matches(non_empty_rhs_ir) is False

    # Invalid case 4: Wrong number of gates in LHS
    wrong_count_ir = QuantumEquivalenceIR(
        motif_id="wrong_count",
        source_system="test",
        created_at=datetime.now(timezone.utc),
        lhs=[GateNode(gate_type=GateType.H, qubits=[0])],
        rhs=[],
        assumptions=[],
    )
    assert rule.matches(wrong_count_ir) is False


def test_double_hadamard_rule_build_goal():
    """Verify DoubleHadamardRule output structure."""
    rule = DoubleHadamardRule()
    ir = QuantumEquivalenceIR(
        motif_id="my_motif_123",
        source_system="test",
        created_at=datetime.now(timezone.utc),
        lhs=[
            GateNode(gate_type=GateType.H, qubits=[0]),
            GateNode(gate_type=GateType.H, qubits=[0]),
        ],
        rhs=[],
        assumptions=[],
    )

    goal, script = rule.build_goal(ir)

    assert isinstance(goal, ProofGoalIR)
    assert goal.goal_id == "proof_my_motif_123"
    assert goal.domain == "quantum"
    assert goal.theorem_statement == "H ⬝ H = I"
    assert goal.source_reference == "my_motif_123"

    # Crucial constraint: Proof script must not start with 'by'
    assert script == "exact H_squared"
    assert not script.strip().startswith("by")


def test_rule_registry():
    """Verify RuleRegistry registration and matching lookup."""
    registry = RuleRegistry()
    rule = DoubleHadamardRule()

    registry.register(rule)

    valid_ir = QuantumEquivalenceIR(
        motif_id="valid_h_h",
        source_system="test",
        created_at=datetime.now(timezone.utc),
        lhs=[
            GateNode(gate_type=GateType.H, qubits=[0]),
            GateNode(gate_type=GateType.H, qubits=[0]),
        ],
        rhs=[],
        assumptions=[],
    )

    matched = registry.find_rule(valid_ir)
    assert matched is rule

    invalid_ir = QuantumEquivalenceIR(
        motif_id="invalid",
        source_system="test",
        created_at=datetime.now(timezone.utc),
        lhs=[GateNode(gate_type=GateType.X, qubits=[0])],
        rhs=[],
        assumptions=[],
    )
    assert registry.find_rule(invalid_ir) is None


def test_translator_mapper_success():
    """Verify QuantumEquivalenceTranslator successfully translates on matching rule."""
    registry = RuleRegistry()
    registry.register(DoubleHadamardRule())
    translator = QuantumEquivalenceTranslator(registry)

    equivalence = QuantumEquivalenceIR(
        motif_id="test_motif",
        source_system="test",
        created_at=datetime.now(timezone.utc),
        lhs=[
            GateNode(gate_type=GateType.H, qubits=[0]),
            GateNode(gate_type=GateType.H, qubits=[0]),
        ],
        rhs=[],
        assumptions=[],
    )

    goal, script = translator.translate(equivalence)
    assert goal.source_reference == "test_motif"
    assert script == "exact H_squared"


def test_translator_mapper_no_matching_rule():
    """Verify QuantumEquivalenceTranslator raises NoMatchingRuleError on mismatch."""
    registry = RuleRegistry()
    # Registry is empty
    translator = QuantumEquivalenceTranslator(registry)

    equivalence = QuantumEquivalenceIR(
        motif_id="mystery_motif",
        source_system="test",
        created_at=datetime.now(timezone.utc),
        lhs=[
            GateNode(gate_type=GateType.X, qubits=[0]),
        ],
        rhs=[],
        assumptions=[],
    )

    with pytest.raises(NoMatchingRuleError) as exc_info:
        translator.translate(equivalence)

    assert exc_info.value.motif_id == "mystery_motif"
    assert "mystery_motif" in str(exc_info.value)
