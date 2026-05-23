import os
import sys
import json
import time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.fft import fft
from scipy.stats import spearmanr, pearsonr
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, auc, f1_score, precision_score, recall_score
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

from core.autonomous.latent_snapshot_exporter import compute_embedding_vector

# Paths
REPORT_DIR = os.path.join(ROOT_DIR, "dashboard", "public", "artifacts", "discoveries")
REPORT_FILE = os.path.join(REPORT_DIR, "adversarial_scientific_audit_report.json")

# Seeds
SEEDS = [42, 1337, 9001]

# V3 features order
V3_KEYS = [
    "perm_entropy", "spectral_entropy", "svd_entropy",
    "fractal_dim", "autocorr_decay", "robust_skewness",
    "robust_kurtosis", "temporal_irreversibility"
]

# ─────────────────────────────────────────────────────────────────────────────
# CORE UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def generate_pink_noise(length, seed):
    np.random.seed(seed)
    white = np.random.normal(0, 1.0, length)
    f = fft(white)
    freqs = np.fft.fftfreq(length)
    scale = np.zeros(len(freqs))
    # We only scale positive frequencies and mirror them
    half = len(freqs) // 2
    scale[1:half] = 1.0 / np.sqrt(np.abs(freqs[1:half]))
    scale[-half:] = 1.0 / np.sqrt(np.abs(freqs[-half:]))
    f_scaled = f * scale
    pink = np.real(np.fft.ifft(f_scaled))
    std = np.std(pink)
    return pink / std if std > 0 else pink

def generate_phase_randomized(base_signal, seed):
    np.random.seed(seed)
    length = len(base_signal)
    f = fft(base_signal)
    phases = np.random.uniform(-np.pi, np.pi, length)
    # Maintain Hermitian symmetry for real signals
    half = length // 2
    phases[0] = 0.0
    if length % 2 == 0:
        phases[half] = 0.0
    phases[half+1:] = -phases[1:half][::-1]
    
    f_surr = np.abs(f) * np.exp(1j * phases)
    surr = np.real(np.fft.ifft(f_surr))
    std = np.std(surr)
    return surr / std if std > 0 else surr

def generate_arma_mimic(base_signal, seed, p=20):
    n = len(base_signal)
    sig_centered = base_signal - np.mean(base_signal)
    
    # Fit AR(p) using least squares
    X = np.zeros((n - p, p))
    for i in range(p):
        X[:, i] = sig_centered[p - 1 - i : n - 1 - i]
    y = sig_centered[p:]
    
    try:
        phi, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    except Exception:
        phi = np.zeros(p)
        phi[0] = 0.9  # fallback simple AR(1)
        
    np.random.seed(seed)
    gen = np.zeros(n)
    start_idx = np.random.randint(0, n - p)
    gen[:p] = sig_centered[start_idx : start_idx + p]
    
    residuals = y - X @ phi
    res_std = np.std(residuals) if len(residuals) > 0 else 0.1
    eps = np.random.normal(0, res_std, n)
    
    for t in range(p, n):
        gen[t] = np.dot(phi, gen[t-p:t][::-1]) + eps[t]
        
    std = np.std(gen)
    return gen / std if std > 0 else gen

# ─────────────────────────────────────────────────────────────────────────────
# LYAPUNOV & ENTROPY ESTIMATION
# ─────────────────────────────────────────────────────────────────────────────

def estimate_lyapunov(signal, dt=0.01, emb_dim=3, delay=10):
    """
    Rosenstein-like maximum Lyapunov exponent estimation from time series.
    """
    N = len(signal)
    if N < 500:
        return 0.0
    num_vectors = N - (emb_dim - 1) * delay
    if num_vectors < 100:
        return 0.0
    
    states = np.array([signal[i : i + emb_dim * delay : delay] for i in range(num_vectors)])
    
    # Exclude temporal neighbors using a Theiler window of 50 steps
    theiler = 50
    neighbor_indices = np.zeros(num_vectors, dtype=int)
    
    # We do a batch vector search for speed
    for i in range(num_vectors):
        dists = np.linalg.norm(states - states[i], axis=1)
        dists[max(0, i - theiler) : min(num_vectors, i + theiler)] = np.inf
        neighbor_indices[i] = np.argmin(dists)
        
    steps = 30
    divergence = np.zeros(steps)
    counts = np.zeros(steps)
    
    for i in range(num_vectors):
        n_idx = neighbor_indices[i]
        if n_idx >= num_vectors or n_idx == i:
            continue
        for j in range(steps):
            if i + j < num_vectors and n_idx + j < num_vectors:
                d = np.linalg.norm(states[i + j] - states[n_idx + j])
                if d > 0:
                    divergence[j] += np.log(d)
                    counts[j] += 1
                    
    valid = counts > 0
    if not np.any(valid):
        return 0.0
    log_d = divergence[valid] / counts[valid]
    times = np.arange(len(log_d)) * dt
    fit_steps = min(15, len(log_d))
    if fit_steps < 3:
        return 0.0
    slope, _ = np.polyfit(times[:fit_steps], log_d[:fit_steps], 1)
    return float(slope)

