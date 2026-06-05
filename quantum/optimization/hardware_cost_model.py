import math
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from qiskit import QuantumCircuit, transpile

from quantum.integration.qiskit_adapter import qade_json_to_qiskit


CircuitLike = Union[QuantumCircuit, Dict[str, Any]]

DEFAULT_SINGLE_QUBIT_DURATION_SEC = 50e-9
DEFAULT_TWO_QUBIT_DURATION_SEC = 300e-9
DEFAULT_SINGLE_QUBIT_ERROR = 1e-3
DEFAULT_TWO_QUBIT_ERROR = 1e-2
DEFAULT_READOUT_ERROR = 1e-2
DEFAULT_T1_SEC = 100e-6
DEFAULT_T2_SEC = 50e-6


def _as_quantum_circuit(circuit: CircuitLike) -> QuantumCircuit:
    if isinstance(circuit, QuantumCircuit):
        return circuit
    return qade_json_to_qiskit(circuit)


def _safe_target_get(backend: Any, op_name: str, qargs: Tuple[int, ...]) -> Any:
    target = getattr(backend, "target", None)
    if target is None or op_name not in target:
        return None
    try:
        props = target[op_name].get(qargs)
        if props is None and len(qargs) == 2:
            props = target[op_name].get((qargs[1], qargs[0]))
        return props
    except Exception:
        return None


def _property_value(props: Any, name: str, default: float) -> float:
    if props is None:
        return default
    value = getattr(props, name, None)
    if value is None:
        return default
    try:
        return float(value)
    except Exception:
        return default


def get_qubit_quality(backend: Any, qubit: int) -> Dict[str, float]:
    t1 = DEFAULT_T1_SEC
    t2 = DEFAULT_T2_SEC
    try:
        props = backend.qubit_properties(qubit)
        if props is not None:
            t1 = float(getattr(props, "t1", None) or t1)
            t2 = float(getattr(props, "t2", None) or t2)
    except Exception:
        pass

    readout_error = DEFAULT_READOUT_ERROR
    meas_props = _safe_target_get(backend, "measure", (qubit,))
    if meas_props is not None:
        readout_error = _property_value(meas_props, "error", readout_error)

    return {"t1": t1, "t2": t2, "readout_error": readout_error}


def get_gate_properties(
    backend: Any, gate_name: str, qargs: Iterable[int]
) -> Dict[str, float]:
    q_tuple = tuple(int(q) for q in qargs)
    op_name = gate_name.lower()
    if op_name in ("cnot",):
        op_name = "cx"

    default_duration = (
        DEFAULT_TWO_QUBIT_DURATION_SEC
        if len(q_tuple) >= 2
        else DEFAULT_SINGLE_QUBIT_DURATION_SEC
    )
    default_error = (
        DEFAULT_TWO_QUBIT_ERROR if len(q_tuple) >= 2 else DEFAULT_SINGLE_QUBIT_ERROR
    )
    if op_name in ("rz", "barrier"):
        default_duration = 0.0
        default_error = 0.0

    props = _safe_target_get(backend, op_name, q_tuple)
    duration = _property_value(props, "duration", default_duration)
    error = _property_value(props, "error", default_error)
    return {"duration": duration, "error": error}


def estimate_swap_duration(backend: Any, edge: Tuple[int, int]) -> float:
    props = get_gate_properties(backend, "swap", edge)
    if props["duration"] != DEFAULT_TWO_QUBIT_DURATION_SEC:
        return props["duration"]
    cx_props = get_gate_properties(backend, "cx", edge)
    ecr_props = get_gate_properties(backend, "ecr", edge)
    native = min(cx_props["duration"], ecr_props["duration"])
    return 3.0 * native


def estimate_swap_error(backend: Any, edge: Tuple[int, int]) -> float:
    props = get_gate_properties(backend, "swap", edge)
    if props["error"] != DEFAULT_TWO_QUBIT_ERROR:
        return props["error"]
    cx_props = get_gate_properties(backend, "cx", edge)
    ecr_props = get_gate_properties(backend, "ecr", edge)
    native = min(cx_props["error"], ecr_props["error"])
    return min(1.0, 3.0 * native)


