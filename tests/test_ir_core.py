import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mathematics.ir_core.quantum_ir import GateType, GateNode, QuantumEquivalenceIR
from mathematics.ir_core.physics_ir import ExpressionNode, PhysicsLawIR
from mathematics.ir_core.proof_ir import ProofGoalIR
from mathematics.ir_core.validator import (
    load_and_validate_quantum_ir,
    load_and_validate_physics_ir,
    load_and_validate_proof_ir,
)


def test_quantum_ir_valid():
    """Test successful instantiation and properties of QuantumEquivalenceIR."""
    now = datetime.now(timezone.utc)
    lhs_gate = GateNode(gate_type=GateType.H, qubits=[0])
    rhs_gate = GateNode(gate_type=GateType.RX, qubits=[0], parameters=[3.14159])

    ir = QuantumEquivalenceIR(
        motif_id="hadamard_rx_equiv",
        source_system="empirical_searcher",
        created_at=now,
        lhs=[lhs_gate],
        rhs=[rhs_gate],
        assumptions=["qubit_0_initialized"],
    )

    assert ir.schema_id == "quantum_equivalence_ir"
    assert ir.schema_version == "1.0"
    assert ir.motif_id == "hadamard_rx_equiv"
    assert ir.lhs[0].gate_type == GateType.H
    assert ir.rhs[0].parameters == [3.14159]
    assert ir.created_at == now


def test_quantum_ir_immutability():
    """Verify that GateNode and QuantumEquivalenceIR are frozen (immutable)."""
    gate = GateNode(gate_type=GateType.X, qubits=[1])
    ir = QuantumEquivalenceIR(
        motif_id="test_motif",
        source_system="test_sys",
        created_at=datetime.now(timezone.utc),
        lhs=[gate],
        rhs=[gate],
        assumptions=[],
    )

    with pytest.raises((ValidationError, TypeError)):
        # Attempt to modify a field of GateNode
        gate.qubits = [2]  # type: ignore

    with pytest.raises((ValidationError, TypeError)):
        # Attempt to modify a field of QuantumEquivalenceIR
        ir.motif_id = "new_motif"  # type: ignore


def test_quantum_ir_validation_errors():
    """Verify that invalid field values trigger Pydantic ValidationError."""
    # Invalid gate_type
    with pytest.raises(ValidationError):
        GateNode(gate_type="NOT_A_GATE", qubits=[0])  # type: ignore

    # Qubits as string instead of int
    with pytest.raises(ValidationError):
        GateNode(gate_type=GateType.H, qubits=["zero"])  # type: ignore

    # Incorrect schema_id literal
    with pytest.raises(ValidationError):
        QuantumEquivalenceIR(
            schema_id="wrong_schema_id",  # type: ignore
            motif_id="test",
            source_system="test",
            created_at=datetime.now(timezone.utc),
            lhs=[],
            rhs=[],
            assumptions=[],
        )


def test_physics_ir_ast_and_law():
    """Test AST representation with ExpressionNode and overall PhysicsLawIR."""
    now = datetime.now(timezone.utc)

    # Represents: d/dt(x) = -k * x
    ast = ExpressionNode(
        operator="=",
        children=[
            ExpressionNode(operator="d/dt", children=[ExpressionNode(value="x")]),
            ExpressionNode(
                operator="*",
                children=[ExpressionNode(value=-1.5), ExpressionNode(value="x")],
            ),
        ],
    )

    law = PhysicsLawIR(
        system_id="damped_oscillator",
        source_system="physics_solver",
        created_at=now,
        differential_equation_ast=ast,
        state_variables=["x"],
        invariants=["energy_conservation"],
    )

    assert law.schema_id == "physics_law_ir"
    assert law.differential_equation_ast.operator == "="
    assert law.differential_equation_ast.children[1].children[0].value == -1.5
    assert "x" in law.state_variables


def test_physics_ir_immutability():
    """Verify that ExpressionNode and PhysicsLawIR are frozen."""
    node = ExpressionNode(value="x")
    law = PhysicsLawIR(
        system_id="sys",
        source_system="sys",
        created_at=datetime.now(timezone.utc),
        differential_equation_ast=node,
        state_variables=["x"],
        invariants=[],
    )

    with pytest.raises((ValidationError, TypeError)):
        node.value = "y"  # type: ignore

    with pytest.raises((ValidationError, TypeError)):
        law.system_id = "new_sys"  # type: ignore


def test_proof_ir_valid():
    """Test successful instantiation of ProofGoalIR."""
    ir = ProofGoalIR(
        goal_id="goal_001",
        domain="quantum",
        theorem_statement="H * H = I",
        assumptions=["unitary_H"],
        source_reference="quantum_equivalence_ir:hadamard_rx_equiv",
    )

    assert ir.schema_id == "proof_goal_ir"
    assert ir.domain == "quantum"
    assert ir.theorem_statement == "H * H = I"


def test_proof_ir_invalid_domain():
    """Verify domain constraints in ProofGoalIR."""
    with pytest.raises(ValidationError):
        ProofGoalIR(
            goal_id="goal_002",
            domain="invalid_domain",  # type: ignore
            theorem_statement="1 + 1 = 2",
            assumptions=[],
            source_reference="ref",
        )


def test_validator_functions():
    """Test validator load_and_validate_* functions using temporary files."""
    now = datetime.now(timezone.utc)
    quantum_data = {
        "motif_id": "test_motif",
        "source_system": "test_system",
        "created_at": now.isoformat(),
        "lhs": [{"gate_type": "H", "qubits": [0]}],
        "rhs": [{"gate_type": "RX", "qubits": [0], "parameters": [1.23]}],
        "assumptions": [],
    }

    physics_data = {
        "system_id": "test_sys",
        "source_system": "test_source",
        "created_at": now.isoformat(),
        "differential_equation_ast": {
            "operator": "+",
            "children": [{"value": "a"}, {"value": 2.0}],
        },
        "state_variables": ["a"],
        "invariants": [],
    }

    proof_data = {
        "goal_id": "test_goal",
        "domain": "physics",
        "theorem_statement": "a + 2 = b",
        "assumptions": ["a = b - 2"],
        "source_reference": "physics_law_ir:test_sys",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Quantum IR file test
        q_file = tmp_path / "quantum.json"
        with open(q_file, "w", encoding="utf-8") as f:
            json.dump(quantum_data, f)
        q_model = load_and_validate_quantum_ir(q_file)
        assert q_model.motif_id == "test_motif"
        assert q_model.lhs[0].gate_type == GateType.H
        assert q_model.rhs[0].parameters == [1.23]

        # Physics IR file test
        p_file = tmp_path / "physics.json"
        with open(p_file, "w", encoding="utf-8") as f:
            json.dump(physics_data, f)
        p_model = load_and_validate_physics_ir(p_file)
        assert p_model.system_id == "test_sys"
        assert p_model.differential_equation_ast.operator == "+"
        assert p_model.differential_equation_ast.children[1].value == 2.0

        # Proof IR file test
        pr_file = tmp_path / "proof.json"
        with open(pr_file, "w", encoding="utf-8") as f:
            json.dump(proof_data, f)
        pr_model = load_and_validate_proof_ir(pr_file)
        assert pr_model.goal_id == "test_goal"
        assert pr_model.domain == "physics"

        # Invalid file validation test
        invalid_data = {"motif_id": 12345}  # Missing required fields, invalid type
        bad_file = tmp_path / "bad.json"
        with open(bad_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        with pytest.raises(ValidationError):
            load_and_validate_quantum_ir(bad_file)
