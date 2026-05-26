"""Dynamical Fidelity Index (DFI) metric and FitzHugh-Nagumo reference model."""

from __future__ import annotations

import numpy as np
from typing import Callable


def fitzhugh_nagumo_rhs(
    state: np.ndarray,
    t: float = 0.0,
    a: float = 0.7,
    b: float = 0.8,
    tau: float = 12.5,
    I_ext: float = 0.35,
) -> np.ndarray:
    """The FitzHugh-Nagumo reference physiological model of cardiac action potentials.

    Models the excitability of ventricular cells. The variables are:
        state[0]: Membrane potential v (fast depolarization variable).
        state[1]: Recovery variable w (slow repolarization variable).

    Args:
        state: State vector [v, w] with shape (2,).
        t: Time variable (time-invariant system).
        a: Constant related to threshhold activation.
        b: Constant related to recovery rate.
        tau: Temporal time constant (separation of timescales).
        I_ext: External stimulus current.

    Returns:
        State derivatives [dv/dt, dw/dt] as a numpy array.
    """
    v, w = state[0], state[1]
    dv_dt = v - (v**3) / 3.0 - w + I_ext
    dw_dt = (v + a - b * w) / tau
    return np.array([dv_dt, dw_dt], dtype=float)


def dynamical_fidelity_index(
    learned_field: Callable[[np.ndarray], np.ndarray],
    reference_field: Callable[[np.ndarray], np.ndarray],
    grid_points: np.ndarray,
) -> float:
    """Compute the Dynamical Fidelity Index (DFI) of a learned vector field.

    DFI measures the normalized Mean Squared Error (MSE) between the derivative
    predictions of a learned model and a reference physiological model over a
    malla of points in the state space.

    DFI = 1 - MSE(learned, reference) / Variance(reference)

    Args:
        learned_field: Function mapping a state array to its derivative.
        reference_field: Reference ODE right-hand side function.
        grid_points: State space grid points with shape ``(N, dim)``.

    Returns:
        DFI value in the interval [-inf, 1.0]. A value of 1.0 represents perfect
        dynamical alignment.
    """
    N, dim = grid_points.shape
    
    y_learned = np.zeros((N, dim))
    y_ref = np.zeros((N, dim))
    
    for i in range(N):
        y_learned[i] = learned_field(grid_points[i])
        y_ref[i] = reference_field(grid_points[i])
        
    mse = np.mean(np.linalg.norm(y_learned - y_ref, axis=1) ** 2)
    
    ref_mean = np.mean(y_ref, axis=0)
    ref_variance = np.mean(np.linalg.norm(y_ref - ref_mean, axis=1) ** 2)
    
    if ref_variance <= 1e-12:
        return 0.0
        
    dfi = 1.0 - (mse / ref_variance)
    return float(dfi)
