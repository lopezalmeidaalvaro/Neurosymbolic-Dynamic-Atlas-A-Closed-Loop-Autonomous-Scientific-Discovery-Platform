import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

try:
    import pyzx as zx
    PYZX_AVAILABLE = True
except ImportError:
    PYZX_AVAILABLE = False
    logger.warning("PyZX is not installed. PyZX adapter will use emulated fallbacks.")

def qade_json_to_pyzx(qade_json: Dict[str, Any]) -> Any:
    """
    Translates a QADE JSON circuit to a PyZX Circuit object.
    If PyZX is not available, returns a simulated mock object.
    """
    if not PYZX_AVAILABLE:
        return {"mock_circuit": True, "data": qade_json}
        
    num_qubits = qade_json.get("qubits", 0)
    c = zx.Circuit(num_qubits)
    
    for gate in qade_json.get("gates", []):
        g_type = gate.get("type", "").upper()
        q = gate.get("qubits", [])
        
        if not q:
            continue
            
        if g_type == "H":
            c.add_gate("HAD", q[0])
        elif g_type == "X":
            c.add_gate("NOT", q[0])
        elif g_type == "Y":
            # Y = S * X * S^dag, or we can add it as ZPhase(pi/2) -> XPhase(theta) -> ZPhase(-pi/2)
            c.add_gate("ZPhase", q[0], phase=1.570796)
            c.add_gate("XPhase", q[0], phase=3.141593)
            c.add_gate("ZPhase", q[0], phase=-1.570796)
        elif g_type == "Z":
            c.add_gate("ZPhase", q[0], phase=3.141593)
        elif g_type == "RX":
            theta = float(gate.get("theta", 0.0))
            c.add_gate("XPhase", q[0], phase=theta)
        elif g_type == "RY":
            # RY(theta) can be represented using ZPhase and XPhase
            theta = float(gate.get("theta", 0.0))
            c.add_gate("ZPhase", q[0], phase=1.570796)
            c.add_gate("XPhase", q[0], phase=theta)
            c.add_gate("ZPhase", q[0], phase=-1.570796)
        elif g_type == "RZ":
            theta = float(gate.get("theta", 0.0))
            c.add_gate("ZPhase", q[0], phase=theta)
        elif g_type in ("CNOT", "CX"):
            c.add_gate("CNOT", q[0], q[1])
        elif g_type == "CZ":
            c.add_gate("CZ", q[0], q[1])
        elif g_type == "SWAP":
            c.add_gate("SWAP", q[0], q[1])
            
    return c

def pyzx_to_qade_json(zx_circuit: Any) -> Dict[str, Any]:
    """
    Translates a PyZX Circuit back to QADE JSON format.
    """
    if not PYZX_AVAILABLE:
        if isinstance(zx_circuit, dict) and "data" in zx_circuit:
            return zx_circuit["data"]
        return {"qubits": 0, "gates": []}
        
    num_qubits = zx_circuit.qubits
    gates = []
    
    for g in zx_circuit.gates:
        name = g.name.upper()
        # Map PyZX gate types to QADE gate types
        if name == "HAD":
            gates.append({"type": "H", "qubits": [g.target]})
        elif name == "NOT":
            gates.append({"type": "X", "qubits": [g.target]})
        elif name == "CNOT":
            gates.append({"type": "CNOT", "qubits": [g.control, g.target]})
        elif name == "CZ":
            gates.append({"type": "CZ", "qubits": [g.control, g.target]})
        elif name == "SWAP":
            gates.append({"type": "SWAP", "qubits": [g.control, g.target]})
        elif name == "ZPHASE":
            gates.append({"type": "RZ", "qubits": [g.target], "theta": float(g.phase)})
        elif name == "XPHASE":
            gates.append({"type": "RX", "qubits": [g.target], "theta": float(g.phase)})
            
    return {
        "qubits": num_qubits,
        "gates": gates
    }

def simplify_zx_circuit(qade_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs full ZX graph simplification on the QADE JSON circuit.
    Falls back to simple algebraic cancels if PyZX is not available.
    """
    if not PYZX_AVAILABLE:
        # Fall back to custom algebraic cancels
        from quantum.optimization.pyzx_optimizer import PyZXOptimizer
        opt = PyZXOptimizer()
        res, _ = opt.optimize_circuit(qade_json)
        return res
        
    try:
        # 1. Translate QADE JSON to PyZX Circuit
        c = qade_json_to_pyzx(qade_json)
        # 2. Convert PyZX Circuit to Graph
        g = c.to_graph()
        # 3. Perform standard PyZX interior simplification passes
        zx.simplify.full_reduce(g)
        # 4. Extract simplified circuit from Graph
        c_opt = zx.extract_circuit(g).to_basic_gates()
        # 5. Translate back to QADE JSON
        return pyzx_to_qade_json(c_opt)
    except Exception as e:
        logger.error(f"PyZX full reduction failed: {e}. Falling back to algebraic passes.")
        from quantum.optimization.pyzx_optimizer import PyZXOptimizer
        opt = PyZXOptimizer()
        res, _ = opt.optimize_circuit(qade_json)
        return res
