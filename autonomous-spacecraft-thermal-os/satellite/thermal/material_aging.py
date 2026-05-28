#!/usr/bin/env python3
"""
Phase T25: Material Aging and Temporal Drift Modeler
Models degradation of thermal properties in the space environment (UV, ATOX, fatigue)
and their long-term impact on spacecraft thermal performance.
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Resolve paths
SATELLITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SATELLITE_DIR)

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from thermal.multi_node_thermal_network import ThermalNetwork
from thermal.orbital_environment import compute_orbit_params, solar_flux, albedo_flux, earth_ir_flux

# Set seed for reproducibility
np.random.seed(42)

# Aging Constants
F_ATOX = 1e-22         # m^2/atom - atomic oxygen degradation coefficient in LEO
T_LIFE_NOMINAL = 8760  # Hours (1 year) - standard design lifetime reference

def apply_aging(network, elapsed_orbit_hours, uv_hours, atox_fluence, thermal_cycles=0):
    """
    Modifies network parameters in place according to mission elapsed time.
    1. UV degradation: increases emissivity/absorptivity of panels/radiator.
    2. ATOX erosion: increases roughness and alters radiator emissivity.
    3. Structural conductance drift: MLI degradation increases structure coupling.
    4. Thermal cycling fatigue: degrades node properties.
    """
    # Create copies of baseline parameters if not already backed up
    if not hasattr(network, 'base_eps'):
        network.base_eps = np.copy(network.eps)
        network.base_k = np.copy(network.k)
        network.base_C = np.copy(network.C)

    # 1. UV degradation on exposed surfaces (Radiator=node 4, Panels=node 5)
    # Model: eps(t) = eps_init + delta_eps_sat * (1 - exp(-t/tau_uv))
    tau_uv = 1500.0  # Equivalent sun hours constant
    delta_eps_sat_rad = 0.08
    delta_eps_sat_pan = 0.12
    
    eps_uv_rad = delta_eps_sat_rad * (1.0 - np.exp(-uv_hours / tau_uv))
    eps_uv_pan = delta_eps_sat_pan * (1.0 - np.exp(-uv_hours / tau_uv))
    
    # 2. Atomic Oxygen Attack (ATOX) in LEO (affects radiator emissivity)
    # Model: eps_eff = eps_base + f_ATOX * fluence_accumulated
    # Limit maximum ATOX shift to 0.15
    eps_atox = min(0.15, F_ATOX * atox_fluence)

    # Apply UV and ATOX modifications
    network.eps[4] = min(0.98, network.base_eps[4] - eps_uv_rad + eps_atox)
    network.eps[5] = min(0.98, network.base_eps[5] + eps_uv_pan)

    # 3. Changes in Thermal Conductance (MLI joint/interface fatigue)
    # Model: k_ij(t) = k_ij_0 * (1 + delta_k * t/t_vida)
    # k degrades by -5% over standard lifetime
    delta_k = -0.05
    time_ratio = min(1.5, elapsed_orbit_hours / T_LIFE_NOMINAL)
    network.k = network.base_k * (1.0 + delta_k * time_ratio)

    # 4. Thermal cycling fatigue (modified Miner's law)
    # Accumulation of high-amplitude thermal cycles reduces node capacity
    capacity_degradation = max(0.92, 1.0 - 0.0001 * thermal_cycles)
    network.C = network.base_C * capacity_degradation


def simulate_mission_lifetime(network, mission_duration_days=365, orbit_params=None):
    """
    Simulates the thermal network performance over the spacecraft's lifetime.
    Iteratively applies aging effects and measures orbital peak temperatures.
    """
    if orbit_params is None:
        orbit_params = compute_orbit_params(altitude_km=400)
    
    period = orbit_params["period_sec"]
    
    # Assume 15 orbits per day (approx 90min each)
    orbits_per_day = 86400.0 / period
    total_orbits = int(mission_duration_days * orbits_per_day)
    
    # Time step intervals for logging (e.g. evaluate every 30 days)
    evaluation_interval_days = 30
    eval_steps = list(range(0, mission_duration_days + 1, evaluation_interval_days))
    if mission_duration_days not in eval_steps:
        eval_steps.append(mission_duration_days)
        
    results = []
    print(f"[*] Starting Lifetime Simulation for {mission_duration_days} days...")
    
    for day in eval_steps:
        # Calculate environmental exposures
        elapsed_hours = day * 24.0
        # Assume sun exposure is roughly 65% of orbital lifetime (sunlit phase)
        uv_hours = elapsed_hours * 0.65
        # LEO atomic oxygen flux: ~1e17 atoms/(m2 s)
        atox_fluence = elapsed_hours * 3600.0 * 1e17
        # Thermal cycles count (1 cycle per orbit)
        thermal_cycles = int(day * orbits_per_day)

        # Apply aging to the network
        apply_aging(network, elapsed_hours, uv_hours, atox_fluence, thermal_cycles)

        # Run orbital transient simulation at this age snapshot
        # Integrate for 2 orbits to reach steady cycle
        duration = 2 * period
        
        # Let's couple with the orbit environment solar flux
        alpha_solar = 0.8
        eps_panels = network.eps[5]
        A_panels = network.A[5]
        
        def orbital_heat_func(time):
            sol_f, is_eclipse = solar_flux(time, orbit_params, beta_angle=15)
            alb_f = albedo_flux(time, orbit_params, beta_angle=15)
            ir_f = earth_ir_flux(orbit_params["altitude_km"])
            Q_total = A_panels * (alpha_solar * (sol_f + alb_f) + eps_panels * ir_f)
            return Q_total

        sim_res = network.simulate(
            duration=duration,
            dt=10.0,
            orbit_period=period,
            initial_temp=293.15,
            Q_solar_func=orbital_heat_func
        )
        
        # Log properties
        row = {
            "Day": day,
            "Elapsed_Hours": elapsed_hours,
            "UV_Hours": uv_hours,
            "ATOX_Fluence": atox_fluence,
            "Thermal_Cycles": thermal_cycles,
            "Radiator_Emissivity": network.eps[4],
            "Panels_Emissivity": network.eps[5],
            "CPU_Structure_Conductance": network.k[0, 3],
            "CPU_Capacity": network.C[0],
            "T_Max_CPU": sim_res["max_temps"]["CPU"],
            "T_Max_Battery": sim_res["max_temps"]["Battery"],
            "T_Max_Structure": sim_res["max_temps"]["Structure"],
            "T_Max_Radiator": sim_res["max_temps"]["Radiator"]
        }
        results.append(row)
        print(f" -> Day {day:3d}: CPU Max Temp = {row['T_Max_CPU']:.2f}°C, Radiator Emissivity = {row['Radiator_Emissivity']:.4f}")

    df_results = pd.DataFrame(results)
    csv_path = os.path.join(SATELLITE_DIR, "thermal", "aging_results.csv")
    df_results.to_csv(csv_path, index=False)
    print(f"[+] Lifetime aging results exported to: {csv_path}")
    
    return df_results


def predict_lifetime(df_results, critical_temp_threshold=85.0):
    """
    Extrapolates/estimates when the CPU or critical nodes will exceed safety thresholds.
    """
    days = df_results["Day"].values
    t_max_cpu = df_results["T_Max_CPU"].values
    
    # Check if we already exceed it during the simulation
    exceeded_idx = np.where(t_max_cpu >= critical_temp_threshold)[0]
    if len(exceeded_idx) > 0:
        failure_day = float(days[exceeded_idx[0]])
        return {
            "failure_day": failure_day,
            "margin_days": failure_day,
            "status": "EXCEEDED",
            "regression_r2": 1.0
        }
        
    # Otherwise, fit a linear/quadratic regression to predict future drift
    poly = np.polyfit(days, t_max_cpu, 1) # linear fit: T = m * Day + c
    slope = poly[0]
    intercept = poly[1]
    
    # R2 check
    y_pred = slope * days + intercept
    y_mean = np.mean(t_max_cpu)
    r2 = 1.0 - (np.sum((t_max_cpu - y_pred)**2) / np.sum((t_max_cpu - y_mean)**2))

    if slope <= 0:
        return {
            "failure_day": 9999.0, # Indefinite or safe
            "margin_days": 9999.0,
            "status": "SAFE",
            "regression_r2": float(r2)
        }
        
    failure_day = (critical_temp_threshold - intercept) / slope
    margin_days = max(0.0, failure_day)
    
    return {
        "failure_day": float(failure_day),
        "margin_days": float(margin_days),
        "status": "PREDICTED_LIMIT",
        "regression_r2": float(r2),
        "slope_per_day": float(slope)
    }


def add_sensor_drift(t_real, time_days, node_index=0):
    """
    Simulates sensor aging and drifts on thermocouple readings.
    Model: T_sensor = T_real + bias(t)
    bias(t) = A * t + B * sin(omega * t)
    A = 0.1C / month (0.1 / 30 per day), B = 0.5C, omega = orbit cycle frequency
    """
    # A = 0.1 degC per 30 days = 0.00333 degC per day
    A = 0.1 / 30.0
    B = 0.5
    omega = 2.0 * np.pi / (5400.0 / 86400.0)  # frequency in rad/day
    bias = A * time_days + B * np.sin(omega * time_days)
    return t_real + bias


def plot_degradation_trends(df_results, output_path):
    """
    Renders styled professional degradation trend graphs.
    """
    days = df_results["Day"]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8))
    fig.patch.set_facecolor('#070b19')
    
    # Plot 1: Emissivity and Material Properties Degradation
    ax1.set_facecolor('#0d1527')
    ax1.plot(days, df_results["Radiator_Emissivity"], label="Radiator Emissivity (Node 4)", color="#38bdf8", linewidth=2.0)
    ax1.plot(days, df_results["Panels_Emissivity"], label="Solar Panels Emissivity (Node 5)", color="#ffb821", linewidth=2.0)
    ax1.set_title("Material Thermal Properties Degradation Over Mission Life", color='white', fontsize=12, pad=10)
    ax1.set_ylabel("Emissivity (ε)", color='#94a3b8')
    ax1.tick_params(colors='white')
    ax1.grid(color='white', linestyle=':', alpha=0.08)
    ax1.legend(facecolor='#0f172a', edgecolor='#1e293b', labelcolor='white')

    # Plot 2: Peak Nodal Temperatures
    ax2.set_facecolor('#0d1527')
    ax2.plot(days, df_results["T_Max_CPU"], label="CPU Max Temperature", color="#ff2a5f", linewidth=2.2, marker="o")
    ax2.plot(days, df_results["T_Max_Battery"], label="Battery Max Temperature", color="#26ffad", linewidth=1.8, marker="s")
    ax2.plot(days, df_results["T_Max_Structure"], label="Structure Max Temperature", color="#a55eff", linewidth=1.5)
    ax2.axhline(85.0, color="#ff2a5f", linestyle=":", label="CPU Critical Limit (85°C)", alpha=0.6)
    
    ax2.set_title("Long-term Thermal Peak Drifts and Limit Approximations", color='white', fontsize=12, pad=10)
    ax2.set_xlabel("Mission Elapsed Time (Days)", color='#94a3b8')
    ax2.set_ylabel("Maximum Temperature (°C)", color='#94a3b8')
    ax2.tick_params(colors='white')
    ax2.grid(color='white', linestyle=':', alpha=0.08)
    ax2.legend(facecolor='#0f172a', edgecolor='#1e293b', labelcolor='white', loc="lower right")

    for ax in [ax1, ax2]:
        ax.spines['bottom'].set_color('#334155')
        ax.spines['top'].set_color('#334155')
        ax.spines['left'].set_color('#334155')
        ax.spines['right'].set_color('#334155')
        
    plt.tight_layout()
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', dpi=150)
    plt.close()
    print(f"[+] Material degradation plots saved to: {output_path}")


def generate_aging_report(df_results, pred):
    """
    Generates a publication-grade markdown report describing lifetime results.
    """
    report_path = os.path.join(SATELLITE_DIR, "thermal", "aging_report.md")
    
    latest_cpu_temp = df_results["T_Max_CPU"].iloc[-1]
    latest_eps = df_results["Radiator_Emissivity"].iloc[-1]
    
    status_msg = ""
    if pred["status"] == "EXCEEDED":
        status_msg = f"⚠️ **CRITICAL ALERT:** The spacecraft is expected to experience thermal runaway around Day **{pred['failure_day']:.1f}** when CPU exceeds its safety limit!"
    elif pred["status"] == "PREDICTED_LIMIT":
        status_msg = f"📉 **PREDICTED LIFETIME LIMIT:** The CPU will exceed its 85°C safety margin on Day **{pred['failure_day']:.1f}** ({pred['failure_day']/365.0:.2f} years)."
    else:
        status_msg = "✅ **SAFE:** Nodal temperatures remain within legal safety envelopes for the simulated duration."

    report_template = """# Spacecraft Material Degradation & Thermal Drift Report

