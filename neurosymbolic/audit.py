"""Representational audit metrics."""

from __future__ import annotations

import numpy as np


def linear_cka(x: np.ndarray, y: np.ndarray) -> float:
    """Compute linear centered kernel alignment between two activation matrices.

    Args:
        x: First activation matrix with shape ``(n_samples, n_features_x)``.
        y: Second activation matrix with shape ``(n_samples, n_features_y)``.

    Returns:
        Linear CKA similarity in the closed interval ``[0, 1]``.

    Raises:
        ValueError: If the matrices are not two-dimensional or have different
            sample counts.
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)

    if x_arr.ndim != 2 or y_arr.ndim != 2:
        raise ValueError("CKA inputs must be two-dimensional matrices.")
    if x_arr.shape[0] != y_arr.shape[0]:
        raise ValueError("CKA inputs must have the same number of samples.")

    x_centered = x_arr - np.mean(x_arr, axis=0, keepdims=True)
    y_centered = y_arr - np.mean(y_arr, axis=0, keepdims=True)

    numerator = np.linalg.norm(x_centered.T @ y_centered, ord="fro") ** 2
    x_norm = np.linalg.norm(x_centered.T @ x_centered, ord="fro")
    y_norm = np.linalg.norm(y_centered.T @ y_centered, ord="fro")

    denominator = x_norm * y_norm
    if denominator <= 1e-12:
        return 0.0
    return float(np.clip(numerator / denominator, 0.0, 1.0))


def compute_cka(X: np.ndarray, Y: np.ndarray) -> float:
    """Compute linear centered kernel alignment (CKA) between two activation matrices.

    Args:
        X: First activation matrix with shape ``(n_samples, n_features_x)``.
        Y: Second activation matrix with shape ``(n_samples, n_features_y)``.

    Returns:
        Linear CKA similarity.
    """
    return linear_cka(X, Y)


def compute_ev3(embeddings: np.ndarray) -> float:
    """Compute the effective volume (EV3) of the activation matrix.

    EV3 is computed as the product of normalized singular values of the
    activation matrix.
    """
    arr = np.asarray(embeddings, dtype=float)
    if arr.ndim != 2:
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)
        else:
            raise ValueError("Activation matrix must be two-dimensional.")

    s = np.linalg.svd(arr, compute_uv=False)
    sum_s = np.sum(s)
    if sum_s <= 1e-12:
        return 0.0

    s_norm = s / sum_s
    prod = np.prod(s_norm)
    return float(prod)

