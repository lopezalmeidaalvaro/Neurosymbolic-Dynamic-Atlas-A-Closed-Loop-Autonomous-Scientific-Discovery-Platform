import json
from typing import Any, Dict, List, Optional, Tuple

from qiskit import QuantumCircuit

from quantum.integration.qiskit_adapter import qiskit_to_qade_json


def _as_qade(circuit: Any) -> Dict[str, Any]:
    if isinstance(circuit, QuantumCircuit):
        return qiskit_to_qade_json(circuit)
    return circuit


def _pattern_from_record(value: Any) -> List[Dict[str, Any]]:
    if isinstance(value, str):
        return json.loads(value)
    return value or []


def _gate_matches(pattern_gate: Dict[str, Any], actual_gate: Dict[str, Any], mapping: Dict[int, int]) -> bool:
    if pattern_gate.get("type", "").upper() != actual_gate.get("type", "").upper():
        return False
    p_qubits = pattern_gate.get("qubits", [])
    a_qubits = actual_gate.get("qubits", [])
    if len(p_qubits) != len(a_qubits):
        return False
    for p, a in zip(p_qubits, a_qubits):
        if p in mapping and mapping[p] != a:
            return False
        mapping[p] = a
    if "theta" in pattern_gate:
        if abs(float(pattern_gate["theta"]) - float(actual_gate.get("theta", 0.0))) > 1e-9:
            return False
    return True


def _match_at(gates: List[Dict[str, Any]], start: int, pattern: List[Dict[str, Any]]) -> Optional[Dict[int, int]]:
    if not pattern or start + len(pattern) > len(gates):
        return None
    mapping: Dict[int, int] = {}
    for offset, pattern_gate in enumerate(pattern):
        if not _gate_matches(pattern_gate, gates[start + offset], mapping):
            return None
    return mapping


def _instantiate(pattern: List[Dict[str, Any]], mapping: Dict[int, int]) -> List[Dict[str, Any]]:
    instantiated = []
    for gate in pattern:
        new_gate = dict(gate)
        new_gate["qubits"] = [mapping[q] for q in gate.get("qubits", [])]
        instantiated.append(new_gate)
    return instantiated


class MotifRewriter:
    def __init__(self, motifs: List[Dict[str, Any]]):
        self.motifs = [
            motif
            for motif in motifs
            if motif.get("validated", True)
            and int(motif.get("gate_reduction", 0)) > 0
            and _pattern_from_record(motif.get("pattern_before"))
        ]
        self.motifs.sort(key=lambda motif: (motif.get("score", 0), motif.get("gate_reduction", 0)), reverse=True)

    def rewrite(self, circuit: Any, max_passes: int = 5) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        qade = _as_qade(circuit)
        gates = list(qade.get("gates", []))
        applications = 0
        applied_ids: Dict[str, int] = {}

        for _ in range(max_passes):
            changed = False
            i = 0
            while i < len(gates):
                applied = False
                for motif in self.motifs:
                    before = _pattern_from_record(motif.get("pattern_before"))
                    after = _pattern_from_record(motif.get("pattern_after"))
                    mapping = _match_at(gates, i, before)
                    if mapping is None:
                        continue
                    replacement = _instantiate(after, mapping)
                    gates = gates[:i] + replacement + gates[i + len(before) :]
                    motif_id = motif.get("motif_id", "unknown")
                    applied_ids[motif_id] = applied_ids.get(motif_id, 0) + 1
                    applications += 1
                    changed = True
                    applied = True
                    break
                if not applied:
                    i += 1
            if not changed:
                break

        rewritten = {"qubits": qade.get("qubits", 0), "gates": gates}
        stats = {
            "applications": applications,
            "applied_motifs": applied_ids,
            "input_gate_count": len(qade.get("gates", [])),
            "output_gate_count": len(gates),
            "gate_delta": len(qade.get("gates", [])) - len(gates),
        }
        return rewritten, stats
