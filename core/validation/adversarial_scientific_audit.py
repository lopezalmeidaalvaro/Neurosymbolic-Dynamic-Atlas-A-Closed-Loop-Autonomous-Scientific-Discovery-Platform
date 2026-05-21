import os
import sys
sys_module = sys
import json
import time
import numpy as np
from scipy.stats import spearmanr, pearsonr
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler, QuantileTransformer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE, trustworthiness
import umap
from scipy.spatial.distance import pdist
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.feature_selection import mutual_info_regression
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score, f1_score, confusion_matrix
)
from sklearn.model_selection import train_test_split
from concurrent.futures import ProcessPoolExecutor, as_completed

# System-dependent configuration will be loaded in the main block to prevent multiprocessing stream wrapping issues.

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

from core.autonomous.latent_snapshot_exporter import simulate_system, compute_embedding_vector

# Paths
REPORT_DIR = os.path.join(ROOT_DIR, "dashboard", "public", "artifacts", "discoveries")
REPORT_FILE = os.path.join(REPORT_DIR, "adversarial_audit_report.json")

# Seeds and Noise Levels (10 seeds for general tests)
SEEDS_10 = [42, 1337, 9001, 100, 101, 102, 103, 104, 105, 106]
LORENZ_NOISE = [0.0, 0.2222, 0.4444, 0.5, 0.6667, 0.8889, 1.0, 1.1111, 1.3333, 1.5556, 1.7778, 2.0]
ROSSLER_NOISE = [0.0, 0.2222, 0.4444, 0.6667, 0.8889, 1.1111, 1.3333, 1.5556, 1.7778, 2.0]

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

def generate_ar1(length, seed, phi=0.8):
    np.random.seed(seed)
    x = np.zeros(length)
    eps = np.random.normal(0, 1.0, length)
    for t in range(1, length):
        x[t] = phi * x[t-1] + eps[t]
    std_val = np.std(x)
    return x / std_val if std_val > 0 else x

def generate_ou(length, seed, theta=0.15, mu=0.0, sigma=0.3, dt=0.01):
    np.random.seed(seed)
    x = np.zeros(length)
    x[0] = np.random.normal(mu, sigma / np.sqrt(2 * theta))
    for t in range(1, length):
        dw = np.random.normal(0, np.sqrt(dt))
        x[t] = x[t-1] + theta * (mu - x[t-1]) * dt + sigma * dw
    std_val = np.std(x)
    return x / std_val if std_val > 0 else x

def generate_logistic_map_null(length, seed, r=3.9):
    np.random.seed(seed)
    x = np.zeros(length)
    x[0] = np.random.uniform(0.1, 0.9)
    for t in range(1, length):
        x[t] = r * x[t-1] * (1.0 - x[t-1])
    std_val = np.std(x)
    return x / std_val if std_val > 0 else x

def generate_shuffled_blocks(base_signal, seed, block_size=500):
    np.random.seed(seed)
    length = len(base_signal)
    num_blocks = length // block_size
    block_indices = list(range(num_blocks))
    np.random.shuffle(block_indices)
    shuffled = np.zeros(length)
    for i, idx in enumerate(block_indices):
        shuffled[i*block_size:(i+1)*block_size] = base_signal[idx*block_size:(idx+1)*block_size]
    remainder = length % block_size
    if remainder > 0:
        shuffled[-remainder:] = base_signal[-remainder:]
    std_val = np.std(shuffled)
    return shuffled / std_val if std_val > 0 else shuffled

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
    std_val = np.std(surr)
    return surr / std_val if std_val > 0 else surr

def generate_iaaft(base_signal, seed, max_iter=100):
    np.random.seed(seed)
    x = np.array(base_signal, dtype=float)
    n = len(x)
    x_sorted = np.sort(x)
    x_fft = np.fft.rfft(x)
    amplitudes = np.abs(x_fft)
    y = np.random.permutation(x)
    
    for _ in range(max_iter):
        y_fft = np.fft.rfft(y)
        phases = np.angle(y_fft)
        y_fft_new = amplitudes * np.exp(1j * phases)
        s = np.fft.irfft(y_fft_new, n=n)
        s_ranks = np.argsort(np.argsort(s))
        y_next = x_sorted[s_ranks]
        if np.array_equal(y, y_next):
            break
        y = y_next
    std_val = np.std(y)
    return y / std_val if std_val > 0 else y

# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def extract_embeddings_for_signal(x_signal, dt=0.01):
    trajectory_length = len(x_signal)
    window_size = min(max(500, int(trajectory_length * 0.1)), 2000)
    stride = max(1, min(window_size // 2, (trajectory_length - window_size) // 330))

    # V3 feature order
    V3_KEYS = [
        "perm_entropy", "spectral_entropy", "svd_entropy",
        "fractal_dim", "autocorr_decay", "robust_skewness",
        "robust_kurtosis", "temporal_irreversibility"
    ]

    embeddings = []
    start = 0
    while start + window_size <= trajectory_length:
        x_window = x_signal[start:start + window_size]
        emb = compute_embedding_vector(x_window, dt)

        for k in emb:
            if not np.isfinite(emb[k]):
                emb[k] = 0.0

        vector = [emb[k] for k in V3_KEYS]
        embeddings.append(vector)
        start += stride
    return embeddings

def worker_run_config(params):
    """
    Multiprocessing worker to simulate a trajectory and extract sliding window features.
    """
    sys_type, name, noise, seed = params
    try:
        dt = 0.01
        if sys_type == "physical":
            x_signal, dt = simulate_system(name, noise, seed)
            if x_signal is None:
                return (sys_type, name, noise, seed, None)
            embeddings = extract_embeddings_for_signal(x_signal, dt)
            return (sys_type, name, noise, seed, embeddings)
        
        elif sys_type == "null":
            length = 25000
            
            # Generate clean null signal
            if name in ["phase_surrogate", "iaaft_surrogate", "shuffled_blocks"]:
                x_clean, dt = simulate_system("lorenz", 0.0, seed)
                if x_clean is None:
                    return (sys_type, name, noise, seed, None)
                if name == "phase_surrogate":
                    x_base = generate_phase_randomized(x_clean, seed)
                elif name == "iaaft_surrogate":
                    x_base = generate_iaaft(x_clean, seed)
                else:
                    x_base = generate_shuffled_blocks(x_clean, seed)
            else:
                if name == "white_noise":
                    x_base = generate_white_noise(length, seed)
                elif name == "pink_noise":
                    x_base = generate_pink_noise(length, seed)
                elif name == "brown_noise":
                    x_base = generate_brown_noise(length, seed)
                elif name == "random_walk":
                    x_base = generate_random_walk(length, seed)
                elif name == "ar1":
                    x_base = generate_ar1(length, seed)
                elif name == "ou":
                    x_base = generate_ou(length, seed)
                elif name == "logistic_map":
                    x_base = generate_logistic_map_null(length, seed)
                    dt = 1.0
                else:
                    return (sys_type, name, noise, seed, None)
            
            # Inject noise symmetrically
            if noise > 0.0:
                noise_std = noise * np.std(x_base)
                np.random.seed(seed)
                x_noisy = x_base + np.random.normal(0, noise_std, len(x_base))
            else:
                x_noisy = x_base
                
            embeddings = extract_embeddings_for_signal(x_noisy, dt)
            return (sys_type, name, noise, seed, embeddings)
            
    except Exception as e:
        return (sys_type, name, noise, seed, None)

def compute_topological_metrics(pts_arr):
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
        "cluster_count": int(cluster_count)
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

def bootstrap_ci(data, conf_level=0.95, n_resamples=1000, seed=42):
    np.random.seed(seed)
    n = len(data)
    boot_means = []
    for _ in range(n_resamples):
        sample = np.random.choice(data, size=n, replace=True)
        boot_means.append(np.mean(sample))
    lower = np.percentile(boot_means, (1.0 - conf_level) / 2.0 * 100)
    upper = np.percentile(boot_means, (1.0 + conf_level) / 2.0 * 100)
    return float(np.mean(data)), float(lower), float(upper)

def compute_distance_correlation(X, Y):
    X = np.atleast_2d(X)
    Y = np.atleast_2d(Y)
    n = X.shape[0]
    if n < 2:
        return 0.0
    from scipy.spatial.distance import pdist, squareform
    A = squareform(pdist(X))
    B = squareform(pdist(Y))
    A_row_mean = A.mean(axis=1, keepdims=True)
    A_col_mean = A.mean(axis=0, keepdims=True)
    A_grand_mean = A.mean()
    a = A - A_row_mean - A_col_mean + A_grand_mean
    B_row_mean = B.mean(axis=1, keepdims=True)
    B_col_mean = B.mean(axis=0, keepdims=True)
    B_grand_mean = B.mean()
    b = B - B_row_mean - B_col_mean + B_grand_mean
    dcov2 = np.maximum(0.0, np.sum(a * b) / (n * n))
    dvarx2 = np.maximum(0.0, np.sum(a * a) / (n * n))
    dvary2 = np.maximum(0.0, np.sum(b * b) / (n * n))
    denominator = np.sqrt(dvarx2 * dvary2)
    if denominator <= 1e-12:
        return 0.0
    dcor = np.sqrt(dcov2 / denominator)
    return float(dcor)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN AUDIT SUITE
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("🕵️‍♂️ RUNNING ADVERSARIAL SCIENTIFIC AUDIT (FASE 5.5)")
    print("=" * 65)

    # 1. BUILD SIMULATION TASKS (Primary 10 seeds)
    physical_systems = ["lorenz", "rossler"]
    system_configs = {
        "lorenz": LORENZ_NOISE,
        "rossler": ROSSLER_NOISE
    }
    
    null_models = [
        "white_noise", "pink_noise", "brown_noise", "random_walk",
        "ar1", "phase_surrogate", "iaaft_surrogate", "logistic_map",
        "shuffled_blocks", "ou"
    ]
    
    tasks = []
    # Physical system tasks
    for sys in physical_systems:
        for seed in SEEDS_10:
            for noise in system_configs[sys]:
                tasks.append(("physical", sys, noise, seed))
                
    # Null model tasks (use ROSSLER_NOISE levels as default sweep)
    for nm in null_models:
        for seed in SEEDS_10:
            for noise in ROSSLER_NOISE:
                tasks.append(("null", nm, noise, seed))
                
    print(f"Generated {len(tasks)} simulation/extraction configurations.")
    print("Executing sweep in parallel...")
    
    physical_data = {sys: {} for sys in physical_systems}
    null_data = {nm: {} for nm in null_models}
    
    # Run tasks with ProcessPoolExecutor
    t0 = time.time()
    num_cpus = os.cpu_count() or 4
    workers = min(num_cpus, 12)
    print(f"Spawning ProcessPoolExecutor with {workers} workers...")
    
    completed_count = 0
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(worker_run_config, t): t for t in tasks}
        for fut in as_completed(futures):
            t = futures[fut]
            sys_type, name, noise, seed, embs = fut.result()
            if embs is not None:
                if sys_type == "physical":
                    physical_data[name][(noise, seed)] = embs
                else:
                    null_data[name][(noise, seed)] = embs
            completed_count += 1
            if completed_count % 200 == 0:
                print(f"  Processed {completed_count}/{len(tasks)} runs...")
                
    print(f"Simulation sweep finished in {time.time() - t0:.2f} seconds.")

    # Check that data is collected
    for sys in physical_systems:
        print(f"  System '{sys}': collected {len(physical_data[sys])} configurations.")
    for nm in null_models:
        print(f"  Null model '{nm}': collected {len(null_data[nm])} configurations.")

    print("\nStarting Audit Suite...")
    
    audit_results = {}
    global_passed = True
    global_reasons = []

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 1 — TRUE DIMENSIONALITY REDUCTION AUDIT
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n--- Running Test 1: True Dimensionality Reduction ---")
    # Subsample physical data to make UMAP/t-SNE grids run fast
    # Group physical data by system
    test1_passed = True
    test1_details = {}
    
    for sys in physical_systems:
        configs = sorted(list(physical_data[sys].keys()))
        all_pts = []
        point_metadata = []
        
        for noise, seed in configs:
            embs = physical_data[sys][(noise, seed)]
            all_pts.extend(embs)
            point_metadata.extend([(noise, seed)] * len(embs))
            
        X = np.array(all_pts, dtype=float)
        X = np.nan_to_num(X, nan=0.0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Subsample to 1000 points
        np.random.seed(42)
        idx_sub = np.random.choice(len(X_scaled), min(len(X_scaled), 1000), replace=False)
        X_sub_scaled = X_scaled[idx_sub]
        meta_sub = [point_metadata[i] for i in idx_sub]
        
        # Reference PCA on the subsample
        pca = PCA(n_components=2)
        X_sub_pca = pca.fit_transform(X_sub_scaled)
        
        # Calculate PCA topological metrics for evaluation
        # Group points by noise level in the subsample
        noise_groups_pca = {}
        for idx, (noise, seed) in enumerate(meta_sub):
            if noise not in noise_groups_pca:
                noise_groups_pca[noise] = []
            noise_groups_pca[noise].append(X_sub_pca[idx])
            
        pca_noise_metrics = {}
        for noise, pts in noise_groups_pca.items():
            pca_noise_metrics[noise] = compute_topological_metrics(np.array(pts))
            
        # 1.1 UMAP parameter sweep
        umap_sweep_results = []
        n_neighbors_vals = [15, 30, 50, 100]
        min_dist_vals = [0.01, 0.1, 0.5]
        
        print(f"  Running UMAP sweep (12 configurations) for {sys}...")
        for nn in n_neighbors_vals:
            for md in min_dist_vals:
                # Fit UMAP with random init and 500 epochs
                umap_model = umap.UMAP(
                    n_components=2,
                    n_neighbors=nn,
                    min_dist=md,
                    n_epochs=500,
                    init="random",
                    random_state=42
                )
                X_sub_umap = umap_model.fit_transform(X_sub_scaled)
                
                # Pairwise distance correlation
                dist_corr = compute_distance_correlation(X_sub_scaled, X_sub_umap)
                # Trustworthiness & Continuity
                t_val = float(trustworthiness(X_sub_scaled, X_sub_umap, n_neighbors=15))
                c_val = float(trustworthiness(X_sub_umap, X_sub_scaled, n_neighbors=15))
                
                # Compute UMAP topological metrics
                noise_groups_umap = {}
                for idx, (noise, seed) in enumerate(meta_sub):
                    if noise not in noise_groups_umap:
                        noise_groups_umap[noise] = []
                    noise_groups_umap[noise].append(X_sub_umap[idx])
                    
                umap_noise_metrics = {}
                for noise, pts in noise_groups_umap.items():
                    umap_noise_metrics[noise] = compute_topological_metrics(np.array(pts))
                    
                # Correlation of topological metrics with PCA
                noises = sorted(list(pca_noise_metrics.keys()))
                pca_covs = [pca_noise_metrics[n]["covariance_determinant"] for n in noises]
                umap_covs = [umap_noise_metrics[n]["covariance_determinant"] for n in noises]
                pca_nns = [pca_noise_metrics[n]["nearest_neighbor_distance_mean"] for n in noises]
                umap_nns = [umap_noise_metrics[n]["nearest_neighbor_distance_mean"] for n in noises]
                
                rho_cov, _ = spearmanr(pca_covs, umap_covs)
                rho_nn, _ = spearmanr(pca_nns, umap_nns)
                
                # Correlation with noise
                rho_noise_cov, _ = spearmanr(noises, umap_covs)
                rho_noise_nn, _ = spearmanr(noises, umap_nns)
                
                umap_sweep_results.append({
                    "n_neighbors": nn,
                    "min_dist": md,
                    "pairwise_distance_correlation": dist_corr,
                    "trustworthiness": t_val,
                    "continuity": c_val,
                    "PCA_UMAP_spearman_cov_det": float(rho_cov) if np.isfinite(rho_cov) else 0.0,
                    "PCA_UMAP_spearman_nn_mean": float(rho_nn) if np.isfinite(rho_nn) else 0.0,
                    "noise_spearman_cov_det": float(rho_noise_cov) if np.isfinite(rho_noise_cov) else 0.0,
                    "noise_spearman_nn_mean": float(rho_noise_nn) if np.isfinite(rho_noise_nn) else 0.0
                })
                
        # 1.2 t-SNE parameter sweep
        tsne_sweep_results = []
        perplexity_vals = [20, 30, 50]
        
        print(f"  Running t-SNE sweep (3 configurations) for {sys}...")
        for perp in perplexity_vals:
            tsne_model = TSNE(
                n_components=2,
                perplexity=perp,
                learning_rate="auto",
                max_iter=1500,
                init="random",
                random_state=42
            )
            X_sub_tsne = tsne_model.fit_transform(X_sub_scaled)
            
            dist_corr = compute_distance_correlation(X_sub_scaled, X_sub_tsne)
            t_val = float(trustworthiness(X_sub_scaled, X_sub_tsne, n_neighbors=15))
            c_val = float(trustworthiness(X_sub_tsne, X_sub_scaled, n_neighbors=15))
            
            # Compute t-SNE topological metrics
            noise_groups_tsne = {}
            for idx, (noise, seed) in enumerate(meta_sub):
                if noise not in noise_groups_tsne:
                    noise_groups_tsne[noise] = []
                noise_groups_tsne[noise].append(X_sub_tsne[idx])
                
            tsne_noise_metrics = {}
            for noise, pts in noise_groups_tsne.items():
                tsne_noise_metrics[noise] = compute_topological_metrics(np.array(pts))
                
            # Correlation of topological metrics with PCA
            noises = sorted(list(pca_noise_metrics.keys()))
            pca_covs = [pca_noise_metrics[n]["covariance_determinant"] for n in noises]
            tsne_covs = [tsne_noise_metrics[n]["covariance_determinant"] for n in noises]
            pca_nns = [pca_noise_metrics[n]["nearest_neighbor_distance_mean"] for n in noises]
            tsne_nns = [tsne_noise_metrics[n]["nearest_neighbor_distance_mean"] for n in noises]
            
            rho_cov, _ = spearmanr(pca_covs, tsne_covs)
            rho_nn, _ = spearmanr(pca_nns, tsne_nns)
            
            # Correlation with noise
            rho_noise_cov, _ = spearmanr(noises, tsne_covs)
            rho_noise_nn, _ = spearmanr(noises, tsne_nns)
            
            tsne_sweep_results.append({
                "perplexity": perp,
                "pairwise_distance_correlation": dist_corr,
                "trustworthiness": t_val,
                "continuity": c_val,
                "PCA_tSNE_spearman_cov_det": float(rho_cov) if np.isfinite(rho_cov) else 0.0,
                "PCA_tSNE_spearman_nn_mean": float(rho_nn) if np.isfinite(rho_nn) else 0.0,
                "noise_spearman_cov_det": float(rho_noise_cov) if np.isfinite(rho_noise_cov) else 0.0,
                "noise_spearman_nn_mean": float(rho_noise_nn) if np.isfinite(rho_noise_nn) else 0.0
            })
            
        # Criterio: UMAP & t-SNE Spearman with noise must maintain strong negative correlation (|rho| > 0.75) on average
        mean_umap_noise_rho = np.mean([abs(r["noise_spearman_cov_det"]) for r in umap_sweep_results])
        mean_tsne_noise_rho = np.mean([abs(r["noise_spearman_cov_det"]) for r in tsne_sweep_results])
        
        print(f"    {sys} Mean UMAP noise rho: {mean_umap_noise_rho:.4f}")
        print(f"    {sys} Mean t-SNE noise rho: {mean_tsne_noise_rho:.4f}")
        
        if mean_umap_noise_rho < 0.75:
            test1_passed = False
            global_reasons.append(f"Test 1: UMAP projections for '{sys}' show weak average correlation with noise ({mean_umap_noise_rho:.4f} < 0.75)")
        if mean_tsne_noise_rho < 0.75:
            test1_passed = False
            global_reasons.append(f"Test 1: t-SNE projections for '{sys}' show weak average correlation with noise ({mean_tsne_noise_rho:.4f} < 0.75)")
            
        test1_details[sys] = {
            "umap_sweep": umap_sweep_results,
            "tsne_sweep": tsne_sweep_results,
            "mean_umap_noise_rho": float(mean_umap_noise_rho),
            "mean_tsne_noise_rho": float(mean_tsne_noise_rho)
        }
        
    audit_results["test1_dimensionality_reduction"] = {
        "status": "PASSED" if test1_passed else "FAILED",
        "details": test1_details
    }
    if not test1_passed:
        global_passed = False
        print("  ❌ TEST 1 FAILED")
    else:
        print("  ✅ TEST 1 PASSED")

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 2 — NULL MODEL PURITY AUDIT
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n--- Running Test 2: Null Model Purity Audit ---")
    test2_passed = True
    test2_details = {}
    p_value_records = []
    
    # Extract topological metrics for all null models
    null_projections = {nm: {} for nm in null_models}
    for nm in null_models:
        all_pts = []
        configs = sorted(list(null_data[nm].keys()))
        snapshot_slices = []
        current_idx = 0
        for noise, seed in configs:
            embs = null_data[nm][(noise, seed)]
            all_pts.extend(embs)
            snapshot_slices.append(((noise, seed), current_idx, current_idx + len(embs)))
            current_idx += len(embs)
            
        X_nm = np.array(all_pts, dtype=float)
        X_nm = np.nan_to_num(X_nm, nan=0.0)
        scaler_nm = StandardScaler()
        X_nm_scaled = scaler_nm.fit_transform(X_nm)
        
        pca_nm = PCA(n_components=2)
        X_nm_pca = pca_nm.fit_transform(X_nm_scaled)
        
        for cfg, start, end in snapshot_slices:
            pts_pca = X_nm_pca[start:end]
            null_projections[nm][cfg] = compute_topological_metrics(pts_pca)
            
    # Process physical systems under reference PCA to compare p-values
    physical_projections = {sys: {} for sys in physical_systems}
    for sys in physical_systems:
        all_pts = []
        configs = sorted(list(physical_data[sys].keys()))
        snapshot_slices = []
        current_idx = 0
        for noise, seed in configs:
            embs = physical_data[sys][(noise, seed)]
            all_pts.extend(embs)
            snapshot_slices.append(((noise, seed), current_idx, current_idx + len(embs)))
            current_idx += len(embs)
            
        X_phys = np.array(all_pts, dtype=float)
        X_phys = np.nan_to_num(X_phys, nan=0.0)
        scaler_phys = StandardScaler()
        X_phys_scaled = scaler_phys.fit_transform(X_phys)
        
        pca_phys = PCA(n_components=2)
        X_phys_pca = pca_phys.fit_transform(X_phys_scaled)
        
        for cfg, start, end in snapshot_slices:
            pts_pca = X_phys_pca[start:end]
            physical_projections[sys][cfg] = compute_topological_metrics(pts_pca)
            
    # 2.1 Calculate Spearman and Cohen's d for null models and physical systems
    for sys in physical_systems:
        noises = system_configs[sys]
        for metric in ["covariance_determinant", "nearest_neighbor_distance_mean"]:
            metric_means = []
            for n in noises:
                vals = [physical_projections[sys][(n, s)][metric] for s in SEEDS_10]
                metric_means.append(np.mean(vals))
            rho, pval = spearmanr(noises, metric_means)
            if not np.isfinite(rho): rho = 0.0
            if not np.isfinite(pval): pval = 1.0
            
            # Cohen's d
            vals_base = [physical_projections[sys][(0.0, s)][metric] for s in SEEDS_10]
            vals_max = [physical_projections[sys][(max(noises), s)][metric] for s in SEEDS_10]
            d_val = compute_cohens_d(vals_base, vals_max)
            
            p_value_records.append({
                "type": "physical",
                "name": sys,
                "metric": metric,
                "rho": float(rho),
                "pval": float(pval),
                "cohen_d": float(d_val)
            })
            
    for nm in null_models:
        for metric in ["covariance_determinant", "nearest_neighbor_distance_mean"]:
            metric_means = []
            for n in ROSSLER_NOISE:
                vals = [null_projections[nm][(n, s)][metric] for s in SEEDS_10]
                metric_means.append(np.mean(vals))
            rho, pval = spearmanr(ROSSLER_NOISE, metric_means)
            if not np.isfinite(rho): rho = 0.0
            if not np.isfinite(pval): pval = 1.0
            
            vals_base = [null_projections[nm][(0.0, s)][metric] for s in SEEDS_10]
            vals_max = [null_projections[nm][(max(ROSSLER_NOISE), s)][metric] for s in SEEDS_10]
            d_val = compute_cohens_d(vals_base, vals_max)
            
            p_value_records.append({
                "type": "null",
                "name": nm,
                "metric": metric,
                "rho": float(rho),
                "pval": float(pval),
                "cohen_d": float(d_val)
            })

    # Apply BH Correction
    raw_p_values = [r["pval"] for r in p_value_records]
    adjusted_p_values = benjamini_hochberg(raw_p_values)
    for idx, adj_p in enumerate(adjusted_p_values):
        p_value_records[idx]["adjusted_p"] = adj_p

    # Print Null Model Table and check bounds
    print(f"\n    {'System/Null':<18} | {'Metric':<30} | {'Spearman rho':<12} | {'adjusted_p':<12} | {'Cohen_d':<8}")
    print("    " + "-" * 91)
    
    physical_results_summary = {}
    null_results_summary = {}
    
    for r in p_value_records:
        name = r["name"]
        metric = r["metric"]
        rho = r["rho"]
        adj_p = r["adjusted_p"]
        d = r["cohen_d"]
        
        print(f"    {name:<18} | {metric:<30} | {rho:12.4f} | {adj_p:12.4e} | {d:8.4f}")
        
        if r["type"] == "physical":
            if name not in physical_results_summary:
                physical_results_summary[name] = {}
            physical_results_summary[name][metric] = {
                "rho": rho, "adjusted_p": adj_p, "cohen_d": d
            }
        else:
            if name not in null_results_summary:
                null_results_summary[name] = {}
            null_results_summary[name][metric] = {
                "rho": rho, "adjusted_p": adj_p, "cohen_d": d
            }
            
            # Criterio: Ningún modelo nulo debe pasar simultáneamente |rho|>0.8, adjusted_p<0.05, Cohen_d>0.8
            # Note: We take absolute value of rho to test for monotonic drift in either direction
            if abs(rho) > 0.8 and adj_p < 0.05 and d > 0.8:
                test2_passed = False
                global_reasons.append(f"Test 2: Null model '{name}' passed physical threshold for '{metric}' (rho={rho:.4f}, p_adj={adj_p:.4e}, d={d:.4f})")

    audit_results["test2_null_purity"] = {
        "status": "PASSED" if test2_passed else "FAILED",
        "physical_systems": physical_results_summary,
        "null_models": null_results_summary
    }
    if not test2_passed:
        global_passed = False
        print("  ❌ TEST 2 FAILED")
    else:
        print("  ✅ TEST 2 PASSED")

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 3 — FEATURE LEAKAGE AUDIT
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n--- Running Test 3: Feature Leakage Audit ---")
    test3_passed = True
    test3_details = {}
    
    # V3 feature names (8 amplitude-invariant features, no lyapunov_max placeholder)
    feature_names = [
        "perm_entropy", "spectral_entropy", "svd_entropy",
        "fractal_dim", "autocorr_decay", "robust_skewness",
        "robust_kurtosis", "temporal_irreversibility"
    ]
    
    for sys in physical_systems:
        print(f"  Auditing feature leakage for {sys}...")
        configs = sorted(list(physical_data[sys].keys()))
        all_feats = []
        noises = []
        
        for noise, seed in configs:
            embs = physical_data[sys][(noise, seed)]
            for e in embs:
                # V3: all 8 columns are meaningful, no zero-padded lyapunov_max at index 0
                all_feats.append(e)
                noises.append(noise)
                
        X_feats = np.array(all_feats, dtype=float)
        X_feats = np.nan_to_num(X_feats, nan=0.0)
        y_noise = np.array(noises, dtype=float)
        
        # Calculate Spearman correlation for each feature with noise
        spearmans = {}
        for idx, feat_name in enumerate(feature_names):
            rho, _ = spearmanr(X_feats[:, idx], y_noise)
            spearmans[feat_name] = float(rho) if np.isfinite(rho) else 0.0
            
        # Calculate Mutual Information
        mi = mutual_info_regression(X_feats, y_noise, random_state=42)
        mi_dict = {feat_name: float(m) for feat_name, m in zip(feature_names, mi)}
        
        # Calculate Random Forest Importance
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X_feats, y_noise)
        importances = rf.feature_importances_
        imp_dict = {feat_name: float(imp) for feat_name, imp in zip(feature_names, importances)}
        
        # Criterio: Ninguna feature debe explicar >70% (0.70) del efecto
        max_imp = max(importances)
        max_imp_feat = feature_names[np.argmax(importances)]
        print(f"    Max feature importance for {sys}: {max_imp_feat} ({max_imp:.4f})")
        
        if max_imp > 0.70:
            test3_passed = False
            global_reasons.append(f"Test 3: Feature '{max_imp_feat}' in system '{sys}' has excessive importance ({max_imp:.4f} > 0.70)")
            
        test3_details[sys] = {
            "spearman": spearmans,
            "mutual_information": mi_dict,
            "rf_importance": imp_dict,
            "max_importance_value": float(max_imp),
            "max_importance_feature": max_imp_feat
        }
        
    audit_results["test3_feature_leakage"] = {
        "status": "PASSED" if test3_passed else "FAILED",
        "details": test3_details
    }
    if not test3_passed:
        global_passed = False
        print("  ❌ TEST 3 FAILED")
    else:
        print("  ✅ TEST 3 PASSED")

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 4 — SCALE NORMALIZATION AUDIT
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n--- Running Test 4: Scale Normalization Audit ---")
    test4_passed = True
    test4_details = {}
    
    scalers = {
        "Raw": None,
        "Z-score": StandardScaler(),
        "RobustScaler": RobustScaler(),
        "MinMax": MinMaxScaler(),
        "QuantileTransform": QuantileTransformer(n_quantiles=100, random_state=42)
    }
    
    for scaler_name, scaler_obj in scalers.items():
        print(f"  Evaluating scale normalization: {scaler_name}...")
        test4_details[scaler_name] = {}
        
        for sys in physical_systems:
            configs = sorted(list(physical_data[sys].keys()))
            all_pts = []
            snapshot_slices = []
            current_idx = 0
            for noise, seed in configs:
                embs = physical_data[sys][(noise, seed)]
                all_pts.extend(embs)
                snapshot_slices.append(((noise, seed), current_idx, current_idx + len(embs)))
                current_idx += len(embs)
                
            X_raw = np.array(all_pts, dtype=float)
            X_raw = np.nan_to_num(X_raw, nan=0.0)
            
            # Apply scaler
            if scaler_obj is not None:
                X_scaled = scaler_obj.fit_transform(X_raw)
            else:
                X_scaled = X_raw
                
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_scaled)
            
            # Compute topological metrics
            proj_metrics = {}
            for cfg, start, end in snapshot_slices:
                proj_metrics[cfg] = compute_topological_metrics(X_pca[start:end])
                
            # Compute Spearman correlation and Cohen's d
            noises = system_configs[sys]
            system_metrics_res = {}
            
            for metric in ["covariance_determinant", "nearest_neighbor_distance_mean"]:
                metric_means = []
                for n in noises:
                    vals = [proj_metrics[(n, s)][metric] for s in SEEDS_10]
                    metric_means.append(np.mean(vals))
                rho, pval = spearmanr(noises, metric_means)
                if not np.isfinite(rho): rho = 0.0
                if not np.isfinite(pval): pval = 1.0
                
                vals_base = [proj_metrics[(0.0, s)][metric] for s in SEEDS_10]
                vals_max = [proj_metrics[(max(noises), s)][metric] for s in SEEDS_10]
                d_val = compute_cohens_d(vals_base, vals_max)
                
                system_metrics_res[metric] = {
                    "spearman_rho": float(rho),
                    "spearman_pvalue": float(pval),
                    "cohen_d": float(d_val)
                }
                
                # Criterio: El fenómeno debe persistir (|rho| > 0.8, p < 0.05, d > 0.8)
                if abs(rho) <= 0.8 or pval >= 0.05 or d_val <= 0.8:
                    test4_passed = False
                    global_reasons.append(f"Test 4: System '{sys}' failed validation under {scaler_name} scaling for '{metric}' (rho={rho:.4f}, p={pval:.4e}, d={d_val:.4f})")
                    
            test4_details[scaler_name][sys] = system_metrics_res
            
    audit_results["test4_scale_normalization"] = {
        "status": "PASSED" if test4_passed else "FAILED",
        "details": test4_details
    }
    if not test4_passed:
        global_passed = False
        print("  ❌ TEST 4 FAILED")
    else:
        print("  ✅ TEST 4 PASSED")

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 5 — SEED ROBUSTNESS (100 Seeds Sweep)
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n--- Running Test 5: Seed Robustness (100 Seeds Sweep) ---")
    # Generamos los indices de 100 semillas
    # 3 seeds iniciales, 10 seeds de causal robustness, mas adicionales para completar 100
    seeds_100 = list(SEEDS_10)
    current_seed = 200
    while len(seeds_100) < 100:
        if current_seed not in seeds_100:
            seeds_100.append(current_seed)
        current_seed += 1
        
    print(f"Generated list of 100 unique seeds. Simulating physical systems over all 100 seeds...")
    
    # We build sweep tasks specifically for seeds 11 to 100 (additional 90 seeds)
    additional_seeds = seeds_100[10:]
    test5_tasks = []
    for sys in physical_systems:
        for seed in additional_seeds:
            for noise in system_configs[sys]:
                test5_tasks.append(("physical", sys, noise, seed))
                
    print(f"Simulating additional {len(test5_tasks)} configurations to complete 100 seeds...")
    
    # Reuse physical data from SEEDS_10
    physical_data_100 = {sys: {} for sys in physical_systems}
    for sys in physical_systems:
        for cfg, embs in physical_data[sys].items():
            physical_data_100[sys][cfg] = embs
            
    # Run additional seeds in parallel
    t0 = time.time()
    completed_count = 0
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(worker_run_config, t): t for t in test5_tasks}
        for fut in as_completed(futures):
            t = futures[fut]
            sys_type, name, noise, seed, embs = fut.result()
            if embs is not None:
                physical_data_100[name][(noise, seed)] = embs
            completed_count += 1
            if completed_count % 300 == 0:
                print(f"  Processed {completed_count}/{len(test5_tasks)} runs...")
                
    print(f"Additional simulations finished in {time.time() - t0:.2f} seconds.")
    
    # Perform validation per seed
    test5_passed = True
    test5_details = {}
    
    for sys in physical_systems:
        noises = system_configs[sys]
        print(f"  Computing PCA and topological metrics across 100 seeds for {sys}...")
        
        # Fit a single global scaler and PCA for this system over all 100 seeds to prevent axis flips
        all_pts = []
        configs_sorted = sorted(list(physical_data_100[sys].keys()))
        snapshot_slices = []
        current_idx = 0
        for noise, seed in configs_sorted:
            embs = physical_data_100[sys][(noise, seed)]
            all_pts.extend(embs)
            snapshot_slices.append(((noise, seed), current_idx, current_idx + len(embs)))
            current_idx += len(embs)
            
        X_100 = np.array(all_pts, dtype=float)
        X_100 = np.nan_to_num(X_100, nan=0.0)
        scaler = StandardScaler()
        X_100_scaled = scaler.fit_transform(X_100)
        
        pca = PCA(n_components=2)
        X_100_pca = pca.fit_transform(X_100_scaled)
        
        proj_metrics = {}
        for cfg, start, end in snapshot_slices:
            proj_metrics[cfg] = compute_topological_metrics(X_100_pca[start:end])
            
        test5_details[sys] = {}
        
        for metric in ["covariance_determinant", "nearest_neighbor_distance_mean"]:
            rhos_seed = []
            cohens_d_seed = []
            
            for seed in seeds_100:
                seed_noises = []
                seed_vals = []
                for n in noises:
                    if (n, seed) in proj_metrics:
                        seed_noises.append(n)
                        seed_vals.append(proj_metrics[(n, seed)][metric])
                if len(seed_noises) > 1:
                    rho, _ = spearmanr(seed_noises, seed_vals)
                    if np.isfinite(rho):
                        rhos_seed.append(rho)
                
                # Cohen's d for this seed
                if (0.0, seed) in proj_metrics and (max(noises), seed) in proj_metrics:
                    d_val = compute_cohens_d(
                        [proj_metrics[(0.0, seed)][metric]],
                        [proj_metrics[(max(noises), seed)][metric]]
                    )
                    cohens_d_seed.append(d_val)
                    
            # Compute bootstrap confidence intervals
            rho_mean, rho_lower, rho_upper = bootstrap_ci(rhos_seed)
            d_mean, d_lower, d_upper = bootstrap_ci(cohens_d_seed)
            
            print(f"    Metric '{metric}':")
            print(f"      Spearman rho: {rho_mean:.4f} (95% CI: [{rho_lower:.4f}, {rho_upper:.4f}])")
            print(f"      Cohen's d:    {d_mean:.4f} (95% CI: [{d_lower:.4f}, {d_upper:.4f}])")
            
            # Criterio: Intervalo de confianza no debe cruzar rho=0.8
            # The absolute value of the lower/upper bounds must be > 0.8
            # For negative correlations (like covariance_determinant shrinking with noise), we check if the CI is strictly below -0.8
            if rho_mean < 0:
                if rho_upper > -0.8:
                    test5_passed = False
                    global_reasons.append(f"Test 5: System '{sys}' metric '{metric}' 95% CI for rho crossed -0.8 ([{rho_lower:.4f}, {rho_upper:.4f}])")
            else:
                if rho_lower < 0.8:
                    test5_passed = False
                    global_reasons.append(f"Test 5: System '{sys}' metric '{metric}' 95% CI for rho crossed 0.8 ([{rho_lower:.4f}, {rho_upper:.4f}])")
                    
            test5_details[sys][metric] = {
                "spearman_rho": {
                    "mean": rho_mean, "lower": rho_lower, "upper": rho_upper
                },
                "cohen_d": {
                    "mean": d_mean, "lower": d_lower, "upper": d_upper
                }
            }
            
    audit_results["test5_seed_robustness"] = {
        "status": "PASSED" if test5_passed else "FAILED",
        "details": test5_details
    }
    if not test5_passed:
        global_passed = False
        print("  ❌ TEST 5 FAILED")
    else:
        print("  ✅ TEST 5 PASSED")

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 6 — BLIND LABEL TEST
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n--- Running Test 6: Blind Label Test ---")
    try:
        import traceback as _tb_module
        X_phys_list = []
        for sys in physical_systems:
            for cfg, embs in physical_data[sys].items():
                X_phys_list.extend(embs)

        X_null_list = []
        for nm in null_models:
            for cfg, embs in null_data[nm].items():
                X_null_list.extend(embs)

        X_phys_arr = np.array(X_phys_list, dtype=float)
        X_null_arr = np.array(X_null_list, dtype=float)

        # Subsample to keep memory and compute footprints low
        np.random.seed(42)
        n_samples = min(len(X_phys_arr), len(X_null_arr), 10000)
        idx_phys = np.random.choice(len(X_phys_arr), n_samples, replace=False)
        idx_null = np.random.choice(len(X_null_arr), n_samples, replace=False)

        # V3: all 8 columns are valid features — use full vector
        X_class = np.vstack([X_phys_arr[idx_phys], X_null_arr[idx_null]])
        y_class = np.hstack([np.ones(n_samples), np.zeros(n_samples)])

        # Split train/test (70/30)
        X_train, X_test, y_train, y_test = train_test_split(
            X_class, y_class, test_size=0.3, random_state=42
        )

        # ── Single-class guard ──────────────────────────────────────────────
        unique_test_classes = np.unique(y_test)
        if len(unique_test_classes) < 2:
            print(f"  [INVALID_SPLIT] Test set contains only classes: {unique_test_classes.tolist()}")
            print("  Cannot compute ROC AUC on a single-class test set.")
            audit_results["test6_blind_label"] = {
                "status": "INVALID_SPLIT",
                "reason": f"single-class test set: classes={unique_test_classes.tolist()}",
                "roc_auc": None,
                "precision": None,
                "recall": None,
                "f1": None,
                "confusion_matrix": None
            }
            global_passed = False
            global_reasons.append("Test 6: INVALID_SPLIT — single-class test set. Cannot evaluate classifier.")
            print("  ❌ TEST 6 FAILED (INVALID_SPLIT)")
        else:
            # Train RandomForestClassifier
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X_train, y_train)

            y_pred = clf.predict(X_test)
            y_prob = clf.predict_proba(X_test)[:, 1]

            auc_score = float(roc_auc_score(y_test, y_prob))
            prec      = float(precision_score(y_test, y_pred, zero_division=0))
            rec       = float(recall_score(y_test, y_pred, zero_division=0))
            f1        = float(f1_score(y_test, y_pred, zero_division=0))
            cm        = confusion_matrix(y_test, y_pred).tolist()

            print(f"  Classifier ROC AUC:  {auc_score:.6f}")
            print(f"  Precision:           {prec:.6f}")
            print(f"  Recall:              {rec:.6f}")
            print(f"  F1-score:            {f1:.6f}")
            print(f"  Confusion matrix:    {cm}")

            test6_passed = auc_score > 0.85
            if not test6_passed:
                global_reasons.append(
                    f"Test 6: Classifier failed AUC > 0.85 threshold (AUC = {auc_score:.6f})"
                )
                global_passed = False
                print("  ❌ TEST 6 FAILED")
            else:
                print("  ✅ TEST 6 PASSED")

            audit_results["test6_blind_label"] = {
                "status": "PASSED" if test6_passed else "FAILED",
                "roc_auc": auc_score,
                "precision": prec,
                "recall": rec,
                "f1": f1,
                "confusion_matrix": cm
            }

    except SystemExit:
        raise
    except Exception as _exc:
        _tb_str = _tb_module.format_exc()
        print(f"  [ERROR] Test 6 raised an exception:\n{_tb_str}")
        audit_results["test6_blind_label"] = {
            "status": "ERROR",
            "exception": str(_exc),
            "traceback": _tb_str
        }
        global_passed = False
        global_reasons.append(f"Test 6: Exception — {str(_exc)}")
        print("  ❌ TEST 6 FAILED (EXCEPTION)")

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 7 — TEMPORAL GENERALIZATION TEST
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n--- Running Test 7: Temporal Generalization Test ---")
    test7_passed = True
    test7_details = {}
    
    for sys in physical_systems:
        print(f"  Evaluating temporal generalization for {sys}...")
        noises = system_configs[sys]
        test7_details[sys] = {}
        
        # We simulate 10 seeds first-third vs last-two-thirds
        # We need to collect window embeddings for first 1/3 and last 2/3
        train_emb_map = {}
        test_emb_map = {}
        
        all_train_pts = []
        train_snapshot_slices = []
        current_train_idx = 0
        
        all_test_pts = []
        test_snapshot_slices = []
        current_test_idx = 0
        
        for seed in SEEDS_10:
            for noise in noises:
                x_signal, dt = simulate_system(sys, noise, seed)
                if x_signal is None:
                    continue
                length = len(x_signal)
                
                # Split trajectory
                len_third = length // 3
                x_train = x_signal[:len_third]
                x_test = x_signal[len_third:]
                
                # Extract embeddings
                emb_tr = extract_embeddings_for_signal(x_train, dt)
                emb_te = extract_embeddings_for_signal(x_test, dt)
                
                train_emb_map[(noise, seed)] = emb_tr
                test_emb_map[(noise, seed)] = emb_te
                
                all_train_pts.extend(emb_tr)
                train_snapshot_slices.append(((noise, seed), current_train_idx, current_train_idx + len(emb_tr)))
                current_train_idx += len(emb_tr)
                
                all_test_pts.extend(emb_te)
                test_snapshot_slices.append(((noise, seed), current_test_idx, current_test_idx + len(emb_te)))
                current_test_idx += len(emb_te)
                
        # Fit scaler and PCA on the first 1/3 (train)
        X_train_raw = np.array(all_train_pts, dtype=float)
        X_train_raw = np.nan_to_num(X_train_raw, nan=0.0)
        scaler_temp = StandardScaler()
        X_train_scaled = scaler_temp.fit_transform(X_train_raw)
        
        pca_temp = PCA(n_components=2)
        X_train_pca = pca_temp.fit_transform(X_train_scaled)
        
        # Project the last 2/3 (test) using train PCA
        X_test_raw = np.array(all_test_pts, dtype=float)
        X_test_raw = np.nan_to_num(X_test_raw, nan=0.0)
        X_test_scaled = scaler_temp.transform(X_test_raw)
        X_test_pca = pca_temp.transform(X_test_scaled)
        
        # Calculate topological metrics on test projections
        test_proj_metrics = {}
        for cfg, start, end in test_snapshot_slices:
            pts_pca = X_test_pca[start:end]
            test_proj_metrics[cfg] = compute_topological_metrics(pts_pca)
            
        # Calculate Spearman correlation and Cohen's d for the test projections
        for metric in ["covariance_determinant", "nearest_neighbor_distance_mean"]:
            metric_means = []
            for n in noises:
                vals = [test_proj_metrics[(n, s)][metric] for s in SEEDS_10]
                metric_means.append(np.mean(vals))
            rho, pval = spearmanr(noises, metric_means)
            if not np.isfinite(rho): rho = 0.0
            if not np.isfinite(pval): pval = 1.0
            
            vals_base = [test_proj_metrics[(0.0, s)][metric] for s in SEEDS_10]
            vals_max = [test_proj_metrics[(max(noises), s)][metric] for s in SEEDS_10]
            d_val = compute_cohens_d(vals_base, vals_max)
            
            test7_details[sys][metric] = {
                "spearman_rho": float(rho),
                "spearman_pvalue": float(pval),
                "cohen_d": float(d_val)
            }
            
            # Criterio: El fenómeno debe persistir (|rho| > 0.8, p < 0.05, d > 0.8)
            if abs(rho) <= 0.8 or pval >= 0.05 or d_val <= 0.8:
                test7_passed = False
                global_reasons.append(f"Test 7: Out-of-sample temporal validation failed for system '{sys}' metric '{metric}' (rho={rho:.4f}, p={pval:.4e}, d={d_val:.4f})")
                
    audit_results["test7_temporal_generalization"] = {
        "status": "PASSED" if test7_passed else "FAILED",
        "details": test7_details
    }
    if not test7_passed:
        global_passed = False
        print("  ❌ TEST 7 FAILED")
    else:
        print("  ✅ TEST 7 PASSED")

    # ─────────────────────────────────────────────────────────────────────────────
    # CONSOLIDATE AND WRITE FINAL JSON REPORT
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n=================================================")
    print("🏁 CONSOLIDATING AUDIT REPORT AND GLOBAL STATUS")
    print("=================================================")
    
    report_data = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "approval_status": "PASSED" if global_passed else "FAILED",
            "approval_global": "PASSED" if global_passed else "FAILED",
            "global_failed_reasons": global_reasons
        },
        "audit_results": audit_results
    }
    
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
        
    print(f"\nSaved final adversarial audit report to: {REPORT_FILE}")
    
    if global_passed:
        print("\n✅ GLOBAL ADVERSARIAL AUDIT PASSED SUCCESSFULLY!")
        print("All stress-tests survived. The physical transition phenomenon is mathematically sound.")
        print("=" * 65)
        sys_module.exit(0)
    else:
        print("\n❌ GLOBAL ADVERSARIAL AUDIT FAILED!")
        for r in global_reasons:
            print(f"  - {r}")
        print("=" * 65)
        sys_module.exit(1)

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    main()
