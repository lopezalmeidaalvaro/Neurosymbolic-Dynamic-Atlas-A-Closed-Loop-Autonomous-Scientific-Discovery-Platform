import numpy as np
import pytest

def expm(X):
    # Self-contained matrix exponential via Taylor expansion
    identity = np.eye(X.shape[0], dtype=complex)
    term = identity
    result = identity.copy()
    for n in range(1, 25):
        term = np.dot(term, X) / n
        result += term
    return result

# Pauli matrices
sigma1 = np.array([[0, 1], [1, 0]], dtype=complex)
sigma2 = np.array([[0, -1j], [1j, 0]], dtype=complex)
sigma3 = np.array([[1, 0], [0, -1]], dtype=complex)

# SU(2) generators
T_su2 = [0.5 * sigma1, 0.5 * sigma2, 0.5 * sigma3]

# Gell-Mann matrices
lambda1 = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=complex)
lambda2 = np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=complex)
lambda3 = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=complex)
lambda4 = np.array([[0, 0, 1], [0, 0, 0], [1, 0, 0]], dtype=complex)
lambda5 = np.array([[0, 0, -1j], [0, 0, 0], [1j, 0, 0]], dtype=complex)
lambda6 = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=complex)
lambda7 = np.array([[0, 0, 0], [0, 0, -1j], [0, 1j, 0]], dtype=complex)
lambda8 = (1.0 / np.sqrt(3.0)) * np.array([[1, 0, 0], [0, 1, 0], [0, 0, -2]], dtype=complex)

# SU(3) generators
T_su3 = [
    0.5 * lambda1, 0.5 * lambda2, 0.5 * lambda3,
    0.5 * lambda4, 0.5 * lambda5, 0.5 * lambda6,
    0.5 * lambda7, 0.5 * lambda8
]

# Gell-Mann structure constants f^{abc}
f_abc = np.zeros((8, 8, 8))

# Fill in non-zero independent antisymmetric elements
f_abc[0, 1, 2] = 1.0   # f^{123} = 1
f_abc[0, 3, 6] = 0.5   # f^{147} = 1/2
f_abc[0, 4, 5] = -0.5  # f^{156} = -1/2
f_abc[1, 3, 5] = 0.5   # f^{246} = 1/2
f_abc[1, 4, 6] = 0.5   # f^{257} = 1/2
f_abc[2, 3, 4] = 0.5   # f^{345} = 1/2
f_abc[2, 5, 6] = -0.5  # f^{367} = -1/2
f_abc[3, 4, 7] = np.sqrt(3.0) / 2.0  # f^{458} = sqrt(3)/2
f_abc[5, 6, 7] = np.sqrt(3.0) / 2.0  # f^{678} = sqrt(3)/2

# Enforce full antisymmetry of the structure constants tensor
for a in range(8):
    for b in range(8):
        for c in range(8):
            # Sort indices to check original permutations
            indices = [a, b, c]
            sorted_indices = sorted(indices)
            if sorted_indices == [0, 1, 2]:
                val = 1.0
            elif sorted_indices == [0, 3, 6]:
                val = 0.5
            elif sorted_indices == [0, 4, 5]:
                val = 0.5 if (a, b, c) in [(0, 5, 4), (4, 0, 5), (5, 4, 0)] else -0.5
            elif sorted_indices == [1, 3, 5]:
                val = 0.5
            elif sorted_indices == [1, 4, 6]:
                val = 0.5
            elif sorted_indices == [2, 3, 4]:
                val = 0.5
            elif sorted_indices == [2, 5, 6]:
                val = 0.5 if (a, b, c) in [(2, 6, 5), (5, 2, 6), (6, 5, 2)] else -0.5
            elif sorted_indices == [3, 4, 7]:
                val = np.sqrt(3.0) / 2.0
            elif sorted_indices == [5, 6, 7]:
                val = np.sqrt(3.0) / 2.0
            else:
                val = 0.0

            # Sign is determined by the permutation parity of (a, b, c) relative to the sorted indices
            if val != 0.0:
                # Calculate signature of permutation
                p = [a, b, c]
                sorted_p = sorted(p)
                sign = 1
                if p[0] == sorted_p[1]:
                    if p[1] == sorted_p[0]: sign = -1
                    else: sign = 1 # shift
                elif p[0] == sorted_p[2]:
                    if p[1] == sorted_p[1]: sign = -1
                    else: sign = 1
                else: # p[0] == sorted_p[0]
                    if p[1] == sorted_p[2]: sign = -1
                
                # Correct sign for f_abc[0, 4, 5] and f_abc[2, 5, 6] which already have internal signs
                if sorted_indices == [0, 4, 5] and (a, b, c) in [(0, 4, 5), (4, 5, 0), (5, 0, 4)]:
                    f_abc[a, b, c] = -0.5
                elif sorted_indices == [0, 4, 5]:
                    f_abc[a, b, c] = 0.5
                elif sorted_indices == [2, 5, 6] and (a, b, c) in [(2, 5, 6), (5, 6, 2), (6, 2, 5)]:
                    f_abc[a, b, c] = -0.5
                elif sorted_indices == [2, 5, 6]:
                    f_abc[a, b, c] = 0.5
                else:
                    f_abc[a, b, c] = sign * val


