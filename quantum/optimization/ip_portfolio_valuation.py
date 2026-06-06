from typing import Any, Dict, List


def estimate_ip_portfolio_value(
    motif_economics: List[Dict[str, Any]],
    workload_economics: List[Dict[str, Any]],
) -> Dict[str, Any]:
    number_of_motifs = len(motif_economics)
    validated_motifs = number_of_motifs
    reusable_motifs = sum(1 for row in motif_economics if float(row.get("transferability", 0.0)) > 0)
    transferability_score = reusable_motifs / max(1, number_of_motifs)
    total_savings = sum(
        float(row.get("cost_savings", row.get("economic_savings_per_job", 0.0)))
        for row in workload_economics
    )
    commercial_relevance_score = min(1.0, total_savings / 1000.0)

    engineer_year_cost = 220000.0
    validation_cost_per_motif = 7500.0
    replacement_cost = number_of_motifs * validation_cost_per_motif + 0.5 * engineer_year_cost
    research_equivalent_cost = replacement_cost * (1.0 + transferability_score)
    estimated_ip_value = research_equivalent_cost * (1.0 + commercial_relevance_score)

    return {
        "number_of_motifs": number_of_motifs,
        "validated_motifs": validated_motifs,
        "reusable_motifs": reusable_motifs,
        "transferability_score": transferability_score,
        "commercial_relevance_score": commercial_relevance_score,
        "replacement_cost": replacement_cost,
        "research_equivalent_cost": research_equivalent_cost,
        "estimated_IP_value": estimated_ip_value,
    }
