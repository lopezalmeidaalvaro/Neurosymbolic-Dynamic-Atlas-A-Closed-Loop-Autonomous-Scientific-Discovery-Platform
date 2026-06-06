from typing import Any, Dict, List


def evaluate_business_models() -> List[Dict[str, Any]]:
    models = [
        {
            "model": "A - Compiler License",
            "revenue_scalability": 5,
            "customer_lock_in": 4,
            "defensibility": 4,
            "gross_margin": 8,
            "strategic_value": 5,
        },
        {
            "model": "B - Cloud Optimization API",
            "revenue_scalability": 8,
            "customer_lock_in": 6,
            "defensibility": 6,
            "gross_margin": 8,
            "strategic_value": 7,
        },
        {
            "model": "C - Optimization Knowledge Platform",
            "revenue_scalability": 9,
            "customer_lock_in": 9,
            "defensibility": 9,
            "gross_margin": 9,
            "strategic_value": 10,
        },
    ]
    for model in models:
        model["score"] = (
            0.25 * model["revenue_scalability"]
            + 0.20 * model["customer_lock_in"]
            + 0.25 * model["defensibility"]
            + 0.10 * model["gross_margin"]
            + 0.20 * model["strategic_value"]
        )
    return sorted(models, key=lambda row: row["score"], reverse=True)
