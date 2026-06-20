import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.bootstrap import bootstrap_application
from quantum.adapters.formal_verifier import FormalVerificationAdapter
from quantum.pipeline.phase_v_certification import QADEMotifCertifier
from mathematics.engine import MathEngine
from mathematics.ir_core.quantum_ir import QuantumEquivalenceIR


def test_bootstrap_application():
    """Verify that bootstrap_application wires all systems correctly and returns expected structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test_knowledge.db"
        app = bootstrap_application(
            db_path=str(db_file),
            llm_api_url="http://localhost:8000/v1",
            llm_api_key="test-key",
            llm_model="test-model",
            lean_executable="lean",
        )
        assert isinstance(app, dict)
        assert "math_engine" in app
        assert "quantum_container" in app
        assert "verifier_adapter" in app
        assert "motif_certifier" in app

        assert isinstance(app["math_engine"], MathEngine)
        assert isinstance(app["verifier_adapter"], FormalVerificationAdapter)
        assert isinstance(app["motif_certifier"], QADEMotifCertifier)

        # Verify DI references are correct
        assert app["verifier_adapter"].math_engine is app["math_engine"]
        assert app["motif_certifier"].adapter is app["verifier_adapter"]


def test_adapter_unsupported_gates():
    """Verify that motifs with unsupported gates are filtered immediately."""
    math_engine = MagicMock()
    adapter = FormalVerificationAdapter(math_engine)

    # LHS contains 'RX' which is not in the adapter's SUPPORTED_GATES
    lhs = [{"type": "H", "qubits": [0]}, {"type": "RX", "qubits": [0]}]
    rhs = [{"type": "I", "qubits": [0]}]

    res = adapter.certify_motif("unsupported_motif", lhs, rhs)

    assert res["success"] is False
    assert res["status"] == "UNSUPPORTED_GATES"
    assert "Contiene puertas no soportadas" in res["error"]
    math_engine.verify_discovery.assert_not_called()


def test_adapter_validation_error():
    """Verify validation error mapping for invalid model formats."""
    math_engine = MagicMock()
    adapter = FormalVerificationAdapter(math_engine)

    # Invalid qubits format (string instead of list[int])
    lhs = [{"type": "H", "qubits": "zero"}]
    rhs = [{"type": "I", "qubits": [0]}]

    res = adapter.certify_motif("validation_error_motif", lhs, rhs)

    assert res["success"] is False
    assert res["status"] == "VALIDATION_ERROR"
    assert "Validation failed" in res["error"]
    math_engine.verify_discovery.assert_not_called()


def test_adapter_success_and_caching():
    """Verify successful certification, caching, and audit metadata appending."""
    math_engine = MagicMock()
    # Mock verify_discovery return dict
    mock_verify_res = {
        "success": True,
        "status": "VERIFIED",
        "provenance": "DETERMINISTIC_RULE",
        "proof_script": "exact H_squared",
        "execution_time_ms": 12,
        "error": None,
    }
    math_engine.verify_discovery.return_value = mock_verify_res

    adapter = FormalVerificationAdapter(math_engine)

    lhs = [{"type": "H", "qubits": [0]}, {"type": "H", "qubits": [0]}]
    rhs = [{"type": "I", "qubits": [0]}]

    # First call - executes MathEngine
    res1 = adapter.certify_motif("hadamard_identity", lhs, rhs)

    assert res1["success"] is True
    assert res1["status"] == "VERIFIED"
    assert res1["provenance"] == "DETERMINISTIC_RULE"
    assert "certified_at" in res1
    assert res1["certificate_version"] == "v1.0"
    math_engine.verify_discovery.assert_called_once()

    # Second call - retrieves from cache
    res2 = adapter.certify_motif("hadamard_identity", lhs, rhs)
    assert res2 is res1
    math_engine.verify_discovery.assert_called_once()  # No extra call


def test_certifier_process_discovered_motifs():
    """Verify filtering and certification embedding in QADEMotifCertifier."""
    adapter = MagicMock(spec=FormalVerificationAdapter)
    mock_certificate = {
        "success": True,
        "status": "VERIFIED",
        "certified_at": "2026-06-12T16:00:00Z",
        "certificate_version": "v1.0",
    }
    adapter.certify_motif.return_value = mock_certificate

    certifier = QADEMotifCertifier(adapter)

    motifs = [
        {
            "motif_id": "motif_high_confidence",
            "confidence": 0.98,
            "lhs": [{"type": "H", "qubits": [0]}, {"type": "H", "qubits": [0]}],
            "rhs": [{"type": "I", "qubits": [0]}],
        },
        {
            "motif_id": "motif_low_confidence",
            "confidence": 0.85,
            "lhs": [{"type": "CNOT", "qubits": [0, 1]}],
            "rhs": [{"type": "CNOT", "qubits": [0, 1]}],
        },
    ]

    certified = certifier.process_discovered_motifs(motifs, confidence_threshold=0.90)

    # Only motif_high_confidence (0.98 >= 0.90) should be certified
    assert len(certified) == 1
    assert certified[0]["motif_id"] == "motif_high_confidence"
    assert "formal_certificate" in certified[0]
    assert certified[0]["formal_certificate"] == mock_certificate

    # Adapter certify_motif should only be called for the high-confidence motif
    adapter.certify_motif.assert_called_once_with(
        "motif_high_confidence",
        [{"type": "H", "qubits": [0]}, {"type": "H", "qubits": [0]}],
        [{"type": "I", "qubits": [0]}],
    )