**Date Generated:** {DATE_GENERATED}
**Simulator Version:** 1.2.0 (Fase T25)
**Mission Duration Evaluated:** {MISSION_DAYS} Days
**Reference Standards:** ECSS-E-ST-31C, ECSS-Q-ST-70C

---

## 📊 Executive Summary

This report evaluates space environment degradation (Atomic Oxygen, Solar UV radiation, thermal cycling fatigue, and interface joint ageing) and its long-term impact on the 6-node cubesat thermal design.

* **Initial CPU Peak Temp:** {INIT_CPU_TEMP:.2f}°C
* **End-of-Life CPU Peak Temp:** {EOL_CPU_TEMP:.2f}°C
* **Radiator Emissivity Drift:** {INIT_RAD_EPS:.4f} → {EOL_RAD_EPS:.4f}
* **Thermal Conductance (k_03) Drift:** {INIT_COND:.4f} W/K → {EOL_COND:.4f} W/K

### Operational Verdict
{STATUS_MSG}

---

## 🔬 Mathematical Formulations

### 1. Solar Ultraviolet (UV) Exposure
Exposed structural surfaces suffer polymer/coating darkening, reducing reflectivity and shifting emissivity:
$$\\epsilon(t) = \\epsilon_0 + \\Delta\\epsilon_{sat} \\cdot (1 - e^{-t/\\tau_{uv}})$$

