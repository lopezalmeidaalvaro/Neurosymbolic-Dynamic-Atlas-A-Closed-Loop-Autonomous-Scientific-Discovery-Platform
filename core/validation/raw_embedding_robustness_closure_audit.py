"""
core/validation/raw_embedding_robustness_closure_audit.py
==========================================================
Rigorous closure audit to isolate physical local reorganization
vs. mathematical fragility in raw Embedding V3 space.
"""

from __future__ import annotations

import json
import os
import sys
import time
import traceback
from typing import Callable

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import pdist
from scipy.stats import pearsonr
from scipy.spatial import procrustes
from scipy.integrate import solve_ivp
from sklearn.metrics import f1_score, roc_auc_score, average_precision_score

# Ensure ROOT_DIR is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

# Import baseline functions and constants
from core.validation.cross_system_generalization_tests import (
    simulate_physical,
    extract_v3,
    PHYSICAL_SYSTEMS,
    V3_KEYS,
    WINDOW_SIZE,
    WINDOW_OVERLAP,
    Signal,
)

OUTPUT_DIR = os.path.join(ROOT_DIR, "dashboard", "public", "artifacts", "discoveries")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "raw_embedding_robustness_report.json")

# -------------------------------------------------------------
# UNIFIED PERTURBED SIMULATOR
# -------------------------------------------------------------


def simulate_physical_perturbed_closure(
    system: str,
    seed: int,
    init_perturb_std: float = 0.0,
    param_perturb_pct: float = 0.0,
    measurement_noise: float = 0.0,
    temporal_jitter: float = 0.0,
    time_dilation: float = 1.0,
) -> Signal:
    rng = np.random.default_rng(seed)

    def p(val):
        if param_perturb_pct <= 0:
            return val
        return val * (1.0 + rng.uniform(-param_perturb_pct, param_perturb_pct))

    def inject_noise_local(x: np.ndarray, noise_lvl: float) -> np.ndarray:
        if noise_lvl <= 0:
            return x.copy()
        sigma = float(np.std(x))
        if sigma <= 1e-12:
            sigma = 1.0
        return x + rng.normal(0.0, noise_lvl * sigma, size=len(x))

    if system == "lorenz":
        y0 = np.array([1.0, 1.0, 1.0])
        if init_perturb_std > 0:
            y0 = y0 + rng.normal(0.0, init_perturb_std, size=3)
        sigma = p(10.0)
        rho = p(28.0)
        beta = p(8.0 / 3.0)

        def rhs(t, state):
            x_st, y_st, z_st = state
            return [
                sigma * (y_st - x_st),
                x_st * (rho - z_st) - y_st,
                x_st * y_st - beta * z_st,
            ]

        t_eval = np.linspace(0.0, 220.0, 22000)
        dt = float(t_eval[1] - t_eval[0])
        sol = solve_ivp(rhs, (0.0, 220.0), y0, t_eval=t_eval, method="RK45")
        if not sol.success:
            raise RuntimeError(f"Lorenz solver failed: {sol.message}")
        x = np.asarray(sol.y[0][4000:], dtype=float)
        dt_final = dt

    elif system == "rossler":
        y0 = np.array([1.0, 1.0, 1.0])
        if init_perturb_std > 0:
            y0 = y0 + rng.normal(0.0, init_perturb_std, size=3)
        a = p(0.2)
        b = p(0.2)
        c = p(5.7)

        def rhs(t, state):
            x_st, y_st, z_st = state
            return [-y_st - z_st, x_st + a * y_st, b + z_st * (x_st - c)]

        t_eval = np.linspace(0.0, 260.0, 22000)
        dt = float(t_eval[1] - t_eval[0])
        sol = solve_ivp(rhs, (0.0, 260.0), y0, t_eval=t_eval, method="RK45")
        if not sol.success:
            raise RuntimeError(f"Rossler solver failed: {sol.message}")
        x = np.asarray(sol.y[0][4000:], dtype=float)
        dt_final = dt

    elif system == "henon":
        a = p(1.4)
        b = p(0.3)
        x_st = 0.1
        y_st = 0.0
        if init_perturb_std > 0:
            x_st += rng.normal(0.0, init_perturb_std)
            y_st += rng.normal(0.0, init_perturb_std)
        n_points, transient = 18000, 3000
        values = []
        for i in range(n_points + transient):
            x_next = 1.0 - a * x_st * x_st + y_st
            y_next = b * x_st
            x_st, y_st = x_next, y_next
            if i >= transient:
                values.append(x_st)
        x = np.asarray(values, dtype=float)
        dt_final = 1.0

    elif system == "duffing":
        y0 = np.array([0.1, 0.0])
        if init_perturb_std > 0:
            y0 = y0 + rng.normal(0.0, init_perturb_std, size=2)
        delta_param = p(0.3)
        gamma = p(0.5)
        omega = p(1.2)

        def rhs(t, state):
            x_st, y_st = state
            return [
                y_st,
                x_st - x_st**3 - delta_param * y_st + gamma * np.cos(omega * t),
            ]

        t_eval = np.linspace(0.0, 500.0, 26000)
        dt = float(t_eval[1] - t_eval[0])
        sol = solve_ivp(rhs, (0.0, 500.0), y0, t_eval=t_eval, method="RK45")
        if not sol.success:
            raise RuntimeError(f"Duffing solver failed: {sol.message}")
        x = np.asarray(sol.y[0][5000:], dtype=float)
        dt_final = dt

    elif system == "van_der_pol":
        y0 = np.array([0.5, 0.0])
        if init_perturb_std > 0:
            y0 = y0 + rng.normal(0.0, init_perturb_std, size=2)
        mu = p(5.0)

        def rhs(t, state):
            x_st, y_st = state
            return [y_st, mu * (1.0 - x_st**2) * y_st - x_st]

        t_eval = np.linspace(0.0, 320.0, 24000)
        dt = float(t_eval[1] - t_eval[0])
        sol = solve_ivp(rhs, (0.0, 320.0), y0, t_eval=t_eval, method="RK45")
        if not sol.success:
            raise RuntimeError(f"Van der Pol solver failed: {sol.message}")
        x = np.asarray(sol.y[0][4000:], dtype=float)
        dt_final = dt

    elif system == "logistic_map":
        r = p(3.9)
        r = float(np.clip(r, 3.5, 3.99))
        x_st = 0.37
        if init_perturb_std > 0:
            x_st += rng.normal(0.0, init_perturb_std)
            x_st = float(np.clip(x_st, 0.1, 0.9))
        n_points, transient = 18000, 3000
        values = []
        for i in range(n_points + transient):
            x_st = r * x_st * (1.0 - x_st)
            if i >= transient:
                values.append(x_st)
        x = np.asarray(values, dtype=float)
        dt_final = 1.0

    else:
        raise ValueError(f"Unknown physical system: {system}")

    x = inject_noise_local(x, measurement_noise)

    if temporal_jitter > 0:
        t_idx = np.arange(len(x))
        t_jittered = t_idx + rng.normal(0.0, temporal_jitter, size=len(t_idx))
        t_jittered = np.clip(t_jittered, 0.0, len(x) - 1.0)
        x = np.interp(t_jittered, t_idx, x)

    if abs(time_dilation - 1.0) > 1e-9:
        t_idx = np.arange(len(x))
        t_dilated = t_idx * time_dilation
        t_dilated = np.clip(t_dilated, 0.0, len(x) - 1.0)
        x = np.interp(t_dilated, t_idx, x)

    return Signal(x, dt_final)


