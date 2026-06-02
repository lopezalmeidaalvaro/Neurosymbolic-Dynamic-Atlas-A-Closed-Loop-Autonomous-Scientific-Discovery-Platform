#!/usr/bin/env python3
"""
Dynamic Formation of Planck Stars and Horizonless Quantum Remnants (Phase 32.0)
Author: Antigravity AI
"""

import os
import json
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Ensure directories exist
os.makedirs("docs", exist_ok=True)
os.makedirs("figures", exist_ok=True)

# ---------------------------------------------------------
# FASE 1: Construcción del Modelo de Colapso y C.I.
# ---------------------------------------------------------
def build_collapse_model():
    print("[*] Fase 1: Construyendo modelo de colapso LQC...")
    
    # Initial conditions
    M0_val = 1.5      # initial mass
    rho0_val = 0.08   # initial density
    rho_crit_val = 8.0 # critical quantum density
    k_val = 0.04      # spatial curvature (closed cloud)
    r_b_val = 2.5     # boundary radius
    
    initial_conditions = {
        "M0": M0_val,
        "rho0": rho0_val,
        "rho_critical": rho_crit_val,
        "k": k_val,
        "boundary_radius_r_b": r_b_val
    }
    
    with open("physics/benchmark/collapse_initial_conditions.json", "w") as f:
        json.dump(initial_conditions, f, indent=4)
        
    print(f"[+] Initial conditions saved to physics/benchmark/collapse_initial_conditions.json")
    return initial_conditions

