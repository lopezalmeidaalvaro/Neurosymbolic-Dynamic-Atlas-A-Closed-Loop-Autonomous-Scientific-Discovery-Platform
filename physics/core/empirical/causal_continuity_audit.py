import os
import sys
import json
import time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.signal import butter, filtfilt
from scipy.stats import spearmanr, pearsonr
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
import shap

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

from core.autonomous.latent_snapshot_exporter import compute_embedding_vector

# Paths
REPORT_DIR = os.path.join(ROOT_DIR, "dashboard", "public", "artifacts", "discoveries")
REPORT_FILE = os.path.join(REPORT_DIR, "causal_continuity_report.json")
DATA_DIR = os.path.join(ROOT_DIR, "data", "mitdb")

# MIT-BIH DS2 Records (AAMI Split)
TEST_RECORDS = [
    100,
    103,
    105,
    111,
    113,
    117,
    121,
    123,
    200,
    202,
    210,
    212,
    213,
    214,
    219,
    221,
    222,
    228,
    231,
    232,
    233,
    234,
]

V3_KEYS = [
    "perm_entropy",
    "spectral_entropy",
    "svd_entropy",
    "fractal_dim",
    "autocorr_decay",
    "robust_skewness",
    "robust_kurtosis",
    "temporal_irreversibility",
]

# ─────────────────────────────────────────────────────────────────────────────
# ENTROPY & NMI UTILITIES
# ─────────────────────────────────────────────────────────────────────────────


def compute_discrete_entropy(x, bins=20):
    hist, _ = np.histogram(x, bins=bins, density=False)
    p = hist / np.sum(hist)
    p = p[p > 0]
    return -np.sum(p * np.log(p))


def compute_discrete_mutual_information(x, y, bins=20):
    hist_2d, _, _ = np.histogram2d(x, y, bins=bins)
    p_xy = hist_2d / np.sum(hist_2d)
    p_x = p_xy.sum(axis=1)
    p_y = p_xy.sum(axis=0)

    mi = 0.0
    for i in range(bins):
        for j in range(bins):
            if p_xy[i, j] > 0 and p_x[i] > 0 and p_y[j] > 0:
                mi += p_xy[i, j] * np.log(p_xy[i, j] / (p_x[i] * p_y[j]))
    return mi


def compute_nmi(x, y, bins=20):
    mi = compute_discrete_mutual_information(x, y, bins=bins)
    h_x = compute_discrete_entropy(x, bins=bins)
    h_y = compute_discrete_entropy(y, bins=bins)
    denom = np.sqrt(h_x * h_y)
    if denom <= 1e-12:
        return 0.0
    return float(mi / denom)


def compute_linear_cka(A: np.ndarray, B: np.ndarray) -> float:
    A_centered = A - np.mean(A, axis=0)
    B_centered = B - np.mean(B, axis=0)
    dot_product = np.linalg.norm(B_centered.T @ A_centered, ord="fro") ** 2
    norm_A = np.linalg.norm(A_centered.T @ A_centered, ord="fro")
    norm_B = np.linalg.norm(B_centered.T @ B_centered, ord="fro")
    if norm_A * norm_B == 0:
        return 0.0
    return float(dot_product / (norm_A * norm_B))


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1 — DOMAIN CONSTRUCTION
# ─────────────────────────────────────────────────────────────────────────────


# Domain A: Synthetic (Lorenz vs Duffing)
def simulate_lorenz(length=110000, fs=360):
    t_end = length / fs
    t_eval = np.linspace(0, t_end, length)

    def rhs(t, state):
        x, y, z = state
        return [10.0 * (y - x), x * (28.0 - z) - y, x * y - (8.0 / 3.0) * z]

    sol = solve_ivp(rhs, (0, t_end), [1.0, 1.0, 1.0], t_eval=t_eval, method="RK45")
    return sol.y[0]


def simulate_duffing(length=110000, fs=360):
    t_end = length / fs
    t_eval = np.linspace(0, t_end, length)

    def rhs(t, state):
        x, y = state
        return [y, x - x**3 - 0.3 * y + 0.5 * np.cos(1.2 * t)]

    sol = solve_ivp(rhs, (0, t_end), [0.1, 0.0], t_eval=t_eval, method="RK45")
    return sol.y[0]


