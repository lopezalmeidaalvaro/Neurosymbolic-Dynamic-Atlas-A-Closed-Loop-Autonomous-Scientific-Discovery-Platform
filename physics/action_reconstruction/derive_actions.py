import sympy as sp
import json
import os
import numpy as np

def run_derivations():
    # 1. Simbólico: Sympy para derivar tensores
    r, M0, L = sp.symbols('r M0 L', real=True, positive=True)
    
    # Coeficiente métrico de Hayward
    A = 1 - (2 * M0 * r**2) / (r**3 + 2 * M0 * L**2)
    
    # Derivadas de A
    dA = sp.diff(A, r)
    ddA = sp.diff(dA, r)
    
    # Escalar de Ricci R
    # R = -A'' - 4*A'/r - 2*(A - 1)/r^2
    R = -ddA - 4*dA/r - 2*(A - 1)/r**2
    R = sp.simplify(R)
    
    # Densidad de energía y presiones efectivas
    # G^t_t = -8*pi*rho => rho = -G^t_t / 8*pi
    # Para ds^2 = -A dt^2 + A^-1 dr^2 + r^2 dOmega^2:
    # G^t_t = A'/r + (A - 1)/r^2
    rho = sp.simplify((dA/r + (A - 1)/r**2) / (-8 * sp.pi))
    
    # G^r_r = 8*pi*Pr => Pr = G^r_r / 8*pi
    # G^r_r = A'/r + (A - 1)/r^2 = G^t_t
    Pr = sp.simplify(-rho)
    
    # G^theta_theta = 8*pi*Pt => Pt = G^theta_theta / 8*pi
    # G^theta_theta = A''/2 + A'/r
    Pt = sp.simplify((ddA/2 + dA/r) / (8 * sp.pi))
    
    # Verificar conservación local de energía: dPr/dr + 2/r * (Pr - Pt) = 0
    dPr = sp.diff(Pr, r)
    cons = sp.simplify(dPr + 2/r * (Pr - Pt))
    
    # Evaluar condiciones de energía
    # NEC: rho + Pr >= 0 (radial), rho + Pt >= 0 (transversal)
    nec_r = sp.simplify(rho + Pr)
    nec_t = sp.simplify(rho + Pt)
    
    # SEC: rho + Pr + 2*Pt >= 0
    sec = sp.simplify(rho + Pr + 2 * Pt)
    
    # DEC: rho >= |Pr| y rho >= |Pt|
    dec_diff = sp.simplify(rho - Pt) # Para r grande, Pt > rho (violación de DEC)
    
    # Evaluar límites en r -> 0
    rho_0 = sp.limit(rho, r, 0)
    Pr_0 = sp.limit(Pr, r, 0)
    Pt_0 = sp.limit(Pt, r, 0)
    R_0 = sp.limit(R, r, 0)
    
    # Evaluar límites en r -> oo
    rho_inf = sp.limit(rho * r**6, r, sp.oo) # rho ~ r^-6
    R_inf = sp.limit(R * r**6, r, sp.oo) # R ~ r^-6
    
    # Guardar resultados simbólicos en un diccionario compatible con JSON
    results = {
        "metric": {
            "A": str(sp.simplify(A)),
            "dA": str(sp.simplify(dA)),
            "ddA": str(sp.simplify(ddA)),
        },
        "curvatures": {
            "R": str(R),
            "R_limit_r0": str(R_0),
            "R_limit_r_inf": "0" if R_inf == 0 else f"{str(R_inf)}/r^6",
        },
        "energy_density": {
            "rho": str(rho),
            "rho_limit_r0": str(rho_0),
            "rho_limit_r_inf": f"{str(rho_inf)}/r^6",
        },
        "pressures": {
            "Pr": str(Pr),
            "Pt": str(Pt),
            "Pr_limit_r0": str(Pr_0),
            "Pt_limit_r0": str(Pt_0),
        },
        "energy_conditions": {
            "conservation_residual": str(cons), # Debe ser 0
            "nec_radial": str(nec_r), # Debe ser 0
            "nec_transverse": str(nec_t),
            "sec_factor": str(sec),
            "dec_diff": str(dec_diff),
        }
    }
    
    # 2. Análisis Numérico para f(R) e inversión r(R)
    # Evaluamos con M0 = 1.0, L = 0.866 (2*M0*L^2 = 1.5)
    r_vals = np.linspace(0.01, 10.0, 1000)
    R_func = sp.lambdify(r, R.subs({M0: 1.0, L: 0.866}), 'numpy')
    rho_func = sp.lambdify(r, rho.subs({M0: 1.0, L: 0.866}), 'numpy')
    Pt_func = sp.lambdify(r, Pt.subs({M0: 1.0, L: 0.866}), 'numpy')
    
    R_vals = R_func(r_vals)
    rho_vals = rho_func(r_vals)
    Pt_vals = Pt_func(r_vals)
    
    # Evaluar f(R) reconstrucción:
    # En f(R) vacío, R(r) de Hayward no puede reproducirse con f(R) puro porque
    # la métrica de Hayward requiere T_mu_nu anisotrópico.
    # Si intentamos mapear f(R) efectivo, evaluamos si dR/dr es invertible.
    # dR/dr = 0 define puntos críticos de R.
    dR = sp.simplify(sp.diff(R, r))
    dR_func = sp.lambdify(r, dR.subs({M0: 1.0, L: 0.866}), 'numpy')
    dR_vals = dR_func(r_vals)
    
    # Encontrar máximos de R
    # Para Hayward: R(r) = 24 * M0 * L^2 * (4*M0*L^2 - r^3) / (r^3 + 2*M0*L^2)^3 (verificaremos esto)
    # R(0) = 12/L^2. R'(r) = 0 da los puntos críticos de R.
    critical_r = []
    # Buscamos cambios de signo de dR_vals
    for i in range(len(dR_vals)-1):
        if dR_vals[i] * dR_vals[i+1] < 0:
            critical_r.append(float(r_vals[i]))
            
    results["numerical"] = {
        "critical_points_R": critical_r,
        "max_R": float(np.max(R_vals)),
        "min_R": float(np.min(R_vals)),
        "invertible": len(critical_r) == 0,
    }
    
    # Guardar en archivo JSON
    os.makedirs("physics/action_reconstruction", exist_ok=True)
    with open("physics/action_reconstruction/action_metrics.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print("Derivaciones completadas con éxito.")
    
if __name__ == "__main__":
    run_derivations()
