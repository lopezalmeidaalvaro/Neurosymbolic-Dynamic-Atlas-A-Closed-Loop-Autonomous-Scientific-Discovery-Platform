#!/usr/bin/env python3
"""
Validate Thermal Model - Performs physical sanity checks on the ThermalServerModel.
Generates a validation report in markdown format.
Author: Alvaro Lopez Almeida
"""

import numpy as np
from thermal_server_model import ThermalServerModel

def run_validation():
    # Set seed for reproducibility
    np.random.seed(42)
    
    print("Running Thermal Model Physics Validation...")
    
    report_lines = []
    report_lines.append("# Thermal Model Physical Validation Report")
    report_lines.append(f"Generated at: 2026-05-27")
    report_lines.append("\nThis report validates the lumped capacitance orbital thermal model against fundamental thermodynamic laws.\n")
    
    # ----------------------------------------------------
    # PRUEBA 1 — CONSERVACIÓN DE ENERGÍA
    # ----------------------------------------------------
    print(" -> PRUEBA 1: Conservación de la energía...")
    p1_results = []
    p1_passed = 0
    p1_excellent = 0
    
    for i in range(10):
        # Generate a random physically reasonable configuration
        power = np.random.uniform(10.0, 40.0)
        area = np.random.uniform(0.05, 0.30)
        emissivity = np.random.uniform(0.3, 0.9)
        heat_capacity = 500.0
        
        model = ThermalServerModel(
            power=power,
            area=area,
            emissivity=emissivity,
            heat_capacity=heat_capacity
        )
        
        # High precision simulation for validation
        duration = 3600.0
        dt = 1.0  # fine step size for trapezoidal integration
        res = model.simulate(duration=duration, dt=dt)
        
        times = np.array(res["time"])
        temps_C = np.array(res["temperature"])
        temps_K = temps_C + 273.15
        
        # Calculate Energy terms
        E_gen = power * duration
        E_acum = heat_capacity * (temps_K[-1] - temps_K[0])
        
        # Radiated power Q_rad(t) = ε * σ * A * (T(t)^4 - T_amb^4)
        Q_rad = emissivity * model.stefan_boltzmann * area * (temps_K**4 - model.ambient_temp_K**4)
        E_rad = np.trapz(Q_rad, times)
        
        error = abs(E_gen - (E_acum + E_rad)) / E_gen
        p1_results.append((power, area, emissivity, error))
        
        if error < 0.05:
            p1_passed += 1
        if error < 0.02:
            p1_excellent += 1
            
    p1_verdict = "WARNING"
    if p1_passed == 10:
        p1_verdict = "EXCELLENT" if p1_excellent >= 8 else "PASS"
        
    report_lines.append("## Test 1: Energy Conservation")
    report_lines.append(f"**Verdict:** {p1_verdict} ({p1_passed}/10 Passed, {p1_excellent}/10 Excellent)")
    report_lines.append("| Config | Power (W) | Area (m²) | Emissivity | Energy Balance Error | Status |")
    report_lines.append("| --- | --- | --- | --- | --- | --- |")
    for idx, (p, a, e, err) in enumerate(p1_results):
        status = "EXCELLENT" if err < 0.02 else ("PASS" if err < 0.05 else "FAIL")
        report_lines.append(f"| {idx+1} | {p:.2f} | {a:.4f} | {e:.2f} | {err*100:.4f}% | {status} |")
    report_lines.append("\n")

    # ----------------------------------------------------
    # PRUEBA 2 — LÍMITE ESTACIONARIO
    # ----------------------------------------------------
    print(" -> PRUEBA 2: Límite estacionario...")
    p2_results = []
    p2_passed = 0
    
    for i in range(10):
        power = np.random.uniform(10.0, 40.0)
        area = np.random.uniform(0.05, 0.30)
        emissivity = np.random.uniform(0.3, 0.9)
        
        model = ThermalServerModel(
            power=power,
            area=area,
            emissivity=emissivity,
            heat_capacity=500.0
        )
        
        # Simulate long enough to reach steady state
        res = model.simulate(duration=10000.0, dt=10.0)
        T_final_sim_K = res["temperature"][-1] + 273.15
        T_eq_analitica_K = model.steady_state_temp()
        
        err_rel = abs(T_final_sim_K - T_eq_analitica_K) / T_eq_analitica_K
        p2_results.append((power, area, emissivity, T_final_sim_K - 273.15, T_eq_analitica_K - 273.15, err_rel))
        
        if err_rel < 0.005:
            p2_passed += 1
            
    p2_verdict = "PASS" if p2_passed == 10 else "FAIL"
    
    report_lines.append("## Test 2: Steady State Convergence")
    report_lines.append(f"**Verdict:** {p2_verdict} ({p2_passed}/10 Converged under 0.5%)")
    report_lines.append("| Config | Power (W) | Area (m²) | Emissivity | Sim T_eq (°C) | Analytical T_eq (°C) | Relative Error | Status |")
    report_lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for idx, (p, a, e, sim_t, ana_t, err) in enumerate(p2_results):
        status = "PASS" if err < 0.005 else "FAIL"
        report_lines.append(f"| {idx+1} | {p:.2f} | {a:.4f} | {e:.2f} | {sim_t:.2f} | {ana_t:.2f} | {err*100:.4f}% | {status} |")
    report_lines.append("\n")

    # ----------------------------------------------------
    # PRUEBA 3 — SENSIBILIDAD PARAMÉTRICA
    # ----------------------------------------------------
    print(" -> PRUEBA 3: Sensibilidad paramétrica...")
    p3_passed = True
    p3_logs = []
    
    # Baseline (init at 100K to ensure it heats up and sensitivity is measurable)
    base_model = ThermalServerModel(power=20.0, area=0.10, emissivity=0.80, initial_temp=100.0)
    base_res = base_model.simulate()
    base_max = base_res["max_temp"]
    
    # ↑power
    p_up_model = ThermalServerModel(power=30.0, area=0.10, emissivity=0.80, initial_temp=100.0)
    p_up_max = p_up_model.simulate()["max_temp"]
    if p_up_max > base_max:
        p3_logs.append("PASS: ↑power -> ↑max_temp")
    else:
        p3_passed = False
        p3_logs.append(f"FAIL: ↑power did not increase max_temp (base_max={base_max:.2f}, p_up_max={p_up_max:.2f})")
        
    # ↑area
    a_up_model = ThermalServerModel(power=20.0, area=0.20, emissivity=0.80, initial_temp=100.0)
    a_up_max = a_up_model.simulate()["max_temp"]
    if a_up_max < base_max:
        p3_logs.append("PASS: ↑area -> ↓max_temp")
    else:
        p3_passed = False
        p3_logs.append(f"FAIL: ↑area did not decrease max_temp (base_max={base_max:.2f}, a_up_max={a_up_max:.2f})")
        
    # ↑emissivity
    e_up_model = ThermalServerModel(power=20.0, area=0.10, emissivity=0.90, initial_temp=100.0)
    e_up_max = e_up_model.simulate()["max_temp"]
    if e_up_max < base_max:
        p3_logs.append("PASS: ↑emissivity -> ↓max_temp")
    else:
        p3_passed = False
        p3_logs.append(f"FAIL: ↑emissivity did not decrease max_temp (base_max={base_max:.2f}, e_up_max={e_up_max:.2f})")
        
    p3_verdict = "PASS" if p3_passed else "WARNING"
    
    report_lines.append("## Test 3: Parametric Sensitivity")
    report_lines.append(f"**Verdict:** {p3_verdict}")
    for log in p3_logs:
        report_lines.append(f"- {log}")
    report_lines.append("\n")

    # ----------------------------------------------------
    # VERDICTO FINAL
    # ----------------------------------------------------
    final_verdict = "FAILED — Fix physics before proceeding"
    if p1_passed == 10 and p2_passed == 10 and p3_passed:
        final_verdict = "VALIDATED — Ready for ML"
        
    print(f"Final Verdict: {final_verdict}")
    
    report_lines.append("## Final Validation Summary")
    report_lines.append(f"**Overall Verdict:** `{final_verdict}`")
    
    # Save the report
    report_path = "thermal_validation_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"Validation report saved to {report_path}")
    
    return final_verdict

if __name__ == "__main__":
    run_validation()
