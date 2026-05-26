import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
import math
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from core.io import ARTIFACTS_DIR
from core.validation import certify_session


def load_session(session_id: str) -> Dict[str, Any]:
    file_path = ARTIFACTS_DIR / "sessions" / f"{session_id}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Session file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_embedding_vector(session: Dict[str, Any], system_name: str) -> List[float]:
    """
    Extract the 8D structural embedding vector for a given system name.
    """
    emb = session.get("embeddings", {}).get(system_name, {})
    if not emb:
        return []
    fields = [
        "lyapunov_max",
        "spectral_entropy",
        "dominant_frequency",
        "variance",
        "autocorr_decay",
        "kurtosis",
        "skewness",
        "energy",
    ]
    return [float(emb.get(f, 0.0)) for f in fields]


def compute_euclidean_distance(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(v1, v2)))


def analyze_noise_drift(session_ids: List[str]) -> Dict[str, Any]:
    """
    Analyze Euclidean drift of embeddings across different noise levels compared to the clean baseline.
    Kept for backward compatibility.
    """
    sessions = []
    for s_id in session_ids:
        try:
            sessions.append(load_session(s_id))
        except Exception as e:
            print(f"[ANALYZER] Warning: Failed to load session {s_id}: {e}")

    if not sessions:
        return {}

    sessions.sort(key=lambda s: s.get("metadata", {}).get("noiseLevel", 0.0))
    baseline_session = sessions[0]
    systems = list(baseline_session.get("embeddings", {}).keys())

    results_by_noise = []

    for s in sessions:
        noise = s.get("metadata", {}).get("noiseLevel", 0.0)
        s_id = s.get("metadata", {}).get("id")

        comparisons = s.get("benchmarks", {}).get("comparisons", {})
        emb_v2_acc = comparisons.get("Embedding_V2", {}).get("accuracy", 1.0)
        rocket_acc = comparisons.get("ROCKET", {}).get("accuracy", 1.0)
        dtw_acc = comparisons.get("DTW", {}).get("accuracy", 1.0)

        drift_by_system = {}
        total_drift = 0.0
        count = 0
        for sys_name in systems:
            v_base = extract_embedding_vector(baseline_session, sys_name)
            v_curr = extract_embedding_vector(s, sys_name)
            if v_base and v_curr:
                d = compute_euclidean_distance(v_base, v_curr)
                drift_by_system[sys_name] = round(d, 6)
                total_drift += d
                count += 1

        avg_drift = total_drift / count if count > 0 else 0.0

        results_by_noise.append(
            {
                "session_id": s_id,
                "noise_level": noise,
                "accuracy": emb_v2_acc,
                "rocket_accuracy": rocket_acc,
                "dtw_accuracy": dtw_acc,
                "average_drift": round(avg_drift, 6),
                "drift_by_system": drift_by_system,
            }
        )

    return {
        "baseline_session_id": baseline_session.get("metadata", {}).get("id"),
        "systems_analyzed": systems,
        "runs": results_by_noise,
    }