def build_domain_a_synthetic(n_windows=500):
    print("  Constructing Domain A (Synthetic Lorenz/Duffing)...")
    sig_lorenz = simulate_lorenz()
    sig_duffing = simulate_duffing()

    dt = 1.0 / 360.0
    X, y = [], []

    # Slice sliding windows
    window_size = 1000
    stride = 200

    # Lorenz (label 1)
    start = 5000  # skip transient
    for _ in range(n_windows):
        win = sig_lorenz[start : start + window_size]
        win_std = (win - np.mean(win)) / (np.std(win) + 1e-12)
        emb = compute_embedding_vector(win_std, dt)
        X.append([emb.get(k, 0.0) for k in V3_KEYS])
        y.append(1)
        start += stride

    # Duffing (label 0)
    start = 5000
    for _ in range(n_windows):
        win = sig_duffing[start : start + window_size]
        win_std = (win - np.mean(win)) / (np.std(win) + 1e-12)
        emb = compute_embedding_vector(win_std, dt)
        X.append([emb.get(k, 0.0) for k in V3_KEYS])
        y.append(0)
        start += stride

    return np.array(X), np.array(y)


# Domain B: Composite Biophysical
# Exact components weights (congeladas)
W_MORPH = 0.60
W_HRV_MORPH = 0.20
W_RESP = 0.20
K_INST = 0.10
K_MOTION = 0.10


def generate_biophysical_window(label, seed):
    np.random.seed(seed)
    t = np.arange(1000) / 360.0
    mu_center = 1.389  # 500 / 360

    # 1. Cardiac Morphology
    if label == 1:
        components = [
            {"amp": 0.12, "delay": -0.16, "width": 0.040},  # P wave
            {"amp": -0.22, "delay": -0.02, "width": 0.015},  # Q wave
            {"amp": 1.5, "delay": 0.0, "width": 0.020},  # R wave
            {"amp": -0.35, "delay": 0.02, "width": 0.015},  # S wave
            {"amp": 0.25, "delay": 0.18, "width": 0.060},  # T wave
        ]
    else:  # PVC beat
        components = [
            {"amp": -1.5, "delay": 0.0, "width": 0.080},
            {"amp": 3.5, "delay": 0.03, "width": 0.090},  # Wide QRS
            {"amp": -1.8, "delay": 0.06, "width": 0.080},
            {"amp": -1.0, "delay": 0.24, "width": 0.15},  # Inverted T wave
        ]

    morph = np.zeros(1000)
    for comp in components:
        mu = mu_center + comp["delay"]
        morph += comp["amp"] * np.exp(-((t - mu) ** 2) / (2 * comp["width"] ** 2))

    # 2. HRV (timing shift)
    hrv_shift = np.random.normal(0, 0.04)  # Timing jitter
    mu_hrv = mu_center + hrv_shift
    morph_hrv = np.zeros(1000)
    for comp in components:
        mu = mu_hrv + comp["delay"]
        morph_hrv += comp["amp"] * np.exp(-((t - mu) ** 2) / (2 * comp["width"] ** 2))

    # 3. Respiratory wander
    resp = np.sin(2 * np.pi * 0.25 * t)

    # 4. Instrumental noise
    white = np.random.normal(0, 1.0, 1000)
    f = np.fft.fft(white)
    freqs = np.fft.fftfreq(1000)
    scale = np.zeros(len(freqs))
    scale[1:500] = 1.0 / np.sqrt(np.abs(freqs[1:500]))
    scale[-500:] = 1.0 / np.sqrt(np.abs(freqs[-500:]))
    pink = np.real(np.fft.ifft(f * scale))
    pink = pink / np.std(pink)
    inst_noise = 0.5 * white + 0.5 * pink

    # 5. Motion artifact (decaying wander)
    motion = np.exp(-t / 0.5) * np.sin(2 * np.pi * 0.12 * t)

    # Mixed continuous coupling
    signal = (
        W_MORPH * morph_hrv + W_RESP * resp + K_INST * inst_noise + K_MOTION * motion
    )
    return signal


def build_domain_b_composite(n_windows=500):
    print("  Constructing Domain B (Composite Biophysical)...")
    X, y = [], []
    dt = 1.0 / 360.0

    # Normal (1)
    for s in range(n_windows):
        win = generate_biophysical_window(label=1, seed=s)
        win_std = (win - np.mean(win)) / (np.std(win) + 1e-12)
        emb = compute_embedding_vector(win_std, dt)
        X.append([emb.get(k, 0.0) for k in V3_KEYS])
        y.append(1)

    # PVC (0)
    for s in range(n_windows):
        win = generate_biophysical_window(label=0, seed=s + 2000)
        win_std = (win - np.mean(win)) / (np.std(win) + 1e-12)
        emb = compute_embedding_vector(win_std, dt)
        X.append([emb.get(k, 0.0) for k in V3_KEYS])
        y.append(0)

    return np.array(X), np.array(y)


