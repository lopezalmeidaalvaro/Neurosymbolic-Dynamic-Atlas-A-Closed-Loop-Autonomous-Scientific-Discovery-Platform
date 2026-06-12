import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mathematics.ir_core.quantum_ir import QuantumEquivalenceIR, GateNode, GateType
from mathematics.ir_core.proof_ir import ProofGoalIR
from mathematics.verifier import ProofEvaluator, VerificationResult, VerificationStatus
from mathematics.translator import (
    RuleRegistry,
    DoubleHadamardRule,
    QuantumEquivalenceTranslator,
)
from mathematics.translator.exceptions import FormalizationFailure
from mathematics.llm_translator.models import Provenance, FormalizationAttempt
from mathematics.llm_translator.repair_loop import AutoFormalizationLoop
from mathematics.prover.mcts import MonteCarloTreeSearch
from mathematics.knowledge_base.library_manager import FormalKnowledgeBase
from mathematics.orchestrator.handlers import (
    DeterministicHandler,
    LLMHandler,
    MCTSHandler,
)
from mathematics.orchestrator.pipeline import DomainOrchestrator


@pytest.fixture
def orchestrator_env():
    """Fixture providing setup orchestrator pipeline with temp database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test_knowledge.db"
        kb = FormalKnowledgeBase(db_path=db_file)

        # Mock dependencies
        evaluator = MagicMock(spec=ProofEvaluator)
        repair_loop = MagicMock(spec=AutoFormalizationLoop)
        mcts = MagicMock(spec=MonteCarloTreeSearch)

        # Set up translator with double Hadamard rule
        registry = RuleRegistry()
        registry.register(DoubleHadamardRule())
        translator = QuantumEquivalenceTranslator(registry)

        # Set up chain: Deterministic -> LLM -> MCTS
        deterministic_handler = DeterministicHandler(translator, evaluator)
        llm_handler = LLMHandler(repair_loop)
        mcts_handler = MCTSHandler(mcts, kb)

        deterministic_handler.set_next(llm_handler)
        llm_handler.set_next(mcts_handler)

        orchestrator = DomainOrchestrator(deterministic_handler, kb)

        yield {
            "orchestrator": orchestrator,
            "kb": kb,
            "evaluator": evaluator,
            "repair_loop": repair_loop,
            "mcts": mcts,
        }


def test_orchestrator_deterministic_path(orchestrator_env):
    """Verify routing through Rule-Based Deterministic Handler."""
    env = orchestrator_env
    orchestrator = env["orchestrator"]
    evaluator = env["evaluator"]
    kb = env["kb"]

    # Mock evaluator return value
    evaluator.evaluate.return_value = VerificationResult(
        status=VerificationStatus.VERIFIED, output="Success", execution_time_ms=10
    )

    # Define matching double Hadamard IR
    ir = QuantumEquivalenceIR(
        motif_id="h_h_ident",
        source_system="empirical",
        created_at=datetime.now(timezone.utc),
        lhs=[
            GateNode(gate_type=GateType.H, qubits=[0]),
            GateNode(gate_type=GateType.H, qubits=[0]),
        ],
        rhs=[],
        assumptions=[],
    )

    # Process through pipeline orchestrator
    res = orchestrator.process(ir)

    assert res is not None
    result, script, provenance = res
    assert result.status == VerificationStatus.VERIFIED
    assert script == "exact H_squared"
    assert provenance == Provenance.DETERMINISTIC_RULE

    # Verify evaluated once and LLM fallback was NOT called
    evaluator.evaluate.assert_called_once()
    env["repair_loop"].run.assert_not_called()

    # Verify SQL library storage
    thm = kb.get_theorem("h_h_ident")
    assert thm is not None
    assert thm["id"] == "h_h_ident"
    assert thm["provenance"] == "DETERMINISTIC_RULE"
    assert thm["verified"] is True


def test_orchestrator_llm_fallback_path(orchestrator_env):
    """Verify fallback to LLM Handler on strategy rule mismatch."""
    env = orchestrator_env
    orchestrator = env["orchestrator"]
    repair_loop = env["repair_loop"]
    kb = env["kb"]

    # Mock repair loop return values
    repair_loop.run.return_value = (
        VerificationResult(
            status=VerificationStatus.VERIFIED, output="Success", execution_time_ms=100
        ),
        "exact X_identity",
        [],
    )

    # Define non-matching double X IR (not supported by DoubleHadamardRule)
    ir = QuantumEquivalenceIR(
        motif_id="x_x_ident",
        source_system="empirical",
        created_at=datetime.now(timezone.utc),
        lhs=[
            GateNode(gate_type=GateType.X, qubits=[0]),
            GateNode(gate_type=GateType.X, qubits=[0]),
        ],
        rhs=[],
        assumptions=[],
    )

    res = orchestrator.process(ir)

    assert res is not None
    result, script, provenance = res
    assert result.status == VerificationStatus.VERIFIED
    assert script == "exact X_identity"
    assert provenance == Provenance.AUTO_FORMALIZED

    # Verify repair loop called
    repair_loop.run.assert_called_once_with(ir)

    # Verify SQL library storage
    thm = kb.get_theorem("x_x_ident")
    assert thm is not None
    assert thm["provenance"] == "AUTO_FORMALIZED"


def test_orchestrator_mcts_fallback_on_unsolved_goals(orchestrator_env):
    """Verify routing falls back to MCTS if LLM loop ends with UNSOLVED_GOALS."""
    env = orchestrator_env
    orchestrator = env["orchestrator"]
    repair_loop = env["repair_loop"]
    mcts = env["mcts"]
    kb = env["kb"]

    # Mock LLM handler to fail with UNSOLVED_GOALS
    failed_attempts = [
        FormalizationAttempt(
            attempt_number=1,
            proof_script="sorry",
            verification_status=VerificationStatus.UNSOLVED_GOALS,
            lean_output="goals remaining",
        )
    ]
    repair_loop.run.side_effect = FormalizationFailure(
        "failed to prove", failed_attempts
    )

    # Mock MCTS to succeed
    mcts.search.return_value = (
        VerificationResult(
            status=VerificationStatus.VERIFIED, output="Success", execution_time_ms=200
        ),
        "exact H_squared",
        {"total_simulations": 10, "success": True, "nodes_explored": 15},
    )

    ir = QuantumEquivalenceIR(
        motif_id="mcts_needed",
        source_system="empirical",
        created_at=datetime.now(timezone.utc),
        lhs=[
            GateNode(gate_type=GateType.X, qubits=[0]),
            GateNode(gate_type=GateType.X, qubits=[0]),
        ],
        rhs=[],
        assumptions=[],
    )

    res = orchestrator.process(ir)

    assert res is not None
    result, script, provenance = res
    assert result.status == VerificationStatus.VERIFIED
    assert script == "exact H_squared"
    assert provenance == Provenance.MCTS_DISCOVERY

    # Verify MCTS was executed
    mcts.search.assert_called_once()

    # Verify MCTS telemetry logging in SQLite
    with closing(kb._connect()) as conn:
        row = conn.execute(
            "SELECT * FROM mcts_runs WHERE theorem_id = ?", ("mcts_needed",)
        ).fetchone()
        assert row is not None
        assert row["total_simulations"] == 10
        assert row["success"] == 1
        assert row["nodes_explored"] == 15


def test_orchestrator_halt_on_compilation_error(orchestrator_env):
    """Verify routing halts immediately if LLM loop ends with COMPILATION_ERROR."""
    env = orchestrator_env
    orchestrator = env["orchestrator"]
    repair_loop = env["repair_loop"]
    mcts = env["mcts"]

    # Mock LLM handler to fail with COMPILATION_ERROR
    failed_attempts = [
        FormalizationAttempt(
            attempt_number=1,
            proof_script="syntax_garbage",
            verification_status=VerificationStatus.COMPILATION_ERROR,
            lean_output="syntax error",
        )
    ]
    repair_loop.run.side_effect = FormalizationFailure(
        "syntax failure", failed_attempts
    )

    ir = QuantumEquivalenceIR(
        motif_id="halt_expected",
        source_system="empirical",
        created_at=datetime.now(timezone.utc),
        lhs=[
            GateNode(gate_type=GateType.X, qubits=[0]),
            GateNode(gate_type=GateType.X, qubits=[0]),
        ],
        rhs=[],
        assumptions=[],
    )

    res = orchestrator.process(ir)

    # Verification must halt (returns None)
    assert res is None

    # MCTS search must NOT be called
    mcts.search.assert_not_called()


from contextlib import closing
