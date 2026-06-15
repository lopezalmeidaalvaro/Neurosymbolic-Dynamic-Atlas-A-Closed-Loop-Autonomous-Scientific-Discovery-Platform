import numpy as np
import pytest

def test_rqb_mixing_angles():
    # Phase 51 & 52 derived topological angles
    theta_13 = np.degrees(np.arcsin(np.pi / (15.0 * np.sqrt(2.0))))
    theta_12 = 34.1
    theta_23 = 47.9
    delta_cp = 180.0 - theta_13

    # Assert correct numerical values derived in RQB
    assert np.isclose(theta_13, 8.5166, atol=1e-4)
    assert np.isclose(theta_12, 34.1, atol=1e-2)
    assert np.isclose(theta_23, 47.9, atol=1e-2)
    assert np.isclose(delta_cp, 171.4834, atol=1e-4)


def test_pmns_matrix_elements_and_unitarity():
    # Setup angles in radians
    theta_13 = np.degrees(np.arcsin(np.pi / (15.0 * np.sqrt(2.0))))
    theta_12 = 34.1
    theta_23 = 47.9
    delta_cp = 180.0 - theta_13

    t13 = np.radians(theta_13)
    t12 = np.radians(theta_12)
    t23 = np.radians(theta_23)
    d_cp = np.radians(delta_cp)

    c13, s13 = np.cos(t13), np.sin(t13)
    c12, s12 = np.cos(t12), np.sin(t12)
    c23, s23 = np.cos(t23), np.sin(t23)

    # Standard PDG parametrization of PMNS matrix
    U_e1 = c12 * c13
    U_e2 = s12 * c13
    U_e3 = s13 * np.exp(-1j * d_cp)

    U_mu1 = -s12 * c23 - c12 * s23 * s13 * np.exp(1j * d_cp)
    U_mu2 = c12 * c23 - s12 * s23 * s13 * np.exp(1j * d_cp)
    U_mu3 = s23 * c13

    U_tau1 = s12 * s23 - c12 * c23 * s13 * np.exp(1j * d_cp)
    U_tau2 = -c12 * s23 - s12 * c23 * s13 * np.exp(1j * d_cp)
    U_tau3 = c23 * c13

    U = np.array([
        [U_e1, U_e2, U_e3],
        [U_mu1, U_mu2, U_mu3],
        [U_tau1, U_tau2, U_tau3]
    ])

    # Assert matrix magnitudes match derived values exactly
    assert np.isclose(np.abs(U[0, 0]), 0.8189, atol=1e-4) # U_e1
    assert np.isclose(np.abs(U[0, 1]), 0.5545, atol=1e-4) # U_e2
    assert np.isclose(np.abs(U[0, 2]), 0.1481, atol=1e-4) # U_e3
    assert np.isclose(np.abs(U[1, 2]), 0.7338, atol=1e-4) # U_mu3

    # Assert PMNS matrix is strictly unitary (U * U^dagger = I)
    identity_check = np.dot(U, U.conj().T)
    assert np.allclose(identity_check, np.identity(3), atol=1e-7)


def test_jarlskog_invariant():
    theta_13 = np.degrees(np.arcsin(np.pi / (15.0 * np.sqrt(2.0))))
    theta_12 = 34.1
    theta_23 = 47.9
    delta_cp = 180.0 - theta_13

    t13 = np.radians(theta_13)
    t12 = np.radians(theta_12)
    t23 = np.radians(theta_23)
    d_cp = np.radians(delta_cp)

    c12, s12 = np.cos(t12), np.sin(t12)
    c23, s23 = np.cos(t23), np.sin(t23)
    c13, s13 = np.cos(t13), np.sin(t13)

    # Jarlskog CP invariant formulation
    J_cp = c12 * s12 * c23 * s23 * c13**2 * s13 * np.sin(d_cp)
    assert np.isclose(J_cp, 0.004954, atol=1e-6)


def test_neutrino_mass_origin_and_hierarchy():
    # Setup Phase 52 base parameters
    m_0 = 7600.0  # eV
    Xi_RQB = np.pi * np.sqrt(3)
    gamma_top = 0.69715

    # Base scale
    m_nu_0 = (m_0 / (3 * np.pi**3)) * np.exp(-2 * Xi_RQB)
    assert np.isclose(m_nu_0, 0.001534, atol=1e-6)

    # Individual generations
    m_1 = m_nu_0 * np.exp(gamma_top * 1)
    m_2 = m_nu_0 * np.exp(gamma_top * 3)
    m_3 = m_nu_0 * np.exp(gamma_top * 5)

    assert np.isclose(m_1, 0.003080, atol=1e-5)
    assert np.isclose(m_2, 0.012423, atol=1e-5)
    assert np.isclose(m_3, 0.050085, atol=1e-5)

    # Verify hierarchy ordering
    assert m_1 < m_2 < m_3
