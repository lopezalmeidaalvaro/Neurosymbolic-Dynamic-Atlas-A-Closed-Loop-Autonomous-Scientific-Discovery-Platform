import sys
import tempfile
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mathematics.knowledge_base.library_manager import FormalKnowledgeBase
from mathematics.rlcf.dataset_builder import DPODatasetGenerator
from mathematics.ir_core.quantum_ir import QuantumEquivalenceIR, GateNode, GateType
from mathematics.verifier.models import VerificationResult, VerificationStatus
from mathematics.llm_translator.models import Provenance, FormalizationAttempt
from mathematics.llm_translator.repair_loop import AutoFormalizationLoop
from mathematics.prover.mcts import MonteCarloTreeSearch
from mathematics.orchestrator.handlers import (
    DeterministicHandler,
    LLMHandler,
    MCTSHandler,
)
from mathematics.orchestrator.pipeline import DomainOrchestrator


@pytest.fixture
def temp_kb():
    """Fixture providing a temporary FormalKnowledgeBase database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test_knowledge.db"
        kb = FormalKnowledgeBase(db_path=db_file)
        yield kb


def test_log_and_get_trajectories(temp_kb):
    """Verify that we can log proof trajectories to SQLite and query them back."""
    kb = temp_kb

    kb.log_trajectory(
        run_id="run_123",
        state_context="Initial state",
        tactic_applied="exact H_squared",
        status="VERIFIED",
        reward=1.0,
        metadata={"difficulty": 1},
    )
    kb.log_trajectory(
        run_id="run_123",
        state_context="state: unsolved goals 1. x = y",
        tactic_applied="rfl",
        status="UNSOLVED_GOALS",
        reward=0.1,
    )

    trajectories = kb.get_all_trajectories()
    assert len(trajectories) == 2

    assert trajectories[0]["run_id"] == "run_123"
    assert trajectories[0]["state_context"] == "Initial state"
    assert trajectories[0]["tactic_applied"] == "exact H_squared"
    assert trajectories[0]["status"] == "VERIFIED"
    assert trajectories[0]["reward"] == 1.0
    assert json.loads(trajectories[0]["metadata"]) == {"difficulty": 1}

    assert trajectories[1]["run_id"] == "run_123"
    assert trajectories[1]["state_context"] == "state: unsolved goals 1. x = y"
    assert trajectories[1]["tactic_applied"] == "rfl"
    assert trajectories[1]["status"] == "UNSOLVED_GOALS"
    assert trajectories[1]["reward"] == 0.1
    assert trajectories[1]["metadata"] is None


def test_auto_formalization_loop_trajectory_collection():
    """Verify that AutoFormalizationLoop collects step trajectories with correct contexts and rewards."""
    mock_client = MagicMock()
    mock_evaluator = MagicMock()

    # Define mock LLM responses
    mock_client.generate.side_effect = [
        '{"proof_script": "exact H_squared"}',
        '{"proof_script": "rfl"}',
    ]

    # First attempt fails with unsolved goals, second attempt succeeds
    mock_evaluator.evaluate.side_effect = [
        VerificationResult(
            status=VerificationStatus.UNSOLVED_GOALS,
            output="goals remaining",
            error_details="unsolved goals",
            execution_time_ms=5,
        ),
        VerificationResult(
            status=VerificationStatus.VERIFIED,
            output="Proved!",
            error_details=None,
            execution_time_ms=10,
        ),
    ]

    loop = AutoFormalizationLoop(mock_client, mock_evaluator)
    ir = QuantumEquivalenceIR(
        motif_id="test_hadamard",
        source_system="empirical",
        created_at=datetime.now(timezone.utc),
        lhs=[GateNode(gate_type=GateType.H, qubits=[0])],
        rhs=[],
    )

    res, script, attempts = loop.run(ir, max_attempts=2)

    # 2 trajectories should be logged
    assert len(loop.trajectories) == 2

    # Trajectory 1: Initial state -> exact H_squared -> UNSOLVED_GOALS (+0.1)
    assert loop.trajectories[0]["state_context"] == "Initial state"
    assert loop.trajectories[0]["tactic_applied"] == "exact H_squared"
    assert loop.trajectories[0]["status"] == "UNSOLVED_GOALS"
    assert loop.trajectories[0]["reward"] == 0.1

    # Trajectory 2: compiler feedback 1 -> rfl -> VERIFIED (+1.0)
    assert loop.trajectories[1]["state_context"] == "unsolved goals"
    assert loop.trajectories[1]["tactic_applied"] == "rfl"
    assert loop.trajectories[1]["status"] == "VERIFIED"
    assert loop.trajectories[1]["reward"] == 1.0


def test_mcts_trajectory_collection():
    """Verify that MonteCarloTreeSearch collects trajectories mapping tactic steps from parent states."""
    mock_client = MagicMock()
    mock_evaluator = MagicMock()

    # Mock evaluator
    # First call initializes root goal "sorry"
    # Second call evaluates "rfl"
    mock_evaluator.evaluate.side_effect = [
        VerificationResult(
            status=VerificationStatus.UNSOLVED_GOALS,
            output="unresolved state",
            error_details="1 goal remaining",
            execution_time_ms=2,
        ),
        VerificationResult(
            status=VerificationStatus.VERIFIED,
            output="Proved!",
            error_details=None,
            execution_time_ms=4,
        ),
    ]

    # Mock client returns tactics
    mock_client.generate.return_value = '{"tactics": ["rfl"], "tactic_scores": [0.95]}'

    mcts = MonteCarloTreeSearch(mock_client, mock_evaluator)

    # Setup dummy ProofGoalIR
    from mathematics.ir_core.proof_ir import ProofGoalIR

    goal = ProofGoalIR(
        goal_id="mcts_goal",
        domain="quantum",
        theorem_statement="H * H = I",
        assumptions=[],
        source_reference="test",
    )

    res, script, telemetry = mcts.search(goal, max_simulations=2)

    # Verify trajectory log: parent node had "1 goal remaining"
    assert len(mcts.trajectories) >= 1
    assert mcts.trajectories[0]["state_context"] == "1 goal remaining"
    assert mcts.trajectories[0]["tactic_applied"] == "rfl"
    assert mcts.trajectories[0]["status"] == "VERIFIED"
    assert mcts.trajectories[0]["reward"] == 1.0


def test_orchestrator_bulk_trajectory_logging(temp_kb):
    """Verify that DomainOrchestrator extracts and saves all trajectories in bulk with a single UUID run_id."""
    kb = temp_kb

    # Setup mock handlers
    mock_loop = MagicMock(spec=AutoFormalizationLoop)
    mock_loop.trajectories = [
        {
            "state_context": "Initial state",
            "tactic_applied": "exact H_squared",
            "status": "UNSOLVED_GOALS",
            "reward": 0.1,
        },
        {
            "state_context": "goals remaining",
            "tactic_applied": "rfl",
            "status": "VERIFIED",
            "reward": 1.0,
        },
    ]

    mock_mcts = MagicMock(spec=MonteCarloTreeSearch)
    mock_mcts.trajectories = []

    # Wire handlers: Deterministic -> LLM -> MCTS
    # We will simulate LLM handler processing and returning a result
    llm_handler = LLMHandler(mock_loop)
    mcts_handler = MCTSHandler(mock_mcts, kb)
    llm_handler.set_next(mcts_handler)

    # Mock LLMHandler to return success
    mock_loop.run.return_value = (
        VerificationResult(
            status=VerificationStatus.VERIFIED, output="Success", execution_time_ms=10
        ),
        "exact H_squared\nrfl",
        [],
    )

    orchestrator = DomainOrchestrator(llm_handler, kb)

    ir = QuantumEquivalenceIR(
        motif_id="orch_test",
        source_system="empirical",
        created_at=datetime.now(timezone.utc),
        lhs=[],
        rhs=[],
    )

    res = orchestrator.process(ir)
    assert res is not None

    # Retrieve all logged trajectories from the DB
    trajectories = kb.get_all_trajectories()

    # The 2 trajectories from LLMHandler/mock_loop should be logged under the same run_id
    assert len(trajectories) == 2
    assert trajectories[0]["run_id"] == trajectories[1]["run_id"]
    assert trajectories[0]["tactic_applied"] == "exact H_squared"
    assert trajectories[1]["tactic_applied"] == "rfl"


def test_dpo_dataset_generator(temp_kb):
    """Verify that DPODatasetGenerator builds DPO pairs via relative preference reward comparisons."""
    kb = temp_kb

    # Log proof step trajectories under the same state_context
    state_context = "unsolved goals: 1. H * H = I"

    # Tactic A (reward = 1.0) -> Tactic B (reward = 0.1) -> Tactic C (reward = -1.0)
    kb.log_trajectory(
        run_id="run_1",
        state_context=state_context,
        tactic_applied="exact H_squared",
        status="VERIFIED",
        reward=1.0,
    )
    kb.log_trajectory(
        run_id="run_1",
        state_context=state_context,
        tactic_applied="rfl",
        status="UNSOLVED_GOALS",
        reward=0.1,
    )
    kb.log_trajectory(
        run_id="run_1",
        state_context=state_context,
        tactic_applied="sorry",
        status="TIMEOUT",
        reward=-1.0,
    )

    # Also log a duplicate tactic with same reward (should not be paired with itself)
    kb.log_trajectory(
        run_id="run_1",
        state_context=state_context,
        tactic_applied="rfl",
        status="UNSOLVED_GOALS",
        reward=0.1,
    )

    generator = DPODatasetGenerator(kb)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "dpo_dataset.jsonl"
        count = generator.generate_dpo_jsonl(output_file)

        # Expected pairs (reward comparison):
        # 1. exact H_squared (1.0) > rfl (0.1)
        # 2. exact H_squared (1.0) > sorry (-1.0)
        # 3. rfl (0.1) > sorry (-1.0)
        # Tactic duplicate check avoids matching rfl vs rfl
        assert count == 3

        # Read JSONL file to verify format
        with open(output_file, "r", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f]

        assert len(lines) == 3
        # Check one of the pairs
        assert lines[0]["prompt"] == state_context
        assert lines[0]["chosen"] == "exact H_squared"
        assert lines[0]["rejected"] == "rfl"
