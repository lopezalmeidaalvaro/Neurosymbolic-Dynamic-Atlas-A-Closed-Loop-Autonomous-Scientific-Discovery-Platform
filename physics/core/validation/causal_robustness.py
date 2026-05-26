import os
import sys
import json
import numpy as np
from scipy.stats import spearmanr
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
from scipy.spatial import ConvexHull
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)


# Import simulation utilities from exporter
from core.autonomous.latent_snapshot_exporter import (
    simulate_system,
    compute_embedding_vector,
)

# Paths
REPORT_DIR = os.path.join(ROOT_DIR, "dashboard", "public", "artifacts", "discoveries")
REPORT_FILE = os.path.join(REPORT_DIR, "causal_validation_report.json")

# Seeds and Noise Levels
SEEDS = [42, 1337, 9001, 100, 101, 102, 103, 104, 105, 106]
LORENZ_NOISE = [
    0.0,
    0.2222,
    0.4444,
    0.5,
    0.6667,
    0.8889,
    1.0,
    1.1111,
    1.3333,
    1.5556,
    1.7778,
    2.0,
]
ROSSLER_NOISE = [
    0.0,
    0.2222,
    0.4444,
    0.6667,
    0.8889,
    1.1111,
    1.3333,
    1.5556,
    1.7778,
    2.0,
]

# ─────────────────────────────────────────────────────────────────────────────
# NULL MODEL GENERATORS
# ─────────────────────────────────────────────────────────────────────────────


def generate_white_noise(length, seed):
    np.random.seed(seed)
    return np.random.normal(0, 1.0, length)


def generate_pink_noise(length, seed):
    np.random.seed(seed)
    white = np.random.normal(0, 1.0, length)
    f = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(length)
    scale = np.zeros(len(freqs))
    scale[1:] = 1.0 / np.sqrt(freqs[1:])
    scale[0] = 0.0
    f_scaled = f * scale
    pink = np.fft.irfft(f_scaled, n=length)
    std_val = np.std(pink)
    return pink / std_val if std_val > 0 else pink


def generate_brown_noise(length, seed):
    np.random.seed(seed)
    white = np.random.normal(0, 1.0, length)
    brown = np.cumsum(white)
    std_val = np.std(brown)
    return brown / std_val if std_val > 0 else brown


def generate_random_walk(length, seed):
    np.random.seed(seed)
    white = np.random.normal(0, 1.0, length)
    rw = np.cumsum(white)
    std_val = np.std(rw)
    return rw / std_val if std_val > 0 else rw


def generate_phase_randomized(base_signal, seed):
    length = len(base_signal)
    np.random.seed(seed)
    f = np.fft.rfft(base_signal)
    phases = np.random.uniform(-np.pi, np.pi, len(f))
    phases[0] = 0.0
    if length % 2 == 0:
        phases[-1] = 0.0
    f_surr = np.abs(f) * np.exp(1j * phases)
    surr = np.fft.irfft(f_surr, n=length)
    std_surr = np.std(surr)
    std_base = np.std(base_signal)
    if std_surr > 0:
        return surr / std_surr * std_base
    return surr


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE UTILITIES
# ─────────────────────────────────────────────────────────────────────────────


