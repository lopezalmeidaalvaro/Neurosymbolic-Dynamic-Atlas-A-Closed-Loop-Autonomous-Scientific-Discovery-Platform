import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import os
import sys
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import json

# Ensure root path is imported
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import topological_analysis as tda
import geometric_analysis as geom
import koopman_analysis as koop
import ucr_loader
from synthetic_systems import generate_lorenz


def add_gaussian_noise(signal, snr_db):
    """
    Adds Gaussian noise to a 1D signal to achieve a target SNR in dB.
    """
    sig = np.array(signal, dtype=float)
    sig_power = np.mean(sig**2)
    if sig_power < 1e-10:
        sig_power = 1e-10

    # SNR = 10 * log10(P_sig / P_noise) => P_noise = P_sig / (10**(SNR/10))
    noise_power = sig_power / (10 ** (snr_db / 10.0))
    noise_std = np.sqrt(noise_power)

    # Use fixed seed for deterministic noise in audits
    np.random.seed(42)
    noise = np.random.normal(0, noise_std, len(sig))
    return sig + noise


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN A: TOPOLOGICAL ROBUSTNESS
# ─────────────────────────────────────────────────────────────────────────────


def compute_topological_stability(signal, snr_levels=[30, 20, 10, 0]):
    """
    Measures the degradation of topological persistence diagrams under noise levels
    by calculating the Wasserstein distance between the clean and noisy diagrams.
    """
    print("  [AUDIT] Starting topological stability analysis...")
    pc_clean = tda.reconstruct_phase_space(signal, emb_dim=3, lag=1)
    res_clean = tda.compute_persistence_diagram(pc_clean, max_dim=2)
    dgms_clean = res_clean["dgms"]

    results = []
    for snr in snr_levels:
        noisy_sig = add_gaussian_noise(signal, snr)
        pc_noisy = tda.reconstruct_phase_space(noisy_sig, emb_dim=3, lag=1)
        res_noisy = tda.compute_persistence_diagram(pc_noisy, max_dim=2)
        dgms_noisy = res_noisy["dgms"]

        # Compare diagrams using Wasserstein distance
        w_dist_h0 = tda.compare_persistence_diagrams(
            dgms_clean[0], dgms_noisy[0], dim=0
        )
        w_dist_h1 = tda.compare_persistence_diagrams(
            dgms_clean[1], dgms_noisy[1], dim=1
        )
        w_dist_h2 = tda.compare_persistence_diagrams(
            dgms_clean[2], dgms_noisy[2], dim=2
        )

        results.append(
            {
                "SNR": snr,
                "Wasserstein_H0": w_dist_h0,
                "Wasserstein_H1": w_dist_h1,
                "Wasserstein_H2": w_dist_h2,
            }
        )
        print(
            f"    - SNR: {snr:2d} dB | H0: {w_dist_h0:.4f} | H1: {w_dist_h1:.4f} | H2: {w_dist_h2:.4f}"
        )

    return pd.DataFrame(results)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN B: GEOMETRIC ROBUSTNESS
# ─────────────────────────────────────────────────────────────────────────────


def compute_geometric_stability(signal, snr_levels=[30, 20, 10, 0]):
    """
    Measures the degradation of neighborhood graph Ricci curvature and Laplace-Beltrami
    spectrum eigenvalues under noise levels.
    """
    print("  [AUDIT] Starting geometric stability analysis...")
    pc_clean = tda.reconstruct_phase_space(signal, emb_dim=3, lag=1)
    # Sample a smaller subset for fast graph computations in audits
    n_pts = min(60, len(pc_clean))
    pc_sample_clean = pc_clean[:n_pts]

    G_clean = geom.build_neighborhood_graph(pc_sample_clean, k=6)
    G_ricci_clean = geom.compute_ollivier_ricci_curvature(G_clean)
    node_curvs_clean = geom.compute_node_curvature(G_ricci_clean)

    lb_eigs_clean, _ = geom.compute_laplacian_eigenmap(
        pc_sample_clean, n_components=5, k=6
    )

    results = []
    for snr in snr_levels:
        noisy_sig = add_gaussian_noise(signal, snr)
        pc_noisy = tda.reconstruct_phase_space(noisy_sig, emb_dim=3, lag=1)
        pc_sample_noisy = pc_noisy[:n_pts]

        # 1. Ollivier-Ricci Curvature Spearman Correlation
        G_noisy = geom.build_neighborhood_graph(pc_sample_noisy, k=6)
        G_ricci_noisy = geom.compute_ollivier_ricci_curvature(G_noisy)
        node_curvs_noisy = geom.compute_node_curvature(G_ricci_noisy)

        try:
            spearman_ricci, _ = stats.spearmanr(node_curvs_clean, node_curvs_noisy)
            if np.isnan(spearman_ricci):
                spearman_ricci = 0.0
        except Exception:
            spearman_ricci = 0.0

        # 2. Laplace-Beltrami spectrum relative error
        try:
            lb_eigs_noisy, _ = geom.compute_laplacian_eigenmap(
                pc_sample_noisy, n_components=5, k=6
            )
            rel_error_laplace = np.mean(
                np.abs(lb_eigs_clean - lb_eigs_noisy) / (np.abs(lb_eigs_clean) + 1e-10)
            )
        except Exception:
            rel_error_laplace = 1.0

        results.append(
            {
                "SNR": snr,
                "Spearman_Ricci": float(spearman_ricci),
                "RelError_Laplace": float(rel_error_laplace),
            }
        )
        print(
            f"    - SNR: {snr:2d} dB | Spearman Ricci: {spearman_ricci:.4f} | RelError LB: {rel_error_laplace:.4f}"
        )

    return pd.DataFrame(results)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN C: KOOPMAN ROBUSTNESS
