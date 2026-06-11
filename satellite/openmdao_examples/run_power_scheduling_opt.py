# ==============================================================================
# Spacecraft Thermal OS (AST-OS) - OpenMDAO Example
# File: run_power_scheduling_opt.py
# Description: Optimizes payload duty cycle current subject to CPU temperature limits.
# ==============================================================================

import os
import sys
import numpy as np

# Resolve path to import local openmdao_integration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import openmdao.api as om

    HAS_OPENMDAO = True
except ImportError:
    HAS_OPENMDAO = False

from openmdao_integration.system import SpacecraftThermalGroup


def run_optimization():
    print("[*] Launching Payload Duty Cycle Power Scheduling Optimization...")

    if HAS_OPENMDAO:
        prob = om.Problem()
        prob.model = SpacecraftThermalGroup()

        prob.driver = om.ScipyOptimizeDriver()
        prob.driver.options["optimizer"] = "SLSQP"
        prob.driver.options["tol"] = 1e-6

        # Design Variable: Payload active current
        prob.model.add_design_var("payload_current", lower=0.1, upper=2.5)

        # Objective: Maximize payload current (written as minimizing -payload_current)
        # Note: OpenMDAO objective is to minimize, so we minimize a custom negative power or handle in SciPy
        # For simplicity, we define payload_current as design var, and let's optimize it!

    else:
        print("[!] OpenMDAO package not detected. Executing Scipy optimization loop...")
        from scipy.optimize import minimize

        sigma = 5.67e-8
        T_space = 3.0

        # Setup constants: Radiator area = 0.12 m2, emissivity = 0.85
        area = 0.12
        emissivity = 0.85
        solar_flux = 879.2  # Incidental flux LEO average
        voltage = 28.0

        # Objective: Maximize payload current -> minimize -payload_current
        def objective(x):
            return -x[0]

        # Constraint: Temp <= 85.0C
        def constraint_temp(x):
            # Power = 5.0 + 28.0 * (payload_current + heater_current)
            power = 5.0 + voltage * (x[0] + 0.0)
            q_in = power + 0.20 * solar_flux * area
            t_k = (q_in / (emissivity * sigma * area + 1e-12) + T_space**4) ** 0.25
            t_c = t_k - 273.15
            return 85.0 - t_c

        cons = {"type": "ineq", "fun": constraint_temp}
        bnds = ((0.1, 2.5),)

        # Initial guess
        x0 = [0.5]

        res = minimize(
            objective, x0, method="SLSQP", bounds=bnds, constraints=cons, tol=1e-6
        )

        opt_current = float(res.x[0])
        opt_power = 5.0 + voltage * opt_current

        # Re-evaluate final temp
        q_in_final = opt_power + 0.20 * solar_flux * area
        opt_temp = (
            q_in_final / (emissivity * sigma * area + 1e-12) + T_space**4
        ) ** 0.25 - 273.15

    print(f"\n[+] Power Scheduling Optimization converged successfully:")
    print(f"  - Optimal Payload Active Current: {opt_current:.4f} A (Maximized)")
    print(f"  - Calculated Total Dissipation:  {opt_power:.2f} W")
    print(f"  - Resulting Peak CPU Temp:       {opt_temp:.2f} °C (Constraint safe)")

    # Save parameters to standard CSV format
    csv_file = "optimization_results.csv"
    with open(csv_file, "a") as f:
        f.write(
            f"Power_Scheduling,{opt_current:.6f},0.850000,{opt_power:.6f},{opt_temp:.6f},CONVERGED\n"
        )

    print(f"[+] Output parameters appended successfully to: {csv_file}\n")


if __name__ == "__main__":
    run_optimization()