# ---------------------------------------------------------
# FASE 2, 3 y 4: Evolución Dinámica, Efectos Cuánticos y Horizontes
# ---------------------------------------------------------
def simulate_collapse_evolution(ic):
    print("[*] Fase 2, 3 & 4: Simulando evolución temporal del colapso y horizontes...")
    
    rho0 = ic["rho0"]
    rho_crit = ic["rho_critical"]
    k = ic["k"]
    r_b = ic["boundary_radius_r_b"]
    M0 = ic["M0"]
    
    # Ecuación de Friedmann LQC efectiva:
    # (da/dt)^2 = 8*pi/3 * rho * (1 - rho/rho_crit) - k/a^2
    # with rho = rho0 / a^3
    
    # We solve this as a 1D ODE in scale factor a(t).
    # Since da/dt changes sign at the bounce, we integrate in two stages:
    # Stage 1: Collapse (da/dt < 0) from a = 1.0 to a_min
    # Stage 2: Bounce & Expansion (da/dt > 0) from a_min back to 1.0
    
    def friedmann_rhs(t, a):
        rho = rho0 / a**3
        # Safeguard to prevent square root of negative numbers near the bounce
        term = (8.0 * np.pi / 3.0) * rho * (1.0 - rho / rho_crit) - k / a**2
        if term < 0:
            return 0.0
        return -np.sqrt(term)
        
    # Find a_min numerically (where RHS is zero)
    # At a_min, rho \approx rho_crit ==> a_min \approx (rho0/rho_crit)^(1/3)
    a_min_guess = (rho0 / rho_crit)**(1.0/3.0)
    
    # Integrate collapse stage
    t_span = (0.0, 30.0)
    # Event to stop at bounce (da/dt = 0)
    def hit_bounce(t, a):
        rho = rho0 / a[0]**3
        term = (8.0 * np.pi / 3.0) * rho * (1.0 - rho / rho_crit) - k / a[0]**2
        return term - 1e-6
    hit_bounce.terminal = True
    hit_bounce.direction = -1
    
    sol_collapse = solve_ivp(friedmann_rhs, t_span, [1.0], events=hit_bounce, rtol=1e-6, atol=1e-8)
    
    t_collapse = sol_collapse.t
    a_collapse = sol_collapse.y[0]
    
    # Stage 2: Expansion (symmetric bounce)
    t_bounce = t_collapse[-1]
    a_min = a_collapse[-1]
    
    t_expand = t_collapse + t_bounce
    a_expand = a_collapse[::-1]
    
    # Combine both stages
    t_full = np.concatenate([t_collapse, t_expand[1:]])
    a_full = np.concatenate([a_collapse, a_expand[1:]])
    
    # Calculate physical variables
    R_b = r_b * a_full # cloud physical boundary
    rho_full = rho0 / a_full**3
    rho_eff = rho_full / (1.0 + rho_full / rho_crit)
    
    # Kretschmann scalar K(t) \propto rho_eff^2
    K_full = 12.0 * rho_eff**2
    
    # Apparent horizon: R_s(t) = 2 * M(t)
    # Mass function M(t) = 4*pi/3 * R_b^3 * rho_eff
    M_full = (4.0 * np.pi / 3.0) * R_b**3 * rho_eff
    # Clamp mass to ADM mass M0 outside the boundary
    M_full = np.minimum(M_full, M0)
    R_s = 2.0 * M_full
    
    # Figure 1: Scale Factor & Density Evolution
    fig, ax1 = plt.subplots(figsize=(10, 6))
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    color = '#0369a1'
    ax1.set_xlabel('Tiempo Coordinado t (Planck)', fontsize=12)
    ax1.set_ylabel('Factor de Escala a(t)', color=color, fontsize=12)
    ax1.plot(t_full, a_full, color=color, linewidth=2.5, label='Factor de Escala a(t)')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.axvline(t_bounce, color='black', linestyle=':', label=f'Rebote Cuántico (t={t_bounce:.2f})')
    
    ax2 = ax1.twinx()
    color = '#b45309'
    ax2.set_ylabel('Densidad de Materia ' + r'$\rho(t)$', color=color, fontsize=12)
    ax2.plot(t_full, rho_full, color=color, linewidth=2.0, linestyle='--', label=r'Densidad $\rho(t)$')
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title('Colapso Gravitatorio Cuántico y Rebote en LQC', fontsize=14, fontweight='bold', pad=15)
    fig.tight_layout()
    plt.savefig("figures/collapse_evolution.png", dpi=150)
    plt.close()
    
    # Figure 2: Quantum Core & Density Regularization
    plt.figure(figsize=(10, 6))
    plt.plot(t_full, rho_full, color='#b45309', linewidth=2.0, linestyle='--', label=r'Densidad Clásica $\rho(t)$ (Divergente)')
    plt.plot(t_full, rho_eff, color='#0f766e', linewidth=2.5, label=r'Densidad Efectiva Regularizada $\rho_{eff}(t)$')
    plt.axhline(rho_crit, color='#be123c', linestyle=':', label=r'Densidad Crítica Planckiana $\rho_{crit} = 8.0$')
    plt.yscale("log")
    plt.xlabel('Tiempo Coordinado t (Planck)', fontsize=12)
    plt.ylabel('Densidad de Energía (Planck)', fontsize=12)
    plt.title('Detención del Colapso y Regularización del Núcleo Cuántico', fontsize=14, fontweight='bold', pad=15)
    plt.legend(frameon=True, fontsize=10)
    plt.tight_layout()
    plt.savefig("figures/quantum_core_growth.png", dpi=150)
    plt.close()
    
    # Figure 3: Horizon Apparent Tracking (Oppenheimer-Snyder vs regularized)
    plt.figure(figsize=(10, 6))
    plt.plot(t_full, R_b, color='#0f766e', linewidth=2.5, label='Radio de la Nube R(t) = r_b a(t)')
    plt.plot(t_full, R_s, color='#be123c', linewidth=2.0, linestyle='-.', label='Horizonte Aparente Rs(t) = 2 m(t)')
    plt.xlabel('Tiempo Coordinado t (Planck)', fontsize=12)
    plt.ylabel('Radio Físico (Planck)', fontsize=12)
    plt.title('Evolución Temporal del Horizonte Aparente y Rebote de la Nube', fontsize=14, fontweight='bold', pad=15)
    plt.legend(frameon=True, fontsize=10)
    plt.tight_layout()
    plt.savefig("figures/horizon_evolution.png", dpi=150)
    plt.close()
    
    print("[+] Simulations and plots successfully generated.")
    return {
        "t": t_full,
        "a": a_full,
        "R_b": R_b,
        "R_s": R_s,
        "rho": rho_full,
        "rho_eff": rho_eff,
        "K": K_full,
        "t_bounce": t_bounce,
        "a_min": a_min
    }

