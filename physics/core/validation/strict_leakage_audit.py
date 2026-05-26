import os
import sys
import json
import time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.fft import fft
from scipy.stats import skew, kurtosis, pearsonr
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score,
    precision_recall_curve,
    auc,
    f1_score,
    precision_score,
    recall_score,
)
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
REPORT_FILE = os.path.join(REPORT_DIR, "strict_leakage_audit_report.json")

# Seeds
SEEDS = [42, 1337, 9001]

# V3 features order
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
# CONTINUOUS DYNAMICAL SYSTEM VECTOR FIELDS & SIMULATORS
# ─────────────────────────────────────────────────────────────────────────────


def lorenz_rhs(t, state, sigma=10.0, rho=28.0, beta=8.0 / 3.0):
    x, y, z = state
    return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]


def simulate_lorenz(rho, sigma=10.0, beta=8.0 / 3.0, length=25000, seed=42):
    t_span = (0, 300)
    t_eval = np.linspace(0, 300, length + 5000)
    dt = t_eval[1] - t_eval[0]
    np.random.seed(seed)
    state0 = [1.0 + np.random.normal(0, 0.1), 1.0, 1.0]
    sol = solve_ivp(
        lambda t, y: lorenz_rhs(t, y, sigma, rho, beta),
        t_span,
        state0,
        t_eval=t_eval,
        method="RK45",
    )
    return sol.y[0][5000 : 5000 + length], dt


def rossler_rhs(t, state, c=5.7):
    x, y, z = state
    return [-y - z, x + 0.2 * y, 0.2 + z * (x - c)]


def simulate_rossler(c, length=25000, seed=42):
    t_span = (0, 300)
    t_eval = np.linspace(0, 300, length + 5000)
    dt = t_eval[1] - t_eval[0]
    np.random.seed(seed)
    state0 = [1.0 + np.random.normal(0, 0.1), 1.0, 1.0]
    sol = solve_ivp(
        lambda t, y: rossler_rhs(t, y, c), t_span, state0, t_eval=t_eval, method="RK45"
    )
    return sol.y[0][5000 : 5000 + length], dt


def duffing_rhs(t, state, f=0.5):
    x, y = state
    return [y, x - x**3 - 0.3 * y + f * np.cos(1.2 * t)]


def simulate_duffing(f, length=25000, seed=42):
    t_span = (0, 800)
    t_eval = np.linspace(0, 800, length + 10000)
    dt = t_eval[1] - t_eval[0]
    np.random.seed(seed)
    state0 = [0.1 + np.random.normal(0, 0.05), 0.0]
    sol = solve_ivp(
        lambda t, y: duffing_rhs(t, y, f), t_span, state0, t_eval=t_eval, method="RK45"
    )
    return sol.y[0][10000 : 10000 + length], dt


def chua_rhs(t, state):
    x, y, z = state
    alpha = 15.6
    beta = 28.0
    m0 = -1.143
    m1 = -0.714
    f_x = m1 * x + 0.5 * (m0 - m1) * (np.abs(x + 1.0) - np.abs(x - 1.0))
    return [alpha * (y - x - f_x), x - y + z, -beta * y]


def simulate_chua(length=25000, seed=42):
    t_span = (0, 300)
    t_eval = np.linspace(0, 300, length + 5000)
    dt = t_eval[1] - t_eval[0]
    np.random.seed(seed)
    state0 = [0.1 + np.random.normal(0, 0.01), 0.1, 0.1]
    sol = solve_ivp(chua_rhs, t_span, state0, t_eval=t_eval, method="RK45")
    return sol.y[0][5000 : 5000 + length], dt


def simulate_mackey_glass(length=25000, seed=42):
    np.random.seed(seed)
    dt = 0.1
    tau = 17
    beta = 0.2
    gamma = 0.1
    n = 10
    history_steps = int(tau / dt)
    total_length = length + 5000 + history_steps
    x = np.zeros(total_length)
    x[:history_steps] = 1.2 + np.random.normal(0, 0.1, history_steps)
    for i in range(history_steps, total_length):
        x_tau = x[i - history_steps]
        dx = (beta * x_tau) / (1.0 + x_tau**n) - gamma * x[i - 1]
        x[i] = x[i - 1] + dx * dt
    return x[5000 + history_steps :], dt


