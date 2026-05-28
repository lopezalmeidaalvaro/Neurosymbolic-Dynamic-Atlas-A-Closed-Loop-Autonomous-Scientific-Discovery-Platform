#!/usr/bin/env python3
"""
Stiffness Benchmark - Runs a comparative study of standard integration solvers (RK45, Radau, BDF)
under highly stiff transient spacecraft thermal environments.
Author: Alvaro Lopez Almeida
"""

import os
import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path

# Add project root and register config paths
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config

from thermal.multi_node_thermal_network import ThermalNetwork

def run_benchmark():
    print("Initiating Numerical Stiffness Benchmark...")
    
    # We will simulate high-frequency rapid thermal cycling to exaggerate stiff transients
    # Set C very small for CPU (low thermal inertia) and large Q (high power oscillations)
    config_dict = {
        "C": [10.0, 500.0, 300.0, 1000.0, 200.0, 300.0],  # Stiff: CPU C is extremely small (10 J/K instead of 200 J/K)
        "Q": [50.0, 1.0, 5.0, 0.0, 0.0, 0.0],           # Stiff: High power input Q=50W
    }
    
    # Rapid shadow eclipse cycle (frequency of 3 minutes eclipse out of 10 minutes orbits)
    def rapid_solar_flux(time_sec):
        t_mod = time_sec % 600.0 # 10 minute period
        if t_mod < 180.0:        # 3 minute rapid shadow eclipse
            return 0.0
        return 1361.0 * 0.8 * 0.20 * max(0.0, np.cos((2.0 * np.pi * t_mod) / 600.0))
        
    net = ThermalNetwork(config_dict)
    
    solvers = ["RK45", "Radau", "BDF"]
    results = {}
    
    # Duration: 3 orbits (1800 seconds total)
    duration = 1800.0
    dt = 1.0
    
    print("\n--- Solver Performance Evaluation ---")
    for solver in solvers:
        t_start = time.time()
        try:
            res = net.simulate(
                duration=duration,
                dt=dt,
                orbit_period=600.0,
                initial_temp=293.15,
                Q_solar_func=rapid_solar_flux,
                solver_method=solver
            )
            elapsed = time.time() - t_start
            
            # Compute trajectory properties
            temps = np.array(res["temperatures"])
            max_cpu = np.max(temps[0])
            min_cpu = np.min(temps[0])
            
            results[solver] = {
                "status": "SUCCESS",
                "time_sec": elapsed,
                "max_cpu_temp": max_cpu,
                "min_cpu_temp": min_cpu,
                "error": None
            }
            print(f" -> {solver:5s} | Status: SUCCESS | Elapsed: {elapsed:6.4f}s | CPU bounds: [{min_cpu:5.2f}C, {max_cpu:5.2f}C]")
        except Exception as e:
            elapsed = time.time() - t_start
            results[solver] = {
                "status": "FAILED",
                "time_sec": elapsed,
                "max_cpu_temp": -1.0,
                "min_cpu_temp": -1.0,
                "error": str(e)
            }
            print(f" -> {solver:5s} | Status: FAILED  | Elapsed: {elapsed:6.4f}s | Error: {e}")
            
    # Compile a beautiful Markdown scientific report
    report_lines = [
        "# Spacecraft Thermo-Avionics Numerical Stiffness Report",
        f"\n**Compiled:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "\nThis document outlines the comparative performance and stability bounds of standard integration solvers (RK45, Radau, BDF) when solving the transient spacecraft thermal 6-node network under rapid eclipse transitions.\n",
        "## 1. Experimental Setup",
        "- **Physical Nodes**: 6 coupled nodes (CPU, Battery, Payload, Structure, Radiator, Panels)",
        "- **Stiff Stimulus**: Low CPU thermal mass ($C_{\\text{cpu}} = 10\\text{ J/K}$) and high heating power ($Q_{\\text{cpu}} = 50\\text{ W}$)",
        "- **Rapid Orbit**: 10 minutes (600s) period with a 3-minute eclipse shadow shadow transitions ($1361\\text{ W/m}^2$ to $0\\text{ W/m}^2$)",
        "- **Simulation Duration**: 1800 seconds (30 minutes)\n",
        "## 2. Solver Evaluation Matrix\n",
        "| Solver | Status | Runtime (s) | Min CPU Temp (°C) | Max CPU Temp (°C) |",
        "| :--- | :---: | :---: | :---: | :---: |"
    ]
    
    for solver in solvers:
        data = results[solver]
        if data["status"] == "SUCCESS":
            report_lines.append(f"| **{solver}** | SUCCESS | {data['time_sec']:.4f}s | {data['min_cpu_temp']:.2f}°C | {data['max_cpu_temp']:.2f}°C |")
        else:
            report_lines.append(f"| **{solver}** | FAILED | {data['time_sec']:.4f}s | N/A | N/A |")
            
    report_lines.extend([
        "\n## 3. Scientific Discussion & Guidelines",
        "\n### Numerical Stiffness Phenomenon",
        "> [!IMPORTANT]",
        "> **What is Stiffness in Spacecraft Thermal Networks?**",
        "> Spacecraft digital twins combine elements with highly contrasting thermal timescales. A CPU is extremely small and dissipates or gathers heat rapidly (seconds), whereas the structural aluminum mass is heavy and absorbs heat over hours. This massive difference in time constants creates **stiff ordinary differential equations (ODEs)**.",
        "\n### Solver Selection Guidelines:",
        "1. **Non-Stiff Scenarios (Nominal Cubesats):**",
        "   - **RK45 (Runge-Kutta 4th/5th order)** is highly efficient and standard. It provides fast execution with moderate steps.",
        "2. **Stiff Scenarios (Avionics Throttling, Swift Eclipses, Small Nodes):**",
        "   - **Radau (implicit Runge-Kutta of Radau IIA family)** is the canonical choice. It maintains perfect stability without requiring step sizes near zero, preventing infinite loops or silent divergences.",
        "   - **BDF (Backward Differentiation Formula)** is extremely reliable for stiff systems, utilizing implicit backward integrations to guarantee convergence in stiff regimes."
    ])
    
    # Save the report
    script_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(script_dir, "stiffness_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"\n[+] Generated scientific stiffness report at: {report_path}")

if __name__ == "__main__":
    run_benchmark()
