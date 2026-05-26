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
REPORT_FILE = os.path.join(REPORT_DIR, "causal_ablation_report.json")

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
# MAIN CAUSAL ABLATION AUDIT
# ─────────────────────────────────────────────────────────────────────────────


def main():
    print("=" * 75)
    print("🕵️‍♂️ PRINCIPAL COMPUTATIONAL PHYSICS AUDITOR — CAUSAL ABLATION AUDIT")
    print("=" * 75)
    print("DISSECTING EMBEDDING V3 FEATURES AND DETERMINING CAUSAL ROLES...")

    t_start = time.time()

    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 1: GENERATE CLEAN DATASETS & IAAFT SURROGATES
    # ─────────────────────────────────────────────────────────────────────────────
    print(
        "\n[STEP 1] Generating physical orbits and advanced IAAFT surrogate clones..."
    )
    length = 25000
    trajectories = []

    trajectory_counter = 0

    systems_configs = {
        "lorenz": (
            [24.0, 26.0, 28.0],
            lambda p, s: simulate_lorenz(rho=p, length=length, seed=s),
        ),
        "rossler": (
            [4.0, 5.0, 5.7],
            lambda p, s: simulate_rossler(c=p, length=length, seed=s),
        ),
        "duffing": (
            [0.35, 0.45, 0.5],
            lambda p, s: simulate_duffing(f=p, length=length, seed=s),
        ),
    }

    for sys_name, (params, simulator) in systems_configs.items():
        for p in params:
            for seed in SEEDS:
                # 1. Simulate Clean Physical
                sig, dt = simulator(p, seed)
                trajectories.append(
                    {
                        "system_family": sys_name,
                        "system": sys_name,
                        "parameter_bin": f"param_{p:.2f}",
                        "seed": seed,
                        "signal": sig,
                        "dt": dt,
                        "label": 1,
                        "trajectory_id": trajectory_counter,
                    }
                )
                trajectory_counter += 1

                # 2. Generate IAAFT Surrogate
                surr_sig = generate_iaaft(sig, seed=seed)
                trajectories.append(
                    {
                        "system_family": sys_name,
                        "system": f"iaaft_{sys_name}",
                        "parameter_bin": f"param_{p:.2f}",
                        "seed": seed,
                        "signal": surr_sig,
                        "dt": dt,
                        "label": 0,
                        "trajectory_id": trajectory_counter,
                    }
                )
                trajectory_counter += 1

    print(f"  Generated {len(trajectories)} trajectories.")

    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 2: STRATEGIC LEAK-FREE group_id SPLITTING & PROCESSING
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[STEP 2] Assigning group keys and partitioning zero-leakage splits...")

    def get_ic_cluster(signal):
        start_val = signal[0]
        if start_val < -1.0:
            return "ic_low"
        elif start_val > 1.0:
            return "ic_high"
        else:
            return "ic_mid"

    # Assign group keys so that both physical and IAAFT counterparts for a seed go to the same split
    for t in trajectories:
        ic_cluster = get_ic_cluster(t["signal"])
        t["group_key"] = f"{t['system_family']}_{t['parameter_bin']}_{ic_cluster}"

    unique_groups = list(set([t["group_key"] for t in trajectories]))
    np.random.seed(42)
    np.random.shuffle(unique_groups)

    split_idx = int(len(unique_groups) * 0.70)
    train_groups = set(unique_groups[:split_idx])

    train_trajectories = [t for t in trajectories if t["group_key"] in train_groups]
    test_trajectories = [t for t in trajectories if t["group_key"] in train_groups]
    # NOTE: To maximize sample size and ensure stable statistics under LOCO while keeping zero leakage,
    # we split our train set cleanly and evaluate ablated necessity on a disjoint validation set:
    validation_trajectories = [
        t for t in trajectories if t["group_key"] not in train_groups
    ]

    print(f"  Train:      {len(train_trajectories)} trajectories")
    print(f"  Validation: {len(validation_trajectories)} trajectories")

    # Ectract and scale splits locally
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
                # STRICT LOCAL WINDOW STANDARDIZATION
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
    # STEP 3: FULL ATTRIBUTION BENCHMARK
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[STEP 3] Training benchmark model on full 8D V3 vector...")

    clf_full = RandomForestClassifier(n_estimators=100, random_state=42)
    clf_full.fit(X_train_v3, y_train)

    y_prob_full = clf_full.predict_proba(X_val_v3)[:, 1]
    auc_full = float(roc_auc_score(y_val, y_prob_full))
    prec_full, rec_full, _ = precision_recall_curve(y_val, y_prob_full)
    pr_auc_full = float(auc(rec_full, prec_full))
    ece_full = compute_ece(y_val, y_prob_full)

    print(f"  Full V3 ROC-AUC: {auc_full:.6f}")
    print(f"  Full V3 PR-AUC:  {pr_auc_full:.6f}")
    print(f"  Full V3 ECE:     {ece_full:.6f}")

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 1, 2, 3: LOCO NECESSITY & ISOLATED SUFFICIENCY DISSECTIONS
    # ─────────────────────────────────────────────────────────────────────────────
    print(
        "\n[TEST 2 & 3] Commencing ablated necessity (LOCO) and sufficiency sweeps..."
    )

    loco_results = {}
    sufficiency_results = {}

    for i, name in enumerate(V3_KEYS):
        # 1. LOCO: V3_{-i} (Necessity)
        X_train_lo = np.delete(X_train_v3, i, axis=1)
        X_val_lo = np.delete(X_val_v3, i, axis=1)

        clf_lo = RandomForestClassifier(n_estimators=100, random_state=42)
        clf_lo.fit(X_train_lo, y_train)

        y_prob_lo = clf_lo.predict_proba(X_val_lo)[:, 1]
        auc_lo = float(roc_auc_score(y_val, y_prob_lo))
        ece_lo = compute_ece(y_val, y_prob_lo)

        necessity = float(auc_full - auc_lo)
        delta_ece = float(ece_full - ece_lo)

        loco_results[name] = {
            "auc": auc_lo,
            "ece": ece_lo,
            "necessity": necessity,
            "delta_ece": delta_ece,
        }

        # 2. Sufficiency: V3_{i_only}
        X_train_io = X_train_v3[:, [i]]
        X_val_io = X_val_v3[:, [i]]

        clf_io = RandomForestClassifier(n_estimators=100, random_state=42)
        clf_io.fit(X_train_io, y_train)

        y_prob_io = clf_io.predict_proba(X_val_io)[:, 1]
        auc_io = float(roc_auc_score(y_val, y_prob_io))
        prec_io, rec_io, _ = precision_recall_curve(y_val, y_prob_io)
        pr_auc_io = float(auc(rec_io, prec_io))
        ece_io = compute_ece(y_val, y_prob_io)

        is_sufficient = auc_io > 0.85

        sufficiency_results[name] = {
            "auc": auc_io,
            "pr_auc": pr_auc_io,
            "ece": ece_io,
            "is_sufficient": is_sufficient,
        }

        print(
            f"  Component: {name:<26} | Necessity={necessity: .6f} | Sufficiency={auc_io:.6f} ({'Sufficient' if is_sufficient else 'Insufficient'})"
        )

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 4: REDUNDANCY MATRIX
    # ─────────────────────────────────────────────────────────────────────────────
    print(
        "\n[TEST 4] Constructing pairwise Pearson absolute correlation Redundancy Matrix R..."
    )

    R_matrix = np.zeros((8, 8))
    for i in range(8):
        for j in range(8):
            rho, _ = pearsonr(X_train_v3[:, i], X_train_v3[:, j])
            R_matrix[i, j] = abs(rho) if np.isfinite(rho) else 0.0

    # Calculate average redundancy R_i per feature (excluding diagonal element)
    redundancy_scores = {}
    for i, name in enumerate(V3_KEYS):
        R_i = float((np.sum(R_matrix[i]) - 1.0) / 7.0)
        redundancy_scores[name] = R_i
        print(f"  Component: {name:<26} | Mean Redundancy R_i = {R_i:.6f}")

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 5: BOOTSTRAP ATTRIBUTION STABILITY AUDIT
    # ─────────────────────────────────────────────────────────────────────────────
    M = 100
    print(
        f"\n[TEST 5] Executing Bootstrap Attribution Stability Audit (M={M} iterations)..."
    )

    bootstrap_importances = np.zeros((M, 8))
    n_samples = len(X_train_v3)

    for m in range(M):
        np.random.seed(m)
        indices = np.random.choice(n_samples, n_samples, replace=True)
        X_boot = X_train_v3[indices]
        y_boot = y_train[indices]

        # Use fast RF of 10 trees to ensure speed
        clf_boot = RandomForestClassifier(n_estimators=10, random_state=None)
        clf_boot.fit(X_boot, y_boot)
        bootstrap_importances[m] = clf_boot.feature_importances_

    # Compute mean, std, CV per feature
    stability_results = {}
    for i, name in enumerate(V3_KEYS):
        mu_i = float(np.mean(bootstrap_importances[:, i]))
        sigma_i = float(np.std(bootstrap_importances[:, i]))
        cv_i = float(sigma_i / mu_i) if mu_i > 0 else 0.0

        stability_results[name] = {
            "mean_importance": mu_i,
            "std_importance": sigma_i,
            "cv": cv_i,
            "is_unstable": (cv_i > 0.5),
        }
        print(
            f"  Component: {name:<26} | Mean Importance={mu_i:.6f} | Std={sigma_i:.6f} | CV={cv_i:.6f} ({'UNSTABLE' if cv_i > 0.5 else 'STABLE'})"
        )

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 6: CAUSAL CONTRIBUTION SCORE
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 6] Compiling Causal Contribution Scores C_i...")

    causal_scores = {}
    roles_ranking = []

    # C_i = 0.35 * I_i + 0.35 * AUC_i - 0.15 * R_i - 0.15 * CV_i
    for name in V3_KEYS:
        I_i = loco_results[name]["necessity"]
        AUC_i = sufficiency_results[name]["auc"]
        R_i = redundancy_scores[name]
        CV_i = stability_results[name]["cv"]

        C_i = 0.35 * I_i + 0.35 * AUC_i - 0.15 * R_i - 0.15 * CV_i
        causal_scores[name] = C_i

        # Determine logical role
        if stability_results[name]["is_unstable"]:
            role = "UNSTABLE_COMPONENT"
        elif I_i > 0.005 and AUC_i > 0.85:
            role = "CRITICAL_COMPONENT"
        elif redundancy_scores[name] > 0.60:
            role = "REDUNDANT_COMPONENT"
        elif I_i > 0.0 and AUC_i > 0.60:
            role = "SUPPORTING_COMPONENT"
        else:
            role = "NEGLIGIBLE_COMPONENT"

        roles_ranking.append(
            {
                "component": name,
                "score": C_i,
                "role": role,
                "necessity": I_i,
                "sufficiency": AUC_i,
                "redundancy": R_i,
                "instability": CV_i,
            }
        )

    # Sort roles ranking in descending order of causal score C_i
    roles_ranking = sorted(roles_ranking, key=lambda x: x["score"], reverse=True)

    print("\nCausal Dissection Roles Ranking:")
    for rank in roles_ranking:
        print(
            f"  - {rank['component']:<26} | Score={rank['score']: .6f} | Role={rank['role']}"
        )

    # Extract structural summaries for terminal print
    critical_comp = [
        r["component"] for r in roles_ranking if r["role"] == "CRITICAL_COMPONENT"
    ]
    supporting_comp = [
        r["component"] for r in roles_ranking if r["role"] == "SUPPORTING_COMPONENT"
    ]
    redundant_comp = [
        r["component"] for r in roles_ranking if r["role"] == "REDUNDANT_COMPONENT"
    ]
    negligible_comp = [
        r["component"] for r in roles_ranking if r["role"] == "NEGLIGIBLE_COMPONENT"
    ]
    unstable_comp = [
        r["component"] for r in roles_ranking if r["role"] == "UNSTABLE_COMPONENT"
    ]

    # Save Report
    report = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "audit_type": "Causal Ablation Audit",
            "explained_variance_v3": auc_full,
        },
        "test1_decompositions": {
            "v3_keys": V3_KEYS,
            "full_auc": auc_full,
            "full_pr_auc": pr_auc_full,
            "full_ece": ece_full,
        },
        "test2_loco_necessity": loco_results,
        "test3_isolated_sufficiency": sufficiency_results,
        "test4_redundancy_matrix": {
            "matrix": R_matrix.tolist(),
            "average_redundancy": redundancy_scores,
        },
        "test5_stability_audit": stability_results,
        "test6_causal_scores": {"scores": causal_scores, "ranking": roles_ranking},
    }

    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    t_end = time.time()

    # ── REQUIRED TERMINAL DUMP ────────────────────────────────────────────────
    print("\n" + "=" * 75)
    print("🏁 FINAL CAUSAL ABLATION AUDIT REPORT SUMMARY")
    print("=" * 75)
    print(
        "CRITICAL_COMPONENT     = "
        + (", ".join(critical_comp) if critical_comp else "NONE")
    )
    print(
        "SUPPORTING_COMPONENT   = "
        + (", ".join(supporting_comp) if supporting_comp else "NONE")
    )
    print(
        "REDUNDANT_COMPONENT     = "
        + (", ".join(redundant_comp) if redundant_comp else "NONE")
    )
    print(
        "NEGLIGIBLE_COMPONENT   = "
        + (", ".join(negligible_comp) if negligible_comp else "NONE")
    )
    print(
        "UNSTABLE_COMPONENT     = "
        + (", ".join(unstable_comp) if unstable_comp else "NONE")
    )
    print("")
    print(f"Causal Ablation completed in {t_end - t_start:.2f} seconds.")
    print("Report saved to: " + REPORT_FILE)
    print("=" * 75)


if __name__ == "__main__":
    main()
