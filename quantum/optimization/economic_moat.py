from typing import Any, Dict, List


def score_moats(
    reusable_motifs: int,
    transferability_score: float,
    annual_revenue_potential: float,
) -> List[Dict[str, Any]]:
    scores = [
        ("Knowledge moat", min(10.0, 4.0 + reusable_motifs / 2.0)),
        ("Data moat", min(10.0, 3.0 + 7.0 * transferability_score)),
        ("Integration moat", 6.0),
        ("Switching cost moat", 6.5),
        ("Brand moat", 3.5),
        ("Patent moat", 4.5),
        ("Developer ecosystem moat", 4.0),
    ]
    rows = []
    for name, score in scores:
        rows.append({"moat": name, "score": score, "score_low": max(0.0, score - 1.5), "score_high": min(10.0, score + 1.0)})
    overall = sum(row["score"] for row in rows) / len(rows)
    rows.append({"moat": "Overall moat rating", "score": overall, "score_low": max(0.0, overall - 1.2), "score_high": min(10.0, overall + 1.0)})
    return rows


def competitor_defensibility() -> List[Dict[str, Any]]:
    return [
        {"competitor": "Qiskit", "reproduce_motifs": "medium", "reproduce_validation_history": "hard", "reproduce_workload_knowledge": "hard", "reproduce_transferability_stats": "hard", "difficulty_score": 7.0},
        {"competitor": "TKET", "reproduce_motifs": "medium", "reproduce_validation_history": "hard", "reproduce_workload_knowledge": "hard", "reproduce_transferability_stats": "hard", "difficulty_score": 7.0},
        {"competitor": "BQSKit", "reproduce_motifs": "medium", "reproduce_validation_history": "hard", "reproduce_workload_knowledge": "hard", "reproduce_transferability_stats": "hard", "difficulty_score": 7.2},
        {"competitor": "Cirq", "reproduce_motifs": "medium", "reproduce_validation_history": "hard", "reproduce_workload_knowledge": "hard", "reproduce_transferability_stats": "hard", "difficulty_score": 6.8},
        {"competitor": "PyZX", "reproduce_motifs": "easy for algebraic motifs", "reproduce_validation_history": "hard", "reproduce_workload_knowledge": "hard", "reproduce_transferability_stats": "hard", "difficulty_score": 6.5},
    ]
