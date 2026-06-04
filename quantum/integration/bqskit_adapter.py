import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from bqskit.ir import Circuit as BQSKitCircuit
    from bqskit.ir.gates import HGate, XGate, YGate, ZGate, CXGate, CZGate, SwapGate, RXGate, RYGate, RZGate
    from bqskit.compiler import Compiler as BQCompiler
    from bqskit.passes import QuickPartitioner
    import bqskit
    BQSKIT_AVAILABLE = True
except ImportError:
    BQSKIT_AVAILABLE = False
    logger.warning("bqskit is not installed. BQSKit adapter will use emulated fallbacks.")

def qade_json_to_bqskit(qade_json: Dict[str, Any]) -> Any:
    """
    Translates a QADE JSON circuit to a BQSKit Circuit.
    """
    if not BQSKIT_AVAILABLE:
        return {"mock_bqskit_circuit": True, "data": qade_json}
        
    num_qubits = qade_json.get("qubits", 0)
    c = BQSKitCircuit(num_qubits)
    
    for gate in qade_json.get("gates", []):
        g_type = gate.get("type", "").upper()
        q = gate.get("qubits", [])
        
        if not q:
            continue
            
        if g_type == "H":
            c.append_gate(HGate(), q[0])
        elif g_type == "X":
            c.append_gate(XGate(), q[0])
        elif g_type == "Y":
            c.append_gate(YGate(), q[0])
        elif g_type == "Z":
            c.append_gate(ZGate(), q[0])
        elif g_type in ("RX", "RY", "RZ"):
            theta = float(gate.get("theta", 0.0))
            if g_type == "RX":
                c.append_gate(RXGate(), q[0], [theta])
            elif g_type == "RY":
                c.append_gate(RYGate(), q[0], [theta])
            elif g_type == "RZ":
                c.append_gate(RZGate(), q[0], [theta])
        elif g_type in ("CNOT", "CX"):
            c.append_gate(CXGate(), [q[0], q[1]])
        elif g_type == "CZ":
            c.append_gate(CZGate(), [q[0], q[1]])
        elif g_type == "SWAP":
            c.append_gate(SwapGate(), [q[0], q[1]])
            
    return c

def bqskit_to_qade_json(bqskit_circuit: Any) -> Dict[str, Any]:
    """
    Translates a BQSKit Circuit back to QADE JSON.
    """
    if not BQSKIT_AVAILABLE:
        if isinstance(bqskit_circuit, dict) and "data" in bqskit_circuit:
            return bqskit_circuit["data"]
        return {"qubits": 0, "gates": []}
        
    num_qubits = bqskit_circuit.num_qubits
    gates = []
    
    for op in bqskit_circuit:
        name = op.gate.name.upper()
        qubits = list(op.location)
        
        if "HGATE" in name or name == "H":
            gates.append({"type": "H", "qubits": qubits})
        elif "XGATE" in name or name == "X":
            gates.append({"type": "X", "qubits": qubits})
        elif "YGATE" in name or name == "Y":
            gates.append({"type": "Y", "qubits": qubits})
        elif "ZGATE" in name or name == "Z":
            gates.append({"type": "Z", "qubits": qubits})
        elif "RXGATE" in name or name == "RX":
            theta = float(op.params[0])
            gates.append({"type": "RX", "qubits": qubits, "theta": theta})
        elif "RYGATE" in name or name == "RY":
            theta = float(op.params[0])
            gates.append({"type": "RY", "qubits": qubits, "theta": theta})
        elif "RZGATE" in name or name == "RZ":
            theta = float(op.params[0])
            gates.append({"type": "RZ", "qubits": qubits, "theta": theta})
        elif "CXGATE" in name or name in ("CX", "CNOT"):
            gates.append({"type": "CNOT", "qubits": qubits})
        elif "CZGATE" in name or name == "CZ":
            gates.append({"type": "CZ", "qubits": qubits})
        elif "SWAPGATE" in name or name == "SWAP":
            gates.append({"type": "SWAP", "qubits": qubits})
            
    return {
        "qubits": num_qubits,
        "gates": gates
    }

def compile_with_bqskit(qade_json: Dict[str, Any], coupling_map: Optional[Any] = None) -> Dict[str, Any]:
    """
    Compiles a circuit using BQSKit synthesis/partitioning search optimization.
    Falls back to a standard Qiskit transpilation flow if BQSKit is not available.
    """
    if not BQSKIT_AVAILABLE:
        # Fall back to Qiskit Level 3 transpilation as emulation
        from qiskit.providers.fake_provider import GenericBackendV2
        from qiskit import transpile
        from quantum.integration.qiskit_adapter import qade_json_to_qiskit, qiskit_to_qade_json
        
        qc = qade_json_to_qiskit(qade_json)
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
        c = qade_json_to_bqskit(qade_json)
        # BQSKit synthesis compilation
        with BQCompiler() as compiler:
            # Run quick synthesis partitioning pass
            c_opt = compiler.compile(c, [QuickPartitioner()])
        return bqskit_to_qade_json(c_opt)
    except Exception as e:
        logger.error(f"BQSKit compilation failed: {e}. Returning original circuit.")
        return qade_json
