import numpy as np
import pytest

def test_rqb_ckm_mixing_angles_and_parameters():
    # RQB base parameters
    Xi_RQB = np.pi * np.sqrt(3)
    beta_mix = 0.25
    delta_topo = np.pi / 15.0

    # Derived Wolfenstein CKM parameter formulations
    lambda_c = np.exp(-1.5)
    A = np.pi**2 / 12.0
    delta_cp = 5.5 * delta_topo
    rho_bar = np.sin(2.0 * delta_topo) * np.cos(delta_cp)
    eta_bar = np.sin(2.0 * delta_topo) * np.sin(delta_cp)

    # Angle predictions in degrees
    theta_12_deg = np.degrees(np.arcsin(lambda_c))
    theta_23_deg = np.degrees(np.arcsin(A * lambda_c**2))
    theta_13_deg = np.degrees(np.arcsin(A * lambda_c**3 * np.sin(2.0 * delta_topo)))
    delta_cp_deg = np.degrees(delta_cp)

    assert np.isclose(lambda_c, 0.223130, atol=1e-5)
    assert np.isclose(A, 0.822467, atol=1e-5)
    assert np.isclose(rho_bar, 0.165435, atol=1e-5)
    assert np.isclose(eta_bar, 0.371572, atol=1e-5)
    assert np.isclose(theta_12_deg, 12.8929, atol=1e-2)
    assert np.isclose(theta_23_deg, 2.3468, atol=1e-2)
    assert np.isclose(theta_13_deg, 0.2129, atol=1e-2)
    assert np.isclose(delta_cp_deg, 66.0, atol=1e-2)


def test_ckm_matrix_elements_and_unitarity():
    lambda_c = np.exp(-1.5)
    A = np.pi**2 / 12.0
    delta_topo = np.pi / 15.0
    delta_cp = 5.5 * delta_topo

    theta_12 = np.arcsin(lambda_c)
    theta_23 = np.arcsin(A * lambda_c**2)
    theta_13 = np.arcsin(A * lambda_c**3 * np.sin(2.0 * delta_topo))

    c12, s12 = np.cos(theta_12), np.sin(theta_12)
    c23, s23 = np.cos(theta_23), np.sin(theta_23)
    c13, s13 = np.cos(theta_13), np.sin(theta_13)

    # Unitary CKM parametrization
    V_ud = c12 * c13
    V_us = s12 * c13
    V_ub = s13 * np.exp(-1j * delta_cp)

    V_cd = -s12 * c23 - c12 * s23 * s13 * np.exp(1j * delta_cp)
    V_cs = c12 * c23 - s12 * s23 * s13 * np.exp(1j * delta_cp)
    V_cb = s23 * c13

    V_td = s12 * s23 - c12 * c23 * s13 * np.exp(1j * delta_cp)
    V_ts = -c12 * s23 - s12 * c23 * s13 * np.exp(1j * delta_cp)
    V_tb = c23 * c13

    V = np.array([
        [V_ud, V_us, V_ub],
        [V_cd, V_cs, V_cb],
        [V_td, V_ts, V_tb]
    ])

    # Assert matrix magnitudes match derived values exactly
    assert np.isclose(np.abs(V[0, 0]), 0.974782, atol=1e-4) # V_ud
    assert np.isclose(np.abs(V[0, 1]), 0.223129, atol=1e-4) # V_us
    assert np.isclose(np.abs(V[0, 2]), 0.003716, atol=1e-4) # V_ub
    assert np.isclose(np.abs(V[1, 2]), 0.040948, atol=1e-4) # V_cb
    assert np.isclose(np.abs(V[2, 0]), 0.008347, atol=1e-4) # V_td
    assert np.isclose(np.abs(V[2, 1]), 0.040260, atol=1e-4) # V_ts
    assert np.isclose(np.abs(V[2, 2]), 0.999154, atol=1e-4) # V_tb

    # Verify strict matrix unitarity (V * V^dagger = I)
    identity_check = np.dot(V, V.conj().T)
    assert np.allclose(identity_check, np.identity(3), atol=1e-7)


def test_quark_jarlskog_invariant():
    lambda_c = np.exp(-1.5)
    A = np.pi**2 / 12.0
    delta_topo = np.pi / 15.0
    delta_cp = 5.5 * delta_topo

    theta_12 = np.arcsin(lambda_c)
    theta_23 = np.arcsin(A * lambda_c**2)
    theta_13 = np.arcsin(A * lambda_c**3 * np.sin(2.0 * delta_topo))

    c12, s12 = np.cos(theta_12), np.sin(theta_12)
    c23, s23 = np.cos(theta_23), np.sin(theta_23)
    c13, s13 = np.cos(theta_13), np.sin(theta_13)

    # Jarlskog CP invariant formulation
    J_cp = c12 * s12 * c23 * s23 * c13**2 * s13 * np.sin(delta_cp)
    assert np.isclose(J_cp, 3.021135e-05, atol=1e-8)


def test_meson_oscillation_ratio():
    lambda_c = np.exp(-1.5)
    A = np.pi**2 / 12.0
    delta_topo = np.pi / 15.0
    delta_cp = 5.5 * delta_topo

    theta_12 = np.arcsin(lambda_c)
    theta_23 = np.arcsin(A * lambda_c**2)
    theta_13 = np.arcsin(A * lambda_c**3 * np.sin(2.0 * delta_topo))

    c12, s12 = np.cos(theta_12), np.sin(theta_12)
    c23, s23 = np.cos(theta_23), np.sin(theta_23)
    c13, s13 = np.cos(theta_13), np.sin(theta_13)

    V_td = s12 * s23 - c12 * c23 * s13 * np.exp(1j * delta_cp)
    V_ts = -c12 * s23 - s12 * c23 * s13 * np.exp(1j * delta_cp)

    ratio = np.abs(V_td / V_ts)**2
    assert np.isclose(ratio, 0.042989, atol=1e-5)