def analyze_massive_sweep(session_ids: List[str]) -> Dict[str, Any]:
    """
    Analyze a massive sweep across multiple systems, noise levels, and seeds.
    Calculates derivatives of drift (velocity, acceleration) and confidence intervals.
    """
    sessions = []
    for s_id in session_ids:
        try:
            sessions.append(load_session(s_id))
        except Exception as e:
            print(f"[ANALYZER] Warning: Failed to load session {s_id}: {e}")

    if not sessions:
        return {}

    # Extract metadata fields
    # Group sessions by (system, noise, seed)
    session_map = {}
    systems_set = set()
    noise_set = set()
    seeds_set = set()

    for s in sessions:
        metadata = s.get("metadata", {})
        s_id = metadata.get("id")
        noise = float(metadata.get("noiseLevel", 0.0))

        # seed may be None for sessions created before schema v1.1 — fall back to
        # parsing it from the session id string (e.g. "lorenz_noise_0.25_seed_42").
        raw_seed = metadata.get("seed")
        if raw_seed is not None:
            seed = int(raw_seed)
        else:
            try:
                seed = int(str(s_id).split("_seed_")[-1])
            except (ValueError, IndexError):
                seed = 42

        noise_set.add(noise)
        seeds_set.add(seed)

        # Systems present in this session
        session_systems = list(s.get("embeddings", {}).keys())
        for sys_name in session_systems:
            systems_set.add(sys_name)
            session_map[(sys_name, noise, seed)] = s

    systems = sorted(list(systems_set))
    noise_levels = sorted(list(noise_set))
    seeds = sorted(list(seeds_set))

    results = {}

    for sys_name in systems:
        sys_noise_levels = []
        sys_mean_drifts = []
        sys_std_drifts = []
        sys_mean_accuracies = []
        sys_std_accuracies = []
        sys_mean_rocket_accuracies = []
        sys_std_rocket_accuracies = []
        sys_mean_dtw_accuracies = []
        sys_std_dtw_accuracies = []

        for noise in noise_levels:
            drifts_at_noise = []
            accuracies_at_noise = []
            rocket_accuracies_at_noise = []
            dtw_accuracies_at_noise = []

            for seed in seeds:
                # Find current run session
                curr_s = session_map.get((sys_name, noise, seed))
                # Find baseline run session for SAME seed
                base_s = session_map.get((sys_name, 0.0, seed))

                if curr_s and base_s:
                    v_curr = extract_embedding_vector(curr_s, sys_name)
                    v_base = extract_embedding_vector(base_s, sys_name)

                    if v_curr and v_base:
                        drift = compute_euclidean_distance(v_base, v_curr)
                        drifts_at_noise.append(drift)

                        comparisons = curr_s.get("benchmarks", {}).get(
                            "comparisons", {}
                        )
                        accuracies_at_noise.append(
                            float(
                                comparisons.get("Embedding_V2", {}).get("accuracy", 1.0)
                            )
                        )
                        rocket_accuracies_at_noise.append(
                            float(comparisons.get("ROCKET", {}).get("accuracy", 1.0))
                        )
                        dtw_accuracies_at_noise.append(
                            float(comparisons.get("DTW", {}).get("accuracy", 1.0))
                        )

            if drifts_at_noise:
                sys_noise_levels.append(noise)
                sys_mean_drifts.append(float(np.mean(drifts_at_noise)))
                sys_std_drifts.append(float(np.std(drifts_at_noise)))

                sys_mean_accuracies.append(float(np.mean(accuracies_at_noise)))
                sys_std_accuracies.append(float(np.std(accuracies_at_noise)))

                sys_mean_rocket_accuracies.append(
                    float(np.mean(rocket_accuracies_at_noise))
                )
                sys_std_rocket_accuracies.append(
                    float(np.std(rocket_accuracies_at_noise))
                )

                sys_mean_dtw_accuracies.append(float(np.mean(dtw_accuracies_at_noise)))
                sys_std_dtw_accuracies.append(float(np.std(dtw_accuracies_at_noise)))

        # Numerical derivatives using np.gradient
        if len(sys_noise_levels) > 1:
            velocity = np.gradient(sys_mean_drifts, sys_noise_levels).tolist()
            acceleration = np.gradient(velocity, sys_noise_levels).tolist()
        else:
            velocity = [0.0] * len(sys_noise_levels)
            acceleration = [0.0] * len(sys_noise_levels)

        results[sys_name] = {
            "noise": sys_noise_levels,
            "mean_drift": [round(x, 6) for x in sys_mean_drifts],
            "std_drift": [round(x, 6) for x in sys_std_drifts],
            "velocity": [round(x, 6) for x in velocity],
            "acceleration": [round(x, 6) for x in acceleration],
            "mean_accuracy": [round(x, 4) for x in sys_mean_accuracies],
            "std_accuracy": [round(x, 4) for x in sys_std_accuracies],
            "mean_rocket_accuracy": [round(x, 4) for x in sys_mean_rocket_accuracies],
            "std_rocket_accuracy": [round(x, 4) for x in sys_std_rocket_accuracies],
            "mean_dtw_accuracy": [round(x, 4) for x in sys_mean_dtw_accuracies],
            "std_dtw_accuracy": [round(x, 4) for x in sys_std_dtw_accuracies],
        }

    # ── Phase 3.3: Mathematical analysis complete. Now certify results. ────
    raw_analysis = {
        "metadata": {"systems": systems, "noise_levels": noise_levels, "seeds": seeds},
        "results": results,
    }

    print("[CERTIFIER] Certifying statistical validity of analysis results...")
    certified_analysis = certify_session(raw_analysis)
    print("[CERTIFIER] Certification complete.")

    return certified_analysis