def estimate_shannon_entropy(signal, bins=50):
    hist, _ = np.histogram(signal, bins=bins, density=True)
    hist = hist[hist > 0]
    return float(-np.sum(hist * np.log(hist)))

# ─────────────────────────────────────────────────────────────────────────────
# CKA & CALIBRATION METRICS
# ─────────────────────────────────────────────────────────────────────────────

def compute_cka(X, Y):
    """
    Linear Centered Kernel Alignment (CKA) optimized for D=8, shape NxD.
    """
    X = X - X.mean(axis=0)
    Y = Y - Y.mean(axis=0)
    
    XTX = X.T @ X
    YTY = Y.T @ Y
    XTY = X.T @ Y
    
    hsic_kl = np.sum(XTY ** 2)
    hsic_kk = np.sum(XTX ** 2)
    hsic_ll = np.sum(YTY ** 2)
    
    denom = np.sqrt(hsic_kk * hsic_ll)
    if denom <= 1e-12:
        return 0.0
    return float(hsic_kl / denom)

def compute_ece(y_true, y_prob, n_bins=10):
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        in_bin = (y_prob >= bin_lower) & (y_prob < bin_upper)
        prop_in_bin = np.mean(in_bin)
        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(y_true[in_bin])
            avg_confidence_in_bin = np.mean(y_prob[in_bin])
            ece += prop_in_bin * np.abs(avg_confidence_in_bin - accuracy_in_bin)
    return float(ece)

def compute_calibration_curve(y_true, y_prob, n_bins=10):
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_confs = []
    bin_accs = []
    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        in_bin = (y_prob >= bin_lower) & (y_prob < bin_upper)
        if np.sum(in_bin) > 0:
            bin_confs.append(float(np.mean(y_prob[in_bin])))
            bin_accs.append(float(np.mean(y_true[in_bin])))
        else:
            bin_confs.append(float((bin_lower + bin_upper) / 2))
            bin_accs.append(0.0)
    return bin_confs, bin_accs

# ─────────────────────────────────────────────────────────────────────────────
# PHYSICAL SYSTEM SIMULATORS (CUSTOM PARAMETERS)
# ─────────────────────────────────────────────────────────────────────────────

def lorenz_custom_rhs(t, state, R):
    x, y, z = state
    return [10.0 * (y - x), x * (R - z) - y, x * y - (8.0/3.0) * z]

def simulate_lorenz_custom(R, length=25000, seed=42):
    t_span = (0, 300)
    t_eval = np.linspace(0, 300, length + 5000)
    dt = t_eval[1] - t_eval[0]
    np.random.seed(seed)
    state0 = [1.0 + np.random.normal(0, 0.1), 1.0, 1.0]
    sol = solve_ivp(lambda t, y: lorenz_custom_rhs(t, y, R), t_span, state0, t_eval=t_eval, method='RK45')
    return sol.y[0][5000:5000+length], dt

def rossler_custom_rhs(t, state, c):
    x, y, z = state
    return [-y - z, x + 0.2 * y, 0.2 + z * (x - c)]

def simulate_rossler_custom(c, length=25000, seed=42):
    t_span = (0, 300)
    t_eval = np.linspace(0, 300, length + 5000)
    dt = t_eval[1] - t_eval[0]
    np.random.seed(seed)
    state0 = [1.0 + np.random.normal(0, 0.1), 1.0, 1.0]
    sol = solve_ivp(lambda t, y: rossler_custom_rhs(t, y, c), t_span, state0, t_eval=t_eval, method='RK45')
    return sol.y[0][5000:5000+length], dt

