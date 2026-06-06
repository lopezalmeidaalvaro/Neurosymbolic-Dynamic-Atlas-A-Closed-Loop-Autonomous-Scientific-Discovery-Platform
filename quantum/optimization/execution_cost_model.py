from typing import Any, Dict


COST_MODEL = {
    "cost_per_shot": 0.0008,
    "cost_per_job": 0.25,
    "cost_per_runtime_second": 0.18,
    "default_shots": 4000,
    "max_effective_shots": 1_000_000,
}


def estimate_execution_cost(
    workload: Dict[str, Any],
    cost_per_shot: float = COST_MODEL["cost_per_shot"],
    cost_per_job: float = COST_MODEL["cost_per_job"],
    cost_per_runtime_second: float = COST_MODEL["cost_per_runtime_second"],
    default_shots: int = COST_MODEL["default_shots"],
    max_effective_shots: int = COST_MODEL["max_effective_shots"],
) -> Dict[str, float]:
    original_gate_count = float(workload.get("original_gate_count", 0.0) or 0.0)
    motif_gate_count = float(workload.get("motif_gate_count", original_gate_count) or original_gate_count)
    original_fidelity = max(1e-9, float(workload.get("original_fidelity", 0.0) or 0.0))
    motif_fidelity = max(1e-9, float(workload.get("motif_fidelity", original_fidelity) or original_fidelity))

    original_runtime_sec = original_gate_count * 0.35e-6
    motif_runtime_sec = motif_gate_count * 0.35e-6
    shots_without = min(max_effective_shots, default_shots / original_fidelity)
    shots_with = min(max_effective_shots, default_shots / motif_fidelity)
    cost_without = (
        cost_per_job
        + shots_without * cost_per_shot
        + original_runtime_sec * cost_per_runtime_second
    )
    cost_with = (
        cost_per_job
        + shots_with * cost_per_shot
        + motif_runtime_sec * cost_per_runtime_second
    )
    savings = max(0.0, cost_without - cost_with)
    savings_pct = savings / cost_without if cost_without > 0 else 0.0
    return {
        "cost_without_motif": cost_without,
        "cost_with_motif": cost_with,
        "cost_savings": savings,
        "cost_savings_percentage": savings_pct,
        "shots_without_motif": shots_without,
        "shots_with_motif": shots_with,
    }