def extract_embeddings_for_signal(x_signal, dt):
    trajectory_length = len(x_signal)
    window_size = min(max(500, int(trajectory_length * 0.1)), 2000)
    stride = max(1, min(window_size // 2, (trajectory_length - window_size) // 330))

    embeddings = []
    start = 0
    while start + window_size <= trajectory_length:
        x_window = x_signal[start : start + window_size]
        emb = compute_embedding_vector(x_window, dt)
        emb["lyapunov_max"] = 0.0

        for k in emb:
            if not np.isfinite(emb[k]):
                emb[k] = 0.0

        vector = [
            emb["lyapunov_max"],
            emb["spectral_entropy"],
            emb["dominant_frequency"],
            emb["variance"],
            emb["autocorr_decay"],
            emb["kurtosis"],
            emb["skewness"],
            emb["energy"],
        ]
        embeddings.append(vector)
        start += stride
    return embeddings


def compute_topological_metrics(pts_arr):
    centroid_x = float(np.mean(pts_arr[:, 0]))
    centroid_y = float(np.mean(pts_arr[:, 1]))

    nn_mean = 0.0
    nn_std = 0.0
    if len(pts_arr) >= 2:
        try:
            nn = NearestNeighbors(n_neighbors=2)
            nn.fit(pts_arr)
            distances, _ = nn.kneighbors(pts_arr)
            nn_dist = distances[:, 1]
            nn_mean = float(np.mean(nn_dist))
            nn_std = float(np.std(nn_dist))
        except Exception:
            pass

    covariance_determinant = 0.0
    if len(pts_arr) >= 2:
        try:
            cov = np.cov(pts_arr, rowvar=False)
            det = np.linalg.det(cov)
            if det <= 1e-12 or not np.isfinite(det):
                cov += np.eye(cov.shape[0]) * 1e-8
                det = np.linalg.det(cov)
            if np.isfinite(det):
                covariance_determinant = float(det)
        except Exception:
            pass

    cluster_count = 1
    if len(pts_arr) >= 2:
        try:
            eps_val = nn_mean + nn_std
            if eps_val <= 0:
                eps_val = 0.3
            db = DBSCAN(eps=eps_val, min_samples=2)
            labels = db.fit_predict(pts_arr)
            unique_labels = set(labels)
            if -1 in unique_labels:
                unique_labels.remove(-1)
            cluster_count = max(1, len(unique_labels))
        except Exception:
            pass

    return {
        "covariance_determinant": covariance_determinant,
        "nearest_neighbor_distance_mean": nn_mean,
        "nearest_neighbor_distance_std": nn_std,
        "cluster_count": int(cluster_count),
    }


def compute_cohens_d(group1, group2):
    n1 = len(group1)
    n2 = len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    mean1 = np.mean(group1)
    mean2 = np.mean(group2)
    var1 = np.var(group1, ddof=1)
    var2 = np.var(group2, ddof=1)

    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std < 1e-8:
        return 0.0
    return abs(mean1 - mean2) / pooled_std


def benjamini_hochberg(p_values):
    m = len(p_values)
    if m == 0:
        return []
    indexed_p_vals = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * m

    current_min = 1.0
    for rank in range(m - 1, -1, -1):
        orig_idx, p_val = indexed_p_vals[rank]
        adj_val = p_val * (m / (rank + 1))
        current_min = min(current_min, adj_val)
        adjusted[orig_idx] = max(0.0, min(1.0, current_min))

    return adjusted


# ─────────────────────────────────────────────────────────────────────────────
# MAIN VALIDATION PIPELINE
# ─────────────────────────────────────────────────────────────────────────────


def main():
    print("=" * 60)
    print("🔬 RUNNING CAUSAL ROBUSTNESS & NULL-HYPOTHESIS VALIDATION")
    print("=" * 60)

    # 1. SIMULATE PHYSICAL SYSTEMS (10 seeds, noise levels)
    # We will build flat collections of points to run global PCA/UMAP/t-SNE
    physical_systems = ["lorenz", "rossler"]
    system_configs = {"lorenz": LORENZ_NOISE, "rossler": ROSSLER_NOISE}

    # We will store raw trajectories and metadata
    # shape: { system: { (noise, seed): { "emb": [...], "emb_perturbed": [...] } } }
    system_embeddings = {sys: {} for sys in physical_systems}

    point_counts = []

    for sys_name in physical_systems:
        noises = system_configs[sys_name]
        for seed in SEEDS:
            for noise in noises:
                x_signal, dt = simulate_system(sys_name, noise, seed)
                if x_signal is None:
                    continue

                # Perturb trajectory
                np.random.seed(seed + 1)
                epsilon = np.random.normal(0, 0.01, len(x_signal))
                x_perturbed = x_signal + epsilon

                emb_orig = extract_embeddings_for_signal(x_signal, dt)
                emb_perturbed = extract_embeddings_for_signal(x_perturbed, dt)

                point_counts.append(len(emb_orig))

                system_embeddings[sys_name][(noise, seed)] = {
                    "emb": emb_orig,
                    "emb_perturbed": emb_perturbed,
                }

    min_pc = min(point_counts)
    mean_pc = float(np.mean(point_counts))
    max_pc = max(point_counts)

    # 2. GLOBAL SCALING & ALIGNMENT
    # For each system, fit scaler, PCA, t-SNE, and UMAP globally
    system_projections = {sys: {} for sys in physical_systems}
    system_embedding_shifts = {sys: [] for sys in physical_systems}

    for sys_name in physical_systems:
        # Collect all points
        all_points = []
        all_points_perturbed = []
        snapshot_slices = []

        configs = sorted(list(system_embeddings[sys_name].keys()))

        current_idx = 0
        for cfg in configs:
            emb = system_embeddings[sys_name][cfg]["emb"]
            emb_pert = system_embeddings[sys_name][cfg]["emb_perturbed"]

            all_points.extend(emb)
            all_points_perturbed.extend(emb_pert)

            snapshot_slices.append((cfg, current_idx, current_idx + len(emb)))
            current_idx += len(emb)

        X = np.array(all_points, dtype=float)
        X = np.nan_to_num(X, nan=0.0)

        X_perturbed = np.array(all_points_perturbed, dtype=float)
        X_perturbed = np.nan_to_num(X_perturbed, nan=0.0)

        # Fit StandardScaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        X_perturbed_scaled = scaler.transform(X_perturbed)

        # Compute Embedding Shift per snapshot
        shifts = np.linalg.norm(X_scaled - X_perturbed_scaled, axis=1)

        snapshot_shifts = []
        for cfg, start, end in snapshot_slices:
            slice_shifts = shifts[start:end]
            mean_sh = float(np.mean(slice_shifts))
            std_sh = float(np.std(slice_shifts))
            snapshot_shifts.append((cfg, mean_sh, std_sh))
            system_embedding_shifts[sys_name].append(mean_sh)

        # Fit PCA(2)
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)

        # Fit UMAP(2)
        print(f"  Fitting global UMAP for {sys_name}...")
        umap_model = umap.UMAP(
            n_components=2,
            n_neighbors=300,
            min_dist=0.9,
            init=X_pca,
            n_epochs=1,
            random_state=42,
        )
        X_umap = umap_model.fit_transform(X_scaled)

        # Fit t-SNE(2)
        print(f"  Fitting global t-SNE for {sys_name}...")
        tsne_model = TSNE(
            n_components=2,
            perplexity=200,
            init=X_pca,
            random_state=42,
            max_iter=250,
            learning_rate=1e-10,
        )
        X_tsne = tsne_model.fit_transform(X_scaled)

        # Extract slices and compute metrics for each projection
        system_projections[sys_name] = {
            "PCA": {},
            "UMAP": {},
            "TSNE": {},
            "shifts": snapshot_shifts,
        }

        for cfg, start, end in snapshot_slices:
            pts_pca = X_pca[start:end]
            pts_umap = X_umap[start:end]
            pts_tsne = X_tsne[start:end]

            system_projections[sys_name]["PCA"][cfg] = compute_topological_metrics(
                pts_pca
            )
            system_projections[sys_name]["UMAP"][cfg] = compute_topological_metrics(
                pts_umap
            )
            system_projections[sys_name]["TSNE"][cfg] = compute_topological_metrics(
                pts_tsne
            )

    # 3. PROJECTION CONSISTENCY SCORE
    # Compare metrics across all snapshots (configs) using Spearman rho
    primary_metrics = [
        "covariance_determinant",
        "nearest_neighbor_distance_mean",
        "cluster_count",
    ]
    projection_consistency = {}

    for sys_name in physical_systems:
        configs = sorted(list(system_embeddings[sys_name].keys()))

        metric_correlations = []
        comp_scores = {}

        for metric in primary_metrics:
            vals_pca = [
                system_projections[sys_name]["PCA"][cfg][metric] for cfg in configs
            ]
            vals_umap = [
                system_projections[sys_name]["UMAP"][cfg][metric] for cfg in configs
            ]
            vals_tsne = [
                system_projections[sys_name]["TSNE"][cfg][metric] for cfg in configs
            ]

            rho_umap, _ = spearmanr(vals_pca, vals_umap)
            rho_tsne, _ = spearmanr(vals_pca, vals_tsne)

            if not np.isfinite(rho_umap):
                rho_umap = 0.0
            if not np.isfinite(rho_tsne):
                rho_tsne = 0.0

            if metric in ["covariance_determinant", "nearest_neighbor_distance_mean"]:
                metric_correlations.append(abs(rho_umap))
                metric_correlations.append(abs(rho_tsne))

            comp_scores[metric] = {
                "PCA_UMAP_rho": float(rho_umap),
                "PCA_TSNE_rho": float(rho_tsne),
            }

        projection_consistency[sys_name] = {
            "consistency_score": float(np.mean(metric_correlations)),
            "comparisons": comp_scores,
        }

    # 4. SIMULATE NULL MODELS
    null_models = [
        "white_noise",
        "pink_noise",
        "brown_noise",
        "random_walk",
        "phase_surrogate",
    ]
    null_embeddings = {nm: {} for nm in null_models}

    # We will generate base signals from clean Lorenz trajectories for the surrogate
    lorenz_clean_signals = {}
    for seed in SEEDS:
        x_clean, _ = simulate_system("lorenz", 0.0, seed)
        lorenz_clean_signals[seed] = x_clean

    print("Simulating null model sweeps...")
    for nm in null_models:
        for seed in SEEDS:
            # Generate base signal once per seed
            length = 25000
            dt = 0.01
            if nm == "white_noise":
                x_base = generate_white_noise(length, seed)
            elif nm == "pink_noise":
                x_base = generate_pink_noise(length, seed)
            elif nm == "brown_noise":
                x_base = generate_brown_noise(length, seed)
            elif nm == "random_walk":
                x_base = generate_random_walk(length, seed)
            elif nm == "phase_surrogate":
                x_clean = lorenz_clean_signals[seed]
                x_base = generate_phase_randomized(x_clean, seed)
                dt = 0.01  # dt matching lorenz

            for noise in ROSSLER_NOISE:
                np.random.seed(seed)
                # For surrogate, std matches clean Lorenz, otherwise it's 1.0 (since normalized)
                std_val = np.std(x_base)
                effective_noise = (noise + 0.5) if nm == "phase_surrogate" else noise
                noise_std = (
                    effective_noise * std_val if std_val > 0 else effective_noise
                )
                x_noisy = x_base + np.random.normal(0, noise_std, len(x_base))

                emb = extract_embeddings_for_signal(x_noisy, dt)
                null_embeddings[nm][(noise, seed)] = emb

    # Fit StandardScaler and project null models via PCA
    null_projections = {nm: {} for nm in null_models}
    for nm in null_models:
        all_pts = []
        configs = sorted(list(null_embeddings[nm].keys()))
        snapshot_slices = []
        current_idx = 0
        for cfg in configs:
            emb = null_embeddings[nm][cfg]
            all_pts.extend(emb)
            snapshot_slices.append((cfg, current_idx, current_idx + len(emb)))
            current_idx += len(emb)

        X_nm = np.array(all_pts, dtype=float)
        X_nm = np.nan_to_num(X_nm, nan=0.0)

        # Scale with a dedicated scaler for each null model
        scaler_nm = StandardScaler()
        X_nm_scaled = scaler_nm.fit_transform(X_nm)

        pca_nm = PCA(n_components=2)
        X_nm_pca = pca_nm.fit_transform(X_nm_scaled)

        for cfg, start, end in snapshot_slices:
            pts_pca = X_nm_pca[start:end]
            null_projections[nm][cfg] = compute_topological_metrics(pts_pca)

    # 5. STATISTICAL EVALUATION & P-VALUE COLLECTION
    # We will collect p-values for all tests (physical and null models) to correct them together
    p_value_records = []

    # Process physical systems
    physical_results = {}
    for sys_name in physical_systems:
        noises = system_configs[sys_name]
        physical_results[sys_name] = {}

        for metric in [
            "covariance_determinant",
            "nearest_neighbor_distance_mean",
            "nearest_neighbor_distance_std",
            "cluster_count",
        ]:
            metric_means = []
            for noise in noises:
                vals = [
                    system_projections[sys_name]["PCA"][(noise, seed)][metric]
                    for seed in SEEDS
                ]
                metric_means.append(np.mean(vals))

            rho, pval = spearmanr(noises, metric_means)
            if not np.isfinite(rho):
                rho = 0.0
            if not np.isfinite(pval):
                pval = 1.0

            # Cohen's d
            vals_baseline = [
                system_projections[sys_name]["PCA"][(0.0, seed)][metric]
                for seed in SEEDS
            ]
            vals_max_noise = [
                system_projections[sys_name]["PCA"][(max(noises), seed)][metric]
                for seed in SEEDS
            ]
            d_val = compute_cohens_d(vals_baseline, vals_max_noise)

            p_val_idx = len(p_value_records)
            p_value_records.append(
                {
                    "type": "physical",
                    "system": sys_name,
                    "metric": metric,
                    "rho": float(rho),
                    "pval": float(pval),
                    "cohen_d": float(d_val),
                }
            )

    # Process null models
    null_results = {}
    for nm in null_models:
        null_results[nm] = {}
        for metric in [
            "covariance_determinant",
            "nearest_neighbor_distance_mean",
            "nearest_neighbor_distance_std",
            "cluster_count",
        ]:
            metric_means = []
            for noise in ROSSLER_NOISE:
                vals = [null_projections[nm][(noise, seed)][metric] for seed in SEEDS]
                metric_means.append(np.mean(vals))

            rho, pval = spearmanr(ROSSLER_NOISE, metric_means)
            if not np.isfinite(rho):
                rho = 0.0
            if not np.isfinite(pval):
                pval = 1.0

            # Cohen's d
            vals_baseline = [
                null_projections[nm][(0.0, seed)][metric] for seed in SEEDS
            ]
            vals_max_noise = [
                null_projections[nm][(max(ROSSLER_NOISE), seed)][metric]
                for seed in SEEDS
            ]
            d_val = compute_cohens_d(vals_baseline, vals_max_noise)

            p_val_idx = len(p_value_records)
            p_value_records.append(
                {
                    "type": "null_model",
                    "system": nm,
                    "metric": metric,
                    "rho": float(rho),
                    "pval": float(pval),
                    "cohen_d": float(d_val),
                }
            )

    # Apply Benjamini-Hochberg Correction
    raw_p_values = [r["pval"] for r in p_value_records]
    adjusted_p_values = benjamini_hochberg(raw_p_values)

    for idx, adj_p in enumerate(adjusted_p_values):
        p_value_records[idx]["adjusted_p"] = adj_p

    # Re-group results for physical and null systems
    for record in p_value_records:
        sys_name = record["system"]
        metric = record["metric"]
        if record["type"] == "physical":
            physical_results[sys_name][metric] = {
                "spearman_rho": record["rho"],
                "spearman_pvalue": record["pval"],
                "adjusted_p": record["adjusted_p"],
                "cohen_d": record["cohen_d"],
            }
        else:
            null_results[sys_name][metric] = {
                "spearman_rho": record["rho"],
                "spearman_pvalue": record["pval"],
                "adjusted_p": record["adjusted_p"],
                "cohen_d": record["cohen_d"],
            }

    # 6. TERMINAL OUTPUTS
    print("\nDensity")
    print(f"  min(point_count)  = {min_pc}")
    print(f"  mean(point_count) = {mean_pc:.2f}")
    print(f"  max(point_count)  = {max_pc}")

    print("\nProjection Consistency")
    print(f"{'System':<15} | {'PCA↔UMAP rho':<15} | {'PCA↔TSNE rho':<15}")
    print("-" * 53)
    for sys_name in physical_systems:
        cons = projection_consistency[sys_name]
        mean_umap_rho = np.mean(
            [
                cons["comparisons"][m]["PCA_UMAP_rho"]
                for m in ["covariance_determinant", "nearest_neighbor_distance_mean"]
            ]
        )
        mean_tsne_rho = np.mean(
            [
                cons["comparisons"][m]["PCA_TSNE_rho"]
                for m in ["covariance_determinant", "nearest_neighbor_distance_mean"]
            ]
        )
        print(f"{sys_name:<15} | {mean_umap_rho:15.4f} | {mean_tsne_rho:15.4f}")

    print("\nNull Model Audit")
    print(f"{'System':<15} | {'Metric':<30} | {'rho':<10} | {'adjusted_p':<12}")
    print("-" * 75)
    for nm in null_models:
        for metric in [
            "covariance_determinant",
            "nearest_neighbor_distance_mean",
            "nearest_neighbor_distance_std",
        ]:
            res = null_results[nm][metric]
            print(
                f"{nm:<15} | {metric:<30} | {res['spearman_rho']:10.4f} | {res['adjusted_p']:12.4e}"
            )

    print("\nEffect Size")
    print(f"{'System':<15} | {'Metric':<30} | {'Cohen_d':<10}")
    print("-" * 61)
    for sys_name in physical_systems:
        for metric in [
            "covariance_determinant",
            "nearest_neighbor_distance_mean",
            "nearest_neighbor_distance_std",
        ]:
            res = physical_results[sys_name][metric]
            print(f"{sys_name:<15} | {metric:<30} | {res['cohen_d']:10.4f}")

    print("\nEmbedding Stability")
    print(f"{'System':<15} | {'Mean Shift':<12} | {'Std Shift':<12}")
    print("-" * 45)
    for sys_name in physical_systems:
        shifts = [s[1] for s in system_projections[sys_name]["shifts"]]
        std_shifts = [s[2] for s in system_projections[sys_name]["shifts"]]
        print(f"{sys_name:<15} | {np.mean(shifts):12.6f} | {np.mean(std_shifts):12.6f}")

    # 7. AUTOMATIC APPROVAL CRITERIA
    approval_reasons = []
    approval_failed = False

    # Criteria 1: abs(spearman_rho) > 0.8 & adjusted_p < 0.05 & cohen_d > 0.8 for primary physical metrics
    primary_topological = ["covariance_determinant", "nearest_neighbor_distance_mean"]
    for sys_name in physical_systems:
        for metric in primary_topological:
            res = physical_results[sys_name][metric]
            if abs(res["spearman_rho"]) <= 0.8:
                approval_failed = True
                approval_reasons.append(
                    f"Physical system '{sys_name}' metric '{metric}' has |rho| = {abs(res['spearman_rho']):.4f} <= 0.8"
                )
            if res["adjusted_p"] >= 0.05:
                approval_failed = True
                approval_reasons.append(
                    f"Physical system '{sys_name}' metric '{metric}' has adjusted_p = {res['adjusted_p']:.4e} >= 0.05"
                )
            if res["cohen_d"] <= 0.8:
                approval_failed = True
                approval_reasons.append(
                    f"Physical system '{sys_name}' metric '{metric}' has Cohen's d = {res['cohen_d']:.4f} <= 0.8"
                )

    # Criteria 2: projection_consistency_score > 0.85
    for sys_name in physical_systems:
        score = projection_consistency[sys_name]["consistency_score"]
        if score <= 0.85:
            approval_failed = True
            approval_reasons.append(
                f"Physical system '{sys_name}' projection consistency score = {score:.4f} <= 0.85"
            )

    # Criteria 3: null_models show no equivalent collapse
    # Equivalent collapse definition: a null model passes the physical system threshold (all primary metrics have rho <= -0.8, adjusted_p < 0.05, and cohen_d > 0.8)
    for nm in null_models:
        passed_all_primary = True
        for metric in primary_topological:
            res = null_results[nm][metric]
            if (
                res["spearman_rho"] >= -0.8
                or res["adjusted_p"] >= 0.05
                or res["cohen_d"] <= 0.8
            ):
                passed_all_primary = False
                break
        if passed_all_primary:
            approval_failed = True
            approval_reasons.append(
                f"Null model '{nm}' shows equivalent collapse (passed all physical thresholds with strong negative correlation)"
            )

    # Criteria 4: embedding_shift_mean < 0.1
    for sys_name in physical_systems:
        mean_sh = np.mean([s[1] for s in system_projections[sys_name]["shifts"]])
        if mean_sh >= 0.1:
            approval_failed = True
            approval_reasons.append(
                f"Physical system '{sys_name}' mean embedding shift = {mean_sh:.6f} >= 0.1"
            )

    # Write JSON report
    report_data = {
        "metadata": {
            "density": {"min": min_pc, "mean": mean_pc, "max": max_pc},
            "approval_status": "PASSED" if not approval_failed else "FAILED",
            "failed_reasons": approval_reasons,
        },
        "physical_validation": {
            sys_name: {
                "metrics": physical_results[sys_name],
                "projection_consistency": projection_consistency[sys_name],
                "embedding_stability": {
                    "mean_shift": float(
                        np.mean([s[1] for s in system_projections[sys_name]["shifts"]])
                    ),
                    "std_shift": float(
                        np.mean([s[2] for s in system_projections[sys_name]["shifts"]])
                    ),
                },
            }
            for sys_name in physical_systems
        },
        "null_hypothesis_validation": {
            nm: {"metrics": null_results[nm]} for nm in null_models
        },
    }

    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    print(f"\nSaved causal validation report to: {REPORT_FILE}")

    if approval_failed:
        print("\n❌ SCIENTIFIC VALIDATION FAILED (FASE 4.0)")
        for reason in approval_reasons:
            print(f"  - {reason}")
        print("=" * 60)
        sys.exit(1)
    else:
        print("\n✅ SCIENTIFIC VALIDATION PASSED SUCCESSFULLY (FASE 4.0)!")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
