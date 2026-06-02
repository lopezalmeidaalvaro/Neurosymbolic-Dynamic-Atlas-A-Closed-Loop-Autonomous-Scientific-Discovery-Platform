import sys
from pathlib import Path
import math

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
from quantum.sandbox.qiskit_quantum_sandbox import QiskitQuantumSandbox
from quantum.critics.quantum_critic import QuantumCritic

def test_bell_fidelity_optimal():
    """Valida el Caso A: Circuito Bell óptimo frente al estado Bell objetivo."""
    sandbox = QiskitQuantumSandbox()
    critic = QuantumCritic(alpha=0.01, beta=0.001)

    circuit_spec = {
        "qubits": 2,
        "gates": [
            {"type": "H", "qubits": [0]},
            {"type": "CNOT", "qubits": [0, 1]}
        ]
    }
    
    res_sandbox = sandbox.execute(circuit_spec)
    assert res_sandbox["success"] is True

    # Estado Bell objetivo: (|00> + |11>) / sqrt(2)
    target_state = [1.0/math.sqrt(2), 0.0, 0.0, 1.0/math.sqrt(2)]

    res_critic = critic.validate(res_sandbox, target_state)
    assert res_critic.valid is True
    assert pytest.approx(res_critic.fidelity, abs=1e-7) == 1.0
    
    # depth = 2, gate_count = 2
    # Score esperado: 1.0 - 0.01 * 2 - 0.001 * 2 = 0.978
    assert pytest.approx(res_critic.score, abs=1e-7) == 0.978


def test_bell_fidelity_incorrect():
    """Valida el Caso B: Un circuito incorrecto que produce un estado con fidelidad menor."""
    sandbox = QiskitQuantumSandbox()
    critic = QuantumCritic(alpha=0.01, beta=0.001)

    # Circuito que sólo aplica X en el qubit 0 (produce |10> = [0, 0, 1, 0])
    circuit_spec = {
        "qubits": 2,
        "gates": [
            {"type": "X", "qubits": [0]}
        ]
    }

    res_sandbox = sandbox.execute(circuit_spec)
    assert res_sandbox["success"] is True

    # Estado Bell objetivo: (|00> + |11>) / sqrt(2)
    target_state = [1.0/math.sqrt(2), 0.0, 0.0, 1.0/math.sqrt(2)]

    res_critic = critic.validate(res_sandbox, target_state)
    assert res_critic.valid is True
    # El producto interno con |10> es 0, por lo que la fidelidad es 0.0
    assert pytest.approx(res_critic.fidelity, abs=1e-7) == 0.0
    # Score esperado: 0.0 - 0.01 * 1 - 0.001 * 1 = -0.011
    assert pytest.approx(res_critic.score, abs=1e-7) == -0.011


def test_bell_fidelity_redundant():
    """Valida el Caso C: Un circuito Bell redundante que tiene menor score debido a penalizaciones."""
    sandbox = QiskitQuantumSandbox()
    critic = QuantumCritic(alpha=0.01, beta=0.001)

    # Circuito Bell óptimo (depth 2, gates 2)
    circuit_spec_opt = {
        "qubits": 2,
        "gates": [
            {"type": "H", "qubits": [0]},
            {"type": "CNOT", "qubits": [0, 1]}
        ]
    }
    res_opt = sandbox.execute(circuit_spec_opt)

    # Circuito Bell redundante (aplicar X dos veces en qubit 0, depth 4, gates 4)
    circuit_spec_red = {
        "qubits": 2,
        "gates": [
            {"type": "X", "qubits": [0]},
            {"type": "X", "qubits": [0]},
            {"type": "H", "qubits": [0]},
            {"type": "CNOT", "qubits": [0, 1]}
        ]
    }
    res_red = sandbox.execute(circuit_spec_red)

    target_state = [1.0/math.sqrt(2), 0.0, 0.0, 1.0/math.sqrt(2)]

    verdict_opt = critic.validate(res_opt, target_state)
    verdict_red = critic.validate(res_red, target_state)

    assert verdict_opt.valid is True
    assert verdict_red.valid is True

    # Ambas fidelidades deben ser exactamente 1.0
    assert pytest.approx(verdict_opt.fidelity, abs=1e-7) == 1.0
    assert pytest.approx(verdict_red.fidelity, abs=1e-7) == 1.0

    # El score óptimo debe ser mayor que el redundante
    assert verdict_opt.score > verdict_red.score
    
    # Score redundante esperado: 1.0 - 0.01 * 4 - 0.001 * 4 = 0.956
    assert pytest.approx(verdict_red.score, abs=1e-7) == 0.956


