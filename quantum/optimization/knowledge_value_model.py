import math
from typing import Any, Dict, Iterable, List

import numpy as np


def marginal_motif_values(
    motif_indices: Iterable[int],
    base_value_per_reusable_motif: float,
    compounding_exponent: float = 0.18,
) -> List[Dict[str, Any]]:
    rows = []
    cumulative = 0.0
    for idx in motif_indices:
        marginal = base_value_per_reusable_motif * (idx ** compounding_exponent)
        cumulative += marginal
        rows.append(
            {
                "motif_index": idx,
                "marginal_value": marginal,
                "cumulative_sample_value": cumulative,
            }
        )
    return rows


def fit_value_models(points: List[Dict[str, Any]]) -> Dict[str, Any]:
    x = np.array([float(p["motif_index"]) for p in points])
    y = np.array([float(p["marginal_value"]) for p in points])

    def r2(pred):
        ss_res = float(np.sum((y - pred) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        return 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0

    linear_coef = np.polyfit(x, y, 1)
    linear_pred = np.polyval(linear_coef, x)

    log_coef = np.polyfit(np.log(x), y, 1)
    log_pred = log_coef[0] * np.log(x) + log_coef[1]

    power_coef = np.polyfit(np.log(x), np.log(y), 1)
    power_pred = np.exp(power_coef[1]) * (x ** power_coef[0])

    scores = {
        "linear": r2(linear_pred),
        "logarithmic": r2(log_pred),
        "power_law": r2(power_pred),
    }
    best = max(scores.items(), key=lambda item: item[1])
    saturation = "compounds" if best[0] == "power_law" and power_coef[0] > 0.05 else "saturates"
    return {
        "linear_r2": scores["linear"],
        "logarithmic_r2": scores["logarithmic"],
        "power_law_r2": scores["power_law"],
        "best_fit": best[0],
        "best_fit_r2": best[1],
        "power_law_exponent": float(power_coef[0]),
        "value_behavior": saturation,
    }
