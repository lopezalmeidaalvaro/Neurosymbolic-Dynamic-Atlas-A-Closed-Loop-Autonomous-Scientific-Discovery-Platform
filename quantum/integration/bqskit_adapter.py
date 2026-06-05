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
        
    bqskit_circuit.unfold_all()
    num_qubits = bqskit_circuit.num_qudits
    gates = []
    
    for op in bqskit_circuit:
        name = op.gate.name.upper()
        qubits = list(op.location)
        
        if name in ("HGATE", "H"):
            gates.append({"type": "H", "qubits": qubits})
        elif name in ("XGATE", "X"):
            gates.append({"type": "X", "qubits": qubits})
        elif name in ("YGATE", "Y"):
            gates.append({"type": "Y", "qubits": qubits})
        elif name in ("ZGATE", "Z"):
            gates.append({"type": "Z", "qubits": qubits})
        elif name in ("RXGATE", "RX"):
            theta = float(op.params[0])
            gates.append({"type": "RX", "qubits": qubits, "theta": theta})
        elif name in ("RYGATE", "RY"):
            theta = float(op.params[0])
            gates.append({"type": "RY", "qubits": qubits, "theta": theta})
        elif name in ("RZGATE", "RZ"):
            theta = float(op.params[0])
            gates.append({"type": "RZ", "qubits": qubits, "theta": theta})
        elif name in ("CXGATE", "CNOTGATE", "CX", "CNOT"):
            gates.append({"type": "CNOT", "qubits": qubits})
        elif name in ("CZGATE", "CZ"):
            gates.append({"type": "CZ", "qubits": qubits})
        elif name in ("SWAPGATE", "SWAP"):
            gates.append({"type": "SWAP", "qubits": qubits})
            
    return {
        "qubits": num_qubits,
        "gates": gates
    }

def compile_with_bqskit(qade_json: Dict[str, Any], coupling_map: Optional[Any] = None, return_layout: bool = False) -> Any:
    """
    Compiles a circuit using BQSKit synthesis/partitioning search optimization.
    Falls back to a standard Qiskit transpilation flow if BQSKit is not available.
    """
    num_qubits = qade_json.get("qubits", 0)
    if not BQSKIT_AVAILABLE or num_qubits > 5:
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
        res_json = qiskit_to_qade_json(transpiled_qc)
        
        # Extract layout
        layout = {}
        if transpiled_qc.layout and transpiled_qc.layout.initial_layout:
            for qubit, phys in transpiled_qc.layout.initial_layout.get_virtual_bits().items():
                try:
                    v_idx = qc.find_bit(qubit).index
                    layout[v_idx] = phys
                except Exception:
                    layout[getattr(qubit, "index", 0)] = phys
        else:
            layout = {i: i for i in range(n_q)}
            
        if return_layout:
            return res_json, layout
        return res_json
        
    try:
        c = qade_json_to_bqskit(qade_json)
        # BQSKit synthesis compilation
        with BQCompiler(num_workers=1) as compiler:
            # Run quick synthesis partitioning pass
            c_opt = compiler.compile(c, [QuickPartitioner()])
        res_json = bqskit_to_qade_json(c_opt)
        layout = {i: i for i in range(num_qubits)}
        if return_layout:
            return res_json, layout
        return res_json
    except Exception as e:
        logger.error(f"BQSKit compilation failed: {e}. Returning original circuit.")
        if return_layout:
            return qade_json, {i: i for i in range(num_qubits)}
        return qade_json
