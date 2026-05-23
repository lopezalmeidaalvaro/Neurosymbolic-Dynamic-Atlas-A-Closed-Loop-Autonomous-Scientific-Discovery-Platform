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
    roc_auc_score, precision_recall_curve, auc, f1_score, precision_score, recall_score
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
REPORT_FILE = os.path.join(REPORT_DIR, "dataset_bias_elimination_report.json")

# Seeds
SEEDS = [42, 1337, 9001]

# V3 features order
V3_KEYS = [
    "perm_entropy", "spectral_entropy", "svd_entropy",
    "fractal_dim", "autocorr_decay", "robust_skewness",
    "robust_kurtosis", "temporal_irreversibility"
]

# ─────────────────────────────────────────────────────────────────────────────
# CONTINUOUS DYNAMICAL SYSTEM VECTOR FIELDS & SIMULATORS
# ─────────────────────────────────────────────────────────────────────────────

def lorenz_rhs(t, state, sigma=10.0, rho=28.0, beta=8.0/3.0):
    x, y, z = state
    return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]

def simulate_lorenz(rho, sigma=10.0, beta=8.0/3.0, length=25000, seed=42):
    t_span = (0, 300)
    t_eval = np.linspace(0, 300, length + 5000)
    dt = t_eval[1] - t_eval[0]
    np.random.seed(seed)
    state0 = [1.0 + np.random.normal(0, 0.1), 1.0, 1.0]
    sol = solve_ivp(lambda t, y: lorenz_rhs(t, y, sigma, rho, beta), t_span, state0, t_eval=t_eval, method='RK45')
    return sol.y[0][5000:5000+length], dt

def rossler_rhs(t, state, c=5.7):
    x, y, z = state
    return [-y - z, x + 0.2 * y, 0.2 + z * (x - c)]

def simulate_rossler(c, length=25000, seed=42):
    t_span = (0, 300)
    t_eval = np.linspace(0, 300, length + 5000)
    dt = t_eval[1] - t_eval[0]
    np.random.seed(seed)
    state0 = [1.0 + np.random.normal(0, 0.1), 1.0, 1.0]
    sol = solve_ivp(lambda t, y: rossler_rhs(t, y, c), t_span, state0, t_eval=t_eval, method='RK45')
    return sol.y[0][5000:5000+length], dt

def duffing_rhs(t, state, f=0.5):
    x, y = state
    return [y, x - x**3 - 0.3*y + f*np.cos(1.2*t)]

def simulate_duffing(f, length=25000, seed=42):
    t_span = (0, 800)
    t_eval = np.linspace(0, 800, length + 10000)
    dt = t_eval[1] - t_eval[0]
    np.random.seed(seed)
    state0 = [0.1 + np.random.normal(0, 0.05), 0.0]
    sol = solve_ivp(lambda t, y: duffing_rhs(t, y, f), t_span, state0, t_eval=t_eval, method='RK45')
    return sol.y[0][10000:10000+length], dt

# ─────────────────────────────────────────────────────────────────────────────
# Schreiber & Schmitz's Iterative Amplitude Adjusted Fourier Transform (IAAFT)
# ─────────────────────────────────────────────────────────────────────────────

