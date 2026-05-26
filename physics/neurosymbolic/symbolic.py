"""Sparse symbolic recovery utilities."""

from __future__ import annotations

import numpy as np


def build_linear_library(
    x: np.ndarray, feature_names: list[str] | None = None
) -> tuple[np.ndarray, list[str]]:
    """Build a constant-plus-linear SINDy feature library.

    Args:
        x: State matrix with shape ``(n_samples, n_features)``.
        feature_names: Optional names for the state variables.

    Returns:
        Tuple ``(theta, names)`` containing the feature matrix and term names.

    Raises:
        ValueError: If ``x`` is not two-dimensional or names do not match.
    """
    x_arr = np.asarray(x, dtype=float)
    if x_arr.ndim != 2:
        raise ValueError("x must be a two-dimensional matrix.")
    if feature_names is None:
        feature_names = [f"x{i}" for i in range(x_arr.shape[1])]
    if len(feature_names) != x_arr.shape[1]:
        raise ValueError("feature_names length must match x.shape[1].")

    theta = np.column_stack([np.ones(x_arr.shape[0]), x_arr])
    return theta, ["1", *feature_names]


def recover_sindy_coefficients(
    x: np.ndarray,
    dxdt: np.ndarray,
    feature_names: list[str] | None = None,
    threshold: float = 1e-6,
) -> dict[str, float]:
    """Recover sparse linear SINDy coefficients by least squares thresholding.

    Args:
        x: State matrix with shape ``(n_samples, n_features)``.
        dxdt: Target derivative vector with shape ``(n_samples,)``.
        feature_names: Optional names for the state variables.
        threshold: Absolute coefficient threshold for sparsification.

    Returns:
        Mapping from library term name to recovered coefficient.

    Raises:
        ValueError: If shapes are incompatible or threshold is negative.
        np.linalg.LinAlgError: If the least-squares solve fails.
    """
    if threshold < 0:
        raise ValueError("threshold must be non-negative.")

    y = np.asarray(dxdt, dtype=float)
    if y.ndim != 1:
        raise ValueError("dxdt must be a one-dimensional vector.")

    theta, names = build_linear_library(x, feature_names)
    if theta.shape[0] != y.shape[0]:
        raise ValueError("x and dxdt must have matching sample counts.")

    coefficients, *_ = np.linalg.lstsq(theta, y, rcond=None)
    coefficients[np.abs(coefficients) < threshold] = 0.0
    return {name: float(value) for name, value in zip(names, coefficients)}
