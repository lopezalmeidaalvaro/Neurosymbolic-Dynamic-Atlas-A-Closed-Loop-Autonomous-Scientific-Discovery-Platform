import sys
import json
from unittest.mock import MagicMock
from pathlib import Path
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mathematics.ir_core.proof_ir import ProofGoalIR
from mathematics.verifier import VerificationResult, VerificationStatus, LeanProofState
from mathematics.prover.tree import ProofTree, ProofStateNode, NodeStatistics
from mathematics.prover.rewards import calculate_puct, map_status_to_reward
from mathematics.prover.mcts import MonteCarloTreeSearch


def test_puct_calculation():
    """Verify calculate_puct handles various visit counts correctly."""
    # Child not visited yet: should return prior-based exploration term
    score_unvisited = calculate_puct(
        parent_visits=10,
        child_visits=0,
        child_total_value=0.0,
        prior_prob=0.8,
        c_puct=1.0,
    )
    # parent_visits=10 -> sqrt(10) ~ 3.16. score = 0.0 + 1.0 * 0.8 * 3.16 / 1 = 2.5298...
    assert score_unvisited > 2.5

    # Visited child: U = Q + exploration
    score_visited = calculate_puct(
        parent_visits=10,
        child_visits=1,
        child_total_value=1.0,
        prior_prob=0.8,
        c_puct=1.0,
    )
    # Q = 1.0 / 1 = 1.0. u = 1.0 * 0.8 * sqrt(10) / (1 + 1) = 0.8 * 3.162 / 2 = 1.2649. total = 2.2649
    assert abs(score_visited - 2.2649) < 0.01


def test_map_status_to_reward():
    """Verify reward mappings for MCTS compiler outcomes."""
    assert map_status_to_reward(VerificationStatus.VERIFIED) == 1.0
    assert map_status_to_reward(VerificationStatus.UNSOLVED_GOALS) == 0.1
    assert map_status_to_reward(VerificationStatus.COMPILATION_ERROR) == -1.0
    assert map_status_to_reward(VerificationStatus.TIMEOUT) == -1.0


def test_proof_tree_node_addition():
    """Verify ProofTree manages parent-child relationships and stats initialization."""
    tree = ProofTree()

    root = ProofStateNode(
        state_id="root",
        parent_id=None,
        tactic_applied=None,
        accumulated_script=(),
        lean_feedback="goal",
    )
    tree.add_node(root, prior=1.0)

    child = ProofStateNode(
        state_id="child1",
        parent_id="root",
        tactic_applied="intro h",
        accumulated_script=("intro h",),
        lean_feedback=None,
    )
    tree.add_node(child, prior=0.7)

    assert "root" in tree.nodes
    assert "child1" in tree.nodes
    assert tree.stats["child1"].prior_probability == 0.7
    assert tree.children["root"] == ["child1"]


def test_mcts_search_success():
    """Test successful MCTS proof discovery."""
    mock_client = MagicMock()
    # Mock LLM expansion tactic response
    mock_client.generate.return_value = json.dumps(
        {
            "tactics": ["exact H_squared", "rfl"],
            "tactic_scores": [0.8, 0.2],
        }
    )

    mock_evaluator = MagicMock()
    # Root evaluation (initial with sorry) -> unresolved
    # Child evaluation (exact H_squared) -> verified
    mock_evaluator.evaluate.side_effect = [
        # Root check
        VerificationResult(
            status=VerificationStatus.UNSOLVED_GOALS,
            output="⊢ H ⬝ H = I",
            execution_time_ms=5,
            proof_state=LeanProofState(
                goals=["⊢ H ⬝ H = I"], context="", raw_output=""
            ),
        ),
        # Child check (verified)
        VerificationResult(
            status=VerificationStatus.VERIFIED,
            output="No goals",
            execution_time_ms=10,
        ),
    ]

    mcts = MonteCarloTreeSearch(client=mock_client, evaluator=mock_evaluator)

    goal = ProofGoalIR(
        goal_id="h_h_ident",
        domain="quantum",
        theorem_statement="H ⬝ H = I",
        assumptions=[],
        source_reference="test",
    )

    res, proof_script, telemetry = mcts.search(goal, max_simulations=5)

    assert res.status == VerificationStatus.VERIFIED
    assert proof_script == "exact H_squared"
    assert telemetry["success"] is True
    assert telemetry["total_simulations"] == 1  # Terminates early on first sim success
    assert telemetry["nodes_explored"] == 3  # Root + 2 children expanded
