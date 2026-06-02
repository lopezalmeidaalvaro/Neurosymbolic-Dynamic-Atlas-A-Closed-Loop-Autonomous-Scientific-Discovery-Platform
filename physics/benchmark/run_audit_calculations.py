#!/usr/bin/env python3
"""
Targeted Physical Audit Calculations Script for Quantum Gravity Candidates
Author: Antigravity AI
"""

import os
import json
import re
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

# Create directories if they do not exist
os.makedirs("docs", exist_ok=True)
os.makedirs("figures", exist_ok=True)

# Define symbols
r = sp.Symbol('r', positive=True)
M = sp.Symbol('M', positive=True)

def parse_json_results(filepath):
    """
    Parses reproducibility results and extracts Problem C candidate statistics.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    equations = []
    scores = []
    accepted_seeds = []
    
    for run in data:
        seed = run["seed"]
        prob_c = run["problem_C"]
        eq = prob_c["best_equation"]
        eq = eq.replace(" ", "")
        equations.append(eq)
        scores.append(prob_c["score"])
        if prob_c.get("accepted", False):
            accepted_seeds.append(seed)
            
    # Let's count unique equations
    unique_eqs = {}
    for eq, score in zip(equations, scores):
        if eq not in unique_eqs:
            unique_eqs[eq] = {"count": 0, "scores": []}
        unique_eqs[eq]["count"] += 1
        unique_eqs[eq]["scores"].append(score)
        
    # Summarize stats
    stats = []
    for eq, info in unique_eqs.items():
        cnt = info["count"]
        scs = info["scores"]
        stats.append({
            "equation": eq,
            "count": cnt,
            "frequency": (cnt / len(data)) * 100,
            "mean_score": np.mean(scs),
            "max_score": np.max(scs),
            "scores": scs
        })
        
    # Sort by frequency descending
    stats = sorted(stats, key=lambda x: x["count"], reverse=True)
    return stats, accepted_seeds

def analyze_exponential_params(stats):
    """
    Analyzes parametric stability of the exponential family.
    Equation form: A*exp(-B*(r-C)**2)
    """
    pattern = re.compile(r"([0-9.]+)\*exp\(-([0-9.]+)\*\(r-([0-9.]+)\)\*\*2\)")
    a_vals, b_vals, c_vals = [], [], []
    
    for item in stats:
        eq = item["equation"]
        match = pattern.match(eq)
        if match:
            a, b, c_val = map(float, match.groups())
            # Duplicate by count to represent all seeds
            for _ in range(item["count"]):
                a_vals.append(a)
                b_vals.append(b)
                c_vals.append(c_val)
                
    a_vals = np.array(a_vals)
    b_vals = np.array(b_vals)
    c_vals = np.array(c_vals)
    
    return {
        "A": {"mean": np.mean(a_vals), "std": np.std(a_vals), "min": np.min(a_vals), "max": np.max(a_vals)},
        "B": {"mean": np.mean(b_vals), "std": np.std(b_vals), "min": np.min(b_vals), "max": np.max(b_vals)},
        "C": {"mean": np.mean(c_vals), "std": np.std(c_vals), "min": np.min(c_vals), "max": np.max(c_vals)}
    }

def calculate_invariants(f_expr):
    """
    Computes Ricci scalar R(r) and Kretschmann K(r) using sympy.
    Metric: ds^2 = -A dt^2 + A^-1 dr^2 + r^2 dOmega^2 with A = 1 - 2*M*f(r)/r
    """
    M_val = 1.0
    f_sub = f_expr.subs(M, M_val)
    A = 1 - 2 * M_val * f_sub / r
    
    # Derivatives
    df = sp.diff(f_sub, r)
    d2f = sp.diff(df, r)
    
    # Ricci scalar: R = 2*M/r^2 * (r*f'' + 2*f')
    R = (2 * M_val / r**2) * (r * d2f + 2 * df)
    R = sp.simplify(R)
    
    # Kretschmann scalar: K = A''^2 + 4 A'^2/r^2 + 4 (1-A)^2/r^4
    dA = sp.diff(A, r)
    d2A = sp.diff(dA, r)
    K = d2A**2 + 4 * dA**2 / r**2 + 4 * (1 - A)**2 / r**4
    K = sp.simplify(K)
    
    # Limits as r -> 0
    R_0 = sp.limit(R, r, 0)
    K_0 = sp.limit(K, r, 0)
    A_0 = sp.limit(A, r, 0)
    
    # Limits as r -> inf
    R_inf = sp.limit(R, r, sp.oo)
    K_inf = sp.limit(K, r, sp.oo)
    A_inf = sp.limit(A, r, sp.oo)
    
    return {
        "A_expr": A,
        "R_expr": R,
        "K_expr": K,
        "limits_0": {"A": A_0, "R": R_0, "K": K_0},
        "limits_inf": {"A": A_inf, "R": R_inf, "K": K_inf}
    }

def analyze_horizons(A_expr):
    """
    Finds roots of A(r) = 0 for r > 0.
    """
    A_func = sp.lambdify(r, A_expr, 'numpy')
    
    # Search grid
    r_grid = np.linspace(0.01, 10.0, 1000)
    A_vals = A_func(r_grid)
    
    # Identify sign changes
    sign_changes = np.where(np.diff(np.sign(A_vals)))[0]
    roots = []
    for idx in sign_changes:
        r_start = r_grid[idx]
        r_end = r_grid[idx+1]
        try:
            root = fsolve(A_func, 0.5 * (r_start + r_end))[0]
            if root > 0 and not any(abs(root - existing) < 1e-4 for existing in roots):
                roots.append(float(root))
        except Exception:
            pass
            
    roots = sorted(roots)
    return roots

def analyze_thermodynamics(A_expr, roots):
    """
    Computes superficial gravity, Hawking temperature, and Bekenstein-Hawking entropy.
    """
    dA_expr = sp.diff(A_expr, r)
    dA_func = sp.lambdify(r, dA_expr, 'numpy')
    
    results = []
    for r_h in roots:
        # Superficial gravity: kappa = 1/2 * dA/dr |r=rh
        kappa = 0.5 * dA_func(r_h)
        # Hawking Temperature: T_H = kappa / (2*pi)
        T_H = kappa / (2 * np.pi)
        # Entropy: S = pi * r_h^2
        S = np.pi * r_h**2
        
        # local heat capacity C = dM/dT_H
        # Let's derive it numerically near the horizon
        # For a small change in mass dM, the horizon changes.
        # We can write: T_H = f(r_h, M) and A(r_h, M) = 0
        # Let's calculate C as dM/dT_H numerically.
        # At r_h: M(r_h) = r_h / (2 * f(r_h))
        # So dM/dr_h = 1/(2*f) - r_h * f' / (2 * f^2)
        # And dT_H/dr_h can be calculated.
        # C = (dM/dr_h) / (dT_H/dr_h)
        results.append({
            "r_h": r_h,
            "kappa": float(kappa),
            "T_H": float(T_H),
            "S": float(S)
        })
    return results

def evaluate_energy_conditions(f_expr):
    """
    Evaluates NEC, WEC, SEC, DEC for a candidate.
    rho = M * f'(r) / (4*pi*r^2)
    p_r = -rho
    p_theta = -M * f''(r) / (8*pi*r)
    """
    df = sp.diff(f_expr, r)
    d2f = sp.diff(df, r)
    
    rho = df / (4 * sp.pi * r**2)
    p_r = -rho
    p_theta = -d2f / (8 * sp.pi * r)
    
    rho_func = sp.lambdify(r, rho, 'numpy')
    pr_func = sp.lambdify(r, p_r, 'numpy')
    pth_func = sp.lambdify(r, p_theta, 'numpy')
    
    r_vals = np.linspace(0.01, 5.0, 500)
    rhos = rho_func(r_vals)
    prs = pr_func(r_vals)
    pths = pth_func(r_vals)
    
    nec1 = rhos + prs # always 0
    nec2 = rhos + pths
    wec1 = rhos
    wec2 = rhos + pths
    sec1 = rhos + prs + 2 * pths # = 2 * pths
    dec1 = rhos - np.abs(prs) # always 0
    dec2 = rhos - np.abs(pths)
    
    # Find violation regions
    nec_violated = r_vals[nec2 < -1e-5]
    wec_violated = r_vals[(wec1 < -1e-5) | (wec2 < -1e-5)]
    sec_violated = r_vals[(nec2 < -1e-5) | (sec1 < -1e-5)]
    dec_violated = r_vals[dec2 < -1e-5]
    
    return {
        "r_vals": r_vals,
        "rho": rhos,
        "p_r": prs,
        "p_theta": pths,
        "nec_violated": list(nec_violated),
        "wec_violated": list(wec_violated),
        "sec_violated": list(sec_violated),
        "dec_violated": list(dec_violated)
    }

def main():
    print("[*] Running Targeted Physical Audit Calculations...")
    
    # 1. Parse JSON Results
    stats, accepted_seeds = parse_json_results("physics/benchmark/reproducibility_improved_30.json")
    print(f"[+] Parsed {len(stats)} unique equations.")
    print(f"[+] Accepted seeds: {accepted_seeds}")
    
    # Write Candidate Selection Report data
    print("[*] Selected candidates:")
    # Candidate 1: Hayward-type
    c1_eq = "r**3/(r**3+1.5)"
    c1_sym = r**3 / (r**3 + 1.5)
    # Candidate 2: Gaussian
    c2_eq = "0.535*exp(-0.196*(r-1.612)**2)"
    c2_sym = 0.535 * sp.exp(-0.196 * (r - 1.612)**2)
    # Candidate 3: Quadratic
    c3_eq = "0.891/(1+0.012*r**2)"
    c3_sym = 0.891 / (1 + 0.012 * r**2)
    
    # Compute parametric stability of exponential family
    exp_params = analyze_exponential_params(stats)
    print(f"[+] Exponential family parameters: {exp_params}")
    
    # 2. Curvature Invariants analysis
    c1_inv = calculate_invariants(c1_sym)
    c2_inv = calculate_invariants(c2_sym)
    c3_inv = calculate_invariants(c3_sym)
    
    print("\n--- CURVATURE INVARIANTS ANALYSIS ---")
    for name, inv in [("Candidate 1 (Hayward)", c1_inv), ("Candidate 2 (Gaussian)", c2_inv), ("Candidate 3 (Quadratic)", c3_inv)]:
        print(f"\n{name}:")
        print(f"  Limit r->0 of A: {inv['limits_0']['A']}")
        print(f"  Limit r->0 of R: {inv['limits_0']['R']}")
        print(f"  Limit r->0 of K: {inv['limits_0']['K']}")
        print(f"  Limit r->inf of A: {inv['limits_inf']['A']}")
        print(f"  Limit r->inf of R: {inv['limits_inf']['R']}")
        print(f"  Limit r->inf of K: {inv['limits_inf']['K']}")
        
    # 3. Horizon Audit
    c1_roots = analyze_horizons(c1_inv["A_expr"])
    c2_roots = analyze_horizons(c2_inv["A_expr"])
    c3_roots = analyze_horizons(c3_inv["A_expr"])
    
    print("\n--- HORIZON AUDIT ---")
    print(f"Candidate 1 horizons: {c1_roots}")
    print(f"Candidate 2 horizons: {c2_roots}")
    print(f"Candidate 3 horizons: {c3_roots}")
    
    # 4. Thermodynamic Audit
    c1_thermo = analyze_thermodynamics(c1_inv["A_expr"], c1_roots)
    c2_thermo = analyze_thermodynamics(c2_inv["A_expr"], c2_roots)
    c3_thermo = analyze_thermodynamics(c3_inv["A_expr"], c3_roots)
    
    print("\n--- THERMODYNAMIC AUDIT ---")
    print(f"Candidate 1 thermo: {c1_thermo}")
    print(f"Candidate 2 thermo: {c2_thermo}")
    print(f"Candidate 3 thermo: {c3_thermo}")
    
    # 5. Energy Conditions Audit
    c1_energy = evaluate_energy_conditions(c1_sym)
    c2_energy = evaluate_energy_conditions(c2_sym)
    c3_energy = evaluate_energy_conditions(c3_sym)
    
    print("\n--- ENERGY CONDITIONS AUDIT (Violations) ---")
    for name, energy in [("Candidate 1", c1_energy), ("Candidate 2", c2_energy), ("Candidate 3", c3_energy)]:
        print(f"\n{name}:")
        print(f"  NEC violated at r in: {energy['nec_violated'][:5]}... (length: {len(energy['nec_violated'])})")
        print(f"  WEC violated at r in: {energy['wec_violated'][:5]}... (length: {len(energy['wec_violated'])})")
        print(f"  SEC violated at r in: {energy['sec_violated'][:5]}... (length: {len(energy['sec_violated'])})")
        print(f"  DEC violated at r in: {energy['dec_violated'][:5]}... (length: {len(energy['dec_violated'])})")

    # 6. Comparative Analysis
    # Let's compare candidates to known metrics: Schwarzschild, Hayward, Bardeen, Dymnikova
    # Hayward: A = 1 - 2*M*r^2/(r^3 + 2*M*l^2). For M=1, l=sqrt(0.75), this is 1 - 2*r^2/(r^3 + 1.5).
    # Since our Candidate 1 has f(r) = r^3/(r^3+1.5) ==> A = 1 - 2*f(r)/r = 1 - 2*r^2/(r^3+1.5).
    # Thus Candidate 1 is EXACTLY the Hayward metric with l = sqrt(0.75) approx 0.866.
    
    # Let's compute MSE on [0.01, 10.0] against others
    r_grid = np.linspace(0.01, 10.0, 1000)
    
    # Known metric profiles for M=1
    A_schwarz = 1 - 2.0 / r_grid
    
    # Hayward with M=1, l^2 = 0.75
    A_hayward = 1 - 2.0 * r_grid**2 / (r_grid**3 + 1.5)
    
    # Bardeen with M=1, q = 0.866
    A_bardeen = 1 - 2.0 * r_grid**2 / (r_grid**2 + 0.75)**1.5
    
    # Dymnikova with M=1, l^2 = 0.75
    A_dymnikova = 1 - (2.0 / r_grid) * (1 - np.exp(-r_grid**3 / 1.5))
    
    # Candidate profiles
    A_c1 = 1 - 2.0 * r_grid**2 / (r_grid**3 + 1.5)
    A_c2 = 1 - 2.0 * (0.535 * np.exp(-0.196 * (r_grid - 1.612)**2)) / r_grid
    A_c3 = 1 - 2.0 * (0.891 / (1 + 0.012 * r_grid**2)) / r_grid
    
    mse_results = {}
    for name, c_profile in [("Candidate 1", A_c1), ("Candidate 2", A_c2), ("Candidate 3", A_c3)]:
        mse_results[name] = {
            "Schwarzschild": float(np.mean((c_profile[r_grid >= 2.0] - A_schwarz[r_grid >= 2.0])**2)), # only evaluate outside singularity
            "Hayward": float(np.mean((c_profile - A_hayward)**2)),
            "Bardeen": float(np.mean((c_profile - A_bardeen)**2)),
            "Dymnikova": float(np.mean((c_profile - A_dymnikova)**2))
        }
        
    print("\n--- COMPARATIVE ANALYSIS (MSE) ---")
    print(json.dumps(mse_results, indent=4))
    
    # 7. Generate Scientific Figures
    # Figure 1: Metric g_tt Profile Comparison
    plt.figure(figsize=(10, 6))
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    plt.plot(r_grid, -A_c1, label=r"Candidato 1: Hayward ($g_{tt}$)", color="#0f766e", linewidth=2.5)
    plt.plot(r_grid, -A_c2, label=r"Candidato 2: Gaussian ($g_{tt}$)", color="#b45309", linewidth=2.0, linestyle="--")
    plt.plot(r_grid, -A_c3, label=r"Candidato 3: Quadratic ($g_{tt}$)", color="#4338ca", linewidth=2.0, linestyle="-.")
    plt.plot(r_grid, -A_schwarz, label="Schwarzschild clásico", color="#be123c", linewidth=1.5, linestyle=":")
    plt.ylim(-1.5, 0.5)
    plt.xlim(0.0, 8.0)
    plt.axhline(0, color="black", linewidth=1.0, linestyle="-")
    plt.xlabel("Radio r (Unidades de Planck)", fontsize=12)
    plt.ylabel(r"Componente Métrica $g_{tt}(r)$", fontsize=12)
    plt.title("Perfiles Métricos de los Candidatos de Gravedad Cuántica (M = 1.0)", fontsize=14, fontweight="bold", pad=15)
    plt.legend(frameon=True, fontsize=10)
    plt.tight_layout()
    plt.savefig("figures/qg_metric_profiles.png", dpi=150)
    plt.close()
    
    # Figure 2: Ricci Curvature Profile
    r_grid_near = np.linspace(0.01, 3.0, 500)
    R_c1_func = sp.lambdify(r, c1_inv["R_expr"], 'numpy')
    R_c2_func = sp.lambdify(r, c2_inv["R_expr"], 'numpy')
    R_c3_func = sp.lambdify(r, c3_inv["R_expr"], 'numpy')
    
    plt.figure(figsize=(10, 6))
    plt.plot(r_grid_near, R_c1_func(r_grid_near), label="Candidato 1: Hayward", color="#0f766e", linewidth=2.5)
    plt.plot(r_grid_near, R_c2_func(r_grid_near), label="Candidato 2: Gaussian", color="#b45309", linewidth=2.0, linestyle="--")
    plt.plot(r_grid_near, R_c3_func(r_grid_near), label="Candidato 3: Quadratic", color="#4338ca", linewidth=2.0, linestyle="-.")
    plt.plot(r_grid_near, 4.0 / r_grid_near**3, label="Schwarzschild clásica (Divergente)", color="#be123c", linewidth=1.5, linestyle=":")
    plt.ylim(-10, 30)
    plt.xlim(0.0, 3.0)
    plt.xlabel("Radio r (Unidades de Planck)", fontsize=12)
    plt.ylabel("Ricci Escalar R(r)", fontsize=12)
    plt.title("Resolución de la Singularidad de Curvatura (M = 1.0)", fontsize=14, fontweight="bold", pad=15)
    plt.legend(frameon=True, fontsize=10)
    plt.tight_layout()
    plt.savefig("figures/qg_curvature_profiles.png", dpi=150)
    plt.close()
    
    # Figure 3: Kretschmann Invariant
    K_c1_func = sp.lambdify(r, c1_inv["K_expr"], 'numpy')
    K_c2_func = sp.lambdify(r, c2_inv["K_expr"], 'numpy')
    K_c3_func = sp.lambdify(r, c3_inv["K_expr"], 'numpy')
    
    plt.figure(figsize=(10, 6))
    plt.plot(r_grid_near, K_c1_func(r_grid_near), label="Candidato 1: Hayward", color="#0f766e", linewidth=2.5)
    plt.plot(r_grid_near, K_c2_func(r_grid_near), label="Candidato 2: Gaussian", color="#b45309", linewidth=2.0, linestyle="--")
    plt.plot(r_grid_near, K_c3_func(r_grid_near), label="Candidato 3: Quadratic", color="#4338ca", linewidth=2.0, linestyle="-.")
    plt.plot(r_grid_near, 48.0 / r_grid_near**6, label="Schwarzschild clásica (K ~ 1/r^6)", color="#be123c", linewidth=1.5, linestyle=":")
    plt.yscale("log")
    plt.ylim(1e-2, 1e6)
    plt.xlim(0.0, 3.0)
    plt.xlabel("Radio r (Unidades de Planck)", fontsize=12)
    plt.ylabel("Kretschmann Escalar K(r) (Escala Logarítmica)", fontsize=12)
    plt.title("Invariante de Kretschmann a Corta Distancia (M = 1.0)", fontsize=14, fontweight="bold", pad=15)
    plt.legend(frameon=True, fontsize=10)
    plt.tight_layout()
    plt.savefig("figures/qg_kretschmann_profiles.png", dpi=150)
    plt.close()

    # Save results to JSON file
    results = {
        "parsing": {
            "unique_equations_count": len(stats),
            "accepted_seeds": accepted_seeds,
            "exponential_parametric_stability": exp_params
        },
        "candidates": {
            "candidate_1": {
                "eq": c1_eq,
                "limits_r0": {
                    "g_tt": float(-c1_inv["limits_0"]["A"].evalf()),
                    "R": float(c1_inv["limits_0"]["R"].evalf()),
                    "K": float(c1_inv["limits_0"]["K"].evalf())
                },
                "limits_rinf": {
                    "g_tt": float(-c1_inv["limits_inf"]["A"].evalf()),
                    "R": float(c1_inv["limits_inf"]["R"].evalf()),
                    "K": float(c1_inv["limits_inf"]["K"].evalf())
                },
                "horizons": c1_roots,
                "thermo": c1_thermo,
                "energy_violations": {
                    "nec": len(c1_energy["nec_violated"]),
                    "wec": len(c1_energy["wec_violated"]),
                    "sec": len(c1_energy["sec_violated"]),
                    "dec": len(c1_energy["dec_violated"])
                }
            },
            "candidate_2": {
                "eq": c2_eq,
                "limits_r0": {
                    "g_tt": float(-c2_inv["limits_0"]["A"].evalf()),
                    "R": float(c2_inv["limits_0"]["R"].evalf()),
                    "K": float(c2_inv["limits_0"]["K"].evalf())
                },
                "limits_rinf": {
                    "g_tt": float(-c2_inv["limits_inf"]["A"].evalf()),
                    "R": float(c2_inv["limits_inf"]["R"].evalf()),
                    "K": float(c2_inv["limits_inf"]["K"].evalf())
                },
                "horizons": c2_roots,
                "thermo": c2_thermo,
                "energy_violations": {
                    "nec": len(c2_energy["nec_violated"]),
                    "wec": len(c2_energy["wec_violated"]),
                    "sec": len(c2_energy["sec_violated"]),
                    "dec": len(c2_energy["dec_violated"])
                }
            },
            "candidate_3": {
                "eq": c3_eq,
                "limits_r0": {
                    "g_tt": float(-c3_inv["limits_0"]["A"].evalf()),
                    "R": float(c3_inv["limits_0"]["R"].evalf()),
                    "K": float(c3_inv["limits_0"]["K"].evalf())
                },
                "limits_rinf": {
                    "g_tt": float(-c3_inv["limits_inf"]["A"].evalf()),
                    "R": float(c3_inv["limits_inf"]["R"].evalf()),
                    "K": float(c3_inv["limits_inf"]["K"].evalf())
                },
                "horizons": c3_roots,
                "thermo": c3_thermo,
                "energy_violations": {
                    "nec": len(c3_energy["nec_violated"]),
                    "wec": len(c3_energy["wec_violated"]),
                    "sec": len(c3_energy["sec_violated"]),
                    "dec": len(c3_energy["dec_violated"])
                }
            }
        },
        "mse_comparison": mse_results
    }
    
    with open("physics/benchmark/audit_numerical_results.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print("[+] Calculations finished successfully. Saved results to physics/benchmark/audit_numerical_results.json")

if __name__ == "__main__":
    main()
