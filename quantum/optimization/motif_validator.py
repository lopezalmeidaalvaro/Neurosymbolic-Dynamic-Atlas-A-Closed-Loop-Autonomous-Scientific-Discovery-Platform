import math
from typing import Any, Dict, List

import numpy as np
from qiskit.quantum_info import Operator

from quantum.integration.qiskit_adapter import qade_json_to_qiskit


def _motif_circuit(pattern: List[Dict[str, Any]], qubit_count: int):
    return qade_json_to_qiskit({"qubits": max(1, qubit_count), "gates": pattern})


def operator_fidelity(
    pattern_before: List[Dict[str, Any]],
    pattern_after: List[Dict[str, Any]],
    qubit_count: int,
) -> float:
    before_op = Operator(_motif_circuit(pattern_before, qubit_count)).data
    after_op = Operator(_motif_circuit(pattern_after, qubit_count)).data
    dim = before_op.shape[0]
    overlap = np.trace(before_op.conj().T @ after_op)
    return float(abs(overlap / dim) ** 2)


def validate_motif(motif: Dict[str, Any], threshold: float = 0.999999) -> Dict[str, Any]:
    qubit_count = int(motif.get("qubit_count", 0))
    fidelity = operator_fidelity(
        motif.get("pattern_before", []),
        motif.get("pattern_after", []),
        qubit_count,
    )
    result = dict(motif)
    result["validation_fidelity"] = fidelity
    result["validated"] = fidelity >= threshold and math.isfinite(fidelity)
    return result


class MotifValidator:
    def __init__(self, threshold: float = 0.999999):
        self.threshold = threshold

    def validate(self, motif: Dict[str, Any]) -> Dict[str, Any]:
        return validate_motif(motif, self.threshold)

    def validate_many(self, motifs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.validate(motif) for motif in motifs]
