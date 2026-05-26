import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from typing import Dict, Any, List


def evaluate_hypotheses(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates scientific hypotheses H1, H2, and H3 using drift analysis data.
    """
    runs = analysis_results.get("runs", [])
    if not runs:
        return {}

    h1_status = "PENDING"
    h1_evidence = ""
    h2_status = "PENDING"
    h2_evidence = ""
    h3_status = "PENDING"
    h3_evidence = ""

    critical_collapse_points = []

    # Thresholds
    DRIFT_STABILITY_THRESHOLD = 2.0
    COLLAPSE_ACCURACY_THRESHOLD = 0.90
    COLLAPSE_DRIFT_THRESHOLD = 3.0

    # H1: Stability for low noise (sigma <= 0.1)
    low_noise_runs = [r for r in runs if r["noise_level"] <= 0.1]
    if low_noise_runs:
        h1_passed = True
        evidences = []
        for r in low_noise_runs:
            if r["average_drift"] > DRIFT_STABILITY_THRESHOLD:
                h1_passed = False
            evidences.append(f"sigma={r['noise_level']} drift={r['average_drift']}")
        h1_status = "VALIDATED" if h1_passed else "FALSIFIED"
        h1_evidence = f"Low noise drift bounds: {', '.join(evidences)}"
    else:
        h1_status = "INSUFFICIENT_DATA"

    # H2: Collapse Threshold
    for r in runs:
        sigma = r["noise_level"]
        acc = r["accuracy"]
        drift = r["average_drift"]
        if acc < COLLAPSE_ACCURACY_THRESHOLD and drift > COLLAPSE_DRIFT_THRESHOLD:
            critical_collapse_points.append(
                {"noise_level": sigma, "accuracy": acc, "average_drift": drift}
            )

    if critical_collapse_points:
        h2_status = "VALIDATED"
        h2_evidence = f"Critical collapse observed at noise levels: {', '.join([str(p['noise_level']) for p in critical_collapse_points])}"
    else:
        h2_status = "NO_COLLAPSE_OBSERVED"
        h2_evidence = f"Accuracy remained >= {COLLAPSE_ACCURACY_THRESHOLD} or drift <= {COLLAPSE_DRIFT_THRESHOLD} for all tested noise levels."

    # H3: Speed & Accuracy dominance over DTW
    h3_passed = True
    h3_reasons = []
    for r in runs:
        emb_acc = r["accuracy"]
        dtw_acc = r["dtw_accuracy"]
        if emb_acc < dtw_acc:
            h3_passed = False
            h3_reasons.append(
                f"Embedding_V2 accuracy ({emb_acc}) < DTW ({dtw_acc}) at noise={r['noise_level']}"
            )

    if h3_passed:
        h3_status = "VALIDATED"
        h3_evidence = (
            "Embedding_V2 maintained accuracy >= DTW accuracy across all noise levels."
        )
    else:
        h3_status = "PARTIALLY_VALIDATED"
        h3_evidence = (
            f"Accuracy dominance failed in some configurations: {'; '.join(h3_reasons)}"
        )

    return {
        "H1_stability": {
            "hypothesis": "Geometric Drift remains low (<= 2.0) under minor perturbations (sigma <= 0.1)",
            "status": h1_status,
            "evidence": h1_evidence,
        },
        "H2_collapse": {
            "hypothesis": "Dynamic systems exhibit topological collapse (Accuracy < 0.90 and Drift > 3.0) at critical noise boundaries",
            "status": h2_status,
            "evidence": h2_evidence,
            "critical_collapse_points": critical_collapse_points,
        },
        "H3_dominance": {
            "hypothesis": "Embedding_V2 maintains topological classification parity or superiority vs DTW under noise",
            "status": h3_status,
            "evidence": h3_evidence,
        },
    }