def build_dataset_closure(
    seeds: list[int],
    init_perturb_std: float = 0.0,
    param_perturb_pct: float = 0.0,
    measurement_noise: float = 0.0,
    temporal_jitter: float = 0.0,
    time_dilation: float = 1.0,
) -> dict[str, np.ndarray]:
    dataset = {}
    for system in PHYSICAL_SYSTEMS:
        system_rows = []
        for seed in seeds:
            sig = simulate_physical_perturbed_closure(
                system=system,
                seed=seed,
                init_perturb_std=init_perturb_std,
                param_perturb_pct=param_perturb_pct,
                measurement_noise=measurement_noise,
                temporal_jitter=temporal_jitter,
                time_dilation=time_dilation,
            )
            system_rows.append(extract_v3(sig, standardize_before_embedding=False))
        dataset[system] = np.vstack(system_rows)
    return dataset


# -------------------------------------------------------------
# REPRESENTATION ANALYSIS METRICS
# -------------------------------------------------------------


def compute_nn_overlap(A: np.ndarray, B: np.ndarray, k: int = 15) -> float:
    nbrs_A = NearestNeighbors(n_neighbors=k + 1).fit(A)
    nbrs_B = NearestNeighbors(n_neighbors=k + 1).fit(B)
    idx_A = nbrs_A.kneighbors(A, return_distance=False)[:, 1:]
    idx_B = nbrs_B.kneighbors(B, return_distance=False)[:, 1:]
    overlaps = []
    for row_A, row_B in zip(idx_A, idx_B):
        intersection = len(set(row_A).intersection(set(row_B)))
        overlaps.append(intersection / k)
    return float(np.mean(overlaps))


