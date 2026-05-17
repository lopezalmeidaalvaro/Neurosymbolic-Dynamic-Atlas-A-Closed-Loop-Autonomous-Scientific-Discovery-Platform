import sympy as sp
from sympy.physics.quantum import Operator, Commutator, qapply
from sympy.physics.quantum.constants import hbar
from sympy import I

def run_qg_engine():
    # Variables and Constants
    G, c, l_P = sp.symbols('G c l_P', real=True, positive=True)
    kappa = 16 * sp.pi * G / c**4
    m = sp.symbols('m', real=True, positive=True)
    
    # ADM Gravity Operators (simplified isotropic)
    q = Operator('q')
    p = Operator('p')
    
    # Matter Operators (Scalar field)
    phi = Operator('phi')
    pi_phi = Operator('pi_phi')
    
    # Commutators
    comm_qp = Commutator(q, p)
    comm_phipi = Commutator(phi, pi_phi)
    
    print(f"[q, p] = i * hbar")
    print(f"[phi, pi_phi] = i * hbar")
    
    # Hamiltonian components
    # We use polynomial forms to avoid inverse fractional powers in commutators if possible
    # But ADM requires q^(-1/2). We'll write it symbolically.
    q_inv_sqrt = Operator('q^{-1/2}')
    q_sqrt = Operator('q^{1/2}')
    
    # Kinetic gravity + Potential gravity
    H_grav = kappa * (p**2 * q_inv_sqrt) - (1/kappa) * q_sqrt
    # Kinetic matter + Potential matter
    H_mat = 0.5 * (pi_phi**2 * q_inv_sqrt + q_sqrt * m**2 * phi**2)
    
    H_total = H_grav + H_mat
    
    print("Hamiltonian ADM (H_total):")
    print(H_total)
    
    # Evaluating constraints at Planck scale q -> l_P^2
    H_planck = H_total.subs(q_sqrt, l_P).subs(q_inv_sqrt, 1/l_P)
    
    print("Hamiltonian Constraint at Planck Scale:")
    print(H_planck)
    
    # Try to calculate [H_grav, H_mat] to check for anomalies
    comm_H = Commutator(H_grav, H_mat)
    print("Commutator [H_grav, H_mat]:")
    print(comm_H)

if __name__ == '__main__':
    run_qg_engine()
