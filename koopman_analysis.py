import numpy as np
import scipy.linalg as la
from topological_analysis import reconstruct_phase_space

# Ensure UTF-8 output encoding for Windows terminal
import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN A: KOOPMAN MODES & DMD SOLVER
# ─────────────────────────────────────────────────────────────────────────────


def compute_koopman_modes(signal, emb_dim=3, lag=1, n_modes=5):
    """
    Computes Koopman Operator modes, complex eigenvalues, frequencies,
    and growth/decay rates using Dynamic Mode Decomposition (DMD) on embedded trajectories.
    """
    # 1. Reconstruct phase space
    point_cloud = reconstruct_phase_space(signal, emb_dim=emb_dim, lag=lag)
    n_points, n_dims = point_cloud.shape

    n_modes = min(n_modes, n_dims)

    if n_points < 10:
        print(
            "  [KOOPMAN WARNING] Point cloud too small for Koopman DMD. Returning empty arrays."
        )
        return (
            np.zeros(n_modes, dtype=complex),
            np.zeros((n_dims, n_modes), dtype=complex),
            np.zeros(n_modes),
            np.zeros(n_modes),
        )

    # 2. Divide into snapshots X and Y (X = time t, Y = time t+1)
    # Shape: n_dims x (n_points - 1)
    X = point_cloud[:-1, :].T
    Y = point_cloud[1:, :].T

    try:
        # 3. Approximate Koopman transition matrix K = Y * pinv(X)
        # Using SVD to compute the pseudoinverse of X robustly
        U, S, Vt = np.linalg.svd(X, full_matrices=False)
        # Filter zero singular values
        S_inv = np.zeros_like(S)
        mask = S > 1e-10
        S_inv[mask] = 1.0 / S[mask]

        # Reconstruct pseudo-inverse: X_pinv = V * S_inv * U_T
        X_pinv = Vt.T @ np.diag(S_inv) @ U.T

        # K approximation (n_dims x n_dims)
        K = Y @ X_pinv

        # 4. Eigenvalue and eigenvector decomposition of K
        eigenvalues, modes = la.eig(K)

        # Sort by magnitude descending
        idx = np.argsort(np.abs(eigenvalues))[::-1]
        eigenvalues = eigenvalues[idx][:n_modes]
        modes = modes[:, idx][:, :n_modes]

        # 5. Extract frequencies and growth rates from eigenvalues
        # lambda = exp(growth_rate + i * frequency)
        # log(lambda) = growth_rate + i * frequency
        # Handle eigenvalues near zero safely by clipping
        clipped_eigs = np.where(np.abs(eigenvalues) < 1e-10, 1e-10, eigenvalues)
        log_eigs = np.log(clipped_eigs)

        growth_rates = np.real(log_eigs)
        # Frequency is the imaginary part of the logarithm
        frequencies = np.imag(log_eigs)

        return eigenvalues, modes, frequencies, growth_rates

    except Exception as e:
        print(
            f"  [KOOPMAN ERROR] DMD SVD solver failed ({e}). Returning zero fallbacks."
        )
        return (
            np.zeros(n_modes, dtype=complex),
            np.zeros((n_dims, n_modes), dtype=complex),
            np.zeros(n_modes),
            np.zeros(n_modes),
        )


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN B: KOOPMAN FEATURE EXTRACTOR
# ─────────────────────────────────────────────────────────────────────────────


def extract_koopman_features(signal, emb_dim=3, lag=1, n_modes=5):
    """
    Extracts dynamic features from the Koopman DMD operator.
    Returns a fixed-size 10D vector of descriptors.
    Vector mapping:
      0: Mean of oscillation frequencies
      1: Variance of oscillation frequencies
      2: Mean of growth/decay rates
      3: Variance of growth/decay rates
      4: Count of conservative modes (|lambda| ≈ 1)
      5: Spectral Shannon entropy of eigenvalues
      6: Mean of eigenvalue magnitudes
      7: Variance of eigenvalue magnitudes
      8: Maximum oscillation frequency
      9: Maximum growth/decay rate
    """
    feat_vector = np.full(10, np.nan)

    # Check signal length
    point_cloud = reconstruct_phase_space(signal, emb_dim=emb_dim, lag=lag)
    if len(point_cloud) < 10:
        print(
            "  [KOOPMAN WARNING] Signal too short to extract Koopman features. Returning NaNs."
        )
        return feat_vector

    try:
        eigs, modes, freqs, growths = compute_koopman_modes(
            signal, emb_dim=emb_dim, lag=lag, n_modes=n_modes
        )

        mags = np.abs(eigs)

        feat_vector[0] = float(np.mean(freqs))
        feat_vector[1] = float(np.var(freqs))
        feat_vector[2] = float(np.mean(growths))
        feat_vector[3] = float(np.var(growths))

        # Conservative modes count (|lambda| within 0.05 of 1.0)
        feat_vector[4] = int(np.sum(np.abs(mags - 1.0) < 0.05))

        # Spectral Shannon entropy of eigenvalue magnitudes
        total_mag = np.sum(mags)
        if total_mag > 0.0:
            probs = mags / total_mag
            probs = probs[probs > 0.0]
            feat_vector[5] = float(-np.sum(probs * np.log2(probs)))
        else:
            feat_vector[5] = 0.0

        feat_vector[6] = float(np.mean(mags))
        feat_vector[7] = float(np.var(mags))
        feat_vector[8] = float(np.max(np.abs(freqs))) if len(freqs) > 0 else 0.0
        feat_vector[9] = float(np.max(growths)) if len(growths) > 0 else 0.0

    except Exception as e:
        print(f"  [KOOPMAN ERROR] Failed to extract Koopman features: {e}")

    return feat_vector


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN C: KOOPMAN TEMPORAL INVARIANTS TRACKER
# ─────────────────────────────────────────────────────────────────────────────


def compute_koopman_invariants(signal, emb_dim=3, lag=1):
    """
    Identifies candidate invariant coordinate functions (low temporal variance)
    from conservative Koopman modes (|lambda| ≈ 1).
    """
    invariants = []

    point_cloud = reconstruct_phase_space(signal, emb_dim=emb_dim, lag=lag)
    n_points, n_dims = point_cloud.shape
    if n_points < 10:
        return invariants

    try:
        eigs, modes, _, _ = compute_koopman_modes(
            signal, emb_dim=emb_dim, lag=lag, n_modes=n_dims
        )

        # Threshold for conservative mode: |lambda| within 0.02 of 1.0
        conservative_mask = np.abs(np.abs(eigs) - 1.0) < 0.02
        conservative_modes = modes[:, conservative_mask]

        for idx in range(conservative_modes.shape[1]):
            v = conservative_modes[:, idx]
            # Project embedded point cloud onto the complex eigenvector
            # Shape: (n_points,)
            projection = point_cloud @ v

            # Use real part of the projection as candidate invariant
            real_proj = np.real(projection)

            # Normalize projection to unit variance to compare scale-independent variability
            norm_proj = real_proj / (np.max(np.abs(real_proj)) + 1e-10)
            var_temp = np.var(norm_proj)

            # If temporal variance is low, add to candidate invariants
            if var_temp < 0.05:
                invariants.append(real_proj)

    except Exception as e:
        print(f"  [KOOPMAN ERROR] Failed to compute invariants: {e}")

    return invariants