def duffing_custom_rhs(t, state, f):
    x, y = state
    return [y, x - x**3 - 0.3*y + f*np.cos(1.2*t)]

def simulate_duffing_custom(f, length=25000, seed=42):
    t_span = (0, 800)
    t_eval = np.linspace(0, 800, length + 10000)
    dt = t_eval[1] - t_eval[0]
    np.random.seed(seed)
    state0 = [0.1 + np.random.normal(0, 0.05), 0.0]
    sol = solve_ivp(lambda t, y: duffing_custom_rhs(t, y, f), t_span, state0, t_eval=t_eval, method='RK45')
    return sol.y[0][10000:10000+length], dt

def simulate_logistic_custom(r, length=25000, seed=42):
    np.random.seed(seed)
    x = np.random.uniform(0.1, 0.9)
    for _ in range(5000):
        x = r * x * (1.0 - x)
    series = []
    for _ in range(length):
        x = r * x * (1.0 - x)
        series.append(x)
    return np.array(series), 1.0

def simulate_henon_custom(a=1.4, b=0.3, length=25000, seed=42):
    np.random.seed(seed)
    x = np.zeros(length + 5000)
    y = np.zeros(length + 5000)
    x[0], y[0] = np.random.uniform(-0.1, 0.1), np.random.uniform(-0.1, 0.1)
    for i in range(1, length + 5000):
        x[i] = 1.0 - a * x[i-1]**2 + b * y[i-1]
        y[i] = b * x[i-1]
    return x[5000:], 1.0

# ─────────────────────────────────────────────────────────────────────────────
# EMBEDDING EXTRACTION FOR A SIGNALS GRID
# ─────────────────────────────────────────────────────────────────────────────

def extract_v3_embeddings(signal, dt, window_size=1000, stride=500):
    embeddings = []
    n = len(signal)
    start = 0
    while start + window_size <= n:
        win = signal[start : start + window_size]
        emb = compute_embedding_vector(win, dt)
        vec = [emb.get(k, 0.0) for k in V3_KEYS]
        embeddings.append(vec)
        start += stride
    return np.array(embeddings) if len(embeddings) > 0 else np.zeros((0, len(V3_KEYS)))

