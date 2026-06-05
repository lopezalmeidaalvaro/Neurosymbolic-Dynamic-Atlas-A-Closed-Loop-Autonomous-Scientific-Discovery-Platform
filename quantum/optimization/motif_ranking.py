from typing import Any, Dict, List


def score_motif(motif: Dict[str, Any]) -> float:
    frequency = max(1.0, float(motif.get("observations", motif.get("frequency", 1))))
    gate_saving = max(0.0, float(motif.get("gate_reduction", 0.0)))
    fidelity_improvement = max(1e-6, 1.0 + float(motif.get("fidelity_gain", 0.0)))
    hardware_relevance = 1.0 + max(0.0, float(motif.get("duration_reduction", 0.0)))
    confidence = max(0.1, float(motif.get("confidence_score", 0.5)))
    return frequency * gate_saving * fidelity_improvement * hardware_relevance * confidence


def rank_motifs(motifs: List[Dict[str, Any]], limit: int = 50) -> List[Dict[str, Any]]:
    ranked = []
    for motif in motifs:
        record = dict(motif)
        record["score"] = score_motif(record)
        ranked.append(record)
    return sorted(ranked, key=lambda item: item["score"], reverse=True)[:limit]
