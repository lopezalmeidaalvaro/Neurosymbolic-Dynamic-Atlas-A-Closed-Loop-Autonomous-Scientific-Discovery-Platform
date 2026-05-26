"""
core/validation/embedding_intrinsic_stability_audit.py
======================================================
Rigorous scientific audit of the intrinsic stability of V3 Feature Space
to isolate the cause of latent manifold geometric instability (V3 vs UMAP).
"""

from __future__ import annotations

import json
import os
import sys
import time
import traceback
from typing import Callable

import numpy as np
import umap
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, pairwise_distances
from sklearn.manifold import TSNE, trustworthiness
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import pdist
from scipy.stats import pearsonr
from scipy.spatial import procrustes
from scipy.integrate import solve_ivp

# Ensure ROOT_DIR is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

# Import baseline functions and constants
from core.validation.cross_system_generalization_tests import (
    simulate_physical,
    extract_v3,
    compute_distance_correlation,
    PHYSICAL_SYSTEMS,
    V3_KEYS,
)

OUTPUT_DIR = os.path.join(ROOT_DIR, "dashboard", "public", "artifacts", "discoveries")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "embedding_intrinsic_stability_report.json")

# UMAP configuration
OPT_NN = 50
OPT_MD = 0.5
OPT_MET = "correlation"

# Raw Embedding Stability Thresholds (Test 1 & 2)
THRES_DIST_CORR = 0.90
THRES_NEIGHBOR_OVERLAP = 0.90
THRES_COV_SIM = 0.85
THRES_COMPOSITE_PERSISTENCE = 0.85


class Signal:
    def __init__(self, values: np.ndarray, dt: float):
        self.values = values
        self.dt = dt


# -------------------------------------------------------------
# DYNAMIC PERTURBED SIMULATOR (TRUE RESAMPLING)
# -------------------------------------------------------------


def _inject_noise_local(x: np.ndarray, noise: float, seed: int) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if noise <= 0:
        return x.copy()
    rng = np.random.default_rng(seed)
    sigma = float(np.std(x))
    return x + rng.normal(0.0, noise * sigma, size=len(x))


def _simulate_ode_local(
    rhs: Callable,
    y0: list[float],
    t_end: float,
    n_points: int,
    transient: int,
    noise: float,
    seed: int,
) -> Signal:
    t_eval = np.linspace(0.0, t_end, n_points)
    dt = float(t_eval[1] - t_eval[0])
    sol = solve_ivp(rhs, (0.0, t_end), y0, t_eval=t_eval, method="RK45")
    if not sol.success:
        raise RuntimeError(f"ODE solver failed: {sol.message}")
    x = np.asarray(sol.y[0][transient:], dtype=float)
    return Signal(_inject_noise_local(x, noise, seed), dt)


def _simulate_henon_local(
    x0: float,
    y0: float,
    a: float,
    b: float,
    noise: float,
    seed: int,
    n_points: int = 18000,
    transient: int = 3000,
) -> Signal:
    x, y = x0, y0
    values = []
    for i in range(n_points + transient):
        x_next = 1.0 - a * x * x + y
        y_next = b * x
        x, y = x_next, y_next
        if i >= transient:
            values.append(x)
    return Signal(
        _inject_noise_local(np.asarray(values, dtype=float), noise, seed), 1.0
    )


def _simulate_logistic_map_local(
    x0: float,
    r: float,
    noise: float,
    seed: int,
    n_points: int = 18000,
    transient: int = 3000,
) -> Signal:
    x = x0
    values = []
    for i in range(n_points + transient):
        x = r * x * (1.0 - x)
        if i >= transient:
            values.append(x)
    return Signal(
        _inject_noise_local(np.asarray(values, dtype=float), noise, seed), 1.0
    )