# Domain C: Clinical (MIT-BIH DS2 test split)
def build_domain_c_clinical(max_beats_per_class=20):
    """
    Ingests and processes ECG windows from the local cache data/mitdb/
    exactly like in the previous bifurcated clinical audit.
    """
    print("  Constructing Domain C (Clinical MIT-BIH test)...")
    import wfdb

    X, y = [], []
    window_half = 500
    dt = 1.0 / 360.0

    for r in TEST_RECORDS:
        rec_path = os.path.join(DATA_DIR, str(r))
        if not os.path.exists(rec_path + ".dat"):
            continue

        record = wfdb.rdrecord(rec_path)
        signal = record.p_signal[:, 0]

        annotation = wfdb.rdann(rec_path, "atr")
        sample_indices = annotation.sample
        symbols = annotation.symbol

        n_count = 0
        v_count = 0

        for idx, sym in zip(sample_indices, symbols):
            if sym not in ("N", "V"):
                continue

            if sym == "N":
                if n_count >= max_beats_per_class:
                    continue
                label = 1
            else:
                if v_count >= max_beats_per_class:
                    continue
                label = 0

            if idx - window_half < 0 or idx + window_half > len(signal):
                continue

            win = signal[idx - window_half : idx + window_half]
            win = win[~np.isnan(win)]
            if len(win) < 1000:
                continue

            win_std = (win - np.mean(win)) / (np.std(win) + 1e-12)
            emb = compute_embedding_vector(win_std, dt)
            X.append([emb.get(k, 0.0) for k in V3_KEYS])
            y.append(label)

            if sym == "N":
                n_count += 1
            else:
                v_count += 1

    return np.array(X), np.array(y)


# Domain N: Null Control
def generate_null_window(label, seed):
    np.random.seed(seed)
    t = np.arange(1000) / 360.0
    if label == 1:
        # Gaussian White noise
        sig = np.random.normal(0, 1.0, 1000)
    else:
        # Coloured noise / random phases (Brownian noise)
        white = np.random.normal(0, 1.0, 1000)
        f = np.fft.fft(white)
        freqs = np.fft.fftfreq(1000)
        scale = np.zeros(len(freqs))
        scale[1:500] = 1.0 / np.abs(freqs[1:500])
        scale[-500:] = 1.0 / np.abs(freqs[-500:])
        sig = np.real(np.fft.ifft(f * scale))
        sig = sig / (np.std(sig) + 1e-12)

    # Add non-stationary sinusoidal drift
    sig = (
        sig
        + np.random.normal(0, 0.2)
        + 0.12 * np.sin(2 * np.pi * np.random.uniform(0.1, 1.0) * t)
    )
    return sig


def build_domain_n_null(n_windows=500):
    print("  Constructing Domain N (Null Control)...")
    X, y = [], []
    dt = 1.0 / 360.0

    # White (1)
    for s in range(n_windows):
        win = generate_null_window(label=1, seed=s)
        win_std = (win - np.mean(win)) / (np.std(win) + 1e-12)
        emb = compute_embedding_vector(win_std, dt)
        X.append([emb.get(k, 0.0) for k in V3_KEYS])
        y.append(1)

    # Red (0)
    for s in range(n_windows):
        win = generate_null_window(label=0, seed=s + 4000)
        win_std = (win - np.mean(win)) / (np.std(win) + 1e-12)
        emb = compute_embedding_vector(win_std, dt)
        X.append([emb.get(k, 0.0) for k in V3_KEYS])
        y.append(0)

    return np.array(X), np.array(y)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2 — BOOTSTRAP EXPECTED ATTRIBUTIONS
# ─────────────────────────────────────────────────────────────────────────────