### 2. Atomic Oxygen Attack (LEO ATOX)
In LEO (400km), atomic oxygen collision erodes coatings, increasing surface micro-roughness:
$$\\epsilon_{eff} = \\epsilon_{base} + f_{ATOX} \\cdot \\Phi(t)$$
Where $f_{ATOX} = 10^{-22}\\text{ m}^2/\\text{atom}$ and $\\Phi(t)$ represents the accumulated atomic fluence.

### 3. Joint & Structural Thermal Aging
Long-term structural fatigue and MLI degradation slowly alter structural coupling conductances:
$$k_{ij}(t) = k_{ij,0} \\cdot \\left(1 + \\delta_k \\frac{t}{t_{vida}}\\right)$$

### 4. Thermal Cycling Fatigue
The mechanical stress accumulated during hot-cold transitions ($\Delta T > 50^\\circ\\text{C}$) reduces effective nodal thermal capacity $C_i$ following a linear damage index (Miner's Rule modification).

---

## 📈 Lifetime Telemetry History

| Mission Day | UV Exposure (Hours) | Radiator Emissivity (Node 4) | CPU Peak (°C) | Battery Peak (°C) | Conductance (W/K) |
|-------------|---------------------|------------------------------|---------------|-------------------|-------------------|
"""
    
    report_md = (report_template
        .replace("{DATE_GENERATED}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        .replace("{MISSION_DAYS}", str(df_results['Day'].max()))
        .replace("{INIT_CPU_TEMP}", f"{df_results['T_Max_CPU'].iloc[0]:.2f}")
        .replace("{EOL_CPU_TEMP}", f"{latest_cpu_temp:.2f}")
        .replace("{INIT_RAD_EPS}", f"{df_results['Radiator_Emissivity'].iloc[0]:.4f}")
        .replace("{EOL_RAD_EPS}", f"{latest_eps:.4f}")
        .replace("{INIT_COND}", f"{df_results['CPU_Structure_Conductance'].iloc[0]:.4f}")
        .replace("{EOL_COND}", f"{df_results['CPU_Structure_Conductance'].iloc[-1]:.4f}")
        .replace("{STATUS_MSG}", status_msg)
    )

    for _, row in df_results.iterrows():
        report_md += f"| {int(row['Day']):3d} | {row['UV_Hours']:8.1f} | {row['Radiator_Emissivity']:24.4f} | {row['T_Max_CPU']:12.2f} | {row['T_Max_Battery']:17.2f} | {row['CPU_Structure_Conductance']:17.4f} |\n"

    report_footer = """
---

## 📉 Predictive Lifetime Extrapolation

We executed a standard polynomial regression over the drift telemetry to predict when safety boundaries will be breached:

* **Regression R² Coefficient:** {REG_R2:.6f}
* **Thermal Drift Rate:** {DRIFT_RATE:.4f}°C per month
* **Critical Boundary Threshold:** 85.00°C
* **Estimated Failure Milestone:** Day **{FAILURE_DAY:.1f}**

![Material Degradation Trends](aging_degradation_trends.png)

*Figure 1: Long-term material property degradation and peak temperature drifts.*

---
*DEMONSTRATION ONLY — Requires validation with experimental thermal vacuum chambers (TVAC) or actual flight telemetry.*
"""
    report_md += (report_footer
        .replace("{REG_R2}", f"{pred['regression_r2']:.6f}")
        .replace("{DRIFT_RATE}", f"{pred.get('slope_per_day', 0.0)*30.0:.4f}")
        .replace("{FAILURE_DAY}", f"{pred['failure_day']:.1f}")
    )

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"[+] Material degradation report compiled to: {report_path}")


def main():
    print("=" * 60)
    print("FASE T25: SPACECRAFT MATERIAL AGING & DEGRADATION MODELER")
    print("=" * 60)
    
    # Initialize network
    net = ThermalNetwork()
    
    # Simulate a full 365-day mission lifetime
    df_results = simulate_mission_lifetime(net, mission_duration_days=365)
    
    # Predict failure milestones
    pred = predict_lifetime(df_results, critical_temp_threshold=85.0)
    print(f"\n[+] Failure Prediction:")
    print(f" -> Status: {pred['status']}")
    print(f" -> Predicted Failure Milestone: Day {pred['failure_day']:.1f}")
    print(f" -> Regression R2: {pred['regression_r2']:.6f}")
    
    # Plot results
    plot_path = os.path.join(SATELLITE_DIR, "thermal", "aging_degradation_trends.png")
    plot_degradation_trends(df_results, plot_path)
    
    # Generate report
    generate_aging_report(df_results, pred)
    print("\n[+] Phase T25 execution completed successfully.\n")


if __name__ == '__main__':
    main()
