import os
import sys
import sqlite3
import json
import numpy as np
from scipy.integrate import solve_ivp
from scipy.fft import fft, fftfreq
from scipy.spatial import ConvexHull
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(ROOT_DIR, "runs", "math_search.db")
OUTPUT_DIR = os.path.join(ROOT_DIR, "dashboard", "public", "artifacts", "embeddings")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "manifold_snapshots.json")

# ─────────────────────────────────────────────────────────────────────────────
# CONTINUOUS DYNAMICAL SYSTEM VECTOR FIELDS
# ─────────────────────────────────────────────────────────────────────────────

def lorenz_rhs(t, state):
    x, y, z = state
    return [10.0 * (y - x), x * (28.0 - z) - y, x * y - (8.0/3.0) * z]

def rossler_rhs(t, state):
    x, y, z = state
    return [-y - z, x + 0.2 * y, 0.2 + z * (x - 5.7)]

def chua_rhs(t, state):
    x, y, z = state
    alpha = 15.6
    beta = 28.0
    m0 = -1.143
    m1 = -0.714
    f_x = m1 * x + 0.5 * (m0 - m1) * (np.abs(x + 1.0) - np.abs(x - 1.0))
    return [alpha * (y - x - f_x), x - y + z, -beta * y]

def duffing_rhs(t, state):
    x, y = state
    return [y, x - x**3 - 0.3*y + 0.5*np.cos(1.2*t)]

def vanderpol_rhs(t, state):
    x, y = state
    mu = 5.0
    return [y, mu * (1 - x**2) * y - x]

def kuramoto_rhs(t, theta):
    N_osc = 5
    K = 2.0
    omega = np.array([0.5, 1.0, 1.5, 2.0, 2.5])
    dtheta = np.zeros(N_osc)
    for i in range(N_osc):
        dtheta[i] = omega[i] - (K / N_osc) * np.sum(np.sin(theta[i] - theta))
    return dtheta

# ─────────────────────────────────────────────────────────────────────────────
# SIMULATOR WRAPPER
# ─────────────────────────────────────────────────────────────────────────────

def simulate_system(system_name, noise, seed):
    """
    Simulates a dynamical system trajectory. Descards the transient part,
    injects Gaussian noise, and returns the 1D signal.
    """
    try:
        if system_name == "lorenz":
            t_span = (0, 300)
            t_eval = np.linspace(0, 300, 30000)
            dt = t_eval[1] - t_eval[0]
            sol = solve_ivp(lorenz_rhs, t_span, [1.0, 1.0, 1.0], t_eval=t_eval, method='RK45')
            x_signal = sol.y[0][5000:]
        elif system_name == "rossler":
            t_span = (0, 300)
            t_eval = np.linspace(0, 300, 30000)
            dt = t_eval[1] - t_eval[0]
            sol = solve_ivp(rossler_rhs, t_span, [1.0, 1.0, 1.0], t_eval=t_eval, method='RK45')
            x_signal = sol.y[0][5000:]
        elif system_name == "chua":
            t_span = (0, 300)
            t_eval = np.linspace(0, 300, 30000)
            dt = t_eval[1] - t_eval[0]
            sol = solve_ivp(chua_rhs, t_span, [0.1, 0.1, 0.1], t_eval=t_eval, method='RK45')
            x_signal = sol.y[0][5000:]
        elif system_name in ("duffing", "duffing_oscillator"):
            t_span = (0, 800)
            t_eval = np.linspace(0, 800, 80000)
            dt = t_eval[1] - t_eval[0]
            sol = solve_ivp(duffing_rhs, t_span, [0.1, 0.0], t_eval=t_eval, method='RK45')
            x_signal = sol.y[0][16000:]
        elif system_name == "van_der_pol":
            t_span = (0, 400)
            t_eval = np.linspace(0, 400, 60000)
            dt = t_eval[1] - t_eval[0]
            sol = solve_ivp(vanderpol_rhs, t_span, [0.5, 0.0], t_eval=t_eval, method='RK45')
            x_signal = sol.y[0][12000:]
        elif system_name == "kuramoto_model":
            t_span = (0, 400)
            t_eval = np.linspace(0, 400, 60000)
            dt = t_eval[1] - t_eval[0]
            np.random.seed(42)
            theta0 = np.random.uniform(0, 2*np.pi, 5)
            sol = solve_ivp(kuramoto_rhs, t_span, theta0, t_eval=t_eval, method='RK45')
            x_signal = np.abs(np.mean(np.exp(1j * sol.y[:, 12000:]), axis=0))
        elif system_name == "logistic_map":
            dt = 1.0
            r = 3.9
            fn = lambda x: r * x * (1 - x)
            N = 60000; x = 0.4
            for _ in range(5000): x = fn(x)
            series = []
            for _ in range(N): x = fn(x); series.append(x)
            x_signal = np.array(series[12000:])
        else:
            return None, 1.0
        
        # Inject noise safely
        if noise > 0.0:
            noise_std = noise * np.std(x_signal)
            np.random.seed(seed)
            x_signal = x_signal + np.random.normal(0, noise_std, len(x_signal))
            
        return x_signal, dt
    except Exception as e:
        print(f"  [ERROR] Simulation failed for {system_name} (noise={noise}, seed={seed}): {e}")
        return None, 1.0