def run_bootstrap_attributions(X, y, domain_name, M=50):
    """
    Executes M=50 bootstrap iterations to calculate the expected causal
    explanation vector C_bar, standard deviation, and 95% Confidence Intervals.
    """
    print(
        f"\n⚡ Auditing attributions for Domain {domain_name} via Bootstrap (M={M})..."
    )

    n_samples = len(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    # We will accumulate shap values, redundancies, and sufficiencies over the loops
    bootstrap_shap = np.zeros((M, 8))
    bootstrap_nmi = np.zeros((M, 8))
    bootstrap_suff = np.zeros((M, 8))

    # Pre-calculate NMI redundancy matrices and isolated sufficiencies for bootstrap
    for m in range(M):
        np.random.seed(m)
        indices = np.random.choice(len(X_train), len(X_train), replace=True)
        X_boot = X_train[indices]
        y_boot = y_train[indices]

        # Fit model
        clf_boot = RandomForestClassifier(n_estimators=20, random_state=None)
        clf_boot.fit(X_boot, y_boot)

        # 1. TreeSHAP Attribution
        exp = shap.TreeExplainer(clf_boot)
        vals = exp.shap_values(X_test)
        if isinstance(vals, list):
            vals_c1 = vals[1]
        elif len(vals.shape) == 3:
            vals_c1 = vals[:, :, 1]
        else:
            vals_c1 = vals
        bootstrap_shap[m] = np.mean(np.abs(vals_c1), axis=0)

        # 2. Non-linear redundancy NMI
        R_nmi = np.zeros((8, 8))
        for i in range(8):
            for j in range(8):
                R_nmi[i, j] = compute_nmi(X_boot[:, i], X_boot[:, j])
        for i in range(8):
            bootstrap_nmi[m, i] = float((np.sum(R_nmi[i]) - 1.0) / 7.0)

        # 3. Isolated Sufficiency AUC_i
        for i in range(8):
            clf_io = RandomForestClassifier(n_estimators=20, random_state=42)
            clf_io.fit(X_boot[:, [i]], y_boot)
            prob_io = clf_io.predict_proba(X_test[:, [i]])[:, 1]
            bootstrap_suff[m, i] = float(roc_auc_score(y_test, prob_io))

    # Calculate global Coefficient of Variation (CV) from bootstrap TreeSHAP
    global_cv = np.zeros(8)
    for i in range(8):
        mu_i = np.mean(bootstrap_shap[:, i])
        sigma_i = np.std(bootstrap_shap[:, i])
        global_cv[i] = float(sigma_i / mu_i) if mu_i > 0 else 0.0

    # Calculate C_i for each bootstrap iteration
    bootstrap_C = np.zeros((M, 8))
    for m in range(M):
        max_shap = np.max(bootstrap_shap[m])
        norm_shap = bootstrap_shap[m] / (max_shap if max_shap > 0 else 1.0)
        for i in range(8):
            I_i = norm_shap[i]
            AUC_i = bootstrap_suff[m, i]
            R_i = bootstrap_nmi[m, i]
            CV_i = global_cv[i]
            bootstrap_C[m, i] = 0.35 * I_i + 0.35 * AUC_i - 0.15 * R_i - 0.15 * CV_i

    # Calculate Expected attributions and confidence intervals
    C_bar = np.mean(bootstrap_C, axis=0)
    C_std = np.std(bootstrap_C, axis=0)

    ci_lower = np.percentile(bootstrap_C, 2.5, axis=0)
    ci_upper = np.percentile(bootstrap_C, 97.5, axis=0)

    feature_details = {}
    for i, name in enumerate(V3_KEYS):
        feature_details[name] = {
            "mean": float(C_bar[i]),
            "std": float(C_std[i]),
            "ci95": [float(ci_lower[i]), float(ci_upper[i])],
        }
        print(
            f"    - {name:<25} : C = {C_bar[i]:.4f} ± {C_std[i]:.4f} (95% CI: [{ci_lower[i]:.4f}, {ci_upper[i]:.4f}])"
        )

    return C_bar, feature_details


def permutation_test_continuity(
    X_domA,
    X_domC,
    X_domN,
    n_perm=10000,
    random_state=42,
    y_domA=None,
    y_domC=None,
    y_domN=None,
):
    """
    Executes a rigorous permutation test for the geometric continuity hypothesis.
    """
    print(f"  Initiating Permutation Test with n_perm={n_perm}...")

    if y_domA is None or y_domC is None or y_domN is None:
        # Fallback to standard labels if not provided
        y_domA = np.concatenate([np.ones(len(X_domA) // 2), np.zeros(len(X_domA) // 2)])
        y_domC = np.concatenate([np.ones(len(X_domC) // 2), np.zeros(len(X_domC) // 2)])
        y_domN = np.concatenate([np.ones(len(X_domN) // 2), np.zeros(len(X_domN) // 2)])

    # Align domains by class count to keep samples coupled
    n_class_A_1 = np.sum(y_domA == 1)
    n_class_A_0 = np.sum(y_domA == 0)
    n_class_C_1 = np.sum(y_domC == 1)
    n_class_C_0 = np.sum(y_domC == 0)
    n_class_N_1 = np.sum(y_domN == 1)
    n_class_N_0 = np.sum(y_domN == 0)

    n_samples_per_class = min(
        n_class_A_1, n_class_A_0, n_class_C_1, n_class_C_0, n_class_N_1, n_class_N_0
    )

    def align_domain(X, y, n_samples):
        idx_1 = np.where(y == 1)[0][:n_samples]
        idx_0 = np.where(y == 0)[0][:n_samples]
        idx_all = np.concatenate([idx_1, idx_0])
        return X[idx_all], y[idx_all]

    X_A_aligned, y_aligned = align_domain(X_domA, y_domA, n_samples_per_class)
    X_C_aligned, _ = align_domain(X_domC, y_domC, n_samples_per_class)
    X_N_aligned, _ = align_domain(X_domN, y_domN, n_samples_per_class)

    # Train 100-tree RF models on each domain
    clf_A = RandomForestClassifier(n_estimators=100, random_state=random_state)
    clf_A.fit(X_A_aligned, y_aligned)

    clf_C = RandomForestClassifier(n_estimators=100, random_state=random_state)
    clf_C.fit(X_C_aligned, y_aligned)

    clf_N = RandomForestClassifier(n_estimators=100, random_state=random_state)
    clf_N.fit(X_N_aligned, y_aligned)

    # Extract TreeSHAP attributions
    explainer_A = shap.TreeExplainer(clf_A)
    shap_values_A = explainer_A.shap_values(X_A_aligned)

    explainer_C = shap.TreeExplainer(clf_C)
    shap_values_C = explainer_C.shap_values(X_C_aligned)

    explainer_N = shap.TreeExplainer(clf_N)
    shap_values_N = explainer_N.shap_values(X_N_aligned)

    def get_shap_c1(vals):
        if isinstance(vals, list):
            return vals[1]
        elif len(vals.shape) == 3:
            return vals[:, :, 1]
        else:
            return vals

    shap_A = get_shap_c1(shap_values_A)
    shap_C = get_shap_c1(shap_values_C)
    shap_N = get_shap_c1(shap_values_N)

    def compute_K_from_shap(s_A, s_C, s_N):
        mean_A = np.mean(np.abs(s_A), axis=0)
        mean_C = np.mean(np.abs(s_C), axis=0)
        mean_N = np.mean(np.abs(s_N), axis=0)

        s1 = spearmanr(mean_A, mean_C)[0]
        s2 = spearmanr(mean_C, mean_N)[0]
        s3 = spearmanr(mean_A, mean_N)[0]
        return float(s1 + s2 - s3)

    K_obs = compute_K_from_shap(shap_A, shap_C, shap_N)
    print(f"    - Observed Continuity K: {K_obs:.6f}")

    # Run shuffling permutations
    np.random.seed(random_state)
    null_K = []
    N = len(y_aligned)

    shap_all = np.stack([shap_A, shap_C, shap_N], axis=1)  # shape (N, 3, 8)

    perms = np.array([[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]])

    print("    - Computing permuted null distribution...")
    for _ in range(n_perm):
        idx = np.random.randint(6, size=N)
        row_perms = perms[idx]
        shap_perm = shap_all[np.arange(N)[:, None], row_perms]

        K_perm = compute_K_from_shap(
            shap_perm[:, 0, :], shap_perm[:, 1, :], shap_perm[:, 2, :]
        )
        null_K.append(K_perm)

    null_K = np.array(null_K)
    p_value = float(np.sum(null_K >= K_obs) / n_perm)
    ci_lower = float(np.percentile(null_K, 2.5))
    ci_upper = float(np.percentile(null_K, 97.5))

    print(
        f"    - Permutation test results: p_val={p_value:.4f}, CI_null=[{ci_lower:.4f}, {ci_upper:.4f}]"
    )

    # Export results to json
    results = {
        "p_value": p_value,
        "ΔK_obs": K_obs,
        "CI_null_lower": ci_lower,
        "CI_null_upper": ci_upper,
    }

    out_dir = os.path.join(ROOT_DIR, "artifacts")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "permutation_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
    print(f"  Permutation results exported to: {out_file}")

    return p_value, K_obs, ci_lower, ci_upper


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTINUITY PROCESSOR
# ─────────────────────────────────────────────────────────────────────────────


def main():
    t_start = time.time()

    print("=" * 80)
    print("🔮 PRINCIPAL COMPUTATIONAL PHYSICS AUDITOR — CAUSAL CONTINUITY AUDIT")
    print("=" * 80)

    # TEST 1 — DOMAIN CONSTRUCTION & PERMUTATION TEST
    print("\n[TEST 1] Slicing and constructing domain structures...")

    X_A, y_A = build_domain_a_synthetic()
    X_B, y_B = build_domain_b_composite()
    X_C, y_C = build_domain_c_clinical()
    X_N, y_N = build_domain_n_null()

    print(
        "\n⚡ Running Rigorous Permutation Test for Geometric Continuity Hypothesis..."
    )
    p_value, K_obs, ci_lower, ci_upper = permutation_test_continuity(
        X_A, X_C, X_N, n_perm=10000, random_state=42, y_domA=y_A, y_domC=y_C, y_domN=y_N
    )

    print("\n  Successfully compiled domain points:")
    print(f"    - Domain A (Synthetic) : {X_A.shape[0]} windows")
    print(f"    - Domain B (Composite) : {X_B.shape[0]} windows")
    print(f"    - Domain C (Clinical)  : {X_C.shape[0]} windows")
    print(f"    - Domain N (Null)      : {X_N.shape[0]} windows")

    # TEST 2 — BOOTSTRAP EXPECTED ATTRIBUTIONS (M=50)
    C_bar_A, details_A = run_bootstrap_attributions(X_A, y_A, "A — Synthetic")
    C_bar_B, details_B = run_bootstrap_attributions(
        X_B, y_B, "B — Composite Biophysical"
    )
    C_bar_C, details_C = run_bootstrap_attributions(X_C, y_C, "C — Clinical")
    C_bar_N, details_N = run_bootstrap_attributions(X_N, y_N, "N — Null Control")

    # ── 1000 BOOTSTRAP RESAMPLES FOR GEOMETRIC DEFORMATION ────────────────────
    print("\n⚡ Running 1000 Bootstrap Resamples for D_emb and D_attr distributions...")
    D_emb_samples = []
    D_attr_samples = []

    # Train/test split exactly like in run_bootstrap_attributions
    X_A_train, X_A_test, y_A_train, y_A_test = train_test_split(
        X_A, y_A, test_size=0.3, random_state=42
    )
    X_C_train, X_C_test, y_C_train, y_C_test = train_test_split(
        X_C, y_C, test_size=0.3, random_state=42
    )

    min_samples = min(len(X_A), len(X_C))

    def get_shap_c1_local(vals):
        if isinstance(vals, list):
            return vals[1]
        elif len(vals.shape) == 3:
            return vals[:, :, 1]
        else:
            return vals

    for m in range(1000):
        # 1. Bootstrap A
        np.random.seed(m)
        idx_A = np.random.choice(len(X_A_train), len(X_A_train), replace=True)
        X_A_boot = X_A_train[idx_A]
        y_A_boot = y_A_train[idx_A]

        clf_A = RandomForestClassifier(
            n_estimators=100, random_state=42, max_depth=None, n_jobs=-1
        )
        clf_A.fit(X_A_boot, y_A_boot)

        exp_A = shap.TreeExplainer(clf_A)
        vals_A = exp_A.shap_values(X_A_test)
        shap_mean_A = np.mean(np.abs(get_shap_c1_local(vals_A)), axis=0)

        # 2. Bootstrap C
        idx_C = np.random.choice(len(X_C_train), len(X_C_train), replace=True)
        X_C_boot = X_C_train[idx_C]
        y_C_boot = y_C_train[idx_C]

        clf_C = RandomForestClassifier(
            n_estimators=100, random_state=42, max_depth=None, n_jobs=-1
        )
        clf_C.fit(X_C_boot, y_C_boot)

        exp_C = shap.TreeExplainer(clf_C)
        vals_C = exp_C.shap_values(X_C_test)
        shap_mean_C = np.mean(np.abs(get_shap_c1_local(vals_C)), axis=0)

        # 3. D_emb (Linear CKA) on bootstrapped input features
        idx_A_all = np.random.choice(len(X_A), len(X_A), replace=True)
        idx_C_all = np.random.choice(len(X_C), len(X_C), replace=True)
        X_A_all_boot = X_A[idx_A_all][:min_samples]
        X_C_all_boot = X_C[idx_C_all][:min_samples]

        cka_boot = compute_linear_cka(X_A_all_boot, X_C_all_boot)
        D_emb_samples.append(1.0 - cka_boot)

        # 4. D_attr (Spearman) on SHAP importances
        s3_boot = spearmanr(shap_mean_A, shap_mean_C)[0]
        D_attr_samples.append(1.0 - s3_boot)

        if (m + 1) % 200 == 0:
            print(f"    - Completed {m + 1}/1000 bootstrap iterations...")

    # Calculate statistics and CIs
    D_emb_samples = np.array(D_emb_samples)
    D_attr_samples = np.array(D_attr_samples)

    D_emb_mean = float(np.mean(D_emb_samples))
    D_emb_ci_lower = float(np.percentile(D_emb_samples, 2.5))
    D_emb_ci_upper = float(np.percentile(D_emb_samples, 97.5))

    D_attr_mean = float(np.mean(D_attr_samples))
    D_attr_ci_lower = float(np.percentile(D_attr_samples, 2.5))
    D_attr_ci_upper = float(np.percentile(D_attr_samples, 97.5))

    print(
        f"  D_emb (CKA)      : {D_emb_mean:.6f} (95% CI: [{D_emb_ci_lower:.6f}, {D_emb_ci_upper:.6f}])"
    )
    print(
        f"  D_attr (Spearman): {D_attr_mean:.6f} (95% CI: [{D_attr_ci_lower:.6f}, {D_attr_ci_upper:.6f}])"
    )

    # Export bootstrap results to artifacts/bootstrap_results.json
    boot_results = {
        "D_emb_mean": D_emb_mean,
        "D_emb_ci_lower": D_emb_ci_lower,
        "D_emb_ci_upper": D_emb_ci_upper,
        "D_attr_mean": D_attr_mean,
        "D_attr_ci_lower": D_attr_ci_lower,
        "D_attr_ci_upper": D_attr_ci_upper,
        "D_emb_samples": D_emb_samples.tolist(),
        "D_attr_samples": D_attr_samples.tolist(),
    }

    boot_out_dir = os.path.join(ROOT_DIR, "artifacts")
    os.makedirs(boot_out_dir, exist_ok=True)
    boot_out_file = os.path.join(boot_out_dir, "bootstrap_results.json")
    with open(boot_out_file, "w", encoding="utf-8") as f:
        json.dump(boot_results, f, indent=4)
    print(f"  Bootstrap results exported to: {boot_out_file}")

    # TEST 3 — TRANSITION MATRICES
    print("\n[TEST 3] Calculating Transition Matrix Correlations...")
    # Spearman rank correlation on expected explanation vectors
    S1 = float(spearmanr(C_bar_A, C_bar_B)[0])
    S2 = float(spearmanr(C_bar_B, C_bar_C)[0])
    S3 = float(spearmanr(C_bar_A, C_bar_C)[0])

    S1_null = float(spearmanr(C_bar_A, C_bar_N)[0])
    S2_null = float(spearmanr(C_bar_N, C_bar_C)[0])

    print(f"  S1 (Synthetic -> Composite)  : {S1:+.6f}")
    print(f"  S2 (Composite -> Clinical)   : {S2:+.6f}")
    print(f"  S3 (Synthetic -> Clinical)   : {S3:+.6f}")
    print(f"  S1_null (Synthetic -> Null)  : {S1_null:+.6f}")
    print(f"  S2_null (Null -> Clinical)   : {S2_null:+.6f}")

    # TEST 4 — CONTINUITY INDICES
    print("\n[TEST 4] Compiling Representational Continuity Indices...")
    K = S1 + S2 - S3
    K_null = S1_null + S2_null - S3

    denom = S1 + S2
    kappa_eps = (2 * (abs(S3) + 0.05)) / denom if abs(denom) > 1e-6 else 99.0

    denom_null = S1_null + S2_null
    kappa_eps_null = (
        (2 * (abs(S3) + 0.05)) / denom_null if abs(denom_null) > 1e-6 else 99.0
    )

    print(f"  Continuity Gain K            : {K:.6f}")
    print(f"  Continuity Gain K_null       : {K_null:.6f}")
    print(f"  Regularized Index κ_ϵ        : {kappa_eps:.6f}")
    print(f"  Regularized Index κ_ϵ_null   : {kappa_eps_null:.6f}")

    # TEST 5 — INTERNAL REPRESENTATION SHIFTS
    print("\n[TEST 5] Evaluating Representation vs Attribution Shifts...")
    # Resize embedding matrices for linear CKA
    min_samples = min(len(X_A), len(X_C))
    X_A_sub = X_A[:min_samples]
    X_C_sub = X_C[:min_samples]
    cka = compute_linear_cka(X_A_sub, X_C_sub)

    D_emb = 1.0 - cka
    D_attr = 1.0 - S3

    print(f"  Latent Representation Shift (D_emb)   : {D_emb:.6f}")
    print(f"  Causal Attribution Shift (D_attr)      : {D_attr:.6f}")

    # DIAGNOSIS CLASSIFICATION
    delta_K = K - K_null
    delta_kappa = kappa_eps - kappa_eps_null

    if delta_K >= 0.35 and delta_kappa <= -0.15:
        continuity_status = "STRONG_CONTINUITY"
    elif delta_K >= 0.15 and delta_kappa <= -0.05:
        continuity_status = "MODERATE_CONTINUITY"
    elif delta_K >= -0.05:
        continuity_status = "WEAK_CONTINUITY"
    else:
        continuity_status = "NO_EVIDENCE_OF_CONTINUITY"

    print(f"\n📢 REPRESENTATIONAL CONTINUITY DIAGNOSIS: {continuity_status}")

    # Compile Report
    report = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "audit_type": "causal representational continuity validation",
            "version": "V3",
            "weights": {
                "w_morph": W_MORPH,
                "w_hrv_morph": W_HRV_MORPH,
                "w_resp": W_RESP,
                "k_inst": K_INST,
                "k_motion": K_MOTION,
            },
        },
        "test1_domains": {
            "domain_a_samples": len(X_A),
            "domain_b_samples": len(X_B),
            "domain_c_samples": len(X_C),
            "domain_n_samples": len(X_N),
        },
        "permutation_test": {
            "p_value": p_value,
            "K_obs": K_obs,
            "ci_null_lower": ci_lower,
            "ci_null_upper": ci_upper,
        },
        "test2_bootstrap_attributions": {
            "domain_a": details_A,
            "domain_b": details_B,
            "domain_c": details_C,
            "domain_n": details_N,
        },
        "test3_transitions": {
            "S1": S1,
            "S2": S2,
            "S3": S3,
            "S1_null": S1_null,
            "S2_null": S2_null,
        },
        "test4_continuity_indices": {
            "K": K,
            "K_null": K_null,
            "kappa_eps": kappa_eps,
            "kappa_eps_null": kappa_eps_null,
            "delta_K": delta_K,
            "delta_kappa": delta_kappa,
        },
        "test5_shifts": {"D_emb": D_emb, "D_attr": D_attr, "cka_val": cka},
        "diagnosis": {"status": continuity_status},
    }

    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"📂 Compiled continuity report exported to: {REPORT_FILE}")

    # ── REQUIRED TERMINAL DUMP (INDICATOR PANEL) ──────────────────────────────
    print("\n" + "═" * 80)
    print("🏆 FINAL REPRESENTATIONAL CONTINUITY METRICS PANEL")
    print("═" * 80)
    print(f"  Continuity Gain (K)           : {K:.6f}")
    print(f"  Continuity Gain Null (K_null)  : {K_null:.6f}")
    print(f"  Regularized Index (κ_ϵ)       : {kappa_eps:.6f}")
    print(f"  Regularized Index Null        : {kappa_eps_null:.6f}")
    print("  " + "─" * 76)
    print(f"  Latent Representation Shift (D_emb)  : {D_emb:.6f}")
    print(f"  Causal Attribution Shift (D_attr)     : {D_attr:.6f}")
    print("  " + "─" * 76)
    print(f"  REPRESENTATIONAL CONTINUITY STATUS   : {continuity_status}")
    print("═" * 80)

    # Regenerate Fig 5 KDE plot dynamically
    print("\n📈 Regenerating Fig 5 KDE plot with real bootstrap results...")
    try:
        import subprocess

        plot_script = os.path.join(ROOT_DIR, "temp_scripts", "fig5_bootstrap_kde.py")
        subprocess.run(["python", plot_script], check=True)
        print("  Fig 5 KDE plot successfully regenerated!")
    except Exception as e:
        print(f"  Warning: Could not regenerate Fig 5 KDE plot: {e}")

    t_end = time.time()
    print(f"Audit completed in {t_end - t_start:.2f} seconds.\n")


if __name__ == "__main__":
    main()
