import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
from quantum.sandbox.qiskit_quantum_sandbox import QiskitQuantumSandbox

def test_bell_state_simulation():
    """Valida la simulación de un estado Bell y sus probabilidades (0.5 para |00> y |11>)."""
    sandbox = QiskitQuantumSandbox()
    circuit_spec = {
        "qubits": 2,
        "gates": [
            {"type": "H", "qubits": [0]},
            {"type": "CNOT", "qubits": [0, 1]}
        ]
    }
    
    res = sandbox.execute(circuit_spec)
    assert res["success"] is True
    
    result = res["result"]
    assert result["depth"] == 2
    assert result["gate_count"] == 2
    
    probabilities = result["probabilities"]
    # 2 qubits = 4 probabilidades correspondientes a 00, 01, 10, 11
    assert len(probabilities) == 4
    
    # Tolerancia numérica de 1e-7
    assert pytest.approx(probabilities[0], abs=1e-7) == 0.5  # |00>
    assert pytest.approx(probabilities[1], abs=1e-7) == 0.0  # |01>
    assert pytest.approx(probabilities[2], abs=1e-7) == 0.0  # |10>
    assert pytest.approx(probabilities[3], abs=1e-7) == 0.5  # |11>


def test_ghz_state_simulation():
    """Valida la simulación de un estado GHZ de 3 qubits."""
    sandbox = QiskitQuantumSandbox()
    circuit_spec = {
        "qubits": 3,
        "gates": [
            {"type": "H", "qubits": [0]},
            {"type": "CNOT", "qubits": [0, 1]},
            {"type": "CNOT", "qubits": [1, 2]}
        ]
    }
    
    res = sandbox.execute(circuit_spec)
    assert res["success"] is True
    
    result = res["result"]
    assert result["depth"] == 3
    assert result["gate_count"] == 3
    
    probabilities = result["probabilities"]
    # 3 qubits = 8 probabilidades
    assert len(probabilities) == 8
    
    assert pytest.approx(probabilities[0], abs=1e-7) == 0.5  # |000>
    assert pytest.approx(probabilities[7], abs=1e-7) == 0.5  # |111>
    assert pytest.approx(sum(probabilities), abs=1e-7) == 1.0


def test_invalid_circuits():
    """Valida que el sandbox intercepte correctamente los circuitos inválidos o qubits fuera de rango."""
    sandbox = QiskitQuantumSandbox()
    
    # Qubit fuera de rango
    circuit_spec_invalid_qubit = {
        "qubits": 2,
        "gates": [
            {"type": "H", "qubits": [2]} # fuera de rango
        ]
    }
    res = sandbox.execute(circuit_spec_invalid_qubit)
    assert res["success"] is False
    assert "fuera de rango" in res["error"]

    # Puerta no soportada
    circuit_spec_invalid_gate = {
        "qubits": 2,
        "gates": [
            {"type": "HADAMARD", "qubits": [0]} # No soportada
        ]
    }
    res = sandbox.execute(circuit_spec_invalid_gate)
    assert res["success"] is False
    assert "no soportada" in res["error"]


def test_circuit_depth_scaling():
    """Valida que la métrica de profundidad calcule correctamente el paralelismo de puertas."""
    sandbox = QiskitQuantumSandbox()
    
    # Dos puertas H en qubits separados paralelamente
    circuit_spec = {
        "qubits": 2,
        "gates": [
            {"type": "H", "qubits": [0]},
            {"type": "H", "qubits": [1]}
        ]
    }
    res = sandbox.execute(circuit_spec)
    assert res["success"] is True
    # En paralelo, la profundidad es 1
    assert res["result"]["depth"] == 1
    
    # Puertas H secuenciales en el mismo qubit
    circuit_spec_seq = {
        "qubits": 1,
        "gates": [
            {"type": "H", "qubits": [0]},
            {"type": "H", "qubits": [0]}
        ]
    }
    res_seq = sandbox.execute(circuit_spec_seq)
    assert res_seq["success"] is True
    # En secuencia, la profundidad es 2
    assert res_seq["result"]["depth"] == 2