# ─────────────────────────────────────────────────────────────────────────────
# MAIN SCIENTIFIC ADVERSARIAL AUDIT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("🕵️‍♂️ PRINCIPAL COMPUTATIONAL PHYSICS ADVERSARY — SCIENTIFIC RED TEAM AUDIT")
    print("=" * 70)
    print("AUDITING EMBEDDING V3 (8D AMPLITUDE-INVARIANT)...")
    print("No system modifications. No parameter adjustment. Raw mathematical limits only.")
    
    t_start = time.time()
    
    # ── TEST 1: HYBRID & CAMOUFLAGED ADVERSARIES ─────────────────────────────
    print("\n[TEST 1] Generating hybrid & camouflaged adversary signals...")
    # Generate clean chaotic signals for 3 seeds
    length = 25000
    
    # Store systems
    phys_signals = {}
    adversarial_signals = {}
    
    # We will compute the V3 embeddings for physical vs adversarial mixtures
    test1_results = {}
    
    for sys_name in ["lorenz", "rossler", "henon", "logistic"]:
        test1_results[sys_name] = {}
        for seed in SEEDS:
            # Clean chaos
            if sys_name == "lorenz":
                chaos, dt = simulate_lorenz_custom(R=28.0, length=length, seed=seed)
            elif sys_name == "rossler":
                chaos, dt = simulate_rossler_custom(c=5.7, length=length, seed=seed)
            elif sys_name == "henon":
                chaos, dt = simulate_henon_custom(length=length, seed=seed)
            else:
                chaos, dt = simulate_logistic_custom(r=3.95, length=length, seed=seed)
            
            # Standardize chaos
            chaos = (chaos - np.mean(chaos)) / np.std(chaos)
            phys_signals[(sys_name, seed)] = (chaos, dt)
            
            # 1) Colored (Pink) noise mixture
            pink = generate_pink_noise(length, seed)
            
            mixture_embs = {}
            for alpha in np.linspace(0.0, 1.0, 11):
                mix = alpha * chaos + (1.0 - alpha) * pink
                mix = (mix - np.mean(mix)) / np.std(mix)
                embs = extract_v3_embeddings(mix, dt, window_size=1000, stride=500)
                mixture_embs[f"{alpha:.1f}"] = embs.tolist()
                
            # 2) Phase randomized
            pr = generate_phase_randomized(chaos, seed)
            pr_embs = extract_v3_embeddings(pr, dt, window_size=1000, stride=500).tolist()
            
            # 3) ARMA Mimic (using AR(20))
            ar = generate_arma_mimic(chaos, seed, p=20)
            ar_embs = extract_v3_embeddings(ar, dt, window_size=1000, stride=500).tolist()
            
            test1_results[sys_name][f"seed_{seed}"] = {
                "mixtures": mixture_embs,
                "phase_randomized": pr_embs,
                "arma_mimic": ar_embs
            }
            
    print("Test 1 generation complete.")
    
    # ── TEST 2: EDGE OF CHAOS REGIMES ─────────────────────────────────────────
    print("\n[TEST 2] Sweeping near critical edge-of-chaos regimes...")
    test2_results = {}
    
    # 2.1 Lorenz Sweep (R: 22 to 28)
    test2_results["lorenz"] = []
    test2_lorenz_edge_raw = []
    for R in [22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0]:
        r_list = []
        for seed in SEEDS:
            signal, dt = simulate_lorenz_custom(R=R, length=length, seed=seed)
            lyap = estimate_lyapunov(signal, dt=dt)
            ent = estimate_shannon_entropy(signal)
            embs = extract_v3_embeddings(signal, dt, window_size=1000, stride=500)
            if R < 24.0:
                test2_lorenz_edge_raw.extend(embs)
            mean_emb = np.mean(embs, axis=0).tolist() if len(embs) > 0 else [0.0]*8
            r_list.append({"lyapunov": lyap, "entropy": ent, "v3": mean_emb})
        test2_results["lorenz"].append({
            "param": R,
            "lyapunov": float(np.mean([r["lyapunov"] for r in r_list])),
            "entropy": float(np.mean([r["entropy"] for r in r_list])),
            "v3": np.mean([r["v3"] for r in r_list], axis=0).tolist()
        })
        
    # 2.2 Logistic Sweep (r: 3.82 to 3.86)
    test2_results["logistic"] = []
    for r in [3.82, 3.83, 3.84, 3.85, 3.86]:
        r_list = []
        for seed in SEEDS:
            signal, dt = simulate_logistic_custom(r=r, length=length, seed=seed)
            lyap = estimate_lyapunov(signal, dt=dt)
            ent = estimate_shannon_entropy(signal)
            embs = extract_v3_embeddings(signal, dt, window_size=1000, stride=500)
            mean_emb = np.mean(embs, axis=0).tolist() if len(embs) > 0 else [0.0]*8
            r_list.append({"lyapunov": lyap, "entropy": ent, "v3": mean_emb})
        test2_results["logistic"].append({
            "param": r,
            "lyapunov": float(np.mean([r["lyapunov"] for r in r_list])),
            "entropy": float(np.mean([r["entropy"] for r in r_list])),
            "v3": np.mean([r["v3"] for r in r_list], axis=0).tolist()
        })
        
    # 2.3 Rössler Sweep (c: 3.0 to 5.7)
    test2_results["rossler"] = []
    for c in [3.0, 3.5, 4.0, 4.5, 5.0, 5.7]:
        r_list = []
        for seed in SEEDS:
            signal, dt = simulate_rossler_custom(c=c, length=length, seed=seed)
            lyap = estimate_lyapunov(signal, dt=dt)
            ent = estimate_shannon_entropy(signal)
            embs = extract_v3_embeddings(signal, dt, window_size=1000, stride=500)
            mean_emb = np.mean(embs, axis=0).tolist() if len(embs) > 0 else [0.0]*8
            r_list.append({"lyapunov": lyap, "entropy": ent, "v3": mean_emb})
        test2_results["rossler"].append({
            "param": c,
            "lyapunov": float(np.mean([r["lyapunov"] for r in r_list])),
            "entropy": float(np.mean([r["entropy"] for r in r_list])),
            "v3": np.mean([r["v3"] for r in r_list], axis=0).tolist()
        })
        
    # 2.4 Duffing Sweep (f: 0.2 to 0.5)
    test2_results["duffing"] = []
    for f in [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]:
        r_list = []
        for seed in SEEDS:
            signal, dt = simulate_duffing_custom(f=f, length=length, seed=seed)
            lyap = estimate_lyapunov(signal, dt=dt)
            ent = estimate_shannon_entropy(signal)
            embs = extract_v3_embeddings(signal, dt, window_size=1000, stride=500)
            mean_emb = np.mean(embs, axis=0).tolist() if len(embs) > 0 else [0.0]*8
            r_list.append({"lyapunov": lyap, "entropy": ent, "v3": mean_emb})
        test2_results["duffing"].append({
            "param": f,
            "lyapunov": float(np.mean([r["lyapunov"] for r in r_list])),
            "entropy": float(np.mean([r["entropy"] for r in r_list])),
            "v3": np.mean([r["v3"] for r in r_list], axis=0).tolist()
        })
        
    print("Test 2 sweeps complete.")
    
    # ── TEST 3: NONSTATIONARY ADVERSARIES ─────────────────────────────────────
    print("\n[TEST 3] Simulating nonstationary regime transition paths (length=25000)...")
    test3_results = {}
    
    # Segment transitions length
    half_l = 12500
    quad_l = 6250
    
    transitions = {
        "A_noise_to_chaos": ("noise", "lorenz"),
        "B_chaos_to_noise": ("lorenz", "noise"),
        "C_chaos_to_chaos": ("lorenz", "rossler"),
        "D_multiple_changes": ("multiple", "multiple")
    }
    
    for t_name, regimes in transitions.items():
        t_list = []
        for seed in SEEDS:
            # Generate signals
            lorenz_sig, lorenz_dt = simulate_lorenz_custom(R=28.0, length=length, seed=seed)
            lorenz_sig = (lorenz_sig - np.mean(lorenz_sig)) / np.std(lorenz_sig)
            
            rossler_sig, rossler_dt = simulate_rossler_custom(c=5.7, length=length, seed=seed)
            rossler_sig = (rossler_sig - np.mean(rossler_sig)) / np.std(rossler_sig)
            
            pink = generate_pink_noise(length, seed)
            white = np.random.normal(0, 1.0, length)
            
            if t_name == "A_noise_to_chaos":
                sig = np.concatenate([pink[:half_l], lorenz_sig[:half_l]])
                dt = lorenz_dt
            elif t_name == "B_chaos_to_noise":
                sig = np.concatenate([lorenz_sig[:half_l], pink[:half_l]])
                dt = lorenz_dt
            elif t_name == "C_chaos_to_chaos":
                sig = np.concatenate([lorenz_sig[:half_l], rossler_sig[:half_l]])
                dt = lorenz_dt
            else:
                sig = np.concatenate([pink[:quad_l], lorenz_sig[:quad_l], rossler_sig[:quad_l], white[:quad_l]])
                dt = lorenz_dt
                
            # Extract window embeddings with window=1000, stride=100 to get high temporal resolution
            win_size = 1000
            stride = 100
            embs = extract_v3_embeddings(sig, dt, window_size=win_size, stride=stride)
            
            # Compute temporal drift metrics
            centers = []
            distances = []
            features_variance = np.var(embs, axis=0).tolist() if len(embs) > 0 else [0.0]*8
            
            start = 0
            idx = 0
            while start + win_size <= len(sig):
                centers.append(start + win_size // 2)
                if idx > 0:
                    dist = np.linalg.norm(embs[idx] - embs[idx-1])
                    distances.append(float(dist))
                else:
                    distances.append(0.0)
                start += stride
                idx += 1
                
            t_list.append({
                "centers": centers,
                "embedding_change": distances,
                "stability": features_variance
            })
            
        test3_results[t_name] = {
            "centers": t_list[0]["centers"],
            "embedding_change": np.mean([t["embedding_change"] for t in t_list], axis=0).tolist(),
            "stability": np.mean([t["stability"] for t in t_list], axis=0).tolist()
        }
        
    print("Test 3 nonstationary runs complete.")
    
    # ── TEST 4: ADVERSARIAL CLASSIFICATION FRONTIER ───────────────────────────
    print("\n[TEST 4] Training RandomForest boundary classifier...")
    # Prepare classification dataset
    X_phys = []
    X_adv = []
    
    # Build a sweep of difficulties
    difficulty_sweep = {f"{a:.1f}": [] for a in np.linspace(0.0, 1.0, 11)}
    difficulty_sweep["phase_randomized"] = []
    difficulty_sweep["arma_mimic"] = []
    
    for sys_name in ["lorenz", "rossler", "henon", "logistic"]:
        for seed in SEEDS:
            # Physical embeddings (alpha=1.0)
            res1 = test1_results[sys_name][f"seed_{seed}"]
            X_phys.extend(res1["mixtures"]["1.0"])
            
            # Adversaries mapped by alpha
            for a in np.linspace(0.0, 1.0, 11):
                key = f"{a:.1f}"
                difficulty_sweep[key].extend(res1["mixtures"][key])
                
            # Phase randomized and ARMA
            difficulty_sweep["phase_randomized"].extend(res1["phase_randomized"])
            difficulty_sweep["arma_mimic"].extend(res1["arma_mimic"])
            
            # Label as adversarial: alpha <= 0.6, phase_randomized, and ARMA mimics
            for a in np.linspace(0.0, 0.6, 7):
                X_adv.extend(res1["mixtures"][f"{a:.1f}"])
            X_adv.extend(res1["phase_randomized"])
            X_adv.extend(res1["arma_mimic"])
            
    X_phys = np.array(X_phys)
    X_adv = np.array(X_adv)
    
    # We want balanced classes
    n_phys = len(X_phys)
    n_adv = len(X_adv)
    n_samples = min(n_phys, n_adv)
    
    np.random.seed(42)
    idx_phys = np.random.choice(n_phys, n_samples, replace=False)
    idx_adv = np.random.choice(n_adv, n_samples, replace=False)
    
    X_class = np.vstack([X_phys[idx_phys], X_adv[idx_adv]])
    y_class = np.hstack([np.ones(n_samples), np.zeros(n_samples)])
    
    X_train, X_test, y_train, y_test = train_test_split(X_class, y_class, test_size=0.3, random_state=42)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    y_prob = clf.predict_proba(X_test)[:, 1]
    y_pred = clf.predict(X_test)
    
    roc_auc = float(roc_auc_score(y_test, y_prob))
    prec, rec, _ = precision_recall_curve(y_test, y_prob)
    pr_auc = float(auc(rec, prec))
    f1 = float(f1_score(y_test, y_pred))
    ece = compute_ece(y_test, y_prob)
    
    bin_confs, bin_accs = compute_calibration_curve(y_test, y_prob)
    
    # Build Performance-vs-Difficulty curve specifically along alpha mixtures
    perf_curve = []
    breakpoint_alpha = None
    
    for alpha in np.linspace(0.0, 0.9, 10):
        # Evaluate classifier against physical (1.0) vs adversarial (mixture alpha)
        # Class 1: Physical (1.0), Class 0: mixture alpha
        key = f"{alpha:.1f}"
        X_mix = np.array(difficulty_sweep[key])
        
        # Subsample to align sizes
        size = min(len(X_phys), len(X_mix))
        if size < 10:
            continue
        
        idx_p = np.random.choice(len(X_phys), size, replace=False)
        idx_m = np.random.choice(len(X_mix), size, replace=False)
        
        X_eval = np.vstack([X_phys[idx_p], X_mix[idx_m]])
        y_eval = np.hstack([np.ones(size), np.zeros(size)])
        
        probs_eval = clf.predict_proba(X_eval)[:, 1]
        auc_eval = float(roc_auc_score(y_eval, probs_eval))
        
        prec_eval, rec_eval, _ = precision_recall_curve(y_eval, probs_eval)
        pr_auc_eval = float(auc(rec_eval, prec_eval))
        
        perf_curve.append({
            "alpha": float(alpha),
            "roc_auc": auc_eval,
            "pr_auc": pr_auc_eval
        })
        
        # Determine breakpoint threshold
        # Point where ROC-AUC < 0.85 or PR-AUC < 0.80
        if (auc_eval < 0.85 or pr_auc_eval < 0.80) and breakpoint_alpha is None:
            breakpoint_alpha = float(alpha)
            
    if breakpoint_alpha is None:
        breakpoint_alpha = 0.9 # Default fallback if robust throughout
        
    test4_results = {
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "f1_score": f1,
        "ece": ece,
        "calibration_curve": {
            "confidences": bin_confs,
            "accuracies": bin_accs
        },
        "performance_vs_difficulty": perf_curve,
        "breakpoint_alpha": breakpoint_alpha
    }
    
    print(f"Test 4 Complete. ROC-AUC: {roc_auc:.4f}, ECE: {ece:.4f}, Breakpoint alpha: {breakpoint_alpha}")
    
    # ── TEST 5: FAILURE MODE MAPPING ──────────────────────────────────────────
    print("\n[TEST 5] Performing Failure Mode Mapping across adversaries...")
    test5_results = {}
    
    # Compute metrics for each adversary group compared to pure Physical
    adversaries_groups = {
        "pink_noise_mixture_low_alpha": np.array(difficulty_sweep["0.2"]),
        "pink_noise_mixture_high_alpha": np.array(difficulty_sweep["0.8"]),
        "phase_randomized": np.array(difficulty_sweep["phase_randomized"]),
        "arma_mimic": np.array(difficulty_sweep["arma_mimic"]),
        "edge_of_chaos_lorenz": np.array(test2_lorenz_edge_raw),
        "nonstationary_transition": np.array(extract_v3_embeddings(simulate_lorenz_custom(R=28.0, seed=42)[0][:12500], 0.01))
    }
    
    # Clean baseline Physical to compare structure
    X_phys_clean = np.array(difficulty_sweep["1.0"])
    
    # Subsample physical to align size for comparisons
    size_p = len(X_phys_clean)
    
    for adv_name, adv_embs in adversaries_groups.items():
        if len(adv_embs) == 0:
            continue
        
        # Resample to align shapes
        size_a = len(adv_embs)
        eval_size = min(size_p, size_a, 2000)
        
        np.random.seed(42)
        idx_p = np.random.choice(size_p, eval_size, replace=False)
        idx_a = np.random.choice(size_a, eval_size, replace=False)
        
        P = X_phys_clean[idx_p]
        A = adv_embs[idx_a]
        
        # Scale for structure calculations
        scaler = StandardScaler()
        P_scaled = scaler.fit_transform(P)
        A_scaled = scaler.fit_transform(A)
        
        # Determine n_neighbors dynamically to prevent sizing errors
        k_neighbors = min(15, len(P_scaled) - 1, len(A_scaled) - 1)
        if k_neighbors < 1:
            k_neighbors = 1
        
        # 1. Local structure damage: trusthworthiness or nearest neighbor deviation
        nn_p = NearestNeighbors(n_neighbors=k_neighbors)
        nn_p.fit(P_scaled)
        _, indices_p = nn_p.kneighbors(P_scaled)
        
        nn_a = NearestNeighbors(n_neighbors=k_neighbors)
        nn_a.fit(A_scaled)
        _, indices_a = nn_a.kneighbors(A_scaled)
        
        # Neighbor overlap
        overlap = []
        for i in range(eval_size):
            set_p = set(indices_p[i])
            set_a = set(indices_a[i])
            overlap.append(len(set_p.intersection(set_a)) / float(k_neighbors))
        mean_overlap = float(np.mean(overlap))
        
        # Local damage: 1 - mean_overlap
        local_damage = 1.0 - mean_overlap
        
        # 2. Global structure damage: covariance determinant deviation
        cov_p = np.cov(P_scaled, rowvar=False)
        cov_a = np.cov(A_scaled, rowvar=False)
        
        det_p = np.linalg.det(cov_p)
        det_a = np.linalg.det(cov_a)
        global_damage = float(np.abs(det_p - det_a) / (det_p + 1e-12))
        
        # 3. Distance correlation
        # Estimate dcor using simple spearman/pearson pairwise correlation
        dist_p = np.linalg.norm(P_scaled[:, None, :] - P_scaled[None, :, :], axis=-1).flatten()
        dist_a = np.linalg.norm(A_scaled[:, None, :] - A_scaled[None, :, :], axis=-1).flatten()
        # Subsample distances to avoid memory blast
        np.random.seed(42)
        idx_d = np.random.choice(len(dist_p), min(len(dist_p), 5000), replace=False)
        d_cor, _ = pearsonr(dist_p[idx_d], dist_a[idx_d])
        d_cor = float(d_cor) if np.isfinite(d_cor) else 0.0
        
        # 4. Covariance similarity: Frobenius norm
        cov_sim = float(np.linalg.norm(cov_p - cov_a, ord='fro'))
        
        # 5. CKA (Centered Kernel Alignment)
        cka = compute_cka(P, A)
        
        # 6. Automatic Classification
        # FAILURE_TYPE: LOCAL_CONFUSION, GLOBAL_COLLAPSE, TEMPORAL_INSTABILITY, CHAOS_CAMOUFLAGE, TRUE_FAILURE
        if cka > 0.85 and mean_overlap > 0.70:
            fail_type = "CHAOS_CAMOUFLAGE"
        elif mean_overlap > 0.60 and local_damage > 0.40:
            fail_type = "LOCAL_CONFUSION"
        elif global_damage > 10.0 or det_a < 1e-5:
            fail_type = "GLOBAL_COLLAPSE"
        elif adv_name == "nonstationary_transition":
            fail_type = "TEMPORAL_INSTABILITY"
        else:
            fail_type = "TRUE_FAILURE"
            
        test5_results[adv_name] = {
            "local_structure_damage": local_damage,
            "global_structure_damage": global_damage,
            "neighbor_overlap": mean_overlap,
            "distance_correlation": d_cor,
            "covariance_similarity": cov_sim,
            "cka": cka,
            "failure_type": fail_type
        }
        
    print("Test 5 complete.")
    
    # ── CONSOLIDATE & DETERMINE MOST LETHAL ADVERSARY ─────────────────────────
    # Most lethal = lowest CKA, highest global and local damage
    most_lethal = None
    worst_cka = 1.0
    for name, res5 in test5_results.items():
        if res5["cka"] < worst_cka:
            worst_cka = res5["cka"]
            most_lethal = name
            
    # Global status calculation
    # Certification status: conditionally certified, but let's see if audit reveals vulnerability
    global_status = "CONDITIONALLY_CERTIFIED"
    if worst_cka < 0.3 or test4_results["roc_auc"] < 0.75:
        global_status = "VULNERABILITY_DETECTED"
        
    report = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "audit_version": "V3-Adversarial-Audit",
            "global_status": global_status,
            "most_lethal_adversary": most_lethal,
            "breakpoint_threshold": test4_results["breakpoint_alpha"]
        },
        "test1_hybrid_adversaries": test1_results,
        "test2_edge_of_chaos": test2_results,
        "test3_nonstationary": test3_results,
        "test4_classification_frontier": test4_results,
        "test5_failure_modes": test5_results
    }
    
    # Save Report
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    t_end = time.time()
    
    # ── REQUIRED TERMINAL DUMP ────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("🏁 FINAL ADVERSARIAL AUDIT REPORT SUMMARY")
    print("=" * 70)
    print(f"MOST_LETHAL_ADVERSARY  = {most_lethal.upper()}")
    print(f"BREAKPOINT_THRESHOLD   = {test4_results['breakpoint_alpha']:.2f} (alpha boundary)")
    
    # Failure modes summary
    print("\nFAILURE_MODE MAP:")
    for name, res5 in test5_results.items():
        print(f"  - {name:<30} : {res5['failure_type']} (CKA={res5['cka']:.4f}, Overlap={res5['neighbor_overlap']:.4f})")
        
    print("\nROBUSTNESS_CURVE (Performance-vs-Difficulty):")
    for pt in test4_results["performance_vs_difficulty"]:
        print(f"  - Alpha = {pt['alpha']:.1f} | ROC-AUC = {pt['roc_auc']:.4f} | PR-AUC = {pt['pr_auc']:.4f}")
        
    print("\nGLOBAL_STATUS          = " + global_status)
    print(f"Audit completed in {t_end - t_start:.2f} seconds.")
    print("Report saved to: " + REPORT_FILE)
    print("=" * 70)

if __name__ == "__main__":
    main()
