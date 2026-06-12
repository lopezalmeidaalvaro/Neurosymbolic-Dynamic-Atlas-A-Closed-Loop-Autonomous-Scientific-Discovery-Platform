import sys
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mathematics.ir_core.proof_ir import ProofGoalIR
from mathematics.verifier.models import VerificationStatus, VerificationResult
from mathematics.verifier.parser import LeanOutputParser
from mathematics.verifier.document_builder import LeanDocumentBuilder
from mathematics.verifier.runtime import LocalLeanRuntime
from mathematics.verifier.evaluator import ProofEvaluator


def test_parser_verified():
    """Verify that exit code 0 and clean output yields VERIFIED."""
    status, err = LeanOutputParser.parse("Theorem proved!", "", 0)
    assert status == VerificationStatus.VERIFIED
    assert err is None


def test_parser_unsolved_goals():
    """Verify that 'unsolved goals' in stdout/stderr yields UNSOLVED_GOALS."""
    status, err = LeanOutputParser.parse("state: unsolved goals\n  1. x = y", "", 0)
    assert status == VerificationStatus.UNSOLVED_GOALS
    assert "unsolved goals" in err.lower()

    status2, err2 = LeanOutputParser.parse("", "declaration uses sorry", 0)
    assert status2 == VerificationStatus.UNSOLVED_GOALS
    assert "sorry" in err2.lower()


def test_parser_compilation_error():
    """Verify that non-zero exit code yields COMPILATION_ERROR."""
    status, err = LeanOutputParser.parse("", "error: unexpected token", 1)
    assert status == VerificationStatus.COMPILATION_ERROR
    assert "unexpected token" in err


def test_document_builder_fluid():
    """Verify LeanDocumentBuilder fluid chain and formatting."""
    goal = ProofGoalIR(
        goal_id="add_comm",
        domain="mathematics",
        theorem_statement="a + b = b + a",
        assumptions=["(a b : Nat)"],
        source_reference="ref_001",
    )

    builder = LeanDocumentBuilder()
    doc = (
        builder.add_import("Mathlib.Data.Nat.Basic")
        .set_namespace("TestSpace")
        .add_comment("A comment line")
        .set_goal(goal)
        .build_document("rfl")
    )

    assert "import Mathlib.Data.Nat.Basic" in doc
    assert "namespace TestSpace" in doc
    assert "-- A comment line" in doc
    assert "theorem add_comm (a b : Nat) : a + b = b + a := by" in doc
    assert "  rfl" in doc
    assert "end TestSpace" in doc


def test_document_builder_raises_on_missing_goal():
    """Verify that build_document raises ValueError if goal is not set."""
    builder = LeanDocumentBuilder()
    with pytest.raises(ValueError, match="ProofGoalIR must be set"):
        builder.build_document("rfl")


@patch("subprocess.run")
def test_local_runtime_success(mock_run):
    """Test LocalLeanRuntime success case using subprocess mock."""
    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "Proof verified successfully."
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    runtime = LocalLeanRuntime(lean_executable="lean_mock", timeout_seconds=5.0)
    result = runtime.execute_script("mock code")

    assert result.status == VerificationStatus.VERIFIED
    assert result.output == "Proof verified successfully."
    assert result.error_details is None
    assert result.execution_time_ms >= 0


@patch("subprocess.run")
def test_local_runtime_timeout(mock_run):
    """Test LocalLeanRuntime timeout exception handling."""
    mock_run.side_effect = subprocess.TimeoutExpired(
        cmd=["lean_mock"], timeout=5.0, output="partial out", stderr="partial err"
    )

    runtime = LocalLeanRuntime(lean_executable="lean_mock", timeout_seconds=5.0)
    result = runtime.execute_script("mock code")

    assert result.status == VerificationStatus.TIMEOUT
    assert "timed out" in result.error_details
    assert result.output == "partial out"


@patch("subprocess.run")
def test_local_runtime_missing_executable(mock_run):
    """Test LocalLeanRuntime file not found exception handling."""
    mock_run.side_effect = FileNotFoundError("executable not found")

    runtime = LocalLeanRuntime(lean_executable="invalid_lean_path", timeout_seconds=5.0)
    result = runtime.execute_script("mock code")

    assert result.status == VerificationStatus.INTERNAL_ERROR
    assert "not found" in result.error_details


@patch("subprocess.run")
def test_local_runtime_unexpected_exception(mock_run):
    """Test LocalLeanRuntime general exception handling."""
    mock_run.side_effect = RuntimeError("unexpected crash")

    runtime = LocalLeanRuntime(lean_executable="lean_mock", timeout_seconds=5.0)
    result = runtime.execute_script("mock code")

    assert result.status == VerificationStatus.INTERNAL_ERROR
    assert "unexpected crash" in result.error_details


@patch("subprocess.run")
def test_proof_evaluator_coordination(mock_run):
    """Test ProofEvaluator coordinates builder and runtime."""
    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "Verified"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    goal = ProofGoalIR(
        goal_id="test_theorem",
        domain="quantum",
        theorem_statement="statement",
        assumptions=[],
        source_reference="src_ref",
    )

    runtime = LocalLeanRuntime(lean_executable="lean_mock")
    evaluator = ProofEvaluator(runtime)

    result = evaluator.evaluate(goal, "proof_step")

    assert result.status == VerificationStatus.VERIFIED
    # Verify mock was called with temporary file
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0][0] == "lean_mock"
    assert args[0][1].endswith(".lean")
