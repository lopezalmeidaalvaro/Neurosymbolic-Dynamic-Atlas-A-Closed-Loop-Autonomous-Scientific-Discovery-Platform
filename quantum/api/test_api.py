import os
# Set QADE_API_KEY before importing the FastAPI app so main.py reads it
os.environ["QADE_API_KEY"] = "test-key-local"

from fastapi.testclient import TestClient
from quantum.api.main import app
import pytest

client = TestClient(app)
HEADERS = {"X-API-Key": "test-key-local"}

def test_health():
    """
    Tests GET /health returns 200 without authentication.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
    assert data["backend"] == "ibm_fez"

def test_backends():
    """
    Tests GET /backends returns available backend names with authentication.
    """
    response = client.get("/backends", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "available" in data
    assert "fake_fez" in data["available"]
    assert "fake_sherbrooke" in data["available"]
    assert "ibm_fez" in data["available"]

def test_compile_ghz():
    """
    Tests POST /compile with GHZ_5q circuit on fake_fez with authentication.
    """
    qasm_str = (
        "OPENQASM 2.0;\n"
        "include \"qelib1.inc\";\n"
        "qreg q[5];\n"
        "h q[0];\n"
        "cx q[0], q[1];\n"
        "cx q[1], q[2];\n"
        "cx q[2], q[3];\n"
        "cx q[3], q[4];\n"
    )
    payload = {
        "circuit_qasm": qasm_str,
        "backend_name": "fake_fez",
        "optimization_level": 1,
        "hardware_aware": True
    }
    response = client.post("/compile", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "compiled_qasm" in data
    assert "OPENQASM" in data["compiled_qasm"]
    assert data["gate_count"]["total"] > 0
    assert data["gate_count"]["two_qubit"] >= 4
    assert len(data["qubits_selected"]) == 5
    assert data["depth"] > 0
    assert data["compile_time_ms"] > 0.0

def test_compile_fake_backend():
    """
    Tests compiling a simpler circuit on fake_sherbrooke with authentication.
    """
    qasm_str = (
        "OPENQASM 2.0;\n"
        "include \"qelib1.inc\";\n"
        "qreg q[2];\n"
        "h q[0];\n"
        "cx q[0], q[1];\n"
    )
    payload = {
        "circuit_qasm": qasm_str,
        "backend_name": "fake_sherbrooke",
        "optimization_level": 1,
        "hardware_aware": True
    }
    response = client.post("/compile", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "compiled_qasm" in data
    assert data["gate_count"]["total"] > 0
    assert len(data["qubits_selected"]) == 2

def test_invalid_qasm():
    """
    Tests compiling invalid QASM returns 422 with authentication.
    """
    payload = {
        "circuit_qasm": "this is not valid openqasm",
        "backend_name": "fake_fez",
        "optimization_level": 1,
        "hardware_aware": True
    }
    response = client.post("/compile", json=payload, headers=HEADERS)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert "Invalid OpenQASM 2.0" in data["detail"]

def test_invalid_backend():
    """
    Tests compiling against an invalid backend name returns 422 with authentication.
    """
    payload = {
        "circuit_qasm": "OPENQASM 2.0; qreg q[1];",
        "backend_name": "invalid_backend_name",
        "optimization_level": 1,
        "hardware_aware": True
    }
    response = client.post("/compile", json=payload, headers=HEADERS)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert "invalid_backend_name" in data["detail"]

def test_missing_api_key():
    """
    Tests that requests without the X-API-Key header return 403 Forbidden.
    """
    # GET /backends without headers
    response = client.get("/backends")
    assert response.status_code == 403
    assert "Invalid or missing API key" in response.json()["detail"]

    # POST /compile without headers
    response = client.post("/compile", json={})
    assert response.status_code == 403
    assert "Invalid or missing API key" in response.json()["detail"]

def test_bad_api_key():
    """
    Tests that requests with an incorrect X-API-Key header return 403 Forbidden.
    """
    bad_headers = {"X-API-Key": "wrong-key-value"}
    
    # GET /backends
    response = client.get("/backends", headers=bad_headers)
    assert response.status_code == 403
    assert "Invalid or missing API key" in response.json()["detail"]

    # POST /compile
    response = client.post("/compile", json={}, headers=bad_headers)
    assert response.status_code == 403
    assert "Invalid or missing API key" in response.json()["detail"]