def test_ghz_fidelity_optimal():
    """Valida el cálculo de fidelidad para el estado GHZ de 3 qubits."""
    sandbox = QiskitQuantumSandbox()
    critic = QuantumCritic(alpha=0.01, beta=0.001)

    # Circuito GHZ óptimo (H en 0, CNOT 0->1, CNOT 1->2)
    circuit_spec = {
        "qubits": 3,
        "gates": [
            {"type": "H", "qubits": [0]},
            {"type": "CNOT", "qubits": [0, 1]},
            {"type": "CNOT", "qubits": [1, 2]}
        ]
    }

    res_sandbox = sandbox.execute(circuit_spec)
    assert res_sandbox["success"] is True

    # Estado GHZ objetivo: (|000> + |111>) / sqrt(2)
    target_state = [1.0/math.sqrt(2), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0/math.sqrt(2)]

    res_critic = critic.validate(res_sandbox, target_state)
    assert res_critic.valid is True
    assert pytest.approx(res_critic.fidelity, abs=1e-7) == 1.0
    
    # depth = 3, gate_count = 3
    # Score esperado: 1.0 - 0.01 * 3 - 0.001 * 3 = 0.967
    assert pytest.approx(res_critic.score, abs=1e-7) == 0.967


def test_custom_penalties():
    """Valida la flexibilidad de configuraciones dinámicas de penalizaciones alpha y beta."""
    sandbox = QiskitQuantumSandbox()
    
    # Penalizaciones pesadas en constructor
    critic = QuantumCritic(alpha=0.1, beta=0.05)

    circuit_spec = {
        "qubits": 2,
        "gates": [
            {"type": "H", "qubits": [0]},
            {"type": "CNOT", "qubits": [0, 1]}
        ]
    }
    
    res_sandbox = sandbox.execute(circuit_spec)
    target_state = [1.0/math.sqrt(2), 0.0, 0.0, 1.0/math.sqrt(2)]

    # Validación con las penalizaciones del constructor
    verdict1 = critic.validate(res_sandbox, target_state)
    # depth=2, gates=2 -> score = 1.0 - 0.1 * 2 - 0.05 * 2 = 0.70
    assert pytest.approx(verdict1.score, abs=1e-7) == 0.70

    # Validación sobreescribiendo las penalizaciones por kwargs en validate()
    verdict2 = critic.validate(res_sandbox, target_state, alpha=0.5, beta=0.2)
    # depth=2, gates=2 -> score = 1.0 - 0.5 * 2 - 0.2 * 2 = -0.40
    assert pytest.approx(verdict2.score, abs=1e-7) == -0.40


def test_statevector_parsing_formats():
    """Valida la robustez del parser frente a diferentes formatos del vector de estado."""
    critic = QuantumCritic()
    
    candidate_result = {
        "depth": 2,
        "gate_count": 2,
        "statevector": ["0.70710678+0j", "0j", "0.0j", "0.70710678+0j"]
    }
    
    # Formato A: Números complejos directamente en Python
    target_state_complex = [0.70710678+0j, 0j, 0j, 0.70710678+0j]
    res1 = critic.validate(candidate_result, target_state_complex)
    assert res1.valid is True
    assert pytest.approx(res1.fidelity, abs=1e-6) == 1.0

    # Formato B: Lista de dos elementos [real, imag] por cada amplitud
    target_state_nested = [[0.70710678, 0.0], [0.0, 0.0], [0.0, 0.0], [0.70710678, 0.0]]
    res2 = critic.validate(candidate_result, target_state_nested)
    assert res2.valid is True
    assert pytest.approx(res2.fidelity, abs=1e-6) == 1.0

    # Formato C: Cadenas que representan números complejos
    target_state_str = ["0.70710678", "0", "0i", "0.70710678"]
    res3 = critic.validate(candidate_result, target_state_str)
    assert res3.valid is True
    assert pytest.approx(res3.fidelity, abs=1e-6) == 1.0