# ─────────────────────────────────────────────────────────────────────────────


def compute_koopman_stability(signal, snr_levels=[30, 20, 10, 0]):
    """
    Measures the degradation of Koopman DMD complex eigenvalues under noise levels
    by calculating the 1D Wasserstein distance between eigenvalue magnitudes.
    """
    print("  [AUDIT] Starting Koopman stability analysis...")

    # Extract clean Koopman eigenvalues magnitude
    eigs_clean, _, _, _ = koop.compute_koopman_modes(
        signal, emb_dim=3, lag=1, n_modes=5
    )
    mags_clean = np.abs(eigs_clean)

    results = []
    for snr in snr_levels:
        noisy_sig = add_gaussian_noise(signal, snr)
        eigs_noisy, _, _, _ = koop.compute_koopman_modes(
            noisy_sig, emb_dim=3, lag=1, n_modes=5
        )
        mags_noisy = np.abs(eigs_noisy)

        # 1D Wasserstein distance on magnitudes
        w_dist_koopman = float(stats.wasserstein_distance(mags_clean, mags_noisy))

        results.append({"SNR": snr, "Wasserstein_Koopman": w_dist_koopman})
        print(f"    - SNR: {snr:2d} dB | Koopman Wasserstein: {w_dist_koopman:.4f}")

    return pd.DataFrame(results)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN D: FULL STUDY & CONSOLIDATION
# ─────────────────────────────────────────────────────────────────────────────