def test_gauge_commutator_su2():
    # Verify [T^a, T^b] = i \epsilon^{abc} T^c
    epsilon = np.zeros((3, 3, 3))
    epsilon[0, 1, 2] = 1.0
    epsilon[1, 2, 0] = 1.0
    epsilon[2, 0, 1] = 1.0
    epsilon[1, 0, 2] = -1.0
    epsilon[2, 1, 0] = -1.0
    epsilon[0, 2, 1] = -1.0

    for a in range(3):
        for b in range(3):
            commutator = np.dot(T_su2[a], T_su2[b]) - np.dot(T_su2[b], T_su2[a])
            expected = 0j
            for c in range(3):
                expected += 1j * epsilon[a, b, c] * T_su2[c]
            assert np.allclose(commutator, expected)


def test_gauge_commutator_su3():
    # Verify [T^a, T^b] = i f^{abc} T^c
    for a in range(8):
        for b in range(8):
            commutator = np.dot(T_su3[a], T_su3[b]) - np.dot(T_su3[b], T_su3[a])
            expected = np.zeros((3, 3), dtype=complex)
            for c in range(8):
                expected += 1j * f_abc[a, b, c] * T_su3[c]
            assert np.allclose(commutator, expected)


def test_plaquette_holonomy_expansion():
    # Spacing limit a and coupling g
    a = 0.05
    g = 2.0

    # Fields in direction x and y (local Lie algebra elements)
    A_x = 0.1 * T_su3[0] + 0.05 * T_su3[2]
    A_y = 0.08 * T_su3[1] - 0.03 * T_su3[3]

    # Infinitesimal link transport operators
    U1 = expm(1j * g * a * A_x)
    U2 = expm(1j * g * a * A_y)
    U3 = expm(-1j * g * a * A_x)
    U4 = expm(-1j * g * a * A_y)

    # Plaquette loop holonomy
    U_plaq = np.dot(np.dot(np.dot(U1, U2), U3), U4)

    # Field strength tensor component F_xy = -i [A_x, A_y] (since derivatives vanish in this flat test)
    F_xy = -1j * (np.dot(A_x, A_y) - np.dot(A_y, A_x))

    # Plaquette approximation
    U_approx = expm(1j * g * a**2 * F_xy)

    # Plaquette expansion should match to order a^3
    assert np.allclose(U_plaq, U_approx, atol=1e-4)


def test_wilson_loop_gauge_invariance():
    # Define arbitrary unitary link variables along a closed loop of length 3
    U1 = expm(1j * (0.1 * T_su2[0] + 0.2 * T_su2[1]))
    U2 = expm(1j * (0.05 * T_su2[1] - 0.15 * T_su2[2]))
    U3 = expm(1j * (0.3 * T_su2[2] + 0.1 * T_su2[0]))

    # Trace of the closed Wilson loop
    wilson_trace = np.trace(np.dot(np.dot(U1, U2), U3))

    # Unitary gauge transformations at each junction
    # Omega_i in SU(2)
    Omega1 = expm(1j * 0.5 * sigma1)
    Omega2 = expm(1j * 0.3 * sigma2)
    Omega3 = expm(1j * 0.8 * sigma3)

    # Gauge-transformed links: U_ij -> Omega_i U_ij Omega_j^dagger
    U1_prime = np.dot(np.dot(Omega1, U1), Omega2.conj().T)
    U2_prime = np.dot(np.dot(Omega2, U2), Omega3.conj().T)
    U3_prime = np.dot(np.dot(Omega3, U3), Omega1.conj().T)

    # Transformed trace
    wilson_trace_prime = np.trace(np.dot(np.dot(U1_prime, U2_prime), U3_prime))

    # Wilson loop trace is gauge-invariant
    assert np.isclose(wilson_trace, wilson_trace_prime, atol=1e-10)
