import json
from typing import Dict, Any
from qiskit import QuantumCircuit
from qiskit.qasm3 import dumps

def qiskit_to_qade_json(quantum_circuit: QuantumCircuit) -> Dict[str, Any]:
    """
    Converts a Qiskit QuantumCircuit to QADE's internal JSON-compatible dictionary format.
    Supports single-qubit gates (H, X, Y, Z), rotation gates (RX, RY, RZ),
    and multi-qubit gates (CX, CZ, SWAP).
    """
    gates = []
    for instr in quantum_circuit.data:
        name = instr.operation.name.upper()
        # Normalize gate name
        if name == "CX":
            name = "CNOT"
            
        qubits = [quantum_circuit.find_bit(q).index for q in instr.qubits]
        gate_dict = {"type": name, "qubits": qubits}
        
        # Extract rotation parameters for RX, RY, RZ
        if name in ("RX", "RY", "RZ") and instr.operation.params:
            gate_dict["theta"] = float(instr.operation.params[0])
            
        gates.append(gate_dict)
        
    return {
        "qubits": quantum_circuit.num_qubits,
        "gates": gates
    }

def qade_json_to_qiskit(qade_circuit_json: Dict[str, Any]) -> QuantumCircuit:
    """
    Converts a QADE internal JSON-compatible dictionary to a Qiskit QuantumCircuit.
    """
    qubits = qade_circuit_json.get("qubits", 0)
    if qubits <= 0:
        raise ValueError("Circuit must have at least 1 qubit.")
        
    qc = QuantumCircuit(qubits)
    for gate in qade_circuit_json.get("gates", []):
        g_type = gate.get("type", "").upper()
        q = gate.get("qubits", [])
        
        if not q:
            continue
            
        if g_type == "H":
            qc.h(q[0])
        elif g_type == "X":
            qc.x(q[0])
        elif g_type == "Y":
            qc.y(q[0])
        elif g_type == "Z":
            qc.z(q[0])
        elif g_type in ("RX", "RY", "RZ"):
            theta = float(gate.get("theta", 0.0))
            if g_type == "RX":
                qc.rx(theta, q[0])
            elif g_type == "RY":
                qc.ry(theta, q[0])
            elif g_type == "RZ":
                qc.rz(theta, q[0])
        elif g_type in ("CNOT", "CX"):
            qc.cx(q[0], q[1])
        elif g_type == "CZ":
            qc.cz(q[0], q[1])
        elif g_type == "SWAP":
            qc.swap(q[0], q[1])
        else:
            raise ValueError(f"Unsupported gate type: {g_type}")
            
    return qc

def qade_json_to_openqasm(qade_circuit_json: Dict[str, Any]) -> str:
    """
    Converts a QADE internal JSON-compatible dictionary to an OpenQASM 3.0 string.
    """
    qc = qade_json_to_qiskit(qade_circuit_json)
    return dumps(qc)
