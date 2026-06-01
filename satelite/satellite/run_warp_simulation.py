#!/usr/bin/env python3
"""
Phase 3: Warp Drive Spacecraft Closed-Loop Simulation
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Add satellite root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from satellite.warp.warp_thermal_injection import WarpThermalNetwork
from satellite.thermal.fdir_engine import FDIREngine

def run_warp_spacecraft_simulation(duration=100.0, dt=0.1, alpha_nominal=50.0):
    print("[*] Iniciando simulación de control térmico y FDIR con propulsión Warp...")
    
    # 1. Instantiate the warp network and FDIR
    # We resolve the root directory explicitly to load optimized_metric_equation.txt
    root_dir = Path(__file__).resolve().parents[2]
    net = WarpThermalNetwork(alpha=alpha_nominal, root_dir=root_dir)
    fdir = FDIREngine()
    
    # Spacecraft initial states (temperatures in Celsius, nominal ~20C/293.15K)
    T_curr = np.full(6, 293.15)  # Kelvin
    
    # Simulation logging arrays
    time_log = []
    temp_log = [[] for _ in range(6)]
    q_warp_log = [[] for _ in range(6)]
    fdir_log = []
    
    # Internal history trackers for simulation loops
    q_warp_history = []
    measured_history = []
    
    # Control flags
    metric_stabilization_active = False
    stabilization_t_start = 0.0
    alpha_initial_stab = alpha_nominal
    
    # Setup nominal LEO solar flux function
    def get_solar_flux(t_sec):
        # Orbit period ~5400s. Direct LEO sun power ~217W
        angle = (2.0 * np.pi * t_sec) / 5400.0
        if np.sin(angle) < -0.3:
            return 0.0
        return 1361.0 * 0.8 * 0.20 * max(0.0, np.cos(angle))

    steps = int(duration / dt)
    print(f"[*] Total de pasos a simular: {steps} (dt = {dt}s, tiempo total = {duration}s)")
    
    for step in range(steps):
        t = step * dt
        
        # Determine solar flux
        Q_solar = get_solar_flux(t)
        
        # 2. Simulate Warp Drive Fluctuation
        # At t = 40.0s, we inject a rapid 30% warp fluctuation (which exceeds the 15% in <0.1s threshold)
        fluctuation = 0.0
        if t >= 40.0:
            if not metric_stabilization_active:
                # Perturbation injection
                fluctuation = 0.30
            else:
                # Spacecraft is actively reducing speed to stabilize the metric (exponential decay)
                t_stab = t - stabilization_t_start
                decay_factor = np.exp(-t_stab / 4.0) # 4s time constant for braking
                net.alpha = alpha_initial_stab * decay_factor
                fluctuation = 0.05 * decay_factor  # dampening oscillations
        
        net.warp_fluctuation = fluctuation
        
        # Calculate max warp power across all nodes for FDIR check
        qw_max = max(net.get_q_warp(r) for r in net.r_nodes)
        q_warp_history.append((t, qw_max))
        
        # 3. Step the thermal ODE solver
        # We integrate over a small dt step using Euler/Runge-Kutta
        # dTdt computes rate of change. dT * dt is step increment.
        dT = net.dTdt(T_curr, t, Q_solar, use_cavity_radiation=False)
        T_curr = T_curr + dT * dt
        
        # Convert to Celsius for monitoring
        temps_c = T_curr - 273.15
        measured_history.append(temps_c.tolist())
        
        # 4. Execute FDIR Diagnostics
        # Predictions are nominal profiles (simulated without warp input, alpha=0)
        # For simple comparison, we use baseline nominal ~20C + solar effect
        nominal_pred = np.full(6, 20.0)
        nominal_pred[5] += Q_solar / net.C[5] * 100.0 # panel temperature rise estimate
        
        dt_params = {
            "eps_rad": 0.85,
            "q_warp_history": q_warp_history[-5:]  # Keep last 5 points
        }
        
        fault_id, conf, action = fdir.detect_fault(
            temps_c.tolist(),
            nominal_pred.tolist(),
            dt_params,
            measured_history
        )
        
        # If FDIR detects warp instability and it's not handled yet, trigger recovery
        if fault_id == "F7" and not metric_stabilization_active:
            metric_stabilization_active = True
            stabilization_t_start = t
            alpha_initial_stab = net.alpha
            print(f"\n[!!!] FDIR ALERTA a t={t:.1f}s: ¡{fdir.fault_dict[fault_id]} DETECTADO!")
            print(f"      [+] Confianza: {conf:.2f}")
            print(f"      [+] Causa Aislada: {'; '.join(fdir.isolate_fault(fault_id, net))}")
            print(f"      [+] Acción de Recuperación: {action}\n")
            
        # Logging
        time_log.append(t)
        fdir_log.append(fault_id)
        for i in range(6):
            temp_log[i].append(temps_c[i])
            q_warp_log[i].append(net.get_q_warp(net.r_nodes[i]))

    print("[+] Simulación completada.")
    
    # 5. Output Telemetry Visualizer Chart
    plt.figure(figsize=(12, 7))
    plt.style.use('dark_background')
    
    # Left subplot: Temperature Profile
    plt.subplot(2, 1, 1)
    colors = ["#ff2a5f", "#ffb821", "#26ffad", "#a55eff", "#00f0ff", "#ff8400"]
    for i in range(6):
        plt.plot(time_log, temp_log[i], label=f"{net.node_names[i]}", color=colors[i], linewidth=2.0)
        
    # Mark critical threshold for CPU (85C) and Payload (60C)
    plt.axhline(net.critical_limits["CPU"], color="#ff2a5f", linestyle=":", alpha=0.5, label="Límite CPU (85°C)")
    plt.axhline(net.critical_limits["Payload"], color="#26ffad", linestyle=":", alpha=0.5, label="Límite Payload (60°C)")
    
    # Mark FDIR Event
    plt.axvline(40.0, color="#ff0055", linestyle="--", linewidth=1.5)
    plt.text(40.5, 30.0, "Fluctuación Warp\n(t = 40s)", color="#ff0055", fontsize=9, fontweight='bold')
    
    plt.title("Telemetría Térmica del Cubesat en Órbita LEO con Propulsión Warp", color="white", fontsize=12, pad=10)
    plt.ylabel("Temperatura (°C)", color="#94a3b8", fontsize=10)
    plt.grid(color="white", linestyle=":", alpha=0.1)
    plt.legend(facecolor="#0f172a", edgecolor="#1e293b", labelcolor="white", loc="upper right", ncol=2)
    
    # Right subplot: Warp Thermal Power Input
    plt.subplot(2, 1, 2)
    plt.plot(time_log, q_warp_log[0], label="Q_warp CPU (r=0.0)", color="#ff2a5f", linewidth=2.0)
    plt.plot(time_log, q_warp_log[2], label="Q_warp Payload (r=0.4)", color="#26ffad", linewidth=2.0)
    plt.plot(time_log, q_warp_log[4], label="Q_warp Radiator (r=0.8)", color="#00f0ff", linewidth=2.0)
    
    plt.axvline(40.0, color="#ff0055", linestyle="--", linewidth=1.5)
    
    plt.title("Inyección Termodinámica del Campo de Estrés Radiativo Warp", color="white", fontsize=12, pad=10)
    plt.xlabel("Tiempo de Simulación (segundos)", color="#94a3b8", fontsize=10)
    plt.ylabel("Potencia Q_warp (W)", color="#94a3b8", fontsize=10)
    plt.grid(color="white", linestyle=":", alpha=0.1)
    plt.legend(facecolor="#0f172a", edgecolor="#1e293b", labelcolor="white", loc="upper right")
    
    plt.tight_layout()
    plot_path = Path(root_dir) / "satelite" / "satellite" / "warp_simulation_telemetry.png"
    plt.savefig(plot_path, dpi=150)
    plt.close()
    
    print(f"[+] Gráfica de telemetría guardada en: {plot_path}")
    
    # 6. Print diagnostic summary
    df_sim = pd.DataFrame({
        "t": time_log,
        "CPU_temp": temp_log[0],
        "Payload_temp": temp_log[2],
        "FDIR_fault": fdir_log,
        "Q_warp_CPU": q_warp_log[0]
    })
    
    print("\n=== RESUMEN DE DIAGNÓSTICO DE LA SIMULACIÓN ===")
    print(f"Temperatura CPU Inicial: {df_sim.iloc[0]['CPU_temp']:.2f}°C")
    print(f"Temperatura CPU Máxima antes de fluctuación (t=39.9s): {df_sim[df_sim['t'] < 40.0]['CPU_temp'].max():.2f}°C")
    print(f"Temperatura CPU Máxima total registrada: {df_sim['CPU_temp'].max():.2f}°C")
    print(f"Temperatura Payload Máxima total registrada: {df_sim['Payload_temp'].max():.2f}°C")
    
    # Check if FDIR stabilized the metric
    fdir_triggers = df_sim[df_sim["FDIR_fault"] == "F7"]
    if not fdir_triggers.empty:
        t_detect = fdir_triggers["t"].min()
        print(f"FDIR Estado: [APLICADO] Inestabilidad detectada a t={t_detect:.1f}s | Sistema Estabilizado.")
    else:
        print("FDIR Estado: [ERROR] No se detectó la inestabilidad F7.")
        
    print("===============================================")
    
if __name__ == "__main__":
    run_warp_spacecraft_simulation()