# ─────────────────────────────────────────────────────────────────────────────
# EMBEDDING FEATURE EXTRACTION V3 — AMPLITUDE-INVARIANT DYNAMIC FEATURES
# ─────────────────────────────────────────────────────────────────────────────

# ── A1: Permutation Entropy (Bandt–Pompe) ──────────────────────────────────
def _permutation_entropy(x, m=5, delay=1):
    """
    Compute normalized Permutation Entropy (Bandt & Pompe 2002).
    Returns value in [0, 1]. Pure ordinal ranks → amplitude-invariant.
    """
    n = len(x)
    n_patterns = n - (m - 1) * delay
    if n_patterns <= 0:
        return 0.0
    # Build ordinal patterns
    from itertools import permutations as _perms
    import math
    perm_counts = {}
    for i in range(n_patterns):
        pattern = tuple(np.argsort(x[i:i + m * delay:delay]))
        perm_counts[pattern] = perm_counts.get(pattern, 0) + 1
    total = sum(perm_counts.values())
    if total == 0:
        return 0.0
    probs = np.array(list(perm_counts.values()), dtype=float) / total
    probs = probs[probs > 0]
    h = -np.sum(probs * np.log2(probs))
    h_max = np.log2(math.factorial(m))
    return float(h / h_max) if h_max > 0 else 0.0


