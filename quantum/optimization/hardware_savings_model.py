from typing import Any, Dict


HARDWARE_PROFILES: Dict[str, Dict[str, float]] = {
    "ibm_superconducting": {
        "two_qubit_duration_us": 0.35,
        "single_qubit_duration_us": 0.05,
        "two_qubit_error": 0.01,
        "single_qubit_error": 0.001,
    },
    "ion_trap": {
        "two_qubit_duration_us": 120.0,
        "single_qubit_duration_us": 10.0,
        "two_qubit_error": 0.003,
        "single_qubit_error": 0.0005,
    },
    "neutral_atom": {
        "two_qubit_duration_us": 0.8,
        "single_qubit_duration_us": 0.2,
        "two_qubit_error": 0.02,
        "single_qubit_error": 0.002,
    },
}


def estimate_hardware_savings(motif: Dict[str, Any], hardware_type: str) -> Dict[str, float]:
    profile = HARDWARE_PROFILES[hardware_type]
    qubit_count = int(float(motif.get("qubit_count", 1) or 1))
    gate_reduction = max(0.0, float(motif.get("gate_reduction", 0.0) or 0.0))
    duration_reduction = max(0.0, float(motif.get("duration_reduction", 0.0) or 0.0))
    fidelity_gain = max(0.0, float(motif.get("fidelity_gain", 0.0) or 0.0))
    observations = max(1.0, float(motif.get("observations", motif.get("frequency", 1)) or 1))

    two_qubit_fraction = 1.0 if qubit_count >= 2 else 0.0
    saved_two_qubit_operations = gate_reduction * two_qubit_fraction * observations
    saved_single_qubit_operations = gate_reduction * (1.0 - two_qubit_fraction) * observations
    inferred_time = (
        saved_two_qubit_operations * profile["two_qubit_duration_us"]
        + saved_single_qubit_operations * profile["single_qubit_duration_us"]
    )
    saved_execution_time_us = max(duration_reduction * observations, inferred_time)
    saved_error_probability = min(
        1.0,
        saved_two_qubit_operations * profile["two_qubit_error"]
        + saved_single_qubit_operations * profile["single_qubit_error"]
        + fidelity_gain,
    )
    saved_shots_required = max(0.0, 1000.0 * saved_error_probability)
    return {
        "saved_two_qubit_operations": saved_two_qubit_operations,
        "saved_single_qubit_operations": saved_single_qubit_operations,
        "saved_execution_time_us": saved_execution_time_us,
        "saved_error_probability": saved_error_probability,
        "saved_shots_required": saved_shots_required,
    }


def aggregate_hardware_savings(motif: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    return {
        hardware_type: estimate_hardware_savings(motif, hardware_type)
        for hardware_type in HARDWARE_PROFILES
    }