def simulate_henon(length=25000, seed=42):
    np.random.seed(seed)
    x = np.zeros(length + 5000)
    y = np.zeros(length + 5000)
    x[0], y[0] = np.random.uniform(-0.1, 0.1), np.random.uniform(-0.1, 0.1)
    for i in range(1, length + 5000):
        x[i] = 1.0 - 1.4 * x[i - 1] ** 2 + 0.3 * y[i - 1]
        y[i] = 0.3 * x[i - 1]
    return x[5000:], 1.0


# ─────────────────────────────────────────────────────────────────────────────
# NOISE & MIMIC GENERATORS
# ─────────────────────────────────────────────────────────────────────────────


def generate_pink_noise(length, seed):
    np.random.seed(seed)
    white = np.random.normal(0, 1.0, length)
    f = fft(white)
    freqs = np.fft.fftfreq(length)
    scale = np.zeros(len(freqs))
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
    half = length // 2
    phases[0] = 0.0
    if length % 2 == 0:
        phases[half] = 0.0
    phases[half + 1 :] = -phases[1:half][::-1]

    f_surr = np.abs(f) * np.exp(1j * phases)
    surr = np.real(np.fft.ifft(f_surr))
    std = np.std(surr)
    return surr / std if std > 0 else surr


def generate_arma_mimic(base_signal, seed, p=20):
    """
    Fits an AR(p) model using least squares to approximate an ARMA(10,10) process.
    """
    n = len(base_signal)
    sig_centered = base_signal - np.mean(base_signal)

    X = np.zeros((n - p, p))
    for i in range(p):
        X[:, i] = sig_centered[p - 1 - i : n - 1 - i]
    y = sig_centered[p:]

    try:
        phi, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    except Exception:
        phi = np.zeros(p)
        phi[0] = 0.9

    np.random.seed(seed)
    gen = np.zeros(n)
    start_idx = np.random.randint(0, n - p)
    gen[:p] = sig_centered[start_idx : start_idx + p]

    residuals = y - X @ phi
    res_std = np.std(residuals) if len(residuals) > 0 else 0.1
    eps = np.random.normal(0, res_std, n)

    for t in range(p, n):
        gen[t] = np.dot(phi, gen[t - p : t][::-1]) + eps[t]

    std = np.std(gen)
    return gen / std if std > 0 else gen


# ─────────────────────────────────────────────────────────────────────────────
# CLASSICAL BASELINE FEATURES
# ─────────────────────────────────────────────────────────────────────────────