def _native_circuit(circuit: QuantumCircuit, backend: Any) -> QuantumCircuit:
    try:
        return transpile(
            circuit,
            backend=backend,
            optimization_level=0,
            scheduling_method="asap",
        )
    except Exception:
        try:
            return transpile(
                circuit,
                basis_gates=getattr(backend, "operation_names", None),
                optimization_level=0,
            )
        except Exception:
            return circuit


def estimate_physical_cost(
    circuit: CircuitLike,
    backend: Any,
    lambda_duration: float = 0.0,
    lambda_swaps: float = 0.01,
) -> Dict[str, Any]:
    """
    Estimate hardware execution cost from calibrated backend data.

    The returned score is maximized:
        score = log(F_total) - lambda_duration * duration_seconds
                - lambda_swaps * swaps
    """
    qc = _as_quantum_circuit(circuit)
    native = _native_circuit(qc, backend)
    num_qubits = int(getattr(backend, "num_qubits", native.num_qubits))

    active_qubits = set()
    qubit_end_times = {q: 0.0 for q in range(num_qubits)}
    log_gate_fidelity = 0.0
    swap_count = 0
    two_qubit_count = 0
    gate_details: List[Dict[str, Any]] = []

    for instruction in native.data:
        op_name = instruction.operation.name
        qargs = tuple(native.find_bit(qubit).index for qubit in instruction.qubits)
        active_qubits.update(qargs)
        if op_name.lower() == "swap":
            swap_count += 1
        if len(qargs) == 2:
            two_qubit_count += 1

        props = get_gate_properties(backend, op_name, qargs)
        duration = props["duration"]
        error = max(0.0, min(1.0, props["error"]))
        log_gate_fidelity += math.log(max(1e-15, 1.0 - error))

        if qargs:
            start = max(qubit_end_times.get(q, 0.0) for q in qargs)
            finish = start + duration
            for q in qargs:
                qubit_end_times[q] = finish

        gate_details.append(
            {
                "gate": op_name,
                "qubits": qargs,
                "error": error,
                "duration_sec": duration,
            }
        )

    if not active_qubits:
        active_qubits = set(range(native.num_qubits))

    log_readout_fidelity = 0.0
    log_coherence_fidelity = 0.0
    qubit_quality = {}
    for q in active_qubits:
        quality = get_qubit_quality(backend, q)
        qubit_quality[q] = quality
        readout_error = max(0.0, min(1.0, quality["readout_error"]))
        log_readout_fidelity += math.log(max(1e-15, 1.0 - readout_error))

        residence_time = qubit_end_times.get(q, 0.0)
        t1 = max(quality["t1"], 1e-15)
        t2 = max(quality["t2"], 1e-15)
        log_coherence_fidelity += -(residence_time / t1) - (residence_time / t2)

    critical_duration_sec = max(qubit_end_times.values()) if qubit_end_times else 0.0
    log_total = log_gate_fidelity + log_readout_fidelity + log_coherence_fidelity
    total_estimated_fidelity = math.exp(max(-745.0, min(0.0, log_total)))
    score = log_total - lambda_duration * critical_duration_sec - lambda_swaps * swap_count

    return {
        "score": score,
        "log_total_fidelity": log_total,
        "total_estimated_fidelity": total_estimated_fidelity,
        "estimated_fidelity": total_estimated_fidelity,
        "gate_fidelity": math.exp(max(-745.0, min(0.0, log_gate_fidelity))),
        "readout_fidelity": math.exp(max(-745.0, min(0.0, log_readout_fidelity))),
        "coherence_fidelity": math.exp(
            max(-745.0, min(0.0, log_coherence_fidelity))
        ),
        "critical_path_duration_sec": critical_duration_sec,
        "critical_duration_us": critical_duration_sec * 1e6,
        "gate_count": len(native.data),
        "two_qubit_count": two_qubit_count,
        "swap_count": swap_count,
        "active_qubits": sorted(active_qubits),
        "qubit_quality": qubit_quality,
        "gate_details": gate_details,
    }
