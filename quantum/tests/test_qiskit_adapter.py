import pytest
from qiskit import QuantumCircuit
from quantum.integration.qiskit_adapter import qiskit_to_qade_json, qade_json_to_qiskit, qade_json_to_openqasm

def test_adapter_round_trip():
    # 1. Create a test Qiskit circuit with 10 target gates
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.x(1)
    qc.y(2)
    qc.z(0)
    qc.rx(0.5, 1)
    qc.ry(1.0, 2)
    qc.rz(1.5, 0)
    qc.cx(0, 1)
    qc.cz(1, 2)
    qc.swap(0, 2)
    
    # 2. Convert to QADE JSON
    qade_json = qiskit_to_qade_json(qc)
    assert qade_json["qubits"] == 3
    assert len(qade_json["gates"]) == 10
    
    # Verify gate types
    gate_types = [g["type"] for g in qade_json["gates"]]
    assert gate_types == ["H", "X", "Y", "Z", "RX", "RY", "RZ", "CNOT", "CZ", "SWAP"]
    
    # Verify parameters
    assert pytest.approx(qade_json["gates"][4]["theta"]) == 0.5
    assert pytest.approx(qade_json["gates"][5]["theta"]) == 1.0
    assert pytest.approx(qade_json["gates"][6]["theta"]) == 1.5
    
    # 3. Convert QADE JSON back to Qiskit QuantumCircuit
    qc_back = qade_json_to_qiskit(qade_json)
    assert qc_back.num_qubits == 3
    assert len(qc_back.data) == 10
    
    # 4. Check OpenQASM output
    qasm_str = qade_json_to_openqasm(qade_json)
    assert "OPENQASM 3.0" in qasm_str
    assert "h q[0];" in qasm_str
    assert "cx q[0], q[1];" in qasm_str