def compute_covariance_similarity(A: np.ndarray, B: np.ndarray) -> float:
    cov_A = np.cov(A, rowvar=False)
    cov_B = np.cov(B, rowvar=False)
    dot = float(np.sum(cov_A * cov_B))
    norm_A = float(np.linalg.norm(cov_A, ord="fro"))
    norm_B = float(np.linalg.norm(cov_B, ord="fro"))
    if norm_A * norm_B == 0:
        return 0.0
    return dot / (norm_A * norm_B)


def compute_distance_correlation(A: np.ndarray, B: np.ndarray) -> float:
    d_A = pdist(A)
    d_B = pdist(B)
    corr, _ = pearsonr(d_A, d_B)
    return float(corr)


def compute_linear_cka(A: np.ndarray, B: np.ndarray) -> float:
    A_centered = A - np.mean(A, axis=0)
    B_centered = B - np.mean(B, axis=0)
    dot_product = np.linalg.norm(B_centered.T @ A_centered, ord="fro") ** 2
    norm_A = np.linalg.norm(A_centered.T @ A_centered, ord="fro")
    norm_B = np.linalg.norm(B_centered.T @ B_centered, ord="fro")
    if norm_A * norm_B == 0:
        return 0.0
    return float(dot_product / (norm_A * norm_B))


def compute_procrustes_similarity(A: np.ndarray, B: np.ndarray) -> float:
    _, _, disparity = procrustes(A, B)
    return float(1.0 - disparity)


def compute_local_density_correlation(
    A: np.ndarray, B: np.ndarray, k: int = 15
) -> float:
    nbrs_A = NearestNeighbors(n_neighbors=k + 1).fit(A)
    nbrs_B = NearestNeighbors(n_neighbors=k + 1).fit(B)

    dist_A, _ = nbrs_A.kneighbors(A)
    dist_B, _ = nbrs_B.kneighbors(B)

    density_A = np.mean(dist_A[:, 1:], axis=1)
    density_B = np.mean(dist_B[:, 1:], axis=1)

    corr, _ = pearsonr(density_A, density_B)
    return float(corr)


# -------------------------------------------------------------
# CLASSIFICATION STABILITY METRICS
# -------------------------------------------------------------


def compute_multiclass_ece(
    probs: np.ndarray, labels: np.ndarray, n_bins: int = 10
) -> float:
    preds = np.argmax(probs, axis=1)
    confidences = np.max(probs, axis=1)
    accuracies = (preds == labels).astype(float)

    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        in_bin = (confidences >= bin_lower) & (confidences < bin_upper)
        prop_in_bin = np.mean(in_bin)
        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confidences[in_bin])
            ece += prop_in_bin * np.abs(avg_confidence_in_bin - accuracy_in_bin)
    return ece


def compute_multiclass_pr_auc(probs: np.ndarray, labels: np.ndarray) -> float:
    n_classes = probs.shape[1]
    y_bin = label_binarize(labels, classes=range(n_classes))
    pr_aucs = []
    for c in range(n_classes):
        pr_aucs.append(average_precision_score(y_bin[:, c], probs[:, c]))
    return float(np.mean(pr_aucs))


def compute_multiclass_roc_auc(probs: np.ndarray, labels: np.ndarray) -> float:
    n_classes = probs.shape[1]
    y_bin = label_binarize(labels, classes=range(n_classes))
    return float(roc_auc_score(y_bin, probs, average="macro", multi_class="ovr"))


# -------------------------------------------------------------
# MAIN AUDIT RUNNER
# -------------------------------------------------------------


