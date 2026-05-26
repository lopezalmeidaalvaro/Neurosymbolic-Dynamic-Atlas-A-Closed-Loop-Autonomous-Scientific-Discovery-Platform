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


from neurosymbolic.metrics.ev3 import compute_stable_ev3

def compute_ev3(embeddings: np.ndarray) -> float:
    """Compute the stable effective volume (EV3) of the activation matrix.

    EV3 is computed using SVD in log-space to ensure high numerical stability.
    """
    return compute_stable_ev3(embeddings)


def compute_svcca(X: np.ndarray, Y: np.ndarray) -> float:
    """Compute Singular Vector Canonical Correlation Analysis (SVCCA) between X and Y."""
    X_arr = np.asarray(X, dtype=float)
    Y_arr = np.asarray(Y, dtype=float)
    
    if X_arr.ndim != 2 or Y_arr.ndim != 2:
        raise ValueError("SVCCA inputs must be two-dimensional matrices.")
    if X_arr.shape[0] != Y_arr.shape[0]:
        raise ValueError("SVCCA inputs must have the same number of samples.")
        
    X_centered = X_arr - np.mean(X_arr, axis=0, keepdims=True)
    Y_centered = Y_arr - np.mean(Y_arr, axis=0, keepdims=True)
    
    # SVD for dimensionality reduction
    try:
        U_x, s_x, _ = np.linalg.svd(X_centered, full_matrices=False)
        U_y, s_y, _ = np.linalg.svd(Y_centered, full_matrices=False)
    except np.linalg.LinAlgError:
        return 0.0
        
    # Keep components explaining 99% variance or top 25
    def get_num_components(s, threshold=0.99):
        cum_var = np.cumsum(s**2) / (np.sum(s**2) + 1e-12)
        idx = np.where(cum_var >= threshold)[0]
        if len(idx) > 0:
            return max(1, idx[0] + 1)
        return len(s)
        
    m_x = min(get_num_components(s_x), 25)
    m_y = min(get_num_components(s_y), 25)
    
    X_proj = U_x[:, :m_x] * s_x[:m_x]
    Y_proj = U_y[:, :m_y] * s_y[:m_y]
    
    # QR decomposition to get orthogonal bases
    Q_x, _ = np.linalg.qr(X_proj)
    Q_y, _ = np.linalg.qr(Y_proj)
    
    # Singular values of Q_x^T Q_y are the canonical correlations
    C = Q_x.T @ Q_y
    try:
        s = np.linalg.svd(C, compute_uv=False)
        return float(np.mean(s))
    except Exception:
        return 0.0


def compute_pwcca(X: np.ndarray, Y: np.ndarray) -> float:
    """Compute Projection Weighted Canonical Correlation Analysis (PWCCA) between X and Y."""
    X_arr = np.asarray(X, dtype=float)
    Y_arr = np.asarray(Y, dtype=float)
    
    if X_arr.ndim != 2 or Y_arr.ndim != 2:
        raise ValueError("PWCCA inputs must be two-dimensional matrices.")
    if X_arr.shape[0] != Y_arr.shape[0]:
        raise ValueError("PWCCA inputs must have the same number of samples.")
        
    X_centered = X_arr - np.mean(X_arr, axis=0, keepdims=True)
    Y_centered = Y_arr - np.mean(Y_arr, axis=0, keepdims=True)
    
    try:
        U_x, s_x, _ = np.linalg.svd(X_centered, full_matrices=False)
        U_y, s_y, _ = np.linalg.svd(Y_centered, full_matrices=False)
    except np.linalg.LinAlgError:
        return 0.0
        
    m_x = min(max(1, len(s_x)), 25)
    m_y = min(max(1, len(s_y)), 25)
    
    X_proj = U_x[:, :m_x] * s_x[:m_x]
    Y_proj = U_y[:, :m_y] * s_y[:m_y]
    
    Q_x, _ = np.linalg.qr(X_proj)
    Q_y, _ = np.linalg.qr(Y_proj)
    
    C = Q_x.T @ Q_y
    try:
        L, s, _ = np.linalg.svd(C)
        H = Q_x @ L  # shape (N, m_x)
        
        proj_matrix = H.T @ X_proj
        weights = np.sum(np.abs(proj_matrix), axis=1)
        
        sum_w = np.sum(weights)
        if sum_w <= 1e-12:
            return float(np.mean(s))
            
        w_norm = weights / sum_w
        pwcca_val = np.sum(w_norm * s[:len(w_norm)])
        return float(pwcca_val)
    except Exception:
        return 0.0


