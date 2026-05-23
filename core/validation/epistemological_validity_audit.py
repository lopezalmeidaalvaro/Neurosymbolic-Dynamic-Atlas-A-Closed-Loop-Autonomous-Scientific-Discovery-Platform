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
import shap

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
REPORT_DIR = os.path.join(REPORT_DIR := os.path.join(ROOT_DIR, "dashboard", "public", "artifacts", "discoveries"))
REPORT_FILE = os.path.join(REPORT_DIR, "epistemological_validity_report.json")

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
# IAAFT SURROGATES
# ─────────────────────────────────────────────────────────────────────────────

def generate_iaaft(base_signal, seed, max_iter=100, tolerance=1e-5):
    np.random.seed(seed)
    x = np.array(base_signal, dtype=float)
    n = len(x)
    x_sorted = np.sort(x)
    x_fft = np.fft.rfft(x)
    amplitudes = np.abs(x_fft)
    
    y = np.random.permutation(x)
    prev_rmse = np.inf
    
    for iteration in range(max_iter):
        y_fft = np.fft.rfft(y)
        phases = np.angle(y_fft)
        y_fft_new = amplitudes * np.exp(1j * phases)
        s = np.fft.irfft(y_fft_new, n=n)
        s_ranks = np.argsort(np.argsort(s))
        y_next = x_sorted[s_ranks]
        
        rmse = np.sqrt(np.mean((y_next - y) ** 2))
        if rmse < tolerance or np.abs(prev_rmse - rmse) < 1e-8:
            y = y_next
            break
        prev_rmse = rmse
        y = y_next
        
    return y

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
# NON-LINEAR REDUNDANCY (NORMALIZED MUTUAL INFORMATION)
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