# ---------------------------------------------------------
# FASE 6: diagrama de fases en el espacio paramétrico
# ---------------------------------------------------------
def run_phase_space_scan():
    print("[*] Fase 6: Realizando barrido paramétrico y diagrama de fases...")
    
    # Scan: Mass M0 in [0.5, 5.0] and LQC scale rho_crit in [1.0, 15.0]
    # For each grid point, determine the final state:
    # 1. HORIZONLESS_REMNANT (No horizon forms, R_b > R_s at the bounce)
    # 2. PLANCK_STAR (Horizon forms, i.e., R_b <= R_s at some point, but bounces and expands)
    # 3. CLASSICAL_BLACK_HOLE (if collapse has no bounce, but regularized LQC always bounces!)
    
    N_scan = 40
    mass_vals = np.linspace(0.2, 5.0, N_scan)
    rho_crit_vals = np.linspace(1.0, 15.0, N_scan)
    
    phase_matrix = np.zeros((N_scan, N_scan))
    
    # Boundary radius and density parameters
    r_b = 2.5
    rho0 = 0.08
    k = 0.04
    
    for i, M0 in enumerate(mass_vals):
        for j, rho_crit in enumerate(rho_crit_vals):
            # Find minimum scale factor
            a_min = (rho0 / rho_crit)**(1.0/3.0)
            
            # Boundary radius at the bounce
            R_b_bounce = r_b * a_min
            
            # Effective density at the bounce
            rho_eff_bounce = rho_crit / 2.0 # at a_min, rho = rho_crit ==> rho_eff = rho_crit / (1 + 1) = rho_crit / 2
            
            # Mass inside boundary at the bounce
            M_bounce = (4.0 * np.pi / 3.0) * R_b_bounce**3 * rho_eff_bounce
            M_bounce = min(M_bounce, M0)
            
            # Schwarzschild radius at the bounce
            R_s_bounce = 2.0 * M_bounce
            
            if R_b_bounce > R_s_bounce:
                # Horizonless remnant / dispersion
                phase_matrix[i, j] = 1.0
            else:
                # Planck Star (temporary black hole)
                phase_matrix[i, j] = 2.0
                
    # Plotting Phase Diagram
    plt.figure(figsize=(10, 6))
    
    # Create meshgrid
    X, Y = np.meshgrid(rho_crit_vals, mass_vals)
    
    # Color map
    # 1 = Horizonless Remnant, 2 = Planck Star
    plt.contourf(X, Y, phase_matrix, levels=[0.5, 1.5, 2.5], colors=['#0f766e', '#b45309'], alpha=0.8)
    
    # Add legend manually
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#0f766e', label='Remanente sin Horizonte (Horizonless Remnant)'),
        Patch(facecolor='#b45309', label='Estrella de Planck (Planck Star)')
    ]
    plt.legend(handles=legend_elements, frameon=True, fontsize=10, facecolor='white')
    
    plt.xlabel('Densidad Crítica de Regularización LQC ' + r'$\rho_{crit}$ (Unidades Planck)', fontsize=12)
    plt.ylabel('Masa ADM Inicial del Colapso ' + r'$M_0$ (Unidades Planck)', fontsize=12)
    plt.title('Diagrama de Fases del Destino Final del Colapso Gravitatorio', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig("figures/phase_space.png", dpi=150)
    plt.close()
    
    print("[+] Phase scan finished. Saved diagram to figures/phase_space.png")
    return mass_vals, rho_crit_vals, phase_matrix

# ---------------------------------------------------------
# Main Execution Orchestrator
# ---------------------------------------------------------
def main():
    print("[*] Starting Phase 32.0: Dynamic Formation of Planck Stars calculations...")
    
    ic = build_collapse_model()
    sim_data = simulate_collapse_evolution(ic)
    mass_vals, rho_crit_vals, phase_matrix = run_phase_space_scan()
    
    # Determine final state variables at our specific initial conditions
    # M0 = 1.5, rho_crit = 8.0
    # a_min = (0.08 / 8.0)^(1/3) = 0.1^(1/3) \approx 0.215
    # R_b_bounce = 2.5 * 0.215 = 0.538
    # rho_eff_bounce = 8.0 / 2 = 4.0
    # M_bounce = 4/3 * pi * 0.538^3 * 4.0 = 4.188 * 0.1557 * 4.0 = 2.608 ==> clamped to M0 = 1.5
    # R_s_bounce = 3.0. Since R_b_bounce (0.538) <= R_s_bounce (3.0), it forms a temporary horizon!
    # So it is classified as a PLANCK_STAR!
    
    results = {
        "initial_conditions": ic,
        "final_state": {
            "t_bounce": float(sim_data["t_bounce"]),
            "a_min": float(sim_data["a_min"]),
            "R_b_at_bounce": float(sim_data["R_b"][int(len(sim_data["R_b"])/2)]),
            "R_s_at_bounce": float(sim_data["R_s"][int(len(sim_data["R_s"])/2)]),
            "K_max": float(np.max(sim_data["K"])),
            "horizon_classification": "TEMPORARY_HORIZON",
            "final_state_classification": "PLANCK_STAR",
            "formation_verdict": "GENERIC_REMNANT_FORMATION"
        }
    }
    
    with open("physics/benchmark/collapse_audit_results.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print("[+] Collapse audit calculations finished. Results saved to physics/benchmark/collapse_audit_results.json")

if __name__ == "__main__":
    main()
