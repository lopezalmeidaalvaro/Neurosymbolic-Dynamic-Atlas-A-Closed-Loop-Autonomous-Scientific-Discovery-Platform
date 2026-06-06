import math
from typing import Any, Dict, Iterable, List


def simulate_network_effects(
    customer_counts: Iterable[int],
    base_portfolio_value: float,
    base_motifs: int,
    workloads_per_customer_per_year: int = 12,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for customers in customer_counts:
        contributed_workloads = customers * workloads_per_customer_per_year
        acceleration = 1.0 + math.log1p(customers) / 4.0
        new_motifs_per_year = (contributed_workloads ** 0.62) * acceleration
        accumulated_motifs = base_motifs + int(round(new_motifs_per_year))
        value_growth = base_portfolio_value * ((accumulated_motifs / max(1, base_motifs)) ** 1.22)
        customer_value = value_growth / max(1, customers)
        rows.append(
            {
                "customers": customers,
                "contributed_workloads_per_year": contributed_workloads,
                "motif_discovery_acceleration": acceleration,
                "knowledge_accumulation_rate": new_motifs_per_year,
                "portfolio_value": value_growth,
                "customer_value": customer_value,
                "data_network_effect": acceleration > 1.5,
            }
        )
    return rows
