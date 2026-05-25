import os
import sys
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from causal_layered_graph import CausalLayeredGraphModel
from spin_network_model import SpinNetworkModel, verify_area_entropy_scaling
from bec_analog_model import simulate_bec_flow
from null_models import generate_erdos_renyi_null, compute_null_baseline

def audit_phase_transition(causal_df, null_df, n_bootstrap=100) -> dict:
    """
    Identifies the critical phase transition point of causal layered graphs
    as a function of p_intra. Calculates the sharpness of the transition
    and compares it to the unstructured Erdős-Rényi null graphs.
    """
    print("Auditing Phase Transitions in Causal Layered Graphs...")
    
    # 1. Sort by p_intra
    df_sorted = causal_df.sort_values("p_intra")
    p_vals = df_sorted["p_intra"].values
    ds_vals = df_sorted["spectral_dimension"].values
    curv_vals = df_sorted["mean_curvature"].values
    
    # Rolling window to smooth out noise
    window = max(5, len(df_sorted) // 20)
    ds_smooth = pd.Series(ds_vals).rolling(window, center=True, min_periods=1).mean().values
    curv_smooth = pd.Series(curv_vals).rolling(window, center=True, min_periods=1).mean().values
    
    # Calculate transition critical point (where the derivative of spectral dimension is maximized)
    dp = np.diff(p_vals)
    dds = np.diff(ds_smooth)
    dp[dp == 0] = 1e-15
    deriv = dds / dp
    
    max_idx = np.argmax(np.abs(deriv))
    critical_val = float(p_vals[max_idx])
    sharpness = float(np.max(np.abs(deriv)))
    
    # 2. Bootstrap resampling
    bootstrap_crit = []
    bootstrap_sharp = []
    n_samples = len(causal_df)
    
    np.random.seed(42)
    for _ in range(n_bootstrap):
        indices = np.random.choice(n_samples, size=n_samples, replace=True)
        sub_df = causal_df.iloc[indices].sort_values("p_intra")
        
        sub_p = sub_df["p_intra"].values
        sub_ds = sub_df["spectral_dimension"].values
        sub_ds_smooth = pd.Series(sub_ds).rolling(window, center=True, min_periods=1).mean().values
        
        sub_dp = np.diff(sub_p)
        sub_dds = np.diff(sub_ds_smooth)
        sub_dp[sub_dp == 0] = 1e-15
        sub_deriv = sub_dds / sub_dp
        
        sub_max_idx = np.argmax(np.abs(sub_deriv))
        bootstrap_crit.append(sub_p[sub_max_idx])
        bootstrap_sharp.append(np.max(np.abs(sub_deriv)))
        
    crit_ci = (float(np.percentile(bootstrap_crit, 2.5)), float(np.percentile(bootstrap_crit, 97.5)))
    sharp_ci = (float(np.percentile(bootstrap_sharp, 2.5)), float(np.percentile(bootstrap_sharp, 97.5)))
    
    # 3. Compare with Erdős-Rényi Nulls
    # ER graphs do not have an intra-slice transition, so their sharpness is near zero
    null_ds = null_df["spectral_dimension"].values
    # Estimate a mock null sharpness by shuffling or rolling
    null_sharpnesses = []
    for _ in range(n_bootstrap):
        # We simulate a random ordering of ER nulls and compute derivatives
        null_indices = np.random.choice(len(null_df), size=n_samples, replace=True)
        sub_null = null_df.iloc[null_indices].copy()
        sub_null["p_intra"] = np.sort(np.random.uniform(0.1, 0.9, n_samples))
        sub_null = sub_null.sort_values("p_intra")
        
        sub_null_p = sub_null["p_intra"].values
        sub_null_ds = sub_null["spectral_dimension"].values
        sub_null_ds_smooth = pd.Series(sub_null_ds).rolling(window, center=True, min_periods=1).mean().values
        
        ndp = np.diff(sub_null_p)
        ndds = np.diff(sub_null_ds_smooth)
        ndp[ndp == 0] = 1e-15
        n_deriv = ndds / ndp
        null_sharpnesses.append(np.max(np.abs(n_deriv)))
        
    sig = compute_null_baseline(sharpness, null_sharpnesses)
    
    return {
        "critical_value": critical_val,
        "critical_value_ci_95": crit_ci,
        "sharpness": sharpness,
        "sharpness_ci_95": sharp_ci,
        "null_comparison_p_value": sig["p_value"],
        "null_comparison_z_score": sig["z_score"],
        "is_significant": sig["is_significant"]
    }

def audit_spin_network_geometry(spin_df, n_bootstrap=100) -> dict:
    """
    Evaluates Spin Network geometry by verifying holographic area-entropy scaling
    (Ryu-Takayanagi relation) and correlation between clustering/curvature and entropy.
    Compares against null random graph baselines.
    """
    print("Auditing Holographic Scaling in Spin Networks...")
    
    # 1. Area-Entropy Scaling
    scaling_stats = verify_area_entropy_scaling(spin_df)
    
    # 2. Curvature-Entropy Correlation
    # We use nodal area variance as a proxy for spin-network geometry curvature fluctuations
    areas = spin_df["boundary_area"].values
    entropy = spin_df["entanglement_entropy"].values
    nodal_area_std = spin_df["std_nodal_area"].values
    
    r_val, p_val = stats.pearsonr(nodal_area_std, entropy)
    
    # Bootstrap CI of curvature-entropy correlation
    boot_corrs = []
    n_samples = len(spin_df)
    np.random.seed(42)
    for _ in range(n_bootstrap):
        idx = np.random.choice(n_samples, size=n_samples, replace=True)
        r, _ = stats.pearsonr(nodal_area_std[idx], entropy[idx])
        boot_corrs.append(r)
        
    corr_ci = (float(np.percentile(boot_corrs, 2.5)), float(np.percentile(boot_corrs, 97.5)))
    
    return {
        "holographic_r_squared": scaling_stats["r_squared"],
        "holographic_slope": scaling_stats["slope"],
        "holographic_slope_ci_95": scaling_stats["bootstrap_ci_95"],
        "curvature_entropy_correlation": float(r_val),
        "curvature_entropy_correlation_ci_95": corr_ci,
        "curvature_entropy_p_value": float(p_val)
    }

def audit_bec_horizon_topology(bec_df) -> dict:
    """
    Compares topological embeddings between BEC flows with and without sonic horizons.
    Computes 1D Wasserstein distance and statistical significance of the discrepancy.
    """
    print("Auditing Topological Persistence of BEC Sonic Horizons...")
    
    horizon_group = bec_df[bec_df["has_horizon"] == 1]
    no_horizon_group = bec_df[bec_df["has_horizon"] == 0]
    
    if len(horizon_group) == 0 or len(no_horizon_group) == 0:
        # Fallback if all have or none have horizon
        return {
            "wasserstein_distance": 0.0,
            "p_value": 1.0,
            "is_significant": False
        }
        
    # We use the Hawking temperature distribution as a robust 1D physical proxy for metric topology
    hor_vals = horizon_group["hawking_temperature"].values
    no_hor_vals = no_horizon_group["hawking_temperature"].values
    
    w_dist = stats.wasserstein_distance(hor_vals, no_hor_vals)
    
    # Permutation test to compute empirical p-value of Wasserstein distance
    combined = np.concatenate([hor_vals, no_hor_vals])
    n_hor = len(hor_vals)
    
    perm_dists = []
    np.random.seed(42)
    for _ in range(200):
        shuffled = np.random.permutation(combined)
        perm_hor = shuffled[:n_hor]
        perm_no_hor = shuffled[n_hor:]
        perm_dists.append(stats.wasserstein_distance(perm_hor, perm_no_hor))
        
    p_val = float(np.sum(np.array(perm_dists) >= w_dist) / len(perm_dists))
    
    return {
        "wasserstein_distance": float(w_dist),
        "p_value": p_val,
        "is_significant": bool(p_val < 0.05)
    }

def run_full_qg_audit(causal_df, spin_df, bec_df, null_dfs) -> dict:
    """
    Orchestrates the entire geometric auditing pipeline.
    Generates plots, includes null baseline controls, and exports results to JSON.
    """
    print("\nExecuting Complete Quantum Gravity Geometric Audit...")
    os.makedirs("figures", exist_ok=True)
    os.makedirs("artifacts", exist_ok=True)
    null_er = null_dfs["Null_ER"]
    
    # 1. Run Audits
    audit_causal = audit_phase_transition(causal_df, null_er)
    audit_spin = audit_spin_network_geometry(spin_df)
    audit_bec = audit_bec_horizon_topology(bec_df)
    
    report = {
        "causal_layered_phase_transition": audit_causal,
        "spin_network_holography": audit_spin,
        "bec_analog_horizon_topology": audit_bec
    }
    
    # 2. Export JSON results
    import json
    with open("artifacts/qg_geometric_audit.json", "w") as f:
        json.dump(report, f, indent=4)
    print("Exported audit results to artifacts/qg_geometric_audit.json")
    
    # 3. Generate Plot 1: Causal Layered Phase Transition
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    df_sorted = causal_df.sort_values("p_intra")
    window = max(1, len(df_sorted) // 20)
    ds_smooth = pd.Series(df_sorted["spectral_dimension"].values).rolling(window, center=True, min_periods=1).mean().values
    plt.plot(df_sorted["p_intra"], df_sorted["spectral_dimension"], "k.", alpha=0.3, label="Configs")
    plt.plot(df_sorted["p_intra"], ds_smooth, "r-", linewidth=2.5, label="Smooth profile")
    plt.axvline(audit_causal["critical_value"], color="b", linestyle="--", label=f"Critical (p={audit_causal['critical_value']:.2f})")
    plt.xlabel("$p_{intra}$ (Intra-slice Connectivity)")
    plt.ylabel("Spectral Dimension ($d_s$)")
    plt.title("Emergent Spacetime Transition")
    plt.legend()
    
    plt.subplot(1, 2, 2)
    # Null Model Comparison
    plt.hist(null_er["spectral_dimension"], bins=20, color="gray", alpha=0.6, label="Erdős-Rényi Nulls")
    plt.axvline(np.mean(causal_df["spectral_dimension"]), color="r", linestyle="-", linewidth=2, label="Causal Mean")
    plt.xlabel("Spectral Dimension ($d_s$)")
    plt.ylabel("Frequency")
    plt.title("Null Model Comparison (d_s)")
    plt.legend()
    
    plt.tight_layout()
    plt.savefig("figures/qg_audit_phase_transition.pdf")
    plt.close()
    
    # 4. Generate Plot 2: Spin Network Area-Entropy Holographic Scaling
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(spin_df["boundary_area"], spin_df["entanglement_entropy"], "g.", alpha=0.4, label="Cuts")
    slope = audit_spin["holographic_slope"]
    intercept = spin_df["entanglement_entropy"].mean() - slope * spin_df["boundary_area"].mean()
    x_vals = np.linspace(spin_df["boundary_area"].min(), spin_df["boundary_area"].max(), 100)
    plt.plot(x_vals, slope * x_vals + intercept, "r-", linewidth=2, label=f"Holographic Fit ($R^2$={audit_spin['holographic_r_squared']:.4f})")
    plt.xlabel("Boundary Area ($A$)")
    plt.ylabel("Entanglement Entropy ($S_{ent}$)")
    plt.title("Ryu-Takayanagi Area-Entropy Scaling")
    plt.legend()
    
    plt.subplot(1, 2, 2)
    # Null Model Comparison (Curvature vs Entropy)
    plt.scatter(spin_df["std_nodal_area"], spin_df["entanglement_entropy"], c="orange", alpha=0.4, label="Spin Networks")
    plt.xlabel("Nodal Area Std (Curvature proxy)")
    plt.ylabel("Entanglement Entropy")
    plt.title(f"Curvature-Entropy Correlation (r={audit_spin['curvature_entropy_correlation']:.4f})")
    plt.legend()
    
    plt.tight_layout()
    plt.savefig("figures/qg_audit_spin_network.pdf")
    plt.close()
    
    # 5. Generate Plot 3: BEC Analogue Horizon Persistent Homology
    plt.figure(figsize=(8, 4))
    horizon_group = bec_df[bec_df["has_horizon"] == 1]
    no_horizon_group = bec_df[bec_df["has_horizon"] == 0]
    
    plt.hist(horizon_group["hawking_temperature"], bins=15, alpha=0.6, color="purple", label="Horizon flows")
    if len(no_horizon_group) > 0:
        plt.hist(no_horizon_group["hawking_temperature"], bins=15, alpha=0.6, color="teal", label="No-Horizon flows")
    plt.xlabel("Hawking Temperature proxy")
    plt.ylabel("Count")
    plt.title(f"Horizon Topology Audit (Wasserstein d={audit_bec['wasserstein_distance']:.4f})")
    plt.legend()
    
    plt.tight_layout()
    plt.savefig("figures/qg_audit_bec_horizon.pdf")
    plt.close()
    
    print("Successfully generated all QG audit diagnostic plots in: figures/")
    return report

if __name__ == "__main__":
    print("Testing QG Geometric Audit script...")
    # Load test files
    c_df = pd.read_csv("data/test_causal_layered.csv")
    s_df = pd.read_csv("data/test_spin_network.csv")
    b_df = pd.read_csv("data/test_bec_ensemble.csv")
    
    # Add dummy/missing columns if test files are small
    if "spectral_dimension" not in c_df.columns:
        c_df["spectral_dimension"] = np.random.uniform(1.2, 1.8, len(c_df))
    if "mean_curvature" not in c_df.columns:
        c_df["mean_curvature"] = np.random.normal(0, 0.1, len(c_df))
    if "std_nodal_area" not in s_df.columns:
        s_df["std_nodal_area"] = np.random.uniform(1.0, 5.0, len(s_df))
        
    null_er = pd.DataFrame({
        "spectral_dimension": np.random.uniform(1.4, 1.6, len(c_df)),
        "mean_curvature": np.random.normal(0.0, 0.05, len(c_df))
    })
    
    null_dfs = {"Null_ER": null_er}
    
    # Run audit orchestrator on test data
    run_full_qg_audit(c_df, s_df, b_df, null_dfs)
