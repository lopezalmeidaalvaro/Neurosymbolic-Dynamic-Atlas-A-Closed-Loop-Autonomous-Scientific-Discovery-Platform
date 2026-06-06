from typing import Any, Dict, Iterable, List


def estimate_catch_up(
    targets: Iterable[float],
    current_motifs: int,
    replacement_cost: float,
    annual_competitor_budget: float = 450000.0,
    validation_drag: float = 1.35,
    learning_drag: float = 1.25,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    cost_per_motif = replacement_cost / max(1, current_motifs)
    for target in targets:
        motifs_required = current_motifs * target
        effective_cost = motifs_required * cost_per_motif * validation_drag * learning_drag
        years = effective_cost / max(1.0, annual_competitor_budget)
        rows.append(
            {
                "target_portfolio_pct": target,
                "motifs_to_reproduce": motifs_required,
                "estimated_cost": effective_cost,
                "years_to_catch_up": years,
                "low_years": years * 0.65,
                "high_years": years * 1.8,
            }
        )
    return rows