def simulate_physical_perturbed(system: str, seed: int, perturb: bool = True) -> Signal:
    rng = np.random.default_rng(seed)

    if not perturb:
        # Precision replication of clean baseline trajectories
        return simulate_physical(system, noise=0.0, seed=seed)

    initial_perturb_std = 0.05
    param_perturb_pct = 0.02
    noise = 0.01  # 1% physical noise

    def p(val):
        return val * (1.0 + rng.uniform(-param_perturb_pct, param_perturb_pct))

    if system == "lorenz":
        y0 = [1.0, 1.0, 1.0] + rng.normal(0.0, initial_perturb_std, size=3)
        sigma = p(10.0)
        rho = p(28.0)
        beta = p(8.0 / 3.0)

        def rhs(t, state):
            x, y, z = state
            return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]

        return _simulate_ode_local(rhs, y0, 220.0, 22000, 4000, noise, seed)

    elif system == "rossler":
        y0 = [1.0, 1.0, 1.0] + rng.normal(0.0, initial_perturb_std, size=3)
        a = p(0.2)
        b = p(0.2)
        c = p(5.7)

        def rhs(t, state):
            x, y, z = state
            return [-y - z, x + a * y, b + z * (x - c)]

        return _simulate_ode_local(rhs, y0, 260.0, 22000, 4000, noise, seed)

    elif system == "henon":
        x0 = 0.1 + rng.normal(0.0, initial_perturb_std)
        y0 = 0.0 + rng.normal(0.0, initial_perturb_std)
        a = p(1.4)
        b = p(0.3)
        return _simulate_henon_local(x0, y0, a, b, noise, seed)

    elif system == "duffing":
        y0 = [0.1, 0.0] + rng.normal(0.0, initial_perturb_std, size=2)
        delta = p(0.3)
        gamma = p(0.5)
        omega = p(1.2)

        def rhs(t, state):
            x, y = state
            return [y, x - x**3 - delta * y + gamma * np.cos(omega * t)]

        return _simulate_ode_local(rhs, y0, 500.0, 26000, 5000, noise, seed)

    elif system == "van_der_pol":
        y0 = [0.5, 0.0] + rng.normal(0.0, initial_perturb_std, size=2)
        mu = p(5.0)

        def rhs(t, state):
            x, y = state
            return [y, mu * (1.0 - x**2) * y - x]

        return _simulate_ode_local(rhs, y0, 320.0, 24000, 4000, noise, seed)

    elif system == "logistic_map":
        x0 = 0.37 + rng.normal(0.0, initial_perturb_std)
        x0 = float(np.clip(x0, 0.1, 0.9))
        r = p(3.9)
        r = float(np.clip(r, 3.5, 3.99))
        return _simulate_logistic_map_local(x0, r, noise, seed)

    else:
        raise ValueError(f"Unknown physical system: {system}")


def build_dataset_perturbed(
    seeds: list[int], perturb: bool = True, noise_override: float = None
) -> dict[str, np.ndarray]:
    dataset = {}
    for system in PHYSICAL_SYSTEMS:
        system_rows = []
        for seed in seeds:
            if noise_override is not None:
                # Use standard baseline simulation but inject custom noise
                signal = simulate_physical(system, noise=noise_override, seed=seed)
            else:
                signal = simulate_physical_perturbed(system, seed=seed, perturb=perturb)
            system_rows.append(extract_v3(signal, standardize_before_embedding=False))
        dataset[system] = np.vstack(system_rows)
    return dataset


# -------------------------------------------------------------
# MATHEMATICAL REPRESENTATION COMPARISON METRICS
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


def compute_intrinsic_dimensionality(x: np.ndarray) -> float:
    cov = np.cov(x, rowvar=False)
    eigvals = np.linalg.eigvalsh(cov)
    eigvals = eigvals[eigvals > 1e-10]
    if len(eigvals) == 0:
        return 0.0
    sum_eig = np.sum(eigvals)
    sum_eig_sq = np.sum(eigvals**2)
    if sum_eig_sq == 0:
        return 0.0
    return float((sum_eig**2) / sum_eig_sq)


