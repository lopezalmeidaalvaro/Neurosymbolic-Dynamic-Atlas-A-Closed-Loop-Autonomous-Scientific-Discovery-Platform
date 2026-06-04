import logging
import math
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from pytket import Circuit as TKETCircuit
    from pytket.passes import FullPeepholeOptimise, DefaultMappingPass
    from pytket.architecture import Architecture
    PYTKET_AVAILABLE = True
except ImportError:
    PYTKET_AVAILABLE = False
    logger.warning("pytket is not installed. TKET adapter will use emulated fallbacks.")

def qade_json_to_tket(qade_json: Dict[str, Any]) -> Any:
    """
    Translates a QADE JSON circuit to a pytket Circuit.
    """
    if not PYTKET_AVAILABLE:
        return {"mock_tket_circuit": True, "data": qade_json}
        
    num_qubits = qade_json.get("qubits", 0)
    c = TKETCircuit(num_qubits)
    
    for gate in qade_json.get("gates", []):
        g_type = gate.get("type", "").upper()
        q = gate.get("qubits", [])
        
        if not q:
            continue
            
        if g_type == "H":
            c.H(q[0])
        elif g_type == "X":
            c.X(q[0])
        elif g_type == "Y":
            c.Y(q[0])
        elif g_type == "Z":
            c.Z(q[0])
        elif g_type in ("RX", "RY", "RZ"):
            # pytket parameters are in half-turns (divided by pi)
            theta_half_turns = float(gate.get("theta", 0.0)) / math.pi
            if g_type == "RX":
                c.Rx(theta_half_turns, q[0])
            elif g_type == "RY":
                c.Ry(theta_half_turns, q[0])
            elif g_type == "RZ":
                c.Rz(theta_half_turns, q[0])
        elif g_type in ("CNOT", "CX"):
            c.CX(q[0], q[1])
        elif g_type == "CZ":
            c.CZ(q[0], q[1])
        elif g_type == "SWAP":
            c.SWAP(q[0], q[1])
            
    return c

def tket_to_qade_json(tket_circuit: Any) -> Dict[str, Any]:
    """
    Translates a pytket Circuit to QADE JSON format.
    """
    if not PYTKET_AVAILABLE:
        if isinstance(tket_circuit, dict) and "data" in tket_circuit:
            return tket_circuit["data"]
        return {"qubits": 0, "gates": []}
        
    num_qubits = len(tket_circuit.qubits)
    gates = []
    
    for command in tket_circuit.get_commands():
        op = command.op
        name = op.type.name.upper()
        qubits = [q.index[0] for q in command.qubits]
        
        if name == "H":
            gates.append({"type": "H", "qubits": qubits})
        elif name == "X":
            gates.append({"type": "X", "qubits": qubits})
        elif name == "Y":
            gates.append({"type": "Y", "qubits": qubits})
        elif name == "Z":
            gates.append({"type": "Z", "qubits": qubits})
        elif name in ("RX", "RY", "RZ"):
            # pytket parameters are in half-turns, convert back to radians
            theta = float(op.params[0]) * math.pi
            gates.append({"type": name, "qubits": qubits, "theta": theta})
        elif name == "CX":
            gates.append({"type": "CNOT", "qubits": qubits})
        elif name == "CZ":
            gates.append({"type": "CZ", "qubits": qubits})
        elif name == "SWAP":
            gates.append({"type": "SWAP", "qubits": qubits})
            
    return {
        "qubits": num_qubits,
        "gates": gates
    }

def compile_with_tket(qade_json: Dict[str, Any], coupling_map: Optional[Any] = None) -> Dict[str, Any]:
    """
    Compiles a circuit using TKET's FullPeepholeOptimise and optional layout mapping pass.
    Falls back to Qiskit transpile(optimization_level=3) if TKET is not installed.
    """
    if not PYTKET_AVAILABLE:
        # Fall back to Qiskit Level 3 transpilation as emulation
        from qiskit.providers.fake_provider import GenericBackendV2
        from qiskit import transpile
        from quantum.integration.qiskit_adapter import qade_json_to_qiskit, qiskit_to_qade_json
        
        qc = qade_json_to_qiskit(qade_json)
        # Mock backend with coupling map
        n_q = qade_json.get("qubits", 5)
        if coupling_map is not None and len(coupling_map) > 0:
            max_q = max(max(edge) for edge in coupling_map) + 1
            num_backend_qubits = max(n_q, max_q)
        else:
            num_backend_qubits = n_q
        backend = GenericBackendV2(num_qubits=num_backend_qubits, coupling_map=coupling_map)
        transpiled_qc = transpile(qc, backend=backend, optimization_level=3)
        return qiskit_to_qade_json(transpiled_qc)
        
    try:
        c = qade_json_to_tket(qade_json)
        # Apply standard peephole compiler optimizations
        FullPeepholeOptimise().apply(c)
        
        # Apply layout routing if coupling_map is provided
        if coupling_map is not None:
            arch = Architecture(coupling_map)
            DefaultMappingPass(arch).apply(c)
            
        return tket_to_qade_json(c)
    except Exception as e:
        logger.error(f"TKET compilation failed: {e}. Returning original circuit.")
        return qade_json
