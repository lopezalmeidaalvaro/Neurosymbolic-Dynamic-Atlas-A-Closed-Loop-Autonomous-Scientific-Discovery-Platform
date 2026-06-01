#!/usr/bin/env python3
"""
Phase 3: SymPy-Driven Physical Theory Critic Agent (TheoryCritic)
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

class TheoryVerdict:
    def __init__(self, verdict, wec_violation=0.0, singularities=None, analytical_energy=0.0):
        self.verdict = verdict  # ACCEPTED, REJECTED, REQUIRES_MODIFICATION
        self.wec_violation = wec_violation
        self.singularities = singularities if singularities is not None else []
        self.analytical_energy = analytical_energy

class TheoryCritic:
    """
    TheoryCritic Agent: Validates that symbolic metric hypotheses satisfy boundary conditions, 
    energy conditions, and remain free of mathematical singularities.
    """
    def __init__(self, r0=0.5, allow_singularities=False):
        self.r0 = r0  # Throat or bubble center coordinate
        self.allow_singularities = allow_singularities
        self.r_sym = sp.Symbol('r', positive=True)
        self.r0_sym = sp.Symbol('r_0', positive=True)

    def validate(self, hypothesis):
        """
        Parses a Hypothesis and evaluates its physical consistency analytically.
        """
        expr_str = hypothesis.expression
        metric_type = hypothesis.metric_type
        
        # Safe preprocessing of mathematical symbols for SymPy
        expr_str = expr_str.replace("b(r)=", "").replace("f(r)=", "")
        expr_str = expr_str.replace("exp", "sp.exp").replace("tanh", "sp.tanh").replace("sin", "sp.sin")
        
        # Add support for implicit multiplications
        transformations = standard_transformations + (implicit_multiplication_application,)
        
        try:
            # Parse into SymPy object
            # We map local namespace variables so Sp recognizes 'r_0' and functions
            local_ns = {'r': self.r_sym, 'r_0': self.r0_sym, 'sp': sp, 'sigmoid': lambda x: 1.0 / (1.0 + sp.exp(-x))}
            expr_sym = parse_expr(expr_str, local_dict=local_ns, transformations=transformations)
            
            # Substitute r_0 with its actual numerical value (e.g. 0.5)
            expr_num = expr_sym.subs(self.r0_sym, self.r0)
            
            # 1. Compute symbolic derivatives
            df_dr = sp.diff(expr_num, self.r_sym)
            d2f_dr2 = sp.diff(df_dr, self.r_sym)
            
            singularities = []
            wec_violation = 0.0
            analytical_energy = 0.0
            
            # Setup numerical grid evaluation in LEO domain [0.5, 1.5]
            r_grid = np.linspace(0.5, 1.5, 100)
            
            # 2. Check metric boundary and physical conditions
            if metric_type == "wormhole":
                # A. Throat condition: b(r0) = r0
                b_r0 = float(expr_num.subs(self.r_sym, self.r0).evalf())
                if abs(b_r0 - self.r0) > 0.15:
                    print(f"    [-] TheoryCritic: Garganta cerrada. b(r0)={b_r0:.4f} != r0={self.r0}")
                    return TheoryVerdict("REJECTED", wec_violation=0.0, singularities=["Throat Closed"])
                
                # B. Flaring-out condition: b'(r0) < 1.0 (Throat stability)
                db_dr0 = float(df_dr.subs(self.r_sym, self.r0).evalf())
                if db_dr0 >= 1.0:
                    print(f"    [-] TheoryCritic: Falla flaring-out. b'(r0)={db_dr0:.4f} >= 1.0")
                    return TheoryVerdict("REJECTED", wec_violation=0.0, singularities=["Flaring-out failed"])
                
                # C. Energy conditions: compute energy density rho = b'(r) / (8 * pi * r^2)
                # Check for WEC violation magnitude
                rho_vals = []
                for val in r_grid:
                    db = float(df_dr.subs(self.r_sym, val).evalf())
                    rho = db / (8.0 * np.pi * (val**2))
                    rho_vals.append(rho)
                    # Check singularity
                    if np.isnan(rho) or np.isinf(rho):
                        singularities.append(f"Infinity/NaN at r={val:.4f}")
                        
                rho_vals = np.array(rho_vals)
                # WEC violation is the maximum negative energy density
                wec_violation = float(abs(min(0.0, np.min(rho_vals))))
                
                # Analytical energy indicator (integral of square gradient)
                # E = integral of (db/dr)^2 dr from r0 to 1.5
                integrand = df_dr ** 2
                analytical_energy = float(sp.Integral(integrand, (self.r_sym, self.r0, 1.5)).evalf())
                
            elif metric_type == "warp":
                # Boundary conditions: f(0) = 1.0, f(1.0) = 0.0
                f_0 = float(expr_num.subs(self.r_sym, 0.0).evalf())
                f_1 = float(expr_num.subs(self.r_sym, 1.0).evalf())
                
                if abs(f_0 - 1.0) >= 1e-2 or abs(f_1 - 0.0) >= 1e-2:
                    print(f"    [-] TheoryCritic: Fallo condiciones de borde f(0)={f_0:.3f}, f(1)={f_1:.3f}")
                    return TheoryVerdict("REJECTED", wec_violation=0.0, singularities=["Boundary conditions failed"])
                
                # Check singularities in domain
                for val in np.linspace(0.0, 1.0, 100):
                    f_val = float(expr_num.subs(self.r_sym, val).evalf())
                    if np.isnan(f_val) or np.isinf(f_val):
                        singularities.append(f"Infinity/NaN at r={val:.4f}")
                
                # Warp total energy integral of (df/dr)^2
                integrand = df_dr ** 2
                analytical_energy = float(sp.Integral(integrand, (self.r_sym, 0.0, 1.0)).evalf())
                
            elif metric_type == "black_hole":
                # Regularized black hole metric: f(r) correction term where f(0) = 0 and f(inf) = 1
                f_0 = float(expr_num.subs(self.r_sym, 0.0).evalf())
                if abs(f_0) >= 1e-2:
                    print(f"    [-] TheoryCritic: Singuralidad en r=0 no controlada. f(0)={f_0:.4f} != 0")
                    return TheoryVerdict("REJECTED", wec_violation=0.0, singularities=["Singularity at r=0 not regularized"])
                
                # Check limit at infinity: f(r) -> 1
                try:
                    f_inf = float(sp.limit(expr_num, self.r_sym, sp.oo).evalf())
                    if abs(f_inf - 1.0) >= 1e-1:
                        print(f"    [-] TheoryCritic: No recupera Schwarzschild en infinito. f(inf)={f_inf:.4f} != 1.0")
                        return TheoryVerdict("REJECTED", wec_violation=0.0, singularities=["Asymptotic limit failed"])
                except Exception:
                    pass # Ignore limit calculation error if too complex, rely on domain check
                
                # Compute Ricci scalar curvature: R = (2*M/r**2) * (r*d2f/dr2 + 2*df/dr)
                M = 1.0
                R_expr = (2 * M / (self.r_sym ** 2)) * (self.r_sym * d2f_dr2 + 2 * df_dr)
                
                # Analytical limit of R(r) as r -> 0
                try:
                    R_at_0 = sp.limit(R_expr, self.r_sym, 0)
                    if R_at_0 in [sp.oo, -sp.oo, sp.nan] or not R_at_0.is_finite:
                        print(f"    [-] TheoryCritic: Curvatura escalar diverge en r=0: R(0) = {R_at_0}")
                        return TheoryVerdict("REJECTED", wec_violation=0.0, singularities=["Curvature diverges at r=0"])
                    analytical_energy = float(R_at_0.evalf())
                except Exception as limit_err:
                    # If sympy limit fails due to complexity, check numerically at very small r
                    try:
                        r_epsilon = 1e-5
                        R_val = float(R_expr.subs(self.r_sym, r_epsilon).evalf())
                        if np.isnan(R_val) or np.isinf(R_val) or abs(R_val) > 1e4:
                            print(f"    [-] TheoryCritic: Curvatura escalar diverge en epsilon. R(eps) = {R_val:.2f}")
                            return TheoryVerdict("REJECTED", wec_violation=0.0, singularities=["Numerical curvature divergence"])
                        analytical_energy = R_val
                    except Exception:
                        return TheoryVerdict("REJECTED", wec_violation=0.0, singularities=["Curvature expression evaluation failed"])
                
                # Ensure no other division by zero in domain [0, 3]
                for val in np.linspace(0.01, 3.0, 100):
                    f_val = float(expr_num.subs(self.r_sym, val).evalf())
                    if np.isnan(f_val) or np.isinf(f_val):
                        singularities.append(f"NaN/Inf in metric at r={val:.4f}")
            
            # 3. Compile Verdict
            if singularities and not self.allow_singularities:
                print(f"    [-] TheoryCritic: Singularidades detectadas: {singularities}")
                return TheoryVerdict("REJECTED", wec_violation, singularities, analytical_energy)
                
            print(f"    [+] TheoryCritic: Validacion exitosa. WEC Violation={wec_violation:.4f} | E_analitica={analytical_energy:.4f}")
            return TheoryVerdict("ACCEPTED", wec_violation, singularities, analytical_energy)
            
        except Exception as e:
            print(f"    [-] TheoryCritic: Error de parseo o calculo simbolico: {e}")
            return TheoryVerdict("REJECTED", singularities=["Sympy Parse/Math Error"])

if __name__ == "__main__":
    print("[*] Levantando agente TheoryCritic...")
    critic = TheoryCritic()
    print("[+] Critico configurado con exito.")
    
    # Verify valid wormhole hypothesis
    print("\n--- TEST 1: Hipótesis de garganta estable (Válida) ---")
    h1 = Hypothesis("b(r) = 0.5 * exp(-3.2 * (r - 0.5)**2)", confidence=0.8, metric_type="wormhole")
    v1 = critic.validate(h1)
    print(f" -> Resultado: {v1.verdict} | Singularidades: {v1.singularities}")
    
    # Verify singular hypothesis (division by zero at r=1.0)
    print("\n--- TEST 2: Hipótesis singular (Inválida) ---")
    h2 = Hypothesis("b(r) = 0.5 / (r - 0.5)", confidence=0.5, metric_type="wormhole")
    v2 = critic.validate(h2)
    print(f" -> Resultado: {v2.verdict} | Singularidades: {v2.singularities}")
    print("------------------------------------------------------\n")