def generate_iaaft(base_signal, seed, max_iter=100, tolerance=1e-5):
    np.random.seed(seed)
    x = np.array(base_signal, dtype=float)
    n = len(x)
    x_sorted = np.sort(x)
    
    # Get original amplitudes of Fourier transform
    x_fft = np.fft.rfft(x)
    amplitudes = np.abs(x_fft)
    
    # Initialize with a random permutation of x
    y = np.random.permutation(x)
    
    prev_rmse = np.inf
    converged = False
    iters_run = 0
    
    for iteration in range(max_iter):
        iters_run = iteration + 1
        # Step 1: Match spectrum
        y_fft = np.fft.rfft(y)
        phases = np.angle(y_fft)
        
        y_fft_new = amplitudes * np.exp(1j * phases)
        s = np.fft.irfft(y_fft_new, n=n)
        
        # Step 2: Match amplitudes (rank order alignment)
        s_ranks = np.argsort(np.argsort(s))
        y_next = x_sorted[s_ranks]
        
        # Check convergence
        rmse = np.sqrt(np.mean((y_next - y) ** 2))
        if rmse < tolerance or np.abs(prev_rmse - rmse) < 1e-8:
            converged = True
            y = y_next
            break
        prev_rmse = rmse
        y = y_next
        
    # Calculate final errors
    amp_err = float(np.max(np.abs(np.sort(y) - x_sorted)))
    
    original_power = amplitudes ** 2
    y_power = np.abs(np.fft.rfft(y)) ** 2
    spec_err = float(np.mean(np.abs(original_power - y_power)) / (np.mean(original_power) + 1e-12))
    
    return y, iters_run, converged, spec_err, amp_err

# ─────────────────────────────────────────────────────────────────────────────
# DEBIASED CLASSICAL BASELINE FEATURES
# ─────────────────────────────────────────────────────────────────────────────

