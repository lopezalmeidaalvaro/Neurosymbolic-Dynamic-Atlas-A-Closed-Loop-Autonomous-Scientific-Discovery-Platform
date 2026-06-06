import json
from typing import Any, Dict, List

from quantum.optimization.hardware_savings_model import aggregate_hardware_savings


def _safe_json_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value:
        try:
            return json.loads(value)
        except Exception:
            return {}
    return {}


def profile_motif_economics(
    motif: Dict[str, Any],
    reusable_ids: set[str],
) -> Dict[str, Any]:
    motif_id = motif.get("motif_id", "")
    hardware_savings = aggregate_hardware_savings(motif)
    ibm = hardware_savings["ibm_superconducting"]
    frequency = int(float(motif.get("observations", motif.get("frequency", 1)) or 1))
    fidelity_gain = float(motif.get("fidelity_gain", 0.0) or 0.0)
    transferability = 1.0 if motif_id in reusable_ids else 0.0
    families = _safe_json_dict(motif.get("families", {}))
    family_count = len(families)
    return {
        "motif_id": motif_id,
        "motif_type": motif.get("motif_type", ""),
        "gate_reduction": float(motif.get("gate_reduction", 0.0) or 0.0),
        "two_qubit_reduction": ibm["saved_two_qubit_operations"] / max(1, frequency),
        "depth_reduction": float(motif.get("depth_reduction", 0.0) or 0.0),
        "duration_reduction": float(motif.get("duration_reduction", 0.0) or 0.0),
        "estimated_fidelity_gain": fidelity_gain,
        "estimated_error_reduction": max(0.0, fidelity_gain),
        "frequency_of_occurrence": frequency,
        "transferability": transferability,
        "family_count": family_count,
        "ibm_saved_two_qubit_operations": ibm["saved_two_qubit_operations"],
        "ibm_saved_execution_time_us": ibm["saved_execution_time_us"],
        "ibm_saved_error_probability": ibm["saved_error_probability"],
        "ibm_saved_shots_required": ibm["saved_shots_required"],
        "ion_trap_saved_execution_time_us": hardware_savings["ion_trap"]["saved_execution_time_us"],
        "neutral_atom_saved_execution_time_us": hardware_savings["neutral_atom"]["saved_execution_time_us"],
    }


def profile_all_motifs(
    motifs: List[Dict[str, Any]],
    reusable_ids: set[str],
) -> List[Dict[str, Any]]:
    return [profile_motif_economics(motif, reusable_ids) for motif in motifs]