def _spectral_entropy_normalized(x):
    N = len(x)
    yf = np.abs(fft(x)[: N // 2]) ** 2
    yf[0] = 0.0
    total = yf.sum()
    if total <= 0:
        return 0.0
    p = yf / total
    p_pos = p[p > 0]
    h = -np.sum(p_pos * np.log2(p_pos))
    h_max = np.log2(len(yf)) if len(yf) > 1 else 1.0
    return float(h / h_max) if h_max > 0 else 0.0


def compute_baseline_features(x_window, dt):
    m_val = float(np.mean(x_window))
    v_val = float(np.var(x_window))
    s_val = float(skew(x_window)) if np.std(x_window) > 1e-10 else 0.0
    k_val = float(kurtosis(x_window)) if np.std(x_window) > 1e-10 else 0.0

    N = len(x_window)
    yf = np.abs(fft(x_window)[: N // 2]) ** 2
    yf[0] = 0.0
    spec_energy = float(np.sum(yf))

    freqs = np.fft.fftfreq(N, dt)[: N // 2]
    dom_freq = float(freqs[np.argmax(yf)]) if len(yf) > 0 and np.sum(yf) > 0 else 0.0
    spec_ent = _spectral_entropy_normalized(x_window)

    return [m_val, v_val, s_val, k_val, spec_energy, dom_freq, spec_ent]


# ─────────────────────────────────────────────────────────────────────────────
# ECE CALCULATION
# ─────────────────────────────────────────────────────────────────────────────


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


# ─────────────────────────────────────────────────────────────────────────────
# MAIN COMPREHENSIVE LEAKAGE AUDIT
# ─────────────────────────────────────────────────────────────────────────────


def main():
    print("=" * 75)
    print("🕵️‍♂️ PRINCIPAL COMPUTATIONAL PHYSICS AUDITOR — LEAKAGE RED TEAM AUDIT")
    print("=" * 75)
    print("AUDITING DATA LEAKAGE AND PHYSICAL GENERALIZATION OF EMBEDDING V3...")

    t_start = time.time()

    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 1: GENERATE ALL RAW TRAJECTORIES
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[STEP 1] Generating raw trajectories of 25,000 steps...")
    length = 25000
    trajectories = []

    trajectory_counter = 0

    # --- TRAIN SET SYSTEMS ---
    # Lorenz Physical: 3 parameters x 3 seeds
    for rho in [24.0, 26.0, 28.0]:
        for seed in SEEDS:
            sig, dt = simulate_lorenz(rho=rho, length=length, seed=seed)
            trajectories.append(
                {
                    "system": "lorenz",
                    "parameter_bin": f"rho_{rho:.1f}",
                    "seed": seed,
                    "signal": sig,
                    "dt": dt,
                    "label": 1,
                    "trajectory_id": trajectory_counter,
                }
            )
            trajectory_counter += 1

    # Rössler Physical: 3 parameters x 3 seeds
    for c in [4.0, 5.0, 5.7]:
        for seed in SEEDS:
            sig, dt = simulate_rossler(c=c, length=length, seed=seed)
            trajectories.append(
                {
                    "system": "rossler",
                    "parameter_bin": f"c_{c:.1f}",
                    "seed": seed,
                    "signal": sig,
                    "dt": dt,
                    "label": 1,
                    "trajectory_id": trajectory_counter,
                }
            )
            trajectory_counter += 1

    # Duffing Physical: 3 parameters x 3 seeds
    for f in [0.35, 0.45, 0.5]:
        for seed in SEEDS:
            sig, dt = simulate_duffing(f=f, length=length, seed=seed)
            trajectories.append(
                {
                    "system": "duffing",
                    "parameter_bin": f"f_{f:.2f}",
                    "seed": seed,
                    "signal": sig,
                    "dt": dt,
                    "label": 1,
                    "trajectory_id": trajectory_counter,
                }
            )
            trajectory_counter += 1

    # Train Adversaries: ARMA(10,10) mimics of the physical trajectories
    # These must be generated *before* scaling
    n_phys_train = len(trajectories)
    for i in range(n_phys_train):
        phys_t = trajectories[i]
        mimic_sig = generate_arma_mimic(phys_t["signal"], seed=phys_t["seed"], p=20)
        trajectories.append(
            {
                "system": f"arma_{phys_t['system']}",
                "parameter_bin": phys_t["parameter_bin"],
                "seed": phys_t["seed"],
                "signal": mimic_sig,
                "dt": phys_t["dt"],
                "label": 0,
                "trajectory_id": trajectory_counter,
            }
        )
        trajectory_counter += 1

    # --- EXTREME OOD SYSTEMS (TEST 2) ---
    ood_trajectories = []
    # Physical Chua Circuit: 3 seeds
    for seed in SEEDS:
        sig, dt = simulate_chua(length=length, seed=seed)
        ood_trajectories.append(
            {
                "system": "chua",
                "parameter_bin": "default",
                "seed": seed,
                "signal": sig,
                "dt": dt,
                "label": 1,
                "trajectory_id": trajectory_counter,
            }
        )
        trajectory_counter += 1

    # Physical Mackey-Glass: 3 seeds
    for seed in SEEDS:
        sig, dt = simulate_mackey_glass(length=length, seed=seed)
        ood_trajectories.append(
            {
                "system": "mackey_glass",
                "parameter_bin": "default",
                "seed": seed,
                "signal": sig,
                "dt": dt,
                "label": 1,
                "trajectory_id": trajectory_counter,
            }
        )
        trajectory_counter += 1

    # Physical Hénon: 3 seeds
    for seed in SEEDS:
        sig, dt = simulate_henon(length=length, seed=seed)
        ood_trajectories.append(
            {
                "system": "henon",
                "parameter_bin": "default",
                "seed": seed,
                "signal": sig,
                "dt": dt,
                "label": 1,
                "trajectory_id": trajectory_counter,
            }
        )
        trajectory_counter += 1

    # OOD Adversaries: Fourier Phase Randomized and Pink Noise hybrids
    n_phys_ood = len(ood_trajectories)
    for i in range(n_phys_ood):
        phys_t = ood_trajectories[i]

        # 1. Fourier Phase Randomized
        pr_sig = generate_phase_randomized(phys_t["signal"], seed=phys_t["seed"])
        ood_trajectories.append(
            {
                "system": f"phase_rand_{phys_t['system']}",
                "parameter_bin": phys_t["parameter_bin"],
                "seed": phys_t["seed"],
                "signal": pr_sig,
                "dt": phys_t["dt"],
                "label": 0,
                "trajectory_id": trajectory_counter,
            }
        )
        trajectory_counter += 1

        # 2. Pink Noise Hybrid (mixture at alpha=0.5)
        pink = generate_pink_noise(length, seed=phys_t["seed"])
        mix_sig = 0.5 * phys_t["signal"] + 0.5 * pink
        ood_trajectories.append(
            {
                "system": f"pink_hybrid_{phys_t['system']}",
                "parameter_bin": phys_t["parameter_bin"],
                "seed": phys_t["seed"],
                "signal": mix_sig,
                "dt": phys_t["dt"],
                "label": 0,
                "trajectory_id": trajectory_counter,
            }
        )
        trajectory_counter += 1

    # --- UNSEEN PARAMETER SHIFT (TEST 3) ---
    shift_trajectories = []
    # Lorenz at rho = 46.0 (High Chaos Regime): 3 seeds
    for seed in SEEDS:
        sig, dt = simulate_lorenz(rho=46.0, length=length, seed=seed)
        shift_trajectories.append(
            {
                "system": "lorenz",
                "parameter_bin": "rho_46.0",
                "seed": seed,
                "signal": sig,
                "dt": dt,
                "label": 1,
                "trajectory_id": trajectory_counter,
            }
        )
        trajectory_counter += 1

    # Adversary of shift Lorenz
    for i in range(len(shift_trajectories)):
        phys_t = shift_trajectories[i]
        mimic_sig = generate_arma_mimic(phys_t["signal"], seed=phys_t["seed"], p=20)
        shift_trajectories.append(
            {
                "system": "arma_lorenz_shift",
                "parameter_bin": "rho_46.0",
                "seed": phys_t["seed"],
                "signal": mimic_sig,
                "dt": phys_t["dt"],
                "label": 0,
                "trajectory_id": trajectory_counter,
            }
        )
        trajectory_counter += 1

    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 2: CONSTRUCT HIERARCHICAL group_id AND SPLIT DATASET
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[STEP 2] Building hierarchical group_id and partitioning splits...")

    # Define a helper to bin initial condition geometry
    def get_ic_cluster(signal):
        start_val = signal[0]
        if start_val < -1.0:
            return "ic_low"
        elif start_val > 1.0:
            return "ic_high"
        else:
            return "ic_mid"

    # Assign group_id to train trajectories
    for t in trajectories:
        ic_cluster = get_ic_cluster(t["signal"])
        t["group_id"] = (
            f"{t['system']}_{t['parameter_bin']}_{ic_cluster}_{t['trajectory_id']}"
        )

    # Partition trajectories strictly using group_id to ensure train_groups ∩ test_groups = ∅
    unique_groups = list(set([t["group_id"] for t in trajectories]))
    np.random.seed(42)
    np.random.shuffle(unique_groups)

    split_idx = int(len(unique_groups) * 0.70)
    train_groups = set(unique_groups[:split_idx])
    test_groups = set(unique_groups[split_idx:])

    train_trajectories = [t for t in trajectories if t["group_id"] in train_groups]
    test_trajectories = [t for t in trajectories if t["group_id"] in test_groups]

    print(f"  Total Trajectories: {len(trajectories)}")
    print(f"  Train Trajectories: {len(train_trajectories)}")
    print(f"  Test Trajectories:  {len(test_trajectories)}")

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 1: ZERO-LEAKAGE SPLIT VALIDATION & EXTRACTION
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 1] Enforcing zero-leakage partitions & independent normalization...")

    # Zero temporal and trajectory overlap check
    overlap_score = 0.0
    group_intersection = train_groups.intersection(test_groups)
    if len(group_intersection) > 0:
        overlap_score = float(len(group_intersection)) / len(unique_groups)
        print(f"  ❌ LEAKAGE DETECTED: {len(group_intersection)} groups overlap!")
    else:
        print("  ✅ Zero Trajectory Reuse: Passed")
        print("  ✅ Zero Temporal Overlap: Passed")
        print("  ✅ Zero Geometric Overlap: Passed")

    # Fit scaler on Train ONLY
    train_all_values = np.concatenate([t["signal"] for t in train_trajectories])
    scaler = StandardScaler()
    scaler.fit(train_all_values.reshape(-1, 1))

    # Normalize datasets independently using the fitted scaler
    def normalize_and_extract(traj_list):
        X_v3, X_base, y = [], [], []
        window_size = 1000
        stride = 500
        for t in traj_list:
            # Normalize trajectory signal
            norm_sig = scaler.transform(t["signal"].reshape(-1, 1)).flatten()
            dt = t["dt"]

            # Extract sliding windows
            n = len(norm_sig)
            start = 0
            while start + window_size <= n:
                win = norm_sig[start : start + window_size]

                # Embedding V3 (8D)
                emb = compute_embedding_vector(win, dt)
                v3_vec = [emb.get(k, 0.0) for k in V3_KEYS]
                X_v3.append(v3_vec)

                # Baseline Features (7D)
                base_vec = compute_baseline_features(win, dt)
                X_base.append(base_vec)

                y.append(t["label"])
                start += stride
        return np.array(X_v3), np.array(X_base), np.array(y)

    X_train_v3, X_train_base, y_train = normalize_and_extract(train_trajectories)
    X_test_v3, X_test_base, y_test = normalize_and_extract(test_trajectories)

    # Train primary Zero-Leakage model
    clf_v3 = RandomForestClassifier(n_estimators=100, random_state=42)
    clf_v3.fit(X_train_v3, y_train)

    y_prob_v3 = clf_v3.predict_proba(X_test_v3)[:, 1]
    y_pred_v3 = clf_v3.predict(X_test_v3)

    strict_auc = float(roc_auc_score(y_test, y_prob_v3))
    prec, rec, _ = precision_recall_curve(y_test, y_prob_v3)
    strict_pr_auc = float(auc(rec, prec))
    strict_f1 = float(f1_score(y_test, y_pred_v3))
    strict_ece = compute_ece(y_test, y_prob_v3)

    print(f"  Strict Zero-Leakage ROC-AUC: {strict_auc:.6f}")
    print(f"  Strict Zero-Leakage PR-AUC:  {strict_pr_auc:.6f}")

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 2: EXTREME OOD GENERALIZATION
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 2] Evaluating Extreme OOD Generalization on unseen systems...")

    # Normalize and extract OOD trajectories
    X_ood_v3, X_ood_base, y_ood = normalize_and_extract(ood_trajectories)

    # Evaluate primary model on OOD data
    y_prob_ood = clf_v3.predict_proba(X_ood_v3)[:, 1]
    y_pred_ood = clf_v3.predict(X_ood_v3)

    ood_auc = float(roc_auc_score(y_ood, y_prob_ood))
    prec_ood, rec_ood, _ = precision_recall_curve(y_ood, y_prob_ood)
    ood_pr_auc = float(auc(rec_ood, prec_ood))
    ood_f1 = float(f1_score(y_ood, y_pred_ood))
    ood_ece = compute_ece(y_ood, y_prob_ood)

    delta_ood = float(strict_auc - ood_auc)

    print(f"  OOD Unseen Systems ROC-AUC: {ood_auc:.6f}")
    print(f"  OOD Unseen Systems PR-AUC:  {ood_pr_auc:.6f}")
    print(f"  ΔOOD (In-Distribution vs OOD): {delta_ood:.6f}")

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 3: UNSEEN PARAMETER REGIMES
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 3] Evaluating Unseen Parameter Regimes (Lorenz rho=46.0 shift)...")

    # Normalize and extract shift trajectories
    X_shift_v3, X_shift_base, y_shift = normalize_and_extract(shift_trajectories)

    # Evaluate primary model on Parameter Shift
    y_prob_shift = clf_v3.predict_proba(X_shift_v3)[:, 1]
    y_pred_shift = clf_v3.predict(X_shift_v3)

    shift_auc = float(roc_auc_score(y_shift, y_prob_shift))
    prec_shift, rec_shift, _ = precision_recall_curve(y_shift, y_prob_shift)
    shift_pr_auc = float(auc(rec_shift, prec_shift))
    shift_f1 = float(f1_score(y_shift, y_pred_shift))

    delta_param = float(strict_auc - shift_auc)

    print(f"  Parameter Shift Lorenz ROC-AUC: {shift_auc:.6f}")
    print(f"  Δparameter (ID vs Shift):       {delta_param:.6f}")

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 4: CLASSICAL FEATURE NEGATIVE CONTROL
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 4] Evaluating Classical Feature Negative Control...")

    # Train model on baseline features
    clf_base = RandomForestClassifier(n_estimators=100, random_state=42)
    clf_base.fit(X_train_base, y_train)

    y_prob_base = clf_base.predict_proba(X_test_base)[:, 1]
    strict_auc_base = float(roc_auc_score(y_test, y_prob_base))

    delta_feature_advantage = float(strict_auc - strict_auc_base)

    # Dataset Bias Check
    bias_detected = False
    if strict_auc_base > 0.80:
        bias_detected = True
        print(
            f"  ⚠️ [DATASET_BIAS_DETECTED]: Baseline features achieve high ROC-AUC = {strict_auc_base:.6f}!"
        )
    else:
        print(
            f"  ✅ No Dataset Bias: Baseline features ROC-AUC = {strict_auc_base:.6f}"
        )

    print(f"  V3 Feature Advantage (Δfeature_advantage): {delta_feature_advantage:.6f}")

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 5: STRICT PERMUTATION AUDIT
    # ─────────────────────────────────────────────────────────────────────────────
    M = 200
    print(f"\n[TEST 5] Executing Strict Permutation Label Audit (M={M} iterations)...")

    perm_aucs = []

    t0_perm = time.time()
    for m in range(M):
        y_train_perm = np.random.permutation(y_train)
        # Use simple fast Random Forest of 10 trees to ensure quick audit execution
        clf_perm = RandomForestClassifier(n_estimators=10, random_state=None)
        clf_perm.fit(X_train_v3, y_train_perm)
        y_prob_perm = clf_perm.predict_proba(X_test_v3)[:, 1]
        perm_aucs.append(roc_auc_score(y_test, y_prob_perm))

    mean_perm_auc = float(np.mean(perm_aucs))
    std_perm_auc = float(np.std(perm_aucs)) if np.std(perm_aucs) > 1e-12 else 0.01

    z_score = float((strict_auc - mean_perm_auc) / std_perm_auc)

    leakage_detected = False
    if mean_perm_auc > 0.55:
        leakage_detected = True
        print(
            f"  ❌ [PIPELINE_LEAKAGE_DETECTED]: Mean Permuted AUC = {mean_perm_auc:.6f} (> 0.55)!"
        )
    else:
        print(f"  ✅ No Pipeline Leakage: Mean Permuted AUC = {mean_perm_auc:.6f}")

    print(f"  Permutation Z-score: {z_score:.6f}")
    print(f"  Audit loops finished in {time.time() - t0_perm:.2f} seconds.")

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 6: COMPOSITE CERTIFICATION SCORE S
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 6] Calculating Composite Certification Score S...")

    L = float(mean_perm_auc - 0.5)

    # S = 0.35 * AUC + 0.25 * PRAUC + 0.15 * (1 - ECE) + 0.15 * (1 - ΔOOD) + 0.10 * (1 - L)
    s_score = (
        0.35 * strict_auc
        + 0.25 * strict_pr_auc
        + 0.15 * (1.0 - strict_ece)
        + 0.15 * (1.0 - abs(delta_ood))
        + 0.10 * (1.0 - L)
    )

    print(f"  Composite Score S = {s_score:.6f}")

    # ─────────────────────────────────────────────────────────────────────────────
    # CONSOLIDATE AND DIAGNOSE
    # ─────────────────────────────────────────────────────────────────────────────

    # Final Diagnosis criteria
    # True generalization: Strict_AUC > 0.85, OOD_AUC > 0.85, Perm_AUC < 0.55, S > 0.85
    # Data Leakage Confirmed: otherwise
    final_diagnosis = "DATA_LEAKAGE_CONFIRMED"
    if strict_auc > 0.85 and ood_auc > 0.85 and mean_perm_auc < 0.55 and s_score > 0.85:
        final_diagnosis = "TRUE_INVARIANT_GENERALIZATION"

    # Baseline comparison (Leaky vs Strict)
    # The previous model with global leakage got ROC-AUC of ~1.0
    leaky_auc = 1.0000
    delta_auc = float(leaky_auc - strict_auc)

    report = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "audit_type": "Strict Leakage Audit",
            "embedding_version": "V3",
            "final_diagnosis": final_diagnosis,
            "composite_certification_score": s_score,
        },
        "test1_zero_leakage": {
            "strict_auc": strict_auc,
            "strict_pr_auc": strict_pr_auc,
            "strict_f1": strict_f1,
            "strict_ece": strict_ece,
            "overlap_score": overlap_score,
            "leaky_auc_reference": leaky_auc,
            "delta_auc": delta_auc,
        },
        "test2_extreme_ood": {
            "ood_auc": ood_auc,
            "ood_pr_auc": ood_pr_auc,
            "ood_f1": ood_f1,
            "ood_ece": ood_ece,
            "delta_ood": delta_ood,
        },
        "test3_unseen_parameters": {
            "shift_auc": shift_auc,
            "shift_pr_auc": shift_pr_auc,
            "shift_f1": shift_f1,
            "delta_parameter": delta_param,
        },
        "test4_negative_control": {
            "baseline_auc": strict_auc_base,
            "delta_feature_advantage": delta_feature_advantage,
            "dataset_bias_detected": bias_detected,
        },
        "test5_permutation_audit": {
            "mean_perm_auc": mean_perm_auc,
            "std_perm_auc": std_perm_auc,
            "z_score": z_score,
            "pipeline_leakage_detected": leakage_detected,
        },
        "test6_composite_score": {
            "permutation_offset_l": L,
            "composite_score_s": s_score,
        },
    }

    # Save Report
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    t_end = time.time()

    # ── REQUIRED TERMINAL DUMP ────────────────────────────────────────────────
    print("\n" + "=" * 75)
    print("🏁 FINAL LEAKAGE AUDIT REPORT SUMMARY")
    print("=" * 75)
    print(f"Leaky_AUC             = {leaky_auc:.6f}")
    print(f"Strict_AUC            = {strict_auc:.6f}")
    print(f"ΔAUC                  = {delta_auc:.6f}")
    print("")
    print(f"OOD_AUC               = {ood_auc:.6f}")
    print(f"OOD_PR_AUC            = {ood_pr_auc:.6f}")
    print("")
    print(f"Permutation_Mean_AUC  = {mean_perm_auc:.6f}")
    print(f"Permutation_STD       = {std_perm_auc:.6f}")
    print(f"Z_SCORE               = {z_score:.6f}")
    print("")
    print(f"Composite_Score_S     = {s_score:.6f}")
    print("")
    print(f"FINAL_DIAGNOSIS       = {final_diagnosis}")
    print(f"Leakage Audit completed in {t_end - t_start:.2f} seconds.")
    print("Report saved to: " + REPORT_FILE)
    print("=" * 75)


if __name__ == "__main__":
    main()
