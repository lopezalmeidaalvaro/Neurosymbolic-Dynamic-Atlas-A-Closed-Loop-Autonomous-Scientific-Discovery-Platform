import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mathematics.ir_core.quantum_ir import QuantumEquivalenceIR
from mathematics.verifier.models import VerificationStatus, VerificationResult
from mathematics.llm_translator.models import Provenance
from mathematics.orchestrator.pipeline import DomainOrchestrator
from mathematics.knowledge_base.library_manager import FormalKnowledgeBase
from mathematics import bootstrap_math_engine, MathEngine, VerificationResponse


def test_bootstrap_math_engine():
    """Verify that bootstrap_math_engine builds the entire dependency graph and returns a MathEngine."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test_knowledge.db"
        engine = bootstrap_math_engine(
            db_path=str(db_file),
            llm_api_url="http://localhost:8000/v1",
            llm_api_key="test-key",
            llm_model="test-model",
            lean_executable="lean",
        )
        assert isinstance(engine, MathEngine)
        assert isinstance(engine._orchestrator, DomainOrchestrator)
        assert isinstance(engine._kb, FormalKnowledgeBase)


def test_verify_discovery_success():
    """Verify MathEngine.verify_discovery handles successful proof verification from orchestrator."""
    orchestrator = MagicMock(spec=DomainOrchestrator)
    kb = MagicMock(spec=FormalKnowledgeBase)

    # Mock result from the orchestrator
    mock_result = VerificationResult(
        status=VerificationStatus.VERIFIED,
        output="Proof verified!",
        error_details=None,
        execution_time_ms=45,
    )
    orchestrator.process.return_value = (
        mock_result,
        "exact H_squared",
        Provenance.DETERMINISTIC_RULE,
    )

    engine = MathEngine(orchestrator, kb)
    ir = MagicMock()  # Mock FormalizableIR

    response = engine.verify_discovery(ir)

    assert isinstance(response, dict)
    assert response["success"] is True
    assert response["status"] == "VERIFIED"
    assert response["provenance"] == "DETERMINISTIC_RULE"
    assert response["proof_script"] == "exact H_squared"
    assert response["execution_time_ms"] == 45
    assert response["error"] is None


def test_verify_discovery_unverified():
    """Verify MathEngine.verify_discovery handles the case where the orchestrator returns None."""
    orchestrator = MagicMock(spec=DomainOrchestrator)
    kb = MagicMock(spec=FormalKnowledgeBase)

    orchestrator.process.return_value = None

    engine = MathEngine(orchestrator, kb)
    ir = MagicMock()

    response = engine.verify_discovery(ir)

    assert isinstance(response, dict)
    assert response["success"] is False
    assert response["status"] == "UNVERIFIED"
    assert response["provenance"] is None
    assert response["proof_script"] is None
    assert response["execution_time_ms"] is None
    assert response["error"] is not None


def test_verify_discovery_exception():
    """Verify MathEngine.verify_discovery catches all exceptions and wraps them into an INTERNAL_ERROR response."""
    orchestrator = MagicMock(spec=DomainOrchestrator)
    kb = MagicMock(spec=FormalKnowledgeBase)

    orchestrator.process.side_effect = RuntimeError(
        "Lean executable crashed unpredictably"
    )

    engine = MathEngine(orchestrator, kb)
    ir = MagicMock()

    response = engine.verify_discovery(ir)

    assert isinstance(response, dict)
    assert response["success"] is False
    assert response["status"] == "INTERNAL_ERROR"
    assert response["provenance"] is None
    assert response["proof_script"] is None
    assert response["execution_time_ms"] is None
    assert "Lean executable crashed unpredictably" in response["error"]