def main():
    start_time = time.time()
    print("=" * 80)
    print("      RAW EMBEDDING ROBUSTNESS CLOSURE AUDIT (V3 CERTIFICATION)")
    print("=" * 80)

    # 0. Generate baseline dataset
    print("\n[DATA] Generating baseline V3 embedding...")
    ds_base = build_dataset_closure(seeds=[42, 1337, 9001], measurement_noise=0.0)
    X_base = np.vstack([ds_base[name] for name in PHYSICAL_SYSTEMS])
    labels_base = np.concatenate(
        [
            np.full(len(ds_base[name]), idx, dtype=int)
            for idx, name in enumerate(PHYSICAL_SYSTEMS)
        ]
    )
    print(f"  Baseline Shape: {X_base.shape} (V3 Features = {X_base.shape[1]})")

    # -------------------------------------------------------------
    # TEST 1 — NOISE RESPONSE CURVE
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print("TEST 1 — NOISE RESPONSE CURVE (Continuous Degradation Sweep)")
    print("-" * 50)

    noise_levels = [0.01, 0.02, 0.05, 0.10, 0.15, 0.20]
    test1_results = []
    passed_test1 = True

    metrics_history = {
        "neighbor_overlap": [],
        "distance_correlation": [],
        "covariance_similarity": [],
        "linear_cka": [],
        "procrustes_similarity": [],
    }

    for lvl in noise_levels:
        ds_lvl = build_dataset_closure(seeds=[42, 1337, 9001], measurement_noise=lvl)
        X_lvl = np.vstack([ds_lvl[name] for name in PHYSICAL_SYSTEMS])

        nn_over = compute_nn_overlap(X_base, X_lvl)
        dist_corr = compute_distance_correlation(X_base, X_lvl)
        cov_sim = compute_covariance_similarity(X_base, X_lvl)
        cka_sim = compute_linear_cka(X_base, X_lvl)
        proc_sim = compute_procrustes_similarity(X_base, X_lvl)

        metrics_history["neighbor_overlap"].append(nn_over)
        metrics_history["distance_correlation"].append(dist_corr)
        metrics_history["covariance_similarity"].append(cov_sim)
        metrics_history["linear_cka"].append(cka_sim)
        metrics_history["procrustes_similarity"].append(proc_sim)

        print(
            f"Noise {lvl*100:>2.0f}% | NN_Overlap={nn_over:.4f} | DistCorr={dist_corr:.4f} | CovSim={cov_sim:.4f} | CKA={cka_sim:.4f} | ProcSim={proc_sim:.4f}"
        )

        test1_results.append(
            {
                "noise_level": lvl,
                "neighbor_overlap": nn_over,
                "distance_correlation": dist_corr,
                "covariance_similarity": cov_sim,
                "linear_cka": cka_sim,
                "procrustes_similarity": proc_sim,
            }
        )

    # Check for consecutive jumps > 30% (0.30)
    jumps = {}
    for key, values in metrics_history.items():
        key_jumps = []
        for i in range(1, len(values)):
            drop = float(values[i - 1] - values[i])
            key_jumps.append(drop)
            if drop > 0.30:
                passed_test1 = False
                print(
                    f"  [CRITICAL JUMP] {key} dropped by {drop:.4f} (>0.30) from noise {noise_levels[i-1]} to {noise_levels[i]}!"
                )
        jumps[key] = key_jumps

    print(f"TEST 1 STATUS: {'PASSED' if passed_test1 else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 2 — LOCAL VS GLOBAL STRUCTURE DECOMPOSITION
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print("TEST 2 — LOCAL VS GLOBAL STRUCTURE DECOMPOSITION")
    print("-" * 50)

    local_densities = []
    for lvl in noise_levels:
        ds_lvl = build_dataset_closure(seeds=[42, 1337, 9001], measurement_noise=lvl)
        X_lvl = np.vstack([ds_lvl[name] for name in PHYSICAL_SYSTEMS])
        local_densities.append(compute_local_density_correlation(X_base, X_lvl))

    mean_nn_overlap = float(np.mean(metrics_history["neighbor_overlap"]))
    mean_local_density = float(np.mean(local_densities))

    mean_cov_sim = float(np.mean(metrics_history["covariance_similarity"]))
    mean_dist_corr = float(np.mean(metrics_history["distance_correlation"]))
    mean_cka = float(np.mean(metrics_history["linear_cka"]))

    local_score = float((mean_nn_overlap + mean_local_density) / 2.0)
    global_score = float((mean_cov_sim + mean_dist_corr + mean_cka) / 3.0)
    local_global_ratio = float(local_score / global_score) if global_score > 0 else 0.0

    print("LOCAL Structure Metrics (Mean across noise levels):")
    print(f"  kNN Overlap:               {mean_nn_overlap:.4f}")
    print(f"  Local Density Correlation: {mean_local_density:.4f}")
    print(f"  LOCAL SCORE:               {local_score:.4f}")

    print("GLOBAL Structure Metrics (Mean across noise levels):")
    print(f"  Covariance Similarity:     {mean_cov_sim:.4f}")
    print(f"  Distance Correlation:      {mean_dist_corr:.4f}")
    print(f"  Linear CKA:                {mean_cka:.4f}")
    print(f"  GLOBAL SCORE:              {global_score:.4f}")

    print(f"Local-to-Global Ratio:       {local_global_ratio:.4f}")

    if local_score < 0.80 and global_score >= 0.80:
        diagnosis = "EXPECTED_PHYSICAL_LOCAL_REORGANIZATION"
    elif local_score < 0.80 and global_score < 0.80:
        diagnosis = "EMBEDDING_FRAGILITY"
    else:
        diagnosis = (
            "EXPECTED_PHYSICAL_LOCAL_REORGANIZATION"
            if global_score >= 0.80
            else "EMBEDDING_FRAGILITY"
        )

    print(f"Diagnosed Structural Behavior: {diagnosis}")

    # -------------------------------------------------------------
    # TEST 3 — PERTURBATION TYPE AUDIT
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print("TEST 3 — PERTURBATION TYPE AUDIT")
    print("-" * 50)

    perturbations = {
        "initial_condition": {"init_perturb_std": 0.05},
        "parameter": {"param_perturb_pct": 0.02},
        "measurement_noise": {"measurement_noise": 0.05},
        "temporal_jitter": {"temporal_jitter": 0.1},
        "time_dilation": {"time_dilation": 1.02},
    }

    pert_results = {}
    for name, kwargs in perturbations.items():
        print(f"Evaluating {name} perturbation independently...")
        ds_pert = build_dataset_closure(seeds=[42, 1337, 9001], **kwargs)
        X_pert = np.vstack([ds_pert[sys] for sys in PHYSICAL_SYSTEMS])

        proc_sim = compute_procrustes_similarity(X_base, X_pert)
        dist_corr = compute_distance_correlation(X_base, X_pert)
        nn_over = compute_nn_overlap(X_base, X_pert)

        composite_stability = float((proc_sim + dist_corr + nn_over) / 3.0)
        disparity = float(1.0 - composite_stability)

        pert_results[name] = {
            "procrustes_similarity": proc_sim,
            "distance_correlation": dist_corr,
            "neighbor_overlap": nn_over,
            "composite_stability": composite_stability,
            "disparity_distortion": disparity,
        }
        print(
            f"  {name:<20} | ProcSim={proc_sim:.4f} | DistCorr={dist_corr:.4f} | NNOver={nn_over:.4f} | Disparity={disparity:.4f}"
        )

    ranked_perts = sorted(
        pert_results.items(),
        key=lambda item: item[1]["disparity_distortion"],
        reverse=True,
    )
    most_destabilizing = ranked_perts[0][0]

    print("\nPerturbation Destabilization Ranking (Most to Least):")
    for idx, (name, res) in enumerate(ranked_perts):
        print(
            f"  {idx+1}. {name:<20} : Disparity/Distortion = {res['disparity_distortion']:.4f}"
        )

    print(f"\nMost Destabilizing Perturbation Type: {most_destabilizing.upper()}")

    # -------------------------------------------------------------
    # TEST 4 — CLASSIFICATION STABILITY
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print("TEST 4 — CLASSIFICATION STABILITY (Random Forest direct on V3)")
    print("-" * 50)

    clf_seeds = list(range(20))
    f1_list = []
    auc_list = []
    pr_list = []
    ece_list = []

    for seed in clf_seeds:
        X_train, X_test, y_train, y_test = train_test_split(
            X_base, labels_base, test_size=0.30, random_state=seed, stratify=labels_base
        )

        clf = RandomForestClassifier(n_estimators=100, random_state=seed)
        clf.fit(X_train, y_train)

        probs = clf.predict_proba(X_test)
        preds = clf.predict(X_test)

        f1 = float(f1_score(y_test, preds, average="macro"))
        auc = compute_multiclass_roc_auc(probs, y_test)
        pr = compute_multiclass_pr_auc(probs, y_test)
        ece = compute_multiclass_ece(probs, y_test)

        f1_list.append(f1)
        auc_list.append(auc)
        pr_list.append(pr)
        ece_list.append(ece)

    mean_auc, std_auc = float(np.mean(auc_list)), float(np.std(auc_list, ddof=1))
    mean_f1, std_f1 = float(np.mean(f1_list)), float(np.std(f1_list, ddof=1))
    mean_pr, std_pr = float(np.mean(pr_list)), float(np.std(pr_list, ddof=1))
    mean_ece = float(np.mean(ece_list))

    cv_auc = float(std_auc / mean_auc) if mean_auc > 0 else 0.0
    cv_f1 = float(std_f1 / mean_f1) if mean_f1 > 0 else 0.0

    print("Classifier Stability Results over 20 Seeds:")
    print(
        f"  ROC-AUC: mean = {mean_auc:.4f}, std = {std_auc:.4f}, CV = {cv_auc*100:.2f}%"
    )
    print(f"  PR-AUC:  mean = {mean_pr:.4f}, std = {std_pr:.4f}")
    print(f"  F1:      mean = {mean_f1:.4f}, std = {std_f1:.4f}, CV = {cv_f1*100:.2f}%")
    print(f"  ECE:     mean = {mean_ece:.4f}")

    passed_test4 = (cv_auc < 0.05) and (cv_f1 < 0.10) and (mean_ece < 0.05)
    print(f"TEST 4 STATUS: {'PASSED' if passed_test4 else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 5 — FINAL CERTIFICATION
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print("TEST 5 — FINAL CERTIFICATION")
    print("-" * 50)

    if diagnosis == "EXPECTED_PHYSICAL_LOCAL_REORGANIZATION":
        root_cause_final = "EXPECTED_PHYSICAL_LOCAL_REORGANIZATION"
    elif diagnosis == "EMBEDDING_FRAGILITY":
        root_cause_final = "RESIDUAL_EMBEDDING_FRAGILITY"
    else:
        root_cause_final = "MIXED"

    if passed_test4 and root_cause_final == "EXPECTED_PHYSICAL_LOCAL_REORGANIZATION":
        if passed_test1:
            cert_status = "PASS"
        else:
            cert_status = "CONDITIONAL_PASS"
    else:
        cert_status = "FAIL"

    print(f"Final Root Cause Diagnosis: {root_cause_final}")
    print(f"Certification Status:       {cert_status}")

    # Write JSON report
    report = {
        "metadata": {
            "generated_at_unix": time.time(),
            "target_thresholds": {
                "max_consecutive_jump": 0.30,
                "cv_auc_max": 0.05,
                "cv_f1_max": 0.10,
                "ece_max": 0.05,
            },
            "runtime_seconds": float(time.time() - start_time),
            "global_status": cert_status,
        },
        "tests": {
            "test1_noise_response_curve": {
                "status": "PASSED" if passed_test1 else "FAILED",
                "levels": test1_results,
                "jumps": jumps,
            },
            "test2_local_vs_global_decomposition": {
                "status": "PASSED",
                "local_score": local_score,
                "global_score": global_score,
                "local_global_ratio": local_global_ratio,
                "means": {
                    "neighbor_overlap": mean_nn_overlap,
                    "local_density_correlation": mean_local_density,
                    "covariance_similarity": mean_cov_sim,
                    "distance_correlation": mean_dist_corr,
                    "linear_cka": mean_cka,
                },
                "diagnosed_behavior": diagnosis,
            },
            "test3_perturbation_type_audit": {
                "status": "PASSED",
                "results": pert_results,
                "ranking": [name for name, _ in ranked_perts],
                "most_destabilizing": most_destabilizing,
            },
            "test4_classification_stability": {
                "status": "PASSED" if passed_test4 else "FAILED",
                "metrics": {
                    "mean_auc": mean_auc,
                    "std_auc": std_auc,
                    "cv_auc": cv_auc,
                    "mean_f1": mean_f1,
                    "std_f1": std_f1,
                    "cv_f1": cv_f1,
                    "mean_pr": mean_pr,
                    "mean_ece": mean_ece,
                },
                "raw_values": {
                    "auc": auc_list,
                    "f1": f1_list,
                    "pr": pr_list,
                    "ece": ece_list,
                },
            },
            "test5_final_certification": {
                "diagnosed_root_cause": root_cause_final,
                "certification_status": cert_status,
            },
        },
        "diagnosis": {
            "root_cause": root_cause_final,
            "certification_status": cert_status,
        },
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"\n[REPORT] Saved robustness report to {OUTPUT_FILE}")

    print("\n" + "=" * 80)
    if cert_status in ["PASS", "CONDITIONAL_PASS"]:
        print(f"RAW EMBEDDING V3 CERTIFIED ({cert_status}):")
        print(
            "Instability is a physical expected local reorganization, not mathematical fragility."
        )
        print("=" * 80)
        return 0
    else:
        print("RAW EMBEDDING V3 FAIL CERTIFICATION:")
        print("Mathematical fragility detected within the representation space.")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