# ── A2: Normalized Spectral Entropy ─────────────────────────────────────────
def _spectral_entropy_normalized(x, dt):
    """
    Shannon entropy of the normalized power spectral density.
    PSD is divided by its sum before computing entropy → amplitude-invariant.
    Returns value in [0, 1] (normalized by log2(N//2)).
    """
    N = len(x)
    yf = np.abs(fft(x)[:N // 2]) ** 2
    yf[0] = 0.0  # Remove DC component
    total = yf.sum()
    if total <= 0:
        return 0.0
    p = yf / total  # Normalize PSD
    p_pos = p[p > 0]
    h = -np.sum(p_pos * np.log2(p_pos))
    h_max = np.log2(len(yf)) if len(yf) > 1 else 1.0
    return float(h / h_max) if h_max > 0 else 0.0


# ── A3: SVD Entropy ──────────────────────────────────────────────────────────
def _svd_entropy(x, m=10, delay=1):
    """
    SVD entropy of the time-delay embedding matrix.
    Singular values are normalized before computing entropy → amplitude-invariant.
    """
    n = len(x)
    n_vecs = n - (m - 1) * delay
    if n_vecs <= 1:
        return 0.0
    # Center signal before building the time-delay matrix.
    # A constant offset (DC component) adds a rank-1 column that dominates
    # singular values and collapses entropy to near-zero, breaking offset invariance.
    x_c = x - x.mean()
    # Build embedding matrix (n_vecs × m)
    M = np.array([x_c[i:i + m * delay:delay] for i in range(n_vecs)])
    try:
        s = np.linalg.svd(M, compute_uv=False)
    except np.linalg.LinAlgError:
        return 0.0
    s_sum = s.sum()
    if s_sum <= 0:
        return 0.0
    lam = s / s_sum  # Normalized singular values
    lam_pos = lam[lam > 0]
    h = -np.sum(lam_pos * np.log(lam_pos))
    h_max = np.log(len(s)) if len(s) > 1 else 1.0
    return float(h / h_max) if h_max > 0 else 0.0


# ── A4: Higuchi Fractal Dimension (fallback: Katz FD) ───────────────────────
def _higuchi_fd(x, k_max=10):
    """
    Higuchi (1988) fractal dimension estimate.
    Amplitude-invariant: based on relative length ratios.
    """
    N = len(x)
    L_vals = []
    k_vals = []
    for k in range(1, k_max + 1):
        Lk_list = []
        for m in range(1, k + 1):
            # Sub-series length
            n_m = (N - m) // k
            if n_m < 1:
                continue
            indices = np.arange(0, n_m) * k + (m - 1)
            sub = x[indices]
            if len(sub) < 2:
                continue
            lm = np.sum(np.abs(np.diff(sub))) * (N - 1) / (k * n_m)
            Lk_list.append(lm)
        if Lk_list:
            L_vals.append(np.mean(Lk_list))
            k_vals.append(k)
    if len(k_vals) < 2:
        return _katz_fd(x)
    log_k = np.log(k_vals)
    log_L = np.log(np.array(L_vals) + 1e-12)
    # Linear regression slope
    slope, _ = np.polyfit(log_k, log_L, 1)
    return float(-slope)


def _katz_fd(x):
    """
    Katz (1988) fractal dimension — fallback estimator.
    Amplitude-invariant: uses relative distance ratios.
    """
    diffs = np.abs(np.diff(x))
    if len(diffs) == 0:
        return 0.0
    L = diffs.sum()
    d = np.sqrt(np.sum((np.arange(len(x)) - 0) ** 2 + (x - x[0]) ** 2)).max()
    if L <= 0 or d <= 0:
        return 0.0
    import math
    n = len(x)
    return float(math.log10(n) / (math.log10(n) + math.log10(d / L)))


# ── A5: Autocorrelation Decay at 1/e ─────────────────────────────────────────
def _autocorr_decay(x, dt, max_lag=10000):
    """
    Returns the lag (in time units) at which the normalized autocorrelation
    first crosses 1/e. More robust than first-zero crossing.
    Amplitude-invariant: normalized by variance.
    """
    N = len(x)
    x_c = x - x.mean()
    norm = np.dot(x_c, x_c)
    if norm <= 0:
        return float(N * dt)
    threshold = 1.0 / np.e
    for lag in range(1, min(N, max_lag)):
        rho = np.dot(x_c[:-lag], x_c[lag:]) / norm
        if abs(rho) < threshold:
            return float(lag * dt)
    return float(N * dt)


# ── A6: Robust Skewness (Galton / Groeneveld-Meeden) ────────────────────────
def _robust_skewness(x):
    """
    Galton skewness: (Q75 + Q25 - 2*Q50) / (Q75 - Q25)
    Amplitude-invariant: ratio of inter-quartile quantities.
    """
    q25, q50, q75 = np.percentile(x, [25, 50, 75])
    iqr = q75 - q25
    if iqr < 1e-10:
        return 0.0
    return float((q75 + q25 - 2.0 * q50) / iqr)


# ── A7: Robust Kurtosis (Crow–Siddiqui) ─────────────────────────────────────
def _robust_kurtosis(x):
    """
    Crow-Siddiqui kurtosis: (Q90 - Q10) / (Q75 - Q25)
    Amplitude-invariant: pure quantile ratio.
    """
    q10, q25, q75, q90 = np.percentile(x, [10, 25, 75, 90])
    iqr = q75 - q25
    if iqr < 1e-10:
        return 0.0
    return float((q90 - q10) / iqr)


# ── A8: Temporal Irreversibility ─────────────────────────────────────────────
def _temporal_irreversibility(x):
    """
    A = E[(x_{t+1} - x_t)^3] / sigma^3
    This metric changes sign under time reversal, making it
    a direct probe of dynamical irreversibility.
    """
    diffs = np.diff(x).astype(float)
    sigma = float(np.std(x))
    if sigma < 1e-10:
        return 0.0
    return float(np.mean(diffs ** 3) / (sigma ** 3))


# ── MAIN V3 EMBEDDING VECTOR ──────────────────────────────────────────────────
def compute_embedding_vector(x_window, dt):
    """
    V3 Embedding: 8 amplitude-invariant dynamical features.
    ALL features are dimensionless ratios or normalized entropies;
    NONE scale directly with signal amplitude, variance, or energy.

    Returns dict with keys:
        perm_entropy, spectral_entropy, svd_entropy,
        fractal_dim, autocorr_decay, robust_skewness,
        robust_kurtosis, temporal_irreversibility
    """
    x = np.asarray(x_window, dtype=float)
    # Apply a moving average smoothing filter of length 5 to reduce noise sensitivity
    # while preserving deterministic structure.
    window_len = 5
    if len(x) >= window_len:
        s = np.r_[x[window_len-1:0:-1], x, x[-2:-window_len-1:-1]]
        w = np.ones(window_len, 'd')
        x = np.convolve(w/w.sum(), s, mode='valid')[window_len//2 : -(window_len//2)]

    perm_ent       = _permutation_entropy(x, m=5, delay=1)
    spec_ent       = _spectral_entropy_normalized(x, dt)
    svd_ent        = _svd_entropy(x, m=10, delay=1)
    try:
        frac_dim   = _higuchi_fd(x, k_max=10)
        if not np.isfinite(frac_dim):
            frac_dim = _katz_fd(x)
    except Exception:
        try:
            frac_dim = _katz_fd(x)
        except Exception:
            frac_dim = 0.0
    ac_decay       = _autocorr_decay(x, dt)
    rob_skew       = _robust_skewness(x)
    rob_kurt       = _robust_kurtosis(x)
    temp_irrev     = _temporal_irreversibility(x)

    return {
        "perm_entropy":           float(perm_ent)   if np.isfinite(perm_ent)   else 0.0,
        "spectral_entropy":       float(spec_ent)   if np.isfinite(spec_ent)   else 0.0,
        "svd_entropy":            float(svd_ent)    if np.isfinite(svd_ent)    else 0.0,
        "fractal_dim":            float(frac_dim)   if np.isfinite(frac_dim)   else 0.0,
        "autocorr_decay":         float(ac_decay)   if np.isfinite(ac_decay)   else 0.0,
        "robust_skewness":        float(rob_skew)   if np.isfinite(rob_skew)   else 0.0,
        "robust_kurtosis":        float(rob_kurt)   if np.isfinite(rob_kurt)   else 0.0,
        "temporal_irreversibility": float(temp_irrev) if np.isfinite(temp_irrev) else 0.0,
    }

def get_global_lyapunov(conn, system_name, noise_level, seed):
    """
    Retrieves a stable global Lyapunov exponent from the precomputed db runs
    to avoid short-window noise and parameter instability.
    """
    try:
        row = conn.execute(
            "SELECT lyapunov_max FROM structural_embeddings WHERE system_name=? AND noise_level=? AND seed=?",
            (system_name, noise_level, seed)
        ).fetchone()
        if row and row[0] is not None:
            return float(row[0])
        
        row = conn.execute(
            "SELECT lyapunov_max FROM structural_embeddings WHERE system_name=? LIMIT 1",
            (system_name,)
        ).fetchone()
        if row and row[0] is not None:
            return float(row[0])
    except Exception:
        pass
    return 0.5

# ─────────────────────────────────────────────────────────────────────────────
# MAIN EXPORT ROUTINE
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🔮 STARTING DENSE LATENT MANIFOLD GEOMETRY EXPORTER")
    print("=" * 60)

    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}. Run sweeps first.")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    
    # 1. Get unique active configurations from database
    query = """
        SELECT DISTINCT system_name, noise_level, seed
        FROM structural_embeddings
        ORDER BY system_name, noise_level, seed
    """
    configs = conn.execute(query).fetchall()
    
    if not configs:
        print("❌ No configurations found in SQLite database.")
        conn.close()
        sys.exit(1)

    print(f"Found {len(configs)} unique runs. Building sliding window point clouds...")
    
    all_points_flat = []  # List of 8D vectors
    points_metadata = []  # Maps each flat point back to (system, noise, seed)
    
    # 2. Extract sliding window embeddings or direct sweeps
    for system_name, noise_level, seed in configs:
        noise_level = float(noise_level)
        seed = int(seed)
        
        if system_name == "logistic_sweep":
            # For logistic_sweep, simulate the map and extract V3 window embeddings
            # (DB columns are V2 features incompatible with V3; we re-simulate instead)
            print(f"Processing '{system_name}' via V3 re-simulation...")
            x_signal, dt = simulate_system("logistic_map", noise_level, seed)
            if x_signal is None:
                continue
            trajectory_length = len(x_signal)
            window_size = min(max(500, int(trajectory_length * 0.1)), 2000)
            stride = max(1, min(window_size // 2, (trajectory_length - window_size) // 330))
            start = 0
            count_windows = 0
            while start + window_size <= trajectory_length:
                x_window = x_signal[start:start + window_size]
                emb = compute_embedding_vector(x_window, dt)
                for k in emb:
                    if not np.isfinite(emb[k]):
                        emb[k] = 0.0
                vector = [
                    emb["perm_entropy"], emb["spectral_entropy"], emb["svd_entropy"],
                    emb["fractal_dim"], emb["autocorr_decay"], emb["robust_skewness"],
                    emb["robust_kurtosis"], emb["temporal_irreversibility"]
                ]
                all_points_flat.append(vector)
                points_metadata.append({
                    "system": system_name,
                    "noise": noise_level,
                    "seed": seed
                })
                start += stride
                count_windows += 1
            print(f"  Generated {count_windows} V3 embeddings for logistic_sweep.")
        else:
            print(f"Simulating '{system_name}' (noise={noise_level:.4f}, seed={seed})...")
            x_signal, dt = simulate_system(system_name, noise_level, seed)
            if x_signal is None:
                continue
            
            # Adaptive Density Strategy (Mandatory sliding window parameters)
            trajectory_length = len(x_signal)
            window_size = min(max(500, int(trajectory_length * 0.1)), 2000)
            # Dynamically adjust stride to guarantee density: minimum 320 points (using 330 safety target)
            stride = max(1, min(window_size // 2, (trajectory_length - window_size) // 330))
            
            # Windowing loop
            start = 0
            count_windows = 0
            while start + window_size <= trajectory_length:
                x_window = x_signal[start:start+window_size]
                emb = compute_embedding_vector(x_window, dt)
                
                # V3: all features are already amplitude-invariant
                # Replace NaNs/Infinities with neutral values
                for k in emb:
                    if not np.isfinite(emb[k]):
                        emb[k] = 0.0

                vector = [
                    emb["perm_entropy"], emb["spectral_entropy"], emb["svd_entropy"],
                    emb["fractal_dim"], emb["autocorr_decay"], emb["robust_skewness"],
                    emb["robust_kurtosis"], emb["temporal_irreversibility"]
                ]
                all_points_flat.append(vector)
                points_metadata.append({
                    "system": system_name,
                    "noise": noise_level,
                    "seed": seed
                })
                start += stride
                count_windows += 1
            print(f"  Generated {count_windows} sliding window embeddings.")
            
    conn.close()

    if not all_points_flat:
        print("❌ No point cloud embeddings could be extracted.")
        sys.exit(1)

    # 3. Fit Global PCA on the entire concatenated feature matrix
    X = np.array(all_points_flat, dtype=float)
    X = np.nan_to_num(X, nan=0.0)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    explained_variance = [float(v) for v in pca.explained_variance_ratio_]
    
    print(f"Global PCA fitted. Combined shape: {X_pca.shape}. Explained variance: {explained_variance}")
    
    # Group coordinates by (system, noise, seed)
    grouped_coordinates = {}
    for idx, meta in enumerate(points_metadata):
        key = (meta["system"], meta["noise"], meta["seed"])
        if key not in grouped_coordinates:
            grouped_coordinates[key] = []
        grouped_coordinates[key].append({
            "x": float(X_pca[idx, 0]),
            "y": float(X_pca[idx, 1])
        })
        
    # 4. Compute baseline (noise=0.0) centroids for each (system, seed)
    baselines = {}
    for (system, noise, seed), pts in grouped_coordinates.items():
        if noise == 0.0:
            xs = [p["x"] for p in pts]
            ys = [p["y"] for p in pts]
            baselines[(system, seed)] = (float(np.mean(xs)), float(np.mean(ys)))
            
    # Fill in missing baselines by taking lowest noise level
    systems_present = set(key[0] for key in grouped_coordinates)
    for sys in systems_present:
        seeds = set(key[2] for key in grouped_coordinates if key[0] == sys)
        for seed in seeds:
            if (sys, seed) not in baselines:
                # Find smallest noise level
                matches = sorted([key for key in grouped_coordinates if key[0] == sys and key[2] == seed], key=lambda k: k[1])
                if matches:
                    lowest_key = matches[0]
                    pts = grouped_coordinates[lowest_key]
                    xs = [p["x"] for p in pts]
                    ys = [p["y"] for p in pts]
                    baselines[(sys, seed)] = (float(np.mean(xs)), float(np.mean(ys)))
                    print(f"  [WARN] Baseline (noise=0.0) missing for system '{sys}', seed {seed}. Using lowest noise={lowest_key[1]:.4f} centroid.")

    # 5. Build snapshots array with full topological metrics
    systems_output_map = {}
    
    for (sys_name, noise, seed), points_2d in grouped_coordinates.items():
        if sys_name not in systems_output_map:
            systems_output_map[sys_name] = []
            
        x_coords = np.array([p["x"] for p in points_2d])
        y_coords = np.array([p["y"] for p in points_2d])
        pts_arr = np.array([[p["x"], p["y"]] for p in points_2d])
        
        centroid_x = float(np.mean(x_coords))
        centroid_y = float(np.mean(y_coords))
        
        # Centroid Displacement
        base_x, base_y = baselines.get((sys_name, seed), (centroid_x, centroid_y))
        centroid_displacement = float(np.sqrt((centroid_x - base_x)**2 + (centroid_y - base_y)**2))
        
        spread_x = float(np.std(x_coords))
        spread_y = float(np.std(y_coords))
        
        # Convex Hull Area
        convex_hull_area = 0.0
        if len(pts_arr) >= 3:
            try:
                hull = ConvexHull(pts_arr)
                convex_hull_area = float(hull.volume)  # In 2D, volume is area
            except Exception:
                pass
                
        # Nearest Neighbors Stats
        nn_mean = 0.0
        nn_std = 0.0
        if len(pts_arr) >= 2:
            try:
                nn = NearestNeighbors(n_neighbors=2)
                nn.fit(pts_arr)
                distances, _ = nn.kneighbors(pts_arr)
                nn_dist = distances[:, 1]  # Nearest neighbor distance
                nn_mean = float(np.mean(nn_dist))
                nn_std = float(np.std(nn_dist))
            except Exception:
                pass

        # Covariance Determinant (Effective Volume)
        covariance_determinant = 0.0
        regularization_applied = False
        if len(pts_arr) >= 2:
            try:
                cov = np.cov(pts_arr, rowvar=False)
                det = np.linalg.det(cov)
                # Numerical Stability check: if singular or near-singular, apply regularization
                if det <= 1e-12 or not np.isfinite(det):
                    cov += np.eye(cov.shape[0]) * 1e-8
                    det = np.linalg.det(cov)
                    regularization_applied = True
                if np.isfinite(det):
                    covariance_determinant = float(det)
            except Exception:
                pass
                
        # DBSCAN Cluster Count with Adaptive eps
        cluster_count = 1
        if len(pts_arr) >= 2:
            try:
                eps_val = nn_mean + nn_std
                # Ensure eps_val is strictly positive
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
                
        systems_output_map[sys_name].append({
            "noise": noise,
            "seed": seed,
            "quantitative_metrics": {
                "centroid_displacement": centroid_displacement,
                "point_count": len(points_2d),
                "spread_x": spread_x,
                "spread_y": spread_y,
                "convex_hull_area": convex_hull_area,
                "covariance_determinant": covariance_determinant,
                "nearest_neighbor_distance_mean": nn_mean,
                "nearest_neighbor_distance_std": nn_std,
                "cluster_count": int(cluster_count),
                "regularization_applied": regularization_applied
            },
            "points": points_2d
        })

    systems_output = []
    for sys_name, snapshots in systems_output_map.items():
        # Sort snapshots by noise level, then seed
        snapshots_sorted = sorted(snapshots, key=lambda s: (s["noise"], s["seed"]))
        systems_output.append({
            "system": sys_name,
            "snapshots": snapshots_sorted
        })
        
    # 6. Save JSON artifact
    output_data = {
        "metadata": {
            "projection": "PCA",
            "dimensions": 2,
            "scaling": "global_standard_scaler",
            "alignment": "global_fit",
            "explained_variance_ratio": explained_variance,
            "version": "V3",
            "features": [
                "perm_entropy", "spectral_entropy", "svd_entropy",
                "fractal_dim", "autocorr_decay", "robust_skewness",
                "robust_kurtosis", "temporal_irreversibility"
            ],
            "excluded_features_v2": [
                "variance", "energy", "RMS", "dominant_frequency",
                "kurtosis (moment)", "skewness (moment)"
            ],
            "window_parameters": {
                "window_size_formula": "min(max(500, int(trajectory_length * 0.1)), 2000)",
                "stride_formula": "min(window_size // 2, (trajectory_length - window_size) // 330)"
            },
            "amplitude_invariance": "All V3 features are dimensionless ratios or normalized entropies. None scale with signal amplitude, variance, or energy."
        },
        "systems": systems_output
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"✅ Successfully exported dense manifold snapshots to {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
