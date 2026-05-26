"""Stable Effective Volume representation metric (EV3)."""

from __future__ import annotations

import numpy as np


def compute_stable_ev3(embeddings: np.ndarray, threshold: float = 1e-10) -> float:
    """Compute the stable effective volume (EV3) of the activation matrix.

    EV3 represents the geometric mean of the principal axes of the covariance
    ellipsoid of the embedding space. This is computed in log-space to ensure
    high numerical stability and prevent underflow/overflow.

    Args:
        embeddings: Activation matrix with shape ``(n_samples, n_features)``.
        threshold: Minimum threshold for singular values to prevent log(0).

    Returns:
        Stable EV3 geometric volume metric.
    """
    arr = np.asarray(embeddings, dtype=float)
    if arr.ndim != 2:
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)
        else:
            raise ValueError("Activation matrix must be two-dimensional.")

    # 1. Centering the matrix
    arr_centered = arr - np.mean(arr, axis=0, keepdims=True)

    # 2. Singular Value Decomposition
    try:
        s = np.linalg.svd(arr_centered, compute_uv=False)
    except np.linalg.LinAlgError:
        # Fallback if SVD fails to converge
        return 0.0

    # 3. Filter near-zero singular values (regularization threshold)
    s_filtered = s[s > threshold]
    if len(s_filtered) == 0:
        return 0.0

    # 4. Compute the geometric mean of singular values in log-space
    log_mean = np.mean(np.log(s_filtered))
    ev3 = np.exp(log_mean)

    return float(ev3)
