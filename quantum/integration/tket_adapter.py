import logging
import math
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from pytket import Circuit as TKETCircuit
    from pytket.passes import FullPeepholeOptimise, DefaultMappingPass
    from pytket.architecture import Architecture
    PYTKET_AVAILABLE = True
except Exception:
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
        elif name == "TK1":
            # TK1(alpha, beta, gamma) = Rz(gamma) * Rx(beta) * Rz(alpha) in half-turns
            alpha = float(op.params[0]) * math.pi
            beta = float(op.params[1]) * math.pi
            gamma = float(op.params[2]) * math.pi
            gates.append({"type": "RZ", "qubits": qubits, "theta": alpha})
            gates.append({"type": "RX", "qubits": qubits, "theta": beta})
            gates.append({"type": "RZ", "qubits": qubits, "theta": gamma})
        elif name == "U1":
            lam = float(op.params[0]) * math.pi
            gates.append({"type": "RZ", "qubits": qubits, "theta": lam})
        elif name == "U2":
            phi = float(op.params[0]) * math.pi
            lam = float(op.params[1]) * math.pi
            gates.append({"type": "RZ", "qubits": qubits, "theta": lam})
            gates.append({"type": "RY", "qubits": qubits, "theta": math.pi / 2.0})
            gates.append({"type": "RZ", "qubits": qubits, "theta": phi})
        elif name == "U3":
            theta = float(op.params[0]) * math.pi
            phi = float(op.params[1]) * math.pi
            lam = float(op.params[2]) * math.pi
            gates.append({"type": "RZ", "qubits": qubits, "theta": lam})
            gates.append({"type": "RY", "qubits": qubits, "theta": theta})
            gates.append({"type": "RZ", "qubits": qubits, "theta": phi})
        elif name in ("RX", "RY", "RZ"):
            # pytket parameters are in half-turns, convert back to radians
            theta = float(op.params[0]) * math.pi
            gates.append({"type": name, "qubits": qubits, "theta": theta})
        elif name in ("CX", "CNOT"):
            gates.append({"type": "CNOT", "qubits": qubits})
        elif name == "CZ":
            gates.append({"type": "CZ", "qubits": qubits})
        elif name == "SWAP":
            gates.append({"type": "SWAP", "qubits": qubits})
            
    return {
        "qubits": num_qubits,
        "gates": gates
    }

def compile_with_tket(qade_json: Dict[str, Any], coupling_map: Optional[Any] = None, return_layout: bool = False) -> Any:
    """
    Compiles a circuit using TKET's FullPeepholeOptimise and optional layout mapping pass.
    Raises RuntimeError if pytket is not installed.
    """
    n_q = qade_json.get("qubits", 5)
    if not PYTKET_AVAILABLE:
        raise RuntimeError(
            "TKET is not installed. "
            "Run: pip install pytket>=1.20.0 "
            "This compiler will be excluded from benchmarks."
        )
        
    try:
        c = qade_json_to_tket(qade_json)
        # Apply standard peephole compiler optimizations
        FullPeepholeOptimise().apply(c)
        
        layout = {i: i for i in range(n_q)}
        # Apply layout routing if coupling_map is provided
        if coupling_map is not None:
            arch = Architecture(coupling_map)
            from pytket.placement import GraphPlacement
            from pytket.passes import PlacementPass, RoutingPass
            pl = GraphPlacement(arch)
            try:
                placement_map = pl.get_placement_map(c)
                for q, node in placement_map.items():
                    layout[q.index[0]] = node.index[0]
            except Exception:
                pass
            PlacementPass(pl).apply(c)
            RoutingPass(arch).apply(c)
            
        res_json = tket_to_qade_json(c)
        if return_layout:
            return res_json, layout
        return res_json
    except Exception as e:
        logger.error(f"TKET compilation failed: {e}. Returning original circuit.")
        if return_layout:
            return qade_json, {i: i for i in range(n_q)}
        return qade_json