def compute_cosine_preservation(A: np.ndarray, B: np.ndarray) -> float:
    norm_A = np.linalg.norm(A, axis=1, keepdims=True)
    norm_A[norm_A < 1e-10] = 1.0
    A_norm = A / norm_A

    norm_B = np.linalg.norm(B, axis=1, keepdims=True)
    norm_B[norm_B < 1e-10] = 1.0
    B_norm = B / norm_B

    cos_A = A_norm @ A_norm.T
    cos_B = B_norm @ B_norm.T

    iu = np.triu_indices(len(A), k=1)
    corr, _ = pearsonr(cos_A[iu], cos_B[iu])
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


# -------------------------------------------------------------
# MAIN AUDIT EXECUTION
# -------------------------------------------------------------


def main():
    start_time = time.time()
    print("=" * 80)
    print("      EMBEDDING INTRINSIC STABILITY AUDIT: V3 VS UMAP RESPONSIBILITY")
    print("=" * 80)

    # 0. Load physical baseline dataset (seeds = [42, 1337, 9001], no perturbations)
    print("\n[DATA] Generating baseline V3 embedding...")
    baseline_dataset = build_dataset_perturbed([42, 1337, 9001], perturb=False)

    X_base = np.vstack([baseline_dataset[name] for name in PHYSICAL_SYSTEMS])
    labels_base = np.concatenate(
        [
            np.full(len(baseline_dataset[name]), idx, dtype=int)
            for idx, name in enumerate(PHYSICAL_SYSTEMS)
        ]
    )

    N_samples = X_base.shape[0]
    print(f"  Baseline Shape: {X_base.shape} (V3 Features = {X_base.shape[1]})")
    print(f"  Number of physical categories: {len(PHYSICAL_SYSTEMS)}")

    # -------------------------------------------------------------
    # TEST 1 — RAW EMBEDDING STABILITY
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print("TEST 1 — RAW EMBEDDING STABILITY (Direct V3 Analysis)")
    print("-" * 50)

    # We evaluate directly on raw V3 embeddings across:
    # A) Seed perturbations: Seed 42 vs 1337 vs 9001 isolated
    # B) Physical noise levels: 1%, 5%, 10%, 20%

    # A) Seed comparisons
    dataset_s42 = build_dataset_perturbed([42], perturb=False)
    X_s42 = np.vstack([dataset_s42[name] for name in PHYSICAL_SYSTEMS])

    dataset_s1337 = build_dataset_perturbed([1337], perturb=False)
    X_s1337 = np.vstack([dataset_s1337[name] for name in PHYSICAL_SYSTEMS])

    dataset_s9001 = build_dataset_perturbed([9001], perturb=False)
    X_s9001 = np.vstack([dataset_s9001[name] for name in PHYSICAL_SYSTEMS])

    dist_s42 = pdist(X_s42)
    dist_s1337 = pdist(X_s1337)
    dist_s9001 = pdist(X_s9001)

    seed_dist_corr = float(
        (pearsonr(dist_s42, dist_s1337)[0] + pearsonr(dist_s42, dist_s9001)[0]) / 2.0
    )
    seed_nn_overlap = float(
        (compute_nn_overlap(X_s42, X_s1337) + compute_nn_overlap(X_s42, X_s9001)) / 2.0
    )
    seed_cov_sim = float(
        (
            compute_covariance_similarity(X_s42, X_s1337)
            + compute_covariance_similarity(X_s42, X_s9001)
        )
        / 2.0
    )

    print("Seed Perturbation Results (Raw V3):")
    print(f"  Distance Correlation: {seed_dist_corr:.4f}")
    print(f"  Neighbor Overlap:     {seed_nn_overlap:.4f}")
    print(f"  Covariance Similarity:{seed_cov_sim:.4f}")

    # B) Physical noise levels (compared to baseline)
    noise_levels = [0.01, 0.05, 0.10, 0.20]
    noise_results = []

    dist_base = pdist(X_base)
    base_dim = compute_intrinsic_dimensionality(X_base)
    print(
        f"\nIntrinsic Dimensionality (Participation Ratio) of Baseline V3: {base_dim:.4f}"
    )

    for noise in noise_levels:
        dataset_noise = build_dataset_perturbed(
            [42, 1337, 9001], perturb=False, noise_override=noise
        )
        X_noise = np.vstack([dataset_noise[name] for name in PHYSICAL_SYSTEMS])

        dist_noise = pdist(X_noise)
        d_corr = float(pearsonr(dist_base, dist_noise)[0])
        nn_over = float(compute_nn_overlap(X_base, X_noise))
        cov_sim = float(compute_covariance_similarity(X_base, X_noise))
        cos_pres = float(compute_cosine_preservation(X_base, X_noise))
        noise_dim = compute_intrinsic_dimensionality(X_noise)

        noise_results.append(
            {
                "noise_level": noise,
                "distance_correlation": d_corr,
                "neighbor_overlap": nn_over,
                "covariance_similarity": cov_sim,
                "cosine_preservation": cos_pres,
                "intrinsic_dimensionality": noise_dim,
            }
        )
        print(
            f"Noise {noise*100:>2.0f}% | DistCorr={d_corr:.4f} | NN_Overlap={nn_over:.4f} | CovSim={cov_sim:.4f} | CosPres={cos_pres:.4f} | IntrinsicDim={noise_dim:.4f}"
        )

    mean_noise_dist_corr = float(
        np.mean([item["distance_correlation"] for item in noise_results])
    )
    mean_noise_nn_overlap = float(
        np.mean([item["neighbor_overlap"] for item in noise_results])
    )
    mean_noise_cov_sim = float(
        np.mean([item["covariance_similarity"] for item in noise_results])
    )

    # Overall Test 1 status
    passed_test1 = (
        seed_dist_corr >= THRES_DIST_CORR
        and seed_nn_overlap >= THRES_NEIGHBOR_OVERLAP
        and seed_cov_sim >= THRES_COV_SIM
        and mean_noise_dist_corr >= THRES_DIST_CORR
        and mean_noise_nn_overlap >= THRES_NEIGHBOR_OVERLAP
        and mean_noise_cov_sim >= THRES_COV_SIM
    )
    print(f"\nTEST 1 STATUS: {'PASSED' if passed_test1 else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 2 — EMBEDDING TOPOLOGY PERSISTENCE
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print("TEST 2 — EMBEDDING TOPOLOGY PERSISTENCE")
    print("-" * 50)

    # Compute representation alignment under seed changes and noise perturbations
    # Compare seed 42 vs seed 1337 raw embeddings
    _, _, disparity = procrustes(X_s42, X_s1337)
    proc_sim_seed = float(1.0 - disparity)
    mantel_seed = float(pearsonr(dist_s42, dist_s1337)[0])
    cka_seed = float(compute_linear_cka(X_s42, X_s1337))
    nn_seed = float(compute_nn_overlap(X_s42, X_s1337))
    composite_seed = float((proc_sim_seed + mantel_seed + cka_seed + nn_seed) / 4.0)

    print("Topology Persistence (Seed 42 vs 1337):")
    print(f"  Procrustes Similarity: {proc_sim_seed:.4f}")
    print(f"  Mantel Correlation:    {mantel_seed:.4f}")
    print(f"  CKA Similarity:        {cka_seed:.4f}")
    print(f"  NN Overlap (k=15):     {nn_seed:.4f}")
    print(f"  Composite Score:       {composite_seed:.4f}")

    # Compare baseline vs 5% noise embedding
    dataset_n5 = build_dataset_perturbed(
        [42, 1337, 9001], perturb=False, noise_override=0.05
    )
    X_n5 = np.vstack([dataset_n5[name] for name in PHYSICAL_SYSTEMS])
    dist_n5 = pdist(X_n5)

    _, _, disparity_n5 = procrustes(X_base, X_n5)
    proc_sim_n5 = float(1.0 - disparity_n5)
    mantel_n5 = float(pearsonr(dist_base, dist_n5)[0])
    cka_n5 = float(compute_linear_cka(X_base, X_n5))
    nn_n5 = float(compute_nn_overlap(X_base, X_n5))
    composite_n5 = float((proc_sim_n5 + mantel_n5 + cka_n5 + nn_n5) / 4.0)

    print("\nTopology Persistence (Baseline vs 5% Noise):")
    print(f"  Procrustes Similarity: {proc_sim_n5:.4f}")
    print(f"  Mantel Correlation:    {mantel_n5:.4f}")
    print(f"  CKA Similarity:        {cka_n5:.4f}")
    print(f"  NN Overlap (k=15):     {nn_n5:.4f}")
    print(f"  Composite Score:       {composite_n5:.4f}")

    mean_composite = float((composite_seed + composite_n5) / 2.0)
    passed_test2 = mean_composite >= THRES_COMPOSITE_PERSISTENCE
    print(f"\nMean Composite Topology Persistence: {mean_composite:.4f}")
    print(f"TEST 2 STATUS: {'PASSED' if passed_test2 else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 3 — TRUE RESAMPLING AUDIT
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print("TEST 3 — TRUE RESAMPLING AUDIT (Non-degenerate CIs)")
    print("-" * 50)

    resample_results = []
    resample_seeds = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]

    for i, seed in enumerate(resample_seeds):
        try:
            print(f"Generating perturbed resampling dataset {i+1}/10 (seed={seed})...")
            # Build perturbed trajectories (param, init-state, noise)
            r_dataset = build_dataset_perturbed([seed], perturb=True)

            x_r = np.vstack([r_dataset[name] for name in PHYSICAL_SYSTEMS])
            labels_r = np.concatenate(
                [
                    np.full(len(r_dataset[name]), idx, dtype=int)
                    for idx, name in enumerate(PHYSICAL_SYSTEMS)
                ]
            )

            # Extract standard optimal projection pipeline
            scaled_r = StandardScaler().fit_transform(x_r)
            pca_r = PCA(n_components=5, random_state=42)
            x_pca_r = pca_r.fit_transform(scaled_r)

            reducer = umap.UMAP(
                n_components=2,
                n_neighbors=OPT_NN,
                min_dist=OPT_MD,
                metric=OPT_MET,
                random_state=42,
                n_epochs=500,
            )
            x_umap_r = reducer.fit_transform(x_pca_r)

            sil = float(silhouette_score(x_umap_r, labels_r))
            trust = float(trustworthiness(x_pca_r, x_umap_r, n_neighbors=15))
            dcor = compute_distance_correlation(x_pca_r, x_umap_r)

            resample_results.append(
                {
                    "dataset_idx": i,
                    "seed": seed,
                    "silhouette": sil,
                    "trustworthiness": trust,
                    "distance_correlation": dcor,
                }
            )
            print(
                f"  Dataset {i+1:>2} | Sil={sil:.4f} | Trust={trust:.4f} | DCor={dcor:.4f}"
            )
        except Exception as e:
            print(f"  Error simulating resample dataset index {i+1}: {e}")
            traceback.print_exc()

    # Compute 95% Confidence Intervals
    r_sils = [item["silhouette"] for item in resample_results]
    r_trusts = [item["trustworthiness"] for item in resample_results]
    r_dcors = [item["distance_correlation"] for item in resample_results]

    mean_r_sil, std_r_sil = np.mean(r_sils), np.std(r_sils, ddof=1)
    mean_r_trust, std_r_trust = np.mean(r_trusts), np.std(r_trusts, ddof=1)
    mean_r_dcor, std_r_dcor = np.mean(r_dcors), np.std(r_dcors, ddof=1)

    # Student-t critical value for df=9, alpha=0.05 is 2.262
    t_critical = 2.262
    n_resamples = len(resample_results)

    ci_sil_lower = float(mean_r_sil - t_critical * (std_r_sil / np.sqrt(n_resamples)))
    ci_sil_upper = float(mean_r_sil + t_critical * (std_r_sil / np.sqrt(n_resamples)))

    ci_trust_lower = float(
        mean_r_trust - t_critical * (std_r_trust / np.sqrt(n_resamples))
    )
    ci_trust_upper = float(
        mean_r_trust + t_critical * (std_r_trust / np.sqrt(n_resamples))
    )

    ci_dcor_lower = float(
        mean_r_dcor - t_critical * (std_r_dcor / np.sqrt(n_resamples))
    )
    ci_dcor_upper = float(
        mean_r_dcor + t_critical * (std_r_dcor / np.sqrt(n_resamples))
    )

    print("\nData Resampling 95% Confidence Intervals (Perturbed Sim):")
    print(
        f"  Silhouette: mean = {mean_r_sil:.6f}, std = {std_r_sil:.6f}, 95% CI = [{ci_sil_lower:.6f}, {ci_sil_upper:.6f}]"
    )
    print(
        f"  Trustworthiness: mean = {mean_r_trust:.6f}, std = {std_r_trust:.6f}, 95% CI = [{ci_trust_lower:.6f}, {ci_trust_upper:.6f}]"
    )
    print(
        f"  Distance Corr: mean = {mean_r_dcor:.6f}, std = {std_r_dcor:.6f}, 95% CI = [{ci_dcor_lower:.6f}, {ci_dcor_upper:.6f}]"
    )

    # Verification criteria: intervals must be non-degenerate (std > 1e-6)
    passed_test3 = (
        std_r_sil > 1e-6
        and std_r_trust > 1e-6
        and std_r_dcor > 1e-6
        and ci_sil_lower >= 0.30
        and ci_trust_lower >= 0.95
        and ci_dcor_lower >= 0.80
    )
    print(f"TEST 3 STATUS: {'PASSED' if passed_test3 else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 4 — UMAP RESPONSIBILITY TEST
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print("TEST 4 — UMAP RESPONSIBILITY TEST")
    print("-" * 50)

    # Apply PCA, UMAP, and t-SNE on the clean baseline raw V3 embedding (X_base)
    # and on the 5% noise raw embedding (X_n5)

    scaled_base = StandardScaler().fit_transform(X_base)
    scaled_n5 = StandardScaler().fit_transform(X_n5)

    print("Fitting baseline projections...")
    pca_base = PCA(n_components=2, random_state=42).fit_transform(scaled_base)
    reducer_base = umap.UMAP(
        n_components=2,
        n_neighbors=OPT_NN,
        min_dist=OPT_MD,
        metric=OPT_MET,
        random_state=42,
        n_epochs=500,
    )
    umap_base = reducer_base.fit_transform(scaled_base)
    tsne_base = TSNE(n_components=2, random_state=42).fit_transform(scaled_base)

    print("Fitting 5% noise perturbed projections...")
    pca_n5 = PCA(n_components=2, random_state=42).fit_transform(scaled_n5)
    reducer_n5 = umap.UMAP(
        n_components=2,
        n_neighbors=OPT_NN,
        min_dist=OPT_MD,
        metric=OPT_MET,
        random_state=42,
        n_epochs=500,
    )
    umap_n5 = reducer_n5.fit_transform(scaled_n5)
    tsne_n5 = TSNE(n_components=2, random_state=42).fit_transform(scaled_n5)

    # Measure stability under noise for all spaces (Raw V3, PCA, UMAP, t-SNE)
    def compute_projection_stability(
        P_base: np.ndarray, P_pert: np.ndarray
    ) -> dict[str, float]:
        d_base = pdist(P_base)
        d_pert = pdist(P_pert)

        d_corr = float(pearsonr(d_base, d_pert)[0])
        nn_over = float(compute_nn_overlap(P_base, P_pert))
        _, _, disparity = procrustes(P_base, P_pert)
        proc_sim = float(1.0 - disparity)

        composite = float((d_corr + nn_over + proc_sim) / 3.0)
        return {
            "distance_correlation": d_corr,
            "neighbor_overlap": nn_over,
            "procrustes_similarity": proc_sim,
            "composite_stability": composite,
        }

    raw_stability = compute_projection_stability(X_base, X_n5)
    pca_stability = compute_projection_stability(pca_base, pca_n5)
    umap_stability = compute_projection_stability(umap_base, umap_n5)
    tsne_stability = compute_projection_stability(tsne_base, tsne_n5)

    print("\nProjections Stability under 5% physical noise:")
    print(
        f"  Raw V3 Embedding: Composite = {raw_stability['composite_stability']:.4f} "
        f"(DistCorr={raw_stability['distance_correlation']:.4f}, NN_Overlap={raw_stability['neighbor_overlap']:.4f}, ProcrustesSim={raw_stability['procrustes_similarity']:.4f})"
    )
    print(
        f"  PCA (2D):         Composite = {pca_stability['composite_stability']:.4f} "
        f"(DistCorr={pca_stability['distance_correlation']:.4f}, NN_Overlap={pca_stability['neighbor_overlap']:.4f}, ProcrustesSim={pca_stability['procrustes_similarity']:.4f})"
    )
    print(
        f"  UMAP (2D):        Composite = {umap_stability['composite_stability']:.4f} "
        f"(DistCorr={umap_stability['distance_correlation']:.4f}, NN_Overlap={umap_stability['neighbor_overlap']:.4f}, ProcrustesSim={umap_stability['procrustes_similarity']:.4f})"
    )
    print(
        f"  t-SNE (2D):       Composite = {tsne_stability['composite_stability']:.4f} "
        f"(DistCorr={tsne_stability['distance_correlation']:.4f}, NN_Overlap={tsne_stability['neighbor_overlap']:.4f}, ProcrustesSim={tsne_stability['procrustes_similarity']:.4f})"
    )

    # UMAP Responsibility Score
    # quantifies how much UMAP degrades stability compared to the raw embedding
    resp_score = (
        raw_stability["composite_stability"] - umap_stability["composite_stability"]
    )
    print(f"\nUMAP Responsibility Score: {resp_score:.4f}")

    # Instability Source Diagnostics
    # If raw V3 embedding has high stability (>0.85) but UMAP has low stability (<0.85)
    if (
        raw_stability["composite_stability"] >= 0.85
        and umap_stability["composite_stability"] < 0.85
    ):
        instability_source = "UMAP"
        root_cause = "UMAP_NONLINEAR_PROJECTION_SENSITIVITY"
    elif (
        raw_stability["composite_stability"] < 0.85
        and umap_stability["composite_stability"] < 0.85
    ):
        if pca_stability["composite_stability"] >= 0.85:
            # PCA is stable, but UMAP is not - showing UMAP is specifically fragile
            instability_source = "UMAP"
            root_cause = "UMAP_NONLINEAR_PROJECTION_SENSITIVITY"
        else:
            # Both PCA and UMAP are unstable, meaning the raw embedding itself is drifting
            instability_source = "EMBEDDING"
            root_cause = "EMBEDDING_INTRINSIC_DRIFT"
    else:
        instability_source = "SHARED"
        root_cause = "SHARED_PROJECTION_AND_EMBEDDING_DRIFT"

    print(
        f"Diagnosed Instability Source: {instability_source} (Root Cause = {root_cause})"
    )
    passed_test4 = True  # Audit diagnostics always passes Test 4 as it is an investigatory classification

    # -------------------------------------------------------------
    # CONSOLIDATED REPORT & EXITS
    # -------------------------------------------------------------
    all_passed = passed_test1 and passed_test2 and passed_test3 and passed_test4

    report = {
        "metadata": {
            "generated_at_unix": time.time(),
            "target_thresholds": {
                "distance_correlation": THRES_DIST_CORR,
                "neighbor_overlap": THRES_NEIGHBOR_OVERLAP,
                "covariance_similarity": THRES_COV_SIM,
                "composite_persistence": THRES_COMPOSITE_PERSISTENCE,
            },
            "runtime_seconds": float(time.time() - start_time),
            "global_status": "PASSED" if all_passed else "FAILED",
        },
        "tests": {
            "test1_raw_embedding_stability": {
                "status": "PASSED" if passed_test1 else "FAILED",
                "seed_perturbations": {
                    "distance_correlation": seed_dist_corr,
                    "neighbor_overlap": seed_nn_overlap,
                    "covariance_similarity": seed_cov_sim,
                },
                "noise_sweep": noise_results,
                "noise_sweep_means": {
                    "distance_correlation": mean_noise_dist_corr,
                    "neighbor_overlap": mean_noise_nn_overlap,
                    "covariance_similarity": mean_noise_cov_sim,
                },
            },
            "test2_embedding_topology_persistence": {
                "status": "PASSED" if passed_test2 else "FAILED",
                "seed_persistence": {
                    "procrustes_similarity": proc_sim_seed,
                    "mantel_correlation": mantel_seed,
                    "cka_similarity": cka_seed,
                    "neighbor_overlap": nn_seed,
                    "composite": composite_seed,
                },
                "noise_persistence_5pct": {
                    "procrustes_similarity": proc_sim_n5,
                    "mantel_correlation": mantel_n5,
                    "cka_similarity": cka_n5,
                    "neighbor_overlap": nn_n5,
                    "composite": composite_n5,
                },
                "mean_composite_persistence": mean_composite,
            },
            "test3_true_resampling_audit": {
                "status": "PASSED" if passed_test3 else "FAILED",
                "means": {
                    "silhouette": float(mean_r_sil),
                    "trustworthiness": float(mean_r_trust),
                    "distance_correlation": float(mean_r_dcor),
                },
                "stdevs": {
                    "silhouette": float(std_r_sil),
                    "trustworthiness": float(std_r_trust),
                    "distance_correlation": float(std_r_dcor),
                },
                "confidence_intervals_95": {
                    "silhouette": [ci_sil_lower, ci_sil_upper],
                    "trustworthiness": [ci_trust_lower, ci_trust_upper],
                    "distance_correlation": [ci_dcor_lower, ci_dcor_upper],
                },
                "evaluations": resample_results,
            },
            "test4_umap_responsibility_test": {
                "status": "PASSED" if passed_test4 else "FAILED",
                "projections_stability": {
                    "raw_v3": raw_stability,
                    "pca_2d": pca_stability,
                    "umap_2d": umap_stability,
                    "tsne_2d": tsne_stability,
                },
                "umap_responsibility_score": resp_score,
                "diagnosed_instability_source": instability_source,
                "diagnosed_root_cause": root_cause,
            },
        },
        "diagnosis": {
            "root_cause": root_cause,
            "instability_source": instability_source,
        },
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"\n[REPORT] Saved intrinsic stability report to {OUTPUT_FILE}")

    print("\n" + "=" * 80)
    if all_passed:
        print("PHASE 4.8D PASSED:")
        print("Embedding V3 intrinsic geometry is stable.")
        print("=" * 80)
        return 0
    else:
        print(
            "PHASE 4.8D FAILED: One or more intrinsic stability criteria were not satisfied."
        )
        print("Failed tests:")
        if not passed_test1:
            print("  - Test 1 (Raw embedding stability threshold violated)")
        if not passed_test2:
            print("  - Test 2 (Embedding topology persistence < 0.85 violated)")
        if not passed_test3:
            print(
                "  - Test 3 (True resampling non-degenerate CIs fell below thresholds)"
            )
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