def run_full_topological_robustness_study(
    signal_generator_func, n_signals=10, dataset_name="Lorenz"
):
    """
    Orchestrates the entire topological/geometric robustness study, averaging results
    across multiple generated or UCR signals.
    """
    print("=" * 70)
    print(f"STARTING COMPREHENSIVE ROBUSTNESS AUDIT FOR {dataset_name.upper()}")
    print("=" * 70)

    snr_levels = [30, 20, 10, 0]

    # Accumulators
    tda_dfs = []
    geom_dfs = []
    koop_dfs = []

    for idx in range(n_signals):
        print(f"\n[RUN {idx+1}/{n_signals}] Processing independent signal instance...")
        try:
            sig = signal_generator_func(idx)

            tda_df = compute_topological_stability(sig, snr_levels)
            geom_df = compute_geometric_stability(sig, snr_levels)
            koop_df = compute_koopman_stability(sig, snr_levels)

            tda_dfs.append(tda_df)
            geom_dfs.append(geom_df)
            koop_dfs.append(koop_df)
        except Exception as e:
            print(f"  [RUN ERROR] Skip index {idx} due to error: {e}")

    if not tda_dfs:
        print("[ERROR] No successful audit runs completed.")
        return None

    # Mean reduction
    mean_tda = pd.concat(tda_dfs).groupby("SNR").mean().reset_index()
    mean_geom = pd.concat(geom_dfs).groupby("SNR").mean().reset_index()
    mean_koop = pd.concat(koop_dfs).groupby("SNR").mean().reset_index()

    # 1. Compile consolidated JSON results
    consolidated_results = {
        "dataset_name": dataset_name,
        "n_signals_averaged": n_signals,
        "topological_stability": mean_tda.to_dict(orient="list"),
        "geometric_stability": mean_geom.to_dict(orient="list"),
        "koopman_stability": mean_koop.to_dict(orient="list"),
    }

    # Export JSON
    os.makedirs(os.path.join(ROOT_DIR, "artifacts"), exist_ok=True)
    json_path = os.path.join(
        ROOT_DIR,
        "artifacts",
        f"topological_robustness_{dataset_name.lower()}_results.json",
    )
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(consolidated_results, f, indent=4)
    print(f"\n[AUDIT] Exported consolidated JSON study to: {json_path}")

    # 2. Generate and save premium PDF chart
    os.makedirs(os.path.join(ROOT_DIR, "figures"), exist_ok=True)
    fig_path = os.path.join(
        ROOT_DIR, "figures", f"{dataset_name.lower()}_topological_robustness.pdf"
    )

    plt.style.use(
        "seaborn-v0_8-whitegrid"
        if "seaborn-v0_8-whitegrid" in plt.style.available
        else "default"
    )
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Plot TDA
    axes[0].plot(
        mean_tda["SNR"],
        mean_tda["Wasserstein_H0"],
        marker="o",
        linewidth=2.5,
        color="#06b6d4",
        label="H0 Components",
    )
    axes[0].plot(
        mean_tda["SNR"],
        mean_tda["Wasserstein_H1"],
        marker="s",
        linewidth=2.5,
        color="#f43f5e",
        label="H1 Loops",
    )
    axes[0].plot(
        mean_tda["SNR"],
        mean_tda["Wasserstein_H2"],
        marker="^",
        linewidth=2.5,
        color="#10b981",
        label="H2 Voids",
    )
    axes[0].set_xlabel("Signal-to-Noise Ratio (SNR dB)", fontweight="bold")
    axes[0].set_ylabel("Wasserstein Bipartite Distance", fontweight="bold")
    axes[0].set_title(
        "Topological Stability (TDA Persistence)", fontweight="bold", pad=12
    )
    axes[0].invert_xaxis()
    axes[0].legend()

    # Plot Geometric
    ax_geom_twin = axes[1].twinx()
    (p1,) = axes[1].plot(
        mean_geom["SNR"],
        mean_geom["Spearman_Ricci"],
        marker="o",
        linewidth=2.5,
        color="#8b5cf6",
        label="Spearman Ricci",
    )
    (p2,) = ax_geom_twin.plot(
        mean_geom["SNR"],
        mean_geom["RelError_Laplace"],
        marker="s",
        linewidth=2.5,
        color="#f59e0b",
        label="LB Eigenvalue RelError",
    )

    axes[1].set_xlabel("Signal-to-Noise Ratio (SNR dB)", fontweight="bold")
    axes[1].set_ylabel("Spearman Rank Correlation", color="#8b5cf6", fontweight="bold")
    axes[1].tick_params(axis="y", labelcolor="#8b5cf6")
    ax_geom_twin.set_ylabel(
        "Laplace-Beltrami Mean Relative Error", color="#f59e0b", fontweight="bold"
    )
    ax_geom_twin.tick_params(axis="y", labelcolor="#f59e0b")
    axes[1].set_title("Manifold Geometrical Stability", fontweight="bold", pad=12)
    axes[1].invert_xaxis()

    lines = [p1, p2]
    axes[1].legend(lines, [l.get_label() for l in lines], loc="upper right")

    # Plot Koopman
    axes[2].plot(
        mean_koop["SNR"],
        mean_koop["Wasserstein_Koopman"],
        marker="d",
        linewidth=2.5,
        color="#ec4899",
        label="Koopman Spectrum",
    )
    axes[2].set_xlabel("Signal-to-Noise Ratio (SNR dB)", fontweight="bold")
    axes[2].set_ylabel("1D Wasserstein Distance (Magnitudes)", fontweight="bold")
    axes[2].set_title(
        "Koopman Operator Eigenvalue Stability", fontweight="bold", pad=12
    )
    axes[2].invert_xaxis()
    axes[2].legend()

    plt.suptitle(
        f"Topological & Geometric Robustness Integrity Audit — {dataset_name}",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    plt.savefig(fig_path, bbox_inches="tight", dpi=300)
    plt.close()

    print(f"[AUDIT] Saved premium stability chart to: {fig_path}")
    return consolidated_results


if __name__ == "__main__":
    print(
        "Executing Topological Robustness Study on Lorenz Attractor and ECG200 dataset..."
    )

    # 1. Lorenz Signal Generator
    def lorenz_gen(idx):
        # Generate with slightly varying initial states to get multiple signals
        np.random.seed(idx)
        init = [
            10.0 + np.random.normal(0, 0.1),
            10.0 + np.random.normal(0, 0.1),
            20.0 + np.random.normal(0, 0.1),
        ]
        traj = generate_lorenz(n_timesteps=600, dt=0.01, initial_state=init)
        return traj["x"]  # Return X coordinate

    # Run Lorenz Study (averaging over 3 signals for fast demonstration and stability)
    run_full_topological_robustness_study(
        lorenz_gen, n_signals=3, dataset_name="Lorenz"
    )

    # 2. ECG200 Signal Generator
    try:
        data = ucr_loader.load_ucr_dataset("ECG200")
        X_train = data["X_train"]

        def ecg_gen(idx):
            # Retrieve signals from ECG200 train batch
            return X_train[idx % len(X_train)]

        # Run ECG200 Study (averaging over 3 signals)
        run_full_topological_robustness_study(
            ecg_gen, n_signals=3, dataset_name="ECG200"
        )
    except Exception as e:
        print(f"[AUDIT ERROR] Could not execute ECG200 study: {e}")
