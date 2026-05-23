"""
core/validation/hyperparameter_stability_audit.py
============================================
Rigorous scientific audit of UMAP hyperparameter stability for optimal configuration:
n_neighbors=50, min_dist=0.5, metric="correlation".
Tests local perturbations, random seed variations, trajectory resampling,
and manifold topological persistence (Procrustes, distance correlation, NN overlap).
"""

from __future__ import annotations

import json
import os
import sys
import time
import traceback

import numpy as np
import umap
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.manifold import trustworthiness
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import pdist
from scipy.stats import pearsonr
from scipy.spatial import procrustes

# Ensure ROOT_DIR is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

# Import baseline functions and constants for perfect parity
from core.validation.cross_system_generalization_tests import (
    simulate_physical,
    extract_v3,
    compute_distance_correlation,
    PHYSICAL_SYSTEMS,
    V3_KEYS
)

OUTPUT_DIR = os.path.join(ROOT_DIR, "dashboard", "public", "artifacts", "discoveries")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "hyperparameter_stability_report.json")

# Optimal hyperparameter configuration identified in 4.8B
OPT_NN = 50
OPT_MD = 0.5
OPT_MET = "correlation"

# Thresholds
THRES_SIL = 0.30
THRES_TRUST = 0.95
THRES_DCOR = 0.80

def build_physical_dataset_custom(seeds: list[int], noise: float = 0.0, standardize_before_embedding: bool = False) -> dict[str, np.ndarray]:
    dataset = {}
    for system in PHYSICAL_SYSTEMS:
        system_rows = []
        for seed in seeds:
            signal = simulate_physical(system, noise=noise, seed=seed)
            system_rows.append(extract_v3(signal, standardize_before_embedding))
        dataset[system] = np.vstack(system_rows)
    return dataset

def compute_nn_overlap(A: np.ndarray, B: np.ndarray, k: int = 15) -> float:
    nbrs_A = NearestNeighbors(n_neighbors=k + 1).fit(A)
    nbrs_B = NearestNeighbors(n_neighbors=k + 1).fit(B)
    
    idx_A = nbrs_A.kneighbors(A, return_distance=False)[:, 1:]
    idx_B = nbrs_B.kneighbors(B, return_distance=False)[:, 1:]
    
    overlaps = []
    for row_A, row_B in zip(idx_A, idx_B):
        set_A = set(row_A)
        set_B = set(row_B)
        intersection = len(set_A.intersection(set_B))
        overlaps.append(intersection / k)
        
    return float(np.mean(overlaps))