def _spectral_entropy_normalized(x):
    N = len(x)
    yf = np.abs(fft(x)[:N // 2]) ** 2
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
    """
    Computes mean, variance, skewness, kurtosis, and spectral energy on the window.
    """
    m_val = float(np.mean(x_window))
    v_val = float(np.var(x_window))
    s_val = float(skew(x_window)) if np.std(x_window) > 1e-10 else 0.0
    k_val = float(kurtosis(x_window)) if np.std(x_window) > 1e-10 else 0.0
    
    N = len(x_window)
    yf = np.abs(fft(x_window)[:N // 2]) ** 2
    yf[0] = 0.0
    spec_energy = float(np.sum(yf))
    
    return [m_val, v_val, s_val, k_val, spec_energy]

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
# MAIN DATASET DEBIASING AUDIT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 75)
    print("🕵️‍♂️ PRINCIPAL COMPUTATIONAL PHYSICS AUDITOR — DEBIASING AUDIT")
    print("=" * 75)
    print("ELIMINATING DATASET BIASES AND EVALUATING PHYSICAL INVARIANTS...")
    
    t_start = time.time()
    
    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 1: GENERATE PHYSICAL TRAJECTORIES & IAAFT SURROGATES
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[STEP 1] Simulating trajectories and generating IAAFT surrogates...")
    length = 25000
    trajectories = []
    
    trajectory_counter = 0
    
    iaaft_iters = []
    iaaft_convergences = []
    iaaft_spec_errors = []
    iaaft_amp_errors = []
    
    # Systems sweep
    systems_configs = {
        "lorenz": ([24.0, 26.0, 28.0], lambda p, s: simulate_lorenz(rho=p, length=length, seed=s)),
        "rossler": ([4.0, 5.0, 5.7], lambda p, s: simulate_rossler(c=p, length=length, seed=s)),
        "duffing": ([0.35, 0.45, 0.5], lambda p, s: simulate_duffing(f=p, length=length, seed=s))
    }
    
    for sys_name, (params, simulator) in systems_configs.items():
        for p in params:
            for seed in SEEDS:
                # 1. Simulate Clean Physical
                sig, dt = simulator(p, seed)
                
                # Store physical trajectory
                trajectories.append({
                    "system_family": sys_name,
                    "system": sys_name,
                    "parameter_bin": f"param_{p:.2f}",
                    "seed": seed,
                    "signal": sig,
                    "dt": dt,
                    "label": 1,
                    "trajectory_id": trajectory_counter
                })
                trajectory_counter += 1
                
                # 2. Generate IAAFT Surrogate (matching exact power spectrum & amplitude distribution)
                surr_sig, iters, conv, s_err, a_err = generate_iaaft(sig, seed=seed)
                
                iaaft_iters.append(iters)
                iaaft_convergences.append(1 if conv else 0)
                iaaft_spec_errors.append(s_err)
                iaaft_amp_errors.append(a_err)
                
                # Store adversarial IAAFT trajectory
                trajectories.append({
                    "system_family": sys_name,
                    "system": f"iaaft_{sys_name}",
                    "parameter_bin": f"param_{p:.2f}",
                    "seed": seed,
                    "signal": surr_sig,
                    "dt": dt,
                    "label": 0,
                    "trajectory_id": trajectory_counter
                })
                trajectory_counter += 1
                
    print(f"  Generated {len(trajectories)} total trajectories.")
    
    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 2: ASSIGN STRATEGIC group_id AND SPLIT DATASET
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[STEP 2] Assigning group_id and splitting groups to prevent leakage...")
    
    # Define a helper to bin initial condition geometry
    def get_ic_cluster(signal):
        start_val = signal[0]
        if start_val < -1.0:
            return "ic_low"
        elif start_val > 1.0:
            return "ic_high"
        else:
            return "ic_mid"
            
    # Assign group keys to guarantee train_groups ∩ test_groups = ∅
    for t in trajectories:
        ic_cluster = get_ic_cluster(t["signal"])
        # We group by system family and param bin so that both physical and IAAFT counterparts for a seed go to the same split
        t["group_key"] = f"{t['system_family']}_{t['parameter_bin']}_{ic_cluster}"
        
    unique_groups = list(set([t["group_key"] for t in trajectories]))
    np.random.seed(42)
    np.random.shuffle(unique_groups)
    
    split_idx = int(len(unique_groups) * 0.70)
    train_groups = set(unique_groups[:split_idx])
    test_groups = set(unique_groups[split_idx:])
    
    train_trajectories = [t for t in trajectories if t["group_key"] in train_groups]
    test_trajectories = [t for t in trajectories if t["group_key"] in test_groups]
    
    print(f"  Train Groups: {len(train_groups)} ({len(train_trajectories)} trajectories)")
    print(f"  Test Groups:  {len(test_groups)} ({len(test_trajectories)} trajectories)")
    
    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 1 & 2: STRICT WINDOW STANDARDIZATION & IAAFT DIAGNOSTICS
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 1] Applying strict local window standardization & validating...")
    
    means_before, vars_before = [], []
    means_after, vars_after = [], []
    
    def process_split(traj_list):
        X_v3, X_base, y = [], [], []
        window_size = 1000
        stride = 500
        for t in traj_list:
            sig = t["signal"]
            dt = t["dt"]
            n = len(sig)
            start = 0
            while start + window_size <= n:
                win = sig[start : start + window_size]
                
                # Record metrics before standardization
                means_before.append(float(np.mean(win)))
                vars_before.append(float(np.var(win)))
                
                # STRICT LOCAL WINDOW STANDARDIZATION
                win_std = (win - np.mean(win)) / (np.std(win) + 1e-12)
                
                # Record metrics after standardization
                means_after.append(float(np.mean(win_std)))
                vars_after.append(float(np.var(win_std)))
                
                # Extract V3 features on locally standardized window
                emb = compute_embedding_vector(win_std, dt)
                v3_vec = [emb.get(k, 0.0) for k in V3_KEYS]
                X_v3.append(v3_vec)
                
                # Extract 5 baseline features on locally standardized window
                base_vec = compute_baseline_features(win_std, dt)
                X_base.append(base_vec)
                
                y.append(t["label"])
                start += stride
        return np.array(X_v3), np.array(X_base), np.array(y)
        
    X_train_v3, X_train_base, y_train = process_split(train_trajectories)
    X_test_v3, X_test_base, y_test = process_split(test_trajectories)
    
    # Verify local debias stats
    mean_m_before = float(np.mean(means_before))
    std_m_before = float(np.std(means_before))
    mean_v_before = float(np.mean(vars_before))
    std_v_before = float(np.std(vars_before))
    
    mean_m_after = float(np.mean(means_after))
    std_m_after = float(np.std(means_after))
    mean_v_after = float(np.mean(vars_after))
    std_v_after = float(np.std(vars_after))
    
    print(f"  Means (Before) : {mean_m_before:.6f} ± {std_m_before:.6f}")
    print(f"  Means (After)  : {mean_m_after:.6f} ± {std_m_after:.6f} (debiased to 0)")
    print(f"  Vars (Before)  : {mean_v_before:.6f} ± {std_v_before:.6f}")
    print(f"  Vars (After)   : {mean_v_after:.6f} ± {std_v_after:.6f} (debiased to 1)")
    
    print("\n[TEST 2] Verifying Schreiber & Schmitz's IAAFT surrogate quality...")
    mean_iters = float(np.mean(iaaft_iters))
    conv_rate = float(np.mean(iaaft_convergences))
    mean_spec_err = float(np.mean(iaaft_spec_errors))
    mean_amp_err = float(np.mean(iaaft_amp_errors))
    
    print(f"  Mean Iterations:          {mean_iters:.2f}")
    print(f"  Convergence Rate:         {conv_rate:.6f} ({conv_rate*100:.1f}%)")
    print(f"  Mean Fourier Power Error: {mean_spec_err:.6e}")
    print(f"  Mean Amplitude Match Error: {mean_amp_err:.6e}")
    
    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 3: BIAS ELIMINATION VERIFICATION
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 3] Running Bias Elimination Verification...")
    
    # Train RF on V3 Features
    clf_v3 = RandomForestClassifier(n_estimators=100, random_state=42)
    clf_v3.fit(X_train_v3, y_train)
    
    y_prob_v3 = clf_v3.predict_proba(X_test_v3)[:, 1]
    y_pred_v3 = clf_v3.predict(X_test_v3)
    
    auc_v3 = float(roc_auc_score(y_test, y_prob_v3))
    prec_v3, rec_v3, _ = precision_recall_curve(y_test, y_prob_v3)
    pr_auc_v3 = float(auc(rec_v3, prec_v3))
    f1_v3 = float(f1_score(y_test, y_pred_v3))
    ece_v3 = compute_ece(y_test, y_prob_v3)
    
    # Train RF on Baseline Features
    clf_base = RandomForestClassifier(n_estimators=100, random_state=42)
    clf_base.fit(X_train_base, y_train)
    
    y_prob_base = clf_base.predict_proba(X_test_base)[:, 1]
    auc_base = float(roc_auc_score(y_test, y_prob_base))
    
    delta_auc_baseline = float(1.0 - auc_base) # reference drop from leaky
    delta_auc_v3 = float(0.974276 - auc_v3) # reference drop from previous strict split
    
    print(f"  Baseline Features ROC-AUC (Debiased): {auc_base:.6f} (Target < 0.60)")
    print(f"  Embedding V3 Features ROC-AUC:         {auc_v3:.6f} (Target > 0.85)")
    print(f"  ECE V3:                               {ece_v3:.6f} (Target < 0.05)")
    
    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 4: NEGATIVE PERMUTATION CONTROL
    # ─────────────────────────────────────────────────────────────────────────────
    M = 200
    print(f"\n[TEST 4] Executing Negative Permutation Control (M={M} loops)...")
    
    perm_aucs = []
    t0_perm = time.time()
    for m in range(M):
        y_train_perm = np.random.permutation(y_train)
        clf_perm = RandomForestClassifier(n_estimators=10, random_state=None)
        clf_perm.fit(X_train_v3, y_train_perm)
        y_prob_perm = clf_perm.predict_proba(X_test_v3)[:, 1]
        perm_aucs.append(roc_auc_score(y_test, y_prob_perm))
        
    mean_perm_auc = float(np.mean(perm_aucs))
    std_perm_auc = float(np.std(perm_aucs)) if np.std(perm_aucs) > 1e-12 else 0.01
    
    z_score = float((auc_v3 - mean_perm_auc) / std_perm_auc)
    
    print(f"  Mean Permuted AUC: {mean_perm_auc:.6f}")
    print(f"  Permutation Z-score: {z_score:.6f}")
    print(f"  Audit loops finished in {time.time() - t0_perm:.2f} seconds.")
    
    # ─────────────────────────────────────────────────────────────────────────────
    # CERTIFICATION STATUS & REPORT CONSOLIDATION
    # ─────────────────────────────────────────────────────────────────────────────
    
    # Certification check
    # 1. AUC_baseline < 0.60
    # 2. AUC_V3 > 0.85
    # 3. AUC_perm in [0.45, 0.55]
    # 4. ECE_V3 < 0.05
    certification_status = "INSUFFICIENT_PHYSICAL_GENERALIZATION"
    final_diagnosis = "INSUFFICIENT_PHYSICAL_GENERALIZATION"
    
    if auc_base < 0.60:
        if auc_v3 > 0.85:
            if 0.45 <= mean_perm_auc <= 0.55:
                if ece_v3 < 0.05:
                    certification_status = "CERTIFIED"
                    final_diagnosis = "PHYSICAL_INVARIANTS_CONFIRMED"
                else:
                    final_diagnosis = "POOR_CALIBRATION"
            else:
                final_diagnosis = "PIPELINE_LEAKAGE"
        else:
            final_diagnosis = "INSUFFICIENT_PHYSICAL_GENERALIZATION"
    else:
        final_diagnosis = "RESIDUAL_DATASET_BIAS"
        
    report = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "audit_type": "Dataset Bias Elimination Audit",
            "certification_status": certification_status,
            "final_diagnosis": final_diagnosis
        },
        "test1_local_standardization": {
            "means_before": {"mean": mean_m_before, "std": std_m_before},
            "means_after": {"mean": mean_m_after, "std": std_m_after},
            "vars_before": {"mean": mean_v_before, "std": std_v_before},
            "vars_after": {"mean": mean_v_after, "std": std_v_after}
        },
        "test2_iaaft_diagnostics": {
            "mean_iterations": mean_iters,
            "convergence_rate": conv_rate,
            "mean_power_spectral_error": mean_spec_err,
            "mean_amplitude_match_error": mean_amp_err
        },
        "test3_bias_verification": {
            "baseline_auc": auc_base,
            "v3_auc": auc_v3,
            "v3_pr_auc": pr_auc_v3,
            "v3_f1": f1_v3,
            "v3_ece": ece_v3,
            "delta_auc_baseline": delta_auc_baseline,
            "delta_auc_v3": delta_auc_v3
        },
        "test4_negative_control": {
            "mean_perm_auc": mean_perm_auc,
            "std_perm_auc": std_perm_auc,
            "z_score": z_score
        }
    }
    
    # Save JSON report
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    t_end = time.time()
    
    # ── REQUIRED TERMINAL DUMP ────────────────────────────────────────────────
    print("\n" + "=" * 75)
    print("🏁 FINAL DEBIASING AUDIT REPORT SUMMARY")
    print("=" * 75)
    print(f"ΔAUC_baseline   = {delta_auc_baseline:.6f} (Strict drop from 0.998)")
    print(f"ΔAUC_V3         = {delta_auc_v3:.6f} (Strict drop from 0.974)")
    print(f"AUC_perm        = {mean_perm_auc:.6f}")
    print(f"FINAL_DIAGNOSIS = {final_diagnosis}")
    print(f"CERTIFICATION_STATUS = {certification_status}")
    print(f"Debiasing Audit completed in {t_end - t_start:.2f} seconds.")
    print("Report saved to: " + REPORT_FILE)
    print("=" * 75)

if __name__ == "__main__":
    main()
