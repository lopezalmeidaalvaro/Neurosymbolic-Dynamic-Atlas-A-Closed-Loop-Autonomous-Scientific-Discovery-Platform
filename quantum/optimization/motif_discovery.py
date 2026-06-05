import hashlib
import json
import math
from typing import Any, Dict, List, Optional, Tuple

from qiskit import QuantumCircuit

from quantum.integration.qiskit_adapter import qiskit_to_qade_json
from quantum.optimization.hardware_cost_model import estimate_physical_cost
from quantum.optimization.motif_validator import MotifValidator


SELF_INVERSE = {"H", "X", "Y", "Z", "CNOT", "CX", "CZ", "SWAP"}
ROTATIONS = {"RX", "RY", "RZ"}


def _as_qade(circuit: Any) -> Dict[str, Any]:
    if isinstance(circuit, QuantumCircuit):
        return qiskit_to_qade_json(circuit)
    return circuit


def _gate_key(gate: Dict[str, Any]) -> Tuple[Any, ...]:
    params = tuple(round(float(p), 12) for p in gate.get("params", []))
    theta = round(float(gate.get("theta", 0.0)), 12) if "theta" in gate else None
    return (gate.get("type", "").upper(), tuple(gate.get("qubits", [])), params, theta)


def _canonicalize(pattern: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
    mapping = {}
    next_q = 0
    canonical = []
    for gate in pattern:
        new_gate = {k: v for k, v in gate.items() if k != "qubits"}
        qubits = []
        for qubit in gate.get("qubits", []):
            if qubit not in mapping:
                mapping[qubit] = next_q
                next_q += 1
            qubits.append(mapping[qubit])
        new_gate["type"] = new_gate.get("type", "").upper()
        new_gate["qubits"] = qubits
        canonical.append(new_gate)
    return canonical, max(1, next_q)


def _motif_id(before: List[Dict[str, Any]], after: List[Dict[str, Any]]) -> str:
    payload = json.dumps({"before": before, "after": after}, sort_keys=True)
    return "motif_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _depth(pattern: List[Dict[str, Any]], qubit_count: int) -> int:
    depths = [0] * max(1, qubit_count)
    for gate in pattern:
        qubits = gate.get("qubits", [])
        if not qubits:
            continue
        current = max(depths[q] for q in qubits)
        for q in qubits:
            depths[q] = current + 1
    return max(depths) if depths else 0


def _estimate_duration(pattern: List[Dict[str, Any]], qubit_count: int, backend: Any) -> float:
    if backend is None:
        return float(_depth(pattern, qubit_count))
    try:
        return estimate_physical_cost({"qubits": qubit_count, "gates": pattern}, backend)[
            "critical_duration_us"
        ]
    except Exception:
        return float(_depth(pattern, qubit_count))


def _estimate_fidelity(pattern: List[Dict[str, Any]], qubit_count: int, backend: Any) -> float:
    if not pattern:
        return 1.0
    if backend is None:
        return 1.0
    try:
        return estimate_physical_cost({"qubits": qubit_count, "gates": pattern}, backend)[
            "total_estimated_fidelity"
        ]
    except Exception:
        return 1.0


class MotifDiscoveryEngine:
    def __init__(self, backend: Optional[Any] = None, validation_threshold: float = 0.999999):
        self.backend = backend
        self.validator = MotifValidator(validation_threshold)

    def _build_motif(
        self,
        before_raw: List[Dict[str, Any]],
        after_raw: List[Dict[str, Any]],
        motif_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        before, before_qubits = _canonicalize(before_raw)
        after, after_qubits = _canonicalize(after_raw)
        qubit_count = max(before_qubits, after_qubits)
        motif = {
            "motif_id": _motif_id(before, after),
            "motif_type": motif_type,
            "pattern_before": before,
            "pattern_after": after,
            "qubit_count": qubit_count,
            "gate_reduction": len(before) - len(after),
            "depth_reduction": _depth(before, qubit_count) - _depth(after, qubit_count),
            "duration_reduction": _estimate_duration(before, qubit_count, self.backend)
            - _estimate_duration(after, qubit_count, self.backend),
            "fidelity_gain": _estimate_fidelity(after, qubit_count, self.backend)
            - _estimate_fidelity(before, qubit_count, self.backend),
            "frequency": 1,
        }
        if context:
            motif.update(context)
        motif = self.validator.validate(motif)
        return motif if motif.get("validated") else None

    def discover(
        self,
        original_circuit: Any,
        optimized_circuit: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        qade = _as_qade(original_circuit)
        gates = qade.get("gates", [])
        motifs: Dict[str, Dict[str, Any]] = {}

        def add(before: List[Dict[str, Any]], after: List[Dict[str, Any]], motif_type: str) -> None:
            motif = self._build_motif(before, after, motif_type, context=context)
            if motif is None:
                return
            existing = motifs.get(motif["motif_id"])
            if existing:
                existing["frequency"] += 1
            else:
                motifs[motif["motif_id"]] = motif

        for i in range(len(gates) - 1):
            g0 = gates[i]
            g1 = gates[i + 1]
            t0 = g0.get("type", "").upper()
            t1 = g1.get("type", "").upper()
            if t0 == t1 and t0 in SELF_INVERSE and _gate_key(g0) == _gate_key(g1):
                add([g0, g1], [], "cancellation_pattern")

            if t0 == t1 and t0 in ROTATIONS and g0.get("qubits") == g1.get("qubits"):
                theta0 = float(g0.get("theta", g0.get("params", [0.0])[0] if g0.get("params") else 0.0))
                theta1 = float(g1.get("theta", g1.get("params", [0.0])[0] if g1.get("params") else 0.0))
                theta = theta0 + theta1
                if abs(theta) < 1e-10:
                    add([g0, g1], [], "rotation_cancellation")
                else:
                    merged = {"type": t0, "qubits": list(g0.get("qubits", [])), "theta": theta, "params": [theta]}
                    add([g0, g1], [merged], "commuting_rotation_merge")

        for i in range(len(gates) - 2):
            g0, g1, g2 = gates[i], gates[i + 1], gates[i + 2]
            if (
                g0.get("type", "").upper() == "SWAP"
                and g2.get("type", "").upper() == "SWAP"
                and g0.get("qubits") == g2.get("qubits")
                and len(g1.get("qubits", [])) == 2
            ):
                a, b = g0["qubits"]
                mapped = []
                for q in g1["qubits"]:
                    if q == a:
                        mapped.append(b)
                    elif q == b:
                        mapped.append(a)
                    else:
                        mapped.append(q)
                after_gate = dict(g1)
                after_gate["qubits"] = mapped
                add([g0, g1, g2], [after_gate], "routing_shortcut")

        for i in range(len(gates) - 4):
            window = gates[i : i + 5]
            if (
                window[0].get("type", "").upper() == "H"
                and window[1].get("type", "").upper() == "H"
                and window[2].get("type", "").upper() in ("CNOT", "CX")
                and window[3].get("type", "").upper() == "H"
                and window[4].get("type", "").upper() == "H"
            ):
                control, target = window[2].get("qubits", [None, None])
                if (
                    window[0].get("qubits") == [control]
                    and window[1].get("qubits") == [target]
                    and window[3].get("qubits") == [control]
                    and window[4].get("qubits") == [target]
                ):
                    add(window, [{"type": "CNOT", "qubits": [target, control]}], "hardware_aware_rewrite")

        return sorted(motifs.values(), key=lambda motif: motif["gate_reduction"], reverse=True)