def main():
    start_time = time.time()
    print("=" * 80)
    print("   HYPERPARAMETER STABILITY AUDIT: MANIFOLD ROBUSTNESS")
    print("=" * 80)
    
    # 0. Load physical dataset for parity
    print("\n[DATA] Loading baseline physical dataset...")
    # Baseline seeds are [42, 1337, 9001]
    baseline_dataset = build_physical_dataset_custom([42, 1337, 9001])
    
    x = np.vstack([baseline_dataset[name] for name in PHYSICAL_SYSTEMS])
    labels = np.concatenate([
        np.full(len(baseline_dataset[name]), idx, dtype=int)
        for idx, name in enumerate(PHYSICAL_SYSTEMS)
    ])
    
    scaled = StandardScaler().fit_transform(x)
    pca = PCA(n_components=5, random_state=42)
    x_pca = pca.fit_transform(scaled)
    
    # -------------------------------------------------------------
    # TEST 1 — LOCAL HYPERPARAMETER STABILITY
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print("TEST 1 — LOCAL HYPERPARAMETER STABILITY")
    print("-" * 50)
    
    n_neighbors_grid = [40, 45, 50, 55, 60]
    min_dist_grid = [0.3, 0.4, 0.5, 0.6, 0.7]
    
    grid_results = []
    embeddings_by_config = {}  # Store embeddings for Test 4 comparison
    
    for nn in n_neighbors_grid:
        for md in min_dist_grid:
            try:
                reducer = umap.UMAP(
                    n_components=2,
                    n_neighbors=nn,
                    min_dist=md,
                    metric=OPT_MET,
                    random_state=42,
                    n_epochs=500,
                )
                x_umap = reducer.fit_transform(x_pca)
                
                sil = float(silhouette_score(x_umap, labels))
                trust = float(trustworthiness(x_pca, x_umap, n_neighbors=15))
                dcor = compute_distance_correlation(x_pca, x_umap)
                
                config_key = f"nn={nn},md={md}"
                embeddings_by_config[config_key] = x_umap
                
                grid_results.append({
                    "n_neighbors": nn,
                    "min_dist": md,
                    "silhouette": sil,
                    "trustworthiness": trust,
                    "distance_correlation": dcor,
                    "passed_all": sil >= THRES_SIL and trust >= THRES_TRUST and dcor >= THRES_DCOR
                })
                print(f"Neighbors={nn:<2} | Dist={md:<3} | Sil={sil:.4f} | Trust={trust:.4f} | DCor={dcor:.4f} | PassedAll={grid_results[-1]['passed_all']}")
            except Exception as e:
                print(f"Error evaluating local config nn={nn}, md={md}: {e}")
                
    # Calculate stats over grid
    sil_values = [item["silhouette"] for item in grid_results]
    trust_values = [item["trustworthiness"] for item in grid_results]
    dcor_values = [item["distance_correlation"] for item in grid_results]
    
    mean_sil, std_sil = float(np.mean(sil_values)), float(np.std(sil_values))
    mean_trust, std_trust = float(np.mean(trust_values)), float(np.std(trust_values))
    mean_dcor, std_dcor = float(np.mean(dcor_values)), float(np.std(dcor_values))
    
    cv_sil = std_sil / mean_sil if mean_sil != 0 else 0.0
    cv_trust = std_trust / mean_trust if mean_trust != 0 else 0.0
    cv_dcor = std_dcor / mean_dcor if mean_dcor != 0 else 0.0
    
    print("\nLocal stability statistics over 25 configurations:")
    print(f"  Silhouette: mean = {mean_sil:.6f}, std = {std_sil:.6f}, CV = {cv_sil * 100:.2f}%")
    print(f"  Trustworthiness: mean = {mean_trust:.6f}, std = {std_trust:.6f}, CV = {cv_trust * 100:.2f}%")
    print(f"  Distance Corr: mean = {mean_dcor:.6f}, std = {std_dcor:.6f}, CV = {cv_dcor * 100:.2f}%")
    
    passed_test1 = (
        mean_sil >= THRES_SIL and
        mean_trust >= THRES_TRUST and
        mean_dcor >= THRES_DCOR and
        cv_sil < 0.10 and
        cv_trust < 0.10 and
        cv_dcor < 0.10
    )
    print(f"TEST 1 STATUS: {'PASSED' if passed_test1 else 'FAILED'}")
    
    # -------------------------------------------------------------
    # TEST 2 — RANDOM SEED STABILITY
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print("TEST 2 — RANDOM SEED STABILITY")
    print("-" * 50)
    
    seeds = [0, 1, 2, 3, 4, 5, 10, 20, 42, 123]
    seed_results = []
    
    for seed in seeds:
        try:
            reducer = umap.UMAP(
                n_components=2,
                n_neighbors=OPT_NN,
                min_dist=OPT_MD,
                metric=OPT_MET,
                random_state=seed,
                n_epochs=500,
            )
            x_umap_seed = reducer.fit_transform(x_pca)
            
            sil = float(silhouette_score(x_umap_seed, labels))
            trust = float(trustworthiness(x_pca, x_umap_seed, n_neighbors=15))
            dcor = compute_distance_correlation(x_pca, x_umap_seed)
            
            seed_results.append({
                "seed": seed,
                "silhouette": sil,
                "trustworthiness": trust,
                "distance_correlation": dcor
            })
            print(f"Seed={seed:<3} | Sil={sil:.4f} | Trust={trust:.4f} | DCor={dcor:.4f}")
        except Exception as e:
            print(f"Error evaluating seed={seed}: {e}")
            
    # Relative variation check (relative standard deviation / CV)
    seed_sils = [item["silhouette"] for item in seed_results]
    seed_trusts = [item["trustworthiness"] for item in seed_results]
    seed_dcors = [item["distance_correlation"] for item in seed_results]
    
    mean_seed_sil, std_seed_sil = float(np.mean(seed_sils)), float(np.std(seed_sils))
    mean_seed_trust, std_seed_trust = float(np.mean(seed_trusts)), float(np.std(seed_trusts))
    mean_seed_dcor, std_seed_dcor = float(np.mean(seed_dcors)), float(np.std(seed_dcors))
    
    cv_seed_sil = std_seed_sil / mean_seed_sil if mean_seed_sil != 0 else 0.0
    cv_seed_trust = std_seed_trust / mean_seed_trust if mean_seed_trust != 0 else 0.0
    cv_seed_dcor = std_seed_dcor / mean_seed_dcor if mean_seed_dcor != 0 else 0.0
    
    max_min_var_sil = (max(seed_sils) - min(seed_sils)) / mean_seed_sil if mean_seed_sil != 0 else 0.0
    max_min_var_trust = (max(seed_trusts) - min(seed_trusts)) / mean_seed_trust if mean_seed_trust != 0 else 0.0
    max_min_var_dcor = (max(seed_dcors) - min(seed_dcors)) / mean_seed_dcor if mean_seed_dcor != 0 else 0.0
    
    print("\nRandom Seed Stability statistics over 10 seeds:")
    print(f"  Silhouette: CV = {cv_seed_sil * 100:.2f}%, Max-Min Relative Var = {max_min_var_sil * 100:.2f}%")
    print(f"  Trustworthiness: CV = {cv_seed_trust * 100:.2f}%, Max-Min Relative Var = {max_min_var_trust * 100:.2f}%")
    print(f"  Distance Corr: CV = {cv_seed_dcor * 100:.2f}%, Max-Min Relative Var = {max_min_var_dcor * 100:.2f}%")
    
    passed_test2 = (
        cv_seed_sil < 0.05 and
        cv_seed_trust < 0.05 and
        cv_seed_dcor < 0.05
    )
    print(f"TEST 2 STATUS: {'PASSED' if passed_test2 else 'FAILED'}")
    
    # -------------------------------------------------------------
    # TEST 3 — DATA RESAMPLING STABILITY
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print("TEST 3 — DATA RESAMPLING STABILITY")
    print("-" * 50)
    
    resample_results = []
    
    # Generate 10 resampled datasets (each with 3 different seeds)
    # Seeds will be spaced out to ensure independent trajectories
    for i in range(10):
        resample_seeds = [100 + i*3, 101 + i*3, 102 + i*3]
        try:
            print(f"Generating custom dataset {i+1}/10 with seeds {resample_seeds}...")
            r_dataset = build_physical_dataset_custom(resample_seeds)
            
            x_r = np.vstack([r_dataset[name] for name in PHYSICAL_SYSTEMS])
            labels_r = np.concatenate([
                np.full(len(r_dataset[name]), idx, dtype=int)
                for idx, name in enumerate(PHYSICAL_SYSTEMS)
            ])
            
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
            
            resample_results.append({
                "dataset_idx": i,
                "seeds": resample_seeds,
                "silhouette": sil,
                "trustworthiness": trust,
                "distance_correlation": dcor
            })
            print(f"Dataset {i+1} | Sil={sil:.4f} | Trust={trust:.4f} | DCor={dcor:.4f}")
        except Exception as e:
            print(f"Error evaluating resampled dataset {i+1}: {e}")
            
    # Compute 95% Confidence Intervals
    r_sils = [item["silhouette"] for item in resample_results]
    r_trusts = [item["trustworthiness"] for item in resample_results]
    r_dcors = [item["distance_correlation"] for item in resample_results]
    
    mean_r_sil, std_r_sil = np.mean(r_sils), np.std(r_sils, ddof=1)
    mean_r_trust, std_r_trust = np.mean(r_trusts), np.std(r_trusts, ddof=1)
    mean_r_dcor, std_r_dcor = np.mean(r_dcors), np.std(r_dcors, ddof=1)
    
    # Critical t value for df=9, alpha=0.05 (two-tailed) is 2.262
    t_critical = 2.262
    n_resamples = len(resample_results)
    
    ci_sil_lower = float(mean_r_sil - t_critical * (std_r_sil / np.sqrt(n_resamples)))
    ci_sil_upper = float(mean_r_sil + t_critical * (std_r_sil / np.sqrt(n_resamples)))
    
    ci_trust_lower = float(mean_r_trust - t_critical * (std_r_trust / np.sqrt(n_resamples)))
    ci_trust_upper = float(mean_r_trust + t_critical * (std_r_trust / np.sqrt(n_resamples)))
    
    ci_dcor_lower = float(mean_r_dcor - t_critical * (std_r_dcor / np.sqrt(n_resamples)))
    ci_dcor_upper = float(mean_r_dcor + t_critical * (std_r_dcor / np.sqrt(n_resamples)))
    
    print("\nData Resampling 95% Confidence Intervals:")
    print(f"  Silhouette: mean = {mean_r_sil:.6f}, std = {std_r_sil:.6f}, 95% CI = [{ci_sil_lower:.6f}, {ci_sil_upper:.6f}]")
    print(f"  Trustworthiness: mean = {mean_r_trust:.6f}, std = {std_r_trust:.6f}, 95% CI = [{ci_trust_lower:.6f}, {ci_trust_upper:.6f}]")
    print(f"  Distance Corr: mean = {mean_r_dcor:.6f}, std = {std_r_dcor:.6f}, 95% CI = [{ci_dcor_lower:.6f}, {ci_dcor_upper:.6f}]")
    
    passed_test3 = (
        ci_sil_lower >= THRES_SIL and
        ci_trust_lower >= THRES_TRUST and
        ci_dcor_lower >= THRES_DCOR
    )
    print(f"TEST 3 STATUS: {'PASSED' if passed_test3 else 'FAILED'}")
    
    # -------------------------------------------------------------
    # TEST 4 — MANIFOLD TOPOLOGY PERSISTENCE
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print("TEST 4 — MANIFOLD TOPOLOGY PERSISTENCE")
    print("-" * 50)
    
    # We compare neighbor configuration embeddings to the optimal embedding (nn=50, md=0.5)
    opt_key = "nn=50,md=0.5"
    if opt_key not in embeddings_by_config:
        print("[WARN] Optimal configuration embedding not found in Test 1 grid. Re-running optimal configuration...")
        reducer_opt = umap.UMAP(
            n_components=2,
            n_neighbors=OPT_NN,
            min_dist=OPT_MD,
            metric=OPT_MET,
            random_state=42,
            n_epochs=500,
        )
        x_umap_opt = reducer_opt.fit_transform(x_pca)
    else:
        x_umap_opt = embeddings_by_config[opt_key]
        
    d_opt = pdist(x_umap_opt)
    
    persistence_results = []
    
    for key, x_umap_nei in embeddings_by_config.items():
        if key == opt_key:
            continue
            
        try:
            # 1. Distance matrix correlation
            d_nei = pdist(x_umap_nei)
            dist_corr, _ = pearsonr(d_opt, d_nei)
            dist_corr = float(dist_corr)
            
            # 2. Procrustes similarity (disparity-based)
            _, _, disparity = procrustes(x_umap_opt, x_umap_nei)
            procrustes_sim = float(1.0 - disparity)
            
            # 3. Nearest-neighbor overlap
            nn_overlap = float(compute_nn_overlap(x_umap_opt, x_umap_nei, k=15))
            
            composite_persistence = float((dist_corr + procrustes_sim + nn_overlap) / 3.0)
            
            # Extract nn and md from key
            nn_val = int(key.split(",")[0].split("=")[1])
            md_val = float(key.split(",")[1].split("=")[1])
            
            persistence_results.append({
                "key": key,
                "n_neighbors": nn_val,
                "min_dist": md_val,
                "distance_correlation": dist_corr,
                "procrustes_similarity": procrustes_sim,
                "nearest_neighbor_overlap": nn_overlap,
                "composite_persistence": composite_persistence
            })
            print(f"Neighbor {key:<12} | DistCorr={dist_corr:.4f} | ProcrustesSim={procrustes_sim:.4f} | NN_Overlap={nn_overlap:.4f} | Composite={composite_persistence:.4f}")
        except Exception as e:
            print(f"Error computing topology persistence for neighbor {key}: {e}")
            
    # Calculate average topological persistence over all neighbors
    mean_dist_corr = float(np.mean([item["distance_correlation"] for item in persistence_results]))
    mean_procrustes = float(np.mean([item["procrustes_similarity"] for item in persistence_results]))
    mean_nn_overlap = float(np.mean([item["nearest_neighbor_overlap"] for item in persistence_results]))
    mean_composite_persistence = float(np.mean([item["composite_persistence"] for item in persistence_results]))
    
    print("\nManifold Topology Persistence averages over neighborhood:")
    print(f"  Distance Matrix Correlation: {mean_dist_corr:.6f}")
    print(f"  Procrustes Similarity:       {mean_procrustes:.6f}")
    print(f"  Nearest-Neighbor Overlap:    {mean_nn_overlap:.6f}")
    print(f"  Composite Persistence:       {mean_composite_persistence:.6f}")
    
    # Criterio: persistencia topológica >0.85
    passed_test4 = mean_composite_persistence > 0.85
    print(f"TEST 4 STATUS: {'PASSED' if passed_test4 else 'FAILED'}")
    
    # -------------------------------------------------------------
    # CONSOLIDATED ROBUSTNESS RANKING
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("                  CONSOLIDATED ROBUSTNESS RANKING")
    print("=" * 80)
    
    # We rank the 25 configurations of the local hyperparameter sweep.
    # A configuration is robust if it consistently satisfies the target thresholds,
    # and has high topological persistence with the optimal point.
    ranked_configs = []
    
    for item in grid_results:
        nn = item["n_neighbors"]
        md = item["min_dist"]
        sil = item["silhouette"]
        trust = item["trustworthiness"]
        dcor = item["distance_correlation"]
        
        # Get topological persistence with the optimal configuration (if not optimal itself)
        key = f"nn={nn},md={md}"
        if key == opt_key:
            persistence = 1.0  # Perfect persistence with itself
        else:
            p_match = [p for p in persistence_results if p["key"] == key]
            persistence = p_match[0]["composite_persistence"] if p_match else 0.0
            
        # Composite robustness score: average coherence metric ratio + topological persistence weight
        # Robust configs will have high coherence and align well topologically
        robustness_score = (sil / THRES_SIL) + (trust / THRES_TRUST) + (dcor / THRES_DCOR) + persistence
        
        ranked_configs.append({
            "n_neighbors": nn,
            "min_dist": md,
            "silhouette": sil,
            "trustworthiness": trust,
            "distance_correlation": dcor,
            "topological_persistence": persistence,
            "robustness_score": float(robustness_score)
        })
        
    ranked_configs.sort(key=lambda c: c["robustness_score"], reverse=True)
    
    print("Top 5 Most Robust Configurations:")
    for idx, r_conf in enumerate(ranked_configs[:5]):
        print(f"  {idx+1}. n_neighbors={r_conf['n_neighbors']}, min_dist={r_conf['min_dist']} "
              f"| Robustness Score = {r_conf['robustness_score']:.6f} "
              f"| Sil={r_conf['silhouette']:.4f} | Trust={r_conf['trustworthiness']:.4f} "
              f"| DCor={r_conf['distance_correlation']:.4f} | Persistence={r_conf['topological_persistence']:.4f}")
              
    most_robust_config = f"n_neighbors={ranked_configs[0]['n_neighbors']}, min_dist={ranked_configs[0]['min_dist']}, metric='correlation'"
    print(f"\nMost robust configuration = {most_robust_config}")
    
    # -------------------------------------------------------------
    # CRITERIA EVALUATION & EXITS
    # -------------------------------------------------------------
    all_passed = passed_test1 and passed_test2 and passed_test3 and passed_test4
    
    report = {
        "metadata": {
            "generated_at_unix": time.time(),
            "target_thresholds": {
                "silhouette": THRES_SIL,
                "trustworthiness": THRES_TRUST,
                "distance_correlation": THRES_DCOR
            },
            "optimal_configuration": {
                "n_neighbors": OPT_NN,
                "min_dist": OPT_MD,
                "metric": OPT_MET
            },
            "runtime_seconds": float(time.time() - start_time),
            "global_status": "PASSED" if all_passed else "FAILED"
        },
        "tests": {
            "test1_local_hyperparameter_stability": {
                "status": "PASSED" if passed_test1 else "FAILED",
                "means": {
                    "silhouette": mean_sil,
                    "trustworthiness": mean_trust,
                    "distance_correlation": mean_dcor
                },
                "stdevs": {
                    "silhouette": std_sil,
                    "trustworthiness": std_trust,
                    "distance_correlation": std_dcor
                },
                "coefficients_of_variation": {
                    "silhouette": cv_sil,
                    "trustworthiness": cv_trust,
                    "distance_correlation": cv_dcor
                },
                "grid_evaluations": grid_results
            },
            "test2_random_seed_stability": {
                "status": "PASSED" if passed_test2 else "FAILED",
                "means": {
                    "silhouette": mean_seed_sil,
                    "trustworthiness": mean_seed_trust,
                    "distance_correlation": mean_seed_dcor
                },
                "stdevs": {
                    "silhouette": std_seed_sil,
                    "trustworthiness": std_seed_trust,
                    "distance_correlation": std_seed_dcor
                },
                "coefficients_of_variation": {
                    "silhouette": cv_seed_sil,
                    "trustworthiness": cv_seed_trust,
                    "distance_correlation": cv_seed_dcor
                },
                "max_min_relative_variations": {
                    "silhouette": max_min_var_sil,
                    "trustworthiness": max_min_var_trust,
                    "distance_correlation": max_min_var_dcor
                },
                "seed_evaluations": seed_results
            },
            "test3_data_resampling_stability": {
                "status": "PASSED" if passed_test3 else "FAILED",
                "means": {
                    "silhouette": float(mean_r_sil),
                    "trustworthiness": float(mean_r_trust),
                    "distance_correlation": float(mean_r_dcor)
                },
                "stdevs": {
                    "silhouette": float(std_r_sil),
                    "trustworthiness": float(std_r_trust),
                    "distance_correlation": float(std_r_dcor)
                },
                "confidence_intervals_95": {
                    "silhouette": [ci_sil_lower, ci_sil_upper],
                    "trustworthiness": [ci_trust_lower, ci_trust_upper],
                    "distance_correlation": [ci_dcor_lower, ci_dcor_upper]
                },
                "dataset_evaluations": resample_results
            },
            "test4_manifold_topology_persistence": {
                "status": "PASSED" if passed_test4 else "FAILED",
                "means": {
                    "distance_correlation": mean_dist_corr,
                    "procrustes_similarity": mean_procrustes,
                    "nearest_neighbor_overlap": mean_nn_overlap,
                    "composite_persistence": mean_composite_persistence
                },
                "neighbor_evaluations": persistence_results
            }
        },
        "diagnosis": {
            "robustness_ranking": ranked_configs,
            "most_robust_configuration": most_robust_config
        }
    }
    
    # Save JSON report
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"\n[REPORT] Saved stability report to {OUTPUT_FILE}")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("PHASE 4.8C PASSED:")
        print("Optimal manifold configuration is stable and not hyperparameter luck.")
        print("=" * 80)
        return 0
    else:
        print("PHASE 4.8C FAILED: One or more stability criteria were not satisfied.")
        print("Failed tests:")
        if not passed_test1:
            print("  - Test 1 (Local stability mean criteria or CV < 10% violated)")
        if not passed_test2:
            print("  - Test 2 (Seed variation > 5% violated)")
        if not passed_test3:
            print("  - Test 3 (Res resampling CI lower bound fell below target thresholds)")
        if not passed_test4:
            print("  - Test 4 (Manifold topological persistence < 0.85 violated)")
        print("=" * 80)
        return 1

if __name__ == "__main__":
    sys.exit(main())
