import math
from typing import Any, Dict, Iterable, List


def simulate_knowledge_growth(
    workload_counts: Iterable[int],
    base_motifs: int,
    base_validated: int,
    base_reusable: int,
    base_transferability: float,
    base_portfolio_value: float,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for workloads in workload_counts:
        discovery_multiplier = 1.0 + 0.18 * math.log1p(workloads)
        total_motifs = int(round(base_motifs + 1.65 * (workloads ** 0.72)))
        validated_motifs = int(round(total_motifs * min(0.98, base_validated / max(1, base_motifs) + 0.015 * math.log1p(workloads))))
        reusable_motifs = int(round(validated_motifs * min(0.92, base_transferability + 0.035 * math.log1p(workloads))))
        transferability = reusable_motifs / max(1, validated_motifs)
        knowledge_graph_edges = int(round(total_motifs * (3.0 + 0.55 * math.log1p(workloads))))
        value = base_portfolio_value * ((max(1, reusable_motifs) / max(1, base_reusable)) ** 1.18) * (0.75 + 0.25 * discovery_multiplier)
        rows.append(
            {
                "workloads": workloads,
                "total_motifs": total_motifs,
                "validated_motifs": validated_motifs,
                "reusable_motifs": reusable_motifs,
                "knowledge_graph_edges": knowledge_graph_edges,
                "transferability": transferability,
                "expected_portfolio_value": value,
                "low_value": value * 0.55,
                "high_value": value * 1.75,
            }
        )
    return rows


def flywheel_verdict(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(rows) < 2:
        return {"compounds": False, "value_multiple": 1.0}
    first = rows[0]["expected_portfolio_value"]
    last = rows[-1]["expected_portfolio_value"]
    return {
        "compounds": last > first,
        "value_multiple": last / max(first, 1e-9),
        "motif_multiple": rows[-1]["reusable_motifs"] / max(1, rows[0]["reusable_motifs"]),
    }