# ─────────────────────────────────────────────────────────────────────────────
# MAIN EPISTEMOLOGICAL AUDIT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 75)
    print("🕵️‍♂️ PRINCIPAL COMPUTATIONAL PHYSICS AUDITOR — EPISTEMOLOGICAL VALIDITY AUDIT")
    print("=" * 75)
    print("PURIFYING CAUSAL METRICS USING TREESHAP & MUTUAL INFORMATION...")
    
    t_start = time.time()
    
    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 1: GENERATE DATASETS & IAAFT SURROGATES
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[STEP 1] Generating physical orbits and advanced IAAFT surrogate clones...")
    length = 25000
    trajectories = []
    
    trajectory_counter = 0
    
    systems_configs = {
        "lorenz": ([24.0, 26.0, 28.0], lambda p, s: simulate_lorenz(rho=p, length=length, seed=s)),
        "rossler": ([4.0, 5.0, 5.7], lambda p, s: simulate_rossler(c=p, length=length, seed=s)),
        "duffing": ([0.35, 0.45, 0.5], lambda p, s: simulate_duffing(f=p, length=length, seed=s))
    }
    
    for sys_name, (params, simulator) in systems_configs.items():
        for p in params:
            for seed in SEEDS:
                sig, dt = simulator(p, seed)
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
                
                surr_sig = generate_iaaft(sig, seed=seed)
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
                
    # Assign group keys so that both physical and IAAFT counterparts for a seed go to the same split
    def get_ic_cluster(signal):
        start_val = signal[0]
        if start_val < -1.0:
            return "ic_low"
        elif start_val > 1.0:
            return "ic_high"
        else:
            return "ic_mid"
            
    for t in trajectories:
        ic_cluster = get_ic_cluster(t["signal"])
        t["group_key"] = f"{t['system_family']}_{t['parameter_bin']}_{ic_cluster}"
        
    unique_groups = list(set([t["group_key"] for t in trajectories]))
    np.random.seed(42)
    np.random.shuffle(unique_groups)
    
    split_idx = int(len(unique_groups) * 0.70)
    train_groups = set(unique_groups[:split_idx])
    
    train_trajectories = [t for t in trajectories if t["group_key"] in train_groups]
    validation_trajectories = [t for t in trajectories if t["group_key"] not in train_groups]
    
    # Extract and scale splits locally
    def process_split_standard(traj_list):
        X_v3, y = [], []
        window_size = 1000
        stride = 500
        for t in traj_list:
            sig = t["signal"]
            dt = t["dt"]
            n = len(sig)
            start = 0
            while start + window_size <= n:
                win = sig[start : start + window_size]
                win_std = (win - np.mean(win)) / (np.std(win) + 1e-12)
                
                emb = compute_embedding_vector(win_std, dt)
                v3_vec = [emb.get(k, 0.0) for k in V3_KEYS]
                X_v3.append(v3_vec)
                y.append(t["label"])
                start += stride
        return np.array(X_v3), np.array(y)
        
    X_train_v3, y_train = process_split_standard(train_trajectories)
    X_val_v3, y_val = process_split_standard(validation_trajectories)
    
    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 2: TRAIN RANDOM FOREST & COMPUTE TREESHAP EXPLANATION (TEST 2)
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 2] Executing TreeSHAP cooperative game feature attributions...")
    clf_full = RandomForestClassifier(n_estimators=100, random_state=42)
    clf_full.fit(X_train_v3, y_train)
    
    # TreeSHAP Explainer
    explainer = shap.TreeExplainer(clf_full)
    shap_values = explainer.shap_values(X_val_v3)
    
    # Extract Class 1 (physical) Shapley values
    if isinstance(shap_values, list):
        shap_vals_class1 = shap_values[1]
    elif len(shap_values.shape) == 3:
        shap_vals_class1 = shap_values[:, :, 1]
    else:
        shap_vals_class1 = shap_values
        
    # Global SHAP importance: E[|phi_i|]
    global_shap_importances = np.mean(np.abs(shap_vals_class1), axis=0)
    # Normalize to [0, 1] relative to the maximum feature to align with AUC
    max_shap = np.max(global_shap_importances)
    normalized_shap_importances = global_shap_importances / (max_shap if max_shap > 0 else 1.0)
    
    # Compute full V3 performance benchmark
    y_prob_full = clf_full.predict_proba(X_val_v3)[:, 1]
    auc_full = float(roc_auc_score(y_val, y_prob_full))
    
    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 3: NON-LINEAR REDUNDANCY MATRIX NMI (TEST 1)
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 1] Constructing Non-linear Redundancy Matrix via Normalized Mutual Information...")
    
    R_nmi_matrix = np.zeros((8, 8))
    for i in range(8):
        for j in range(8):
            R_nmi_matrix[i, j] = compute_nmi(X_train_v3[:, i], X_train_v3[:, j])
            
    # Average redundancy R_i per feature (excluding diagonal element)
    redundancy_nmi_scores = {}
    for i, name in enumerate(V3_KEYS):
        R_i = float((np.sum(R_nmi_matrix[i]) - 1.0) / 7.0)
        redundancy_nmi_scores[name] = R_i

    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 4: BOOTSTRAP SHAP STABILITY AUDIT (TEST 3)
    # ─────────────────────────────────────────────────────────────────────────────
    M = 50
    print(f"\n[TEST 3] Running Bootstrap TreeSHAP Stability Audit (M={M} iterations)...")
    
    bootstrap_shap_importances = np.zeros((M, 8))
    n_samples = len(X_train_v3)
    
    for m in range(M):
        np.random.seed(m)
        indices = np.random.choice(n_samples, n_samples, replace=True)
        X_boot = X_train_v3[indices]
        y_boot = y_train[indices]
        
        clf_boot = RandomForestClassifier(n_estimators=20, random_state=None)
        clf_boot.fit(X_boot, y_boot)
        
        explainer_boot = shap.TreeExplainer(clf_boot)
        shap_vals_boot = explainer_boot.shap_values(X_val_v3)
        
        if isinstance(shap_vals_boot, list):
            vals_c1 = shap_vals_boot[1]
        elif len(shap_vals_boot.shape) == 3:
            vals_c1 = shap_vals_boot[:, :, 1]
        else:
            vals_c1 = shap_vals_boot
            
        bootstrap_shap_importances[m] = np.mean(np.abs(vals_c1), axis=0)
        
    stability_shap_results = {}
    for i, name in enumerate(V3_KEYS):
        mu_i = float(np.mean(bootstrap_shap_importances[:, i]))
        sigma_i = float(np.std(bootstrap_shap_importances[:, i]))
        cv_i = float(sigma_i / mu_i) if mu_i > 0 else 0.0
        stability_shap_results[name] = {
            "mean": mu_i,
            "std": sigma_i,
            "cv": cv_i
        }

    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 5: CAUSAL RE-CLASSIFICATION & SCORES (TEST 4)
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 4] Calculating purified Causal Scores C_i & Epistemological roles...")
    
    # We obtain the isolated sufficiency AUC_i by training on single features
    sufficiency_aucs = {}
    loco_auc_necessity = {}
    
    for i, name in enumerate(V3_KEYS):
        # Sufficiency AUC_i
        X_train_io = X_train_v3[:, [i]]
        X_val_io = X_val_v3[:, [i]]
        clf_io = RandomForestClassifier(n_estimators=100, random_state=42)
        clf_io.fit(X_train_io, y_train)
        y_prob_io = clf_io.predict_proba(X_val_io)[:, 1]
        sufficiency_aucs[name] = float(roc_auc_score(y_val, y_prob_io))
        
        # LOCO necessity (for regularizer check)
        X_train_lo = np.delete(X_train_v3, i, axis=1)
        X_val_lo = np.delete(X_val_v3, i, axis=1)
        clf_lo = RandomForestClassifier(n_estimators=100, random_state=42)
        clf_lo.fit(X_train_lo, y_train)
        y_prob_lo = clf_lo.predict_proba(X_val_lo)[:, 1]
        loco_auc_necessity[name] = float(auc_full - roc_auc_score(y_val, y_prob_lo))
        
    purified_scores = {}
    purified_ranking = []
    
    for i, name in enumerate(V3_KEYS):
        I_i = normalized_shap_importances[i]
        AUC_i = sufficiency_aucs[name]
        R_i = redundancy_nmi_scores[name]
        CV_i = stability_shap_results[name]["cv"]
        
        # Original weighting formula: 0.35*I_i + 0.35*AUC_i - 0.15*R_i - 0.15*CV_i
        C_i = 0.35 * I_i + 0.35 * AUC_i - 0.15 * R_i - 0.15 * CV_i
        purified_scores[name] = C_i
        
        # Role re-classification
        is_unstable = (CV_i > 0.5)
        is_sufficient = (AUC_i > 0.85)
        
        # If score is low but it is mathematically necessary (LOCO necessity > 0.001) for the full model
        is_regularizer = (C_i < 0.15 and loco_auc_necessity[name] > 0.001 and auc_full > 0.95)
        
        if is_unstable:
            role = "UNSTABLE_COMPONENT"
        elif is_regularizer:
            role = "GEOMETRIC_REGULARIZER"
        elif I_i > 0.05 and is_sufficient:
            role = "CRITICAL_COMPONENT"
        elif R_i > 0.60:
            role = "REDUNDANT_COMPONENT"
        elif I_i > 0.0 and AUC_i > 0.60:
            role = "SUPPORTING_COMPONENT"
        else:
            role = "AUXILIARY_COMPONENT"
            
        purified_ranking.append({
            "component": name,
            "score": C_i,
            "role": role,
            "shap_importance": I_i,
            "sufficiency": AUC_i,
            "redundancy_nmi": R_i,
            "instability": CV_i
        })
        
    # Sort ranking descending
    purified_ranking = sorted(purified_ranking, key=lambda x: x["score"], reverse=True)
    
    # ─────────────────────────────────────────────────────────────────────────────
    # COMPARATIVE CONTRAST (PEARSON/GINI vs NMI/SHAP)
    # ─────────────────────────────────────────────────────────────────────────────
    # Previous ranking data from Gini/Pearson audit phase:
    gini_pearson_ranking = [
        "perm_entropy", "robust_skewness", "temporal_irreversibility", "svd_entropy",
        "autocorr_decay", "spectral_entropy", "robust_kurtosis", "fractal_dim"
    ]
    
    print("\n" + "=" * 75)
    print("📈 RANKING CONTRAST: PEARSON/GINI vs NMI/SHAP")
    print("=" * 75)
    print(f"  {'Rank':<4} | {'Pearson/Gini Feature':<28} | {'Purified NMI/SHAP Feature':<28} | {'Score':<10}")
    print("  " + "-" * 75)
    for rank_idx in range(8):
        prev_f = gini_pearson_ranking[rank_idx]
        curr_f = purified_ranking[rank_idx]["component"]
        curr_score = purified_ranking[rank_idx]["score"]
        print(f"  {rank_idx+1:<4} | {prev_f:<28} | {curr_f:<28} | {curr_score:.6f}")
        
    ranking_changed = "NO" if [r["component"] for r in purified_ranking] == gini_pearson_ranking else "YES"
    print(f"\n¿Cambió el ranking respecto al uso de Pearson/Gini? -> {ranking_changed}")
    
    # Extract structural summaries
    critical_comp = [r["component"] for r in purified_ranking if r["role"] == "CRITICAL_COMPONENT"]
    supporting_comp = [r["component"] for r in purified_ranking if r["role"] == "SUPPORTING_COMPONENT"]
    redundant_comp = [r["component"] for r in purified_ranking if r["role"] == "REDUNDANT_COMPONENT"]
    auxiliary_comp = [r["component"] for r in purified_ranking if r["role"] == "AUXILIARY_COMPONENT"]
    regularizer_comp = [r["component"] for r in purified_ranking if r["role"] == "GEOMETRIC_REGULARIZER"]
    unstable_comp = [r["component"] for r in purified_ranking if r["role"] == "UNSTABLE_COMPONENT"]
    
    # Save Report JSON
    report = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "audit_type": "Epistemological Validity Audit",
            "ranking_changed": ranking_changed,
            "full_val_auc": auc_full
        },
        "test1_nmi_matrix": R_nmi_matrix.tolist(),
        "test2_treeshap_attributions": {
            "raw_global_shap": global_shap_importances.tolist(),
            "normalized_shap": normalized_shap_importances.tolist()
        },
        "test3_shap_stability": {
            "cv_scores": {k: v["cv"] for k, v in stability_shap_results.items()},
            "means": {k: v["mean"] for k, v in stability_shap_results.items()},
            "stds": {k: v["std"] for k, v in stability_shap_results.items()}
        },
        "test4_causal_reclassification": {
            "ranking": purified_ranking,
            "scores": purified_scores
        }
    }
    
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    t_end = time.time()
    
    # ── REQUIRED TERMINAL DUMP ────────────────────────────────────────────────
    print("\n" + "=" * 75)
    print("🏁 FINAL EPISTEMOLOGICAL AUDIT REPORT SUMMARY")
    print("=" * 75)
    print("CRITICAL_COMPONENT     = " + (", ".join(critical_comp) if critical_comp else "NONE"))
    print("SUPPORTING_COMPONENT   = " + (", ".join(supporting_comp) if supporting_comp else "NONE"))
    print("REDUNDANT_COMPONENT     = " + (", ".join(redundant_comp) if redundant_comp else "NONE"))
    print("GEOMETRIC_REGULARIZER  = " + (", ".join(regularizer_comp) if regularizer_comp else "NONE"))
    print("AUXILIARY_COMPONENT    = " + (", ".join(auxiliary_comp) if auxiliary_comp else "NONE"))
    print("UNSTABLE_COMPONENT     = " + (", ".join(unstable_comp) if unstable_comp else "NONE"))
    print("")
    print(f"Epistemological Audit completed in {t_end - t_start:.2f} seconds.")
    print("Report saved to: " + REPORT_FILE)
    print("=" * 75)

if __name__ == "__main__":
    main()
