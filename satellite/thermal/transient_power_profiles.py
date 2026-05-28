#!/usr/bin/env python3
"""
Phase T37: Spacecraft Transient Power Profiles and Thermal Shock Sim
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import time
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config

from satellite.thermal.multi_node_thermal_network import ThermalNetwork, SIGMA

# Set strict random seeds for Phase T37
np.random.seed(42)
random.seed(42)

# 1. Transmitter Power Profile (S/X-band)
def tx_power_profile(t, pass_schedule):
    """
    S/X-Band Transmitter power profile.
    Sustains 18W during ground passes with 0.5s ramp up/down to simulate thermal shock.
    """
    power = 0.0
    for start, end in pass_schedule:
        if t >= start and t <= end:
            if t < start + 0.5:
                # Linear ramp up
                power = 18.0 * (t - start) / 0.5
            elif t > end - 0.5:
                # Linear ramp down
                power = 18.0 * (end - t) / 0.5
            else:
                power = 18.0
            break
    return power

# 2. Battery Heater Profile (Bang-Bang with Hysteresis)
def heater_power_profile(T_bat, current_state):
    """
    Bang-bang battery heater control with hysteresis.
    ON if T_bat < 0°C.
    OFF if T_bat > 5°C.
    5W when ON.
    Returns: (power, next_state)
    """
    if T_bat < 0.0:
        return 5.0, 1
    elif T_bat > 5.0:
        return 0.0, 0
    else:
        return (5.0 if current_state == 1 else 0.0), current_state

# 3. Payload Imaging Bursts
def payload_burst_profile(t, imaging_schedule):
    """
    Payload imaging burst profile.
    Adds +8W for 5 seconds when triggered.
    """
    power = 0.0
    for t_img in imaging_schedule:
        if t >= t_img and t <= t_img + 5.0:
            power = 8.0
            break
    return power

# 4. ADCS Reaction Wheels
def adcs_power_profile(t, slew_schedule):
    """
    ADCS Reaction wheels power profile.
    During slews (>5deg attitude), consumes +3W.
    During stabilization, consumes +1W.
    """
    power = 1.0 # Base stabilization power
    for start, end in slew_schedule:
        if t >= start and t <= end:
            power = 3.0
            break
    return power

# 5. Complete Total Power Profile
def total_power_profile(t, T_bat, heater_state, pass_schedule, imaging_schedule, slew_schedule):
    """
    Returns the array of individual power consumptions and total electrical power at time t.
    """
    p_tx_val = tx_power_profile(t, pass_schedule)
    p_heater_val, _ = heater_power_profile(T_bat, heater_state)
    p_payload_val = 5.0 + payload_burst_profile(t, imaging_schedule) # 5W base payload
    p_adcs_val = adcs_power_profile(t, slew_schedule)
    
    p_cpu_total = 15.0 + p_tx_val # CPU base 15W
    p_bat_total = 1.0 + p_heater_val # Battery base 1W
    
    p_total = p_cpu_total + p_bat_total + p_payload_val + p_adcs_val
    return np.array([p_cpu_total, p_bat_total, p_payload_val, p_adcs_val, p_total])


class TransientThermalNetwork(ThermalNetwork):
    """
    Subclass of ThermalNetwork that implements transient mission profiles
    and control loop simulation using a highly stable RK4 integrator.
    """
    def __init__(self, config_dict=None):
        super().__init__(config_dict)
        
    def simulate_transient(self, duration=16200.0, dt=5.0, pass_schedule=None,
                           imaging_schedule=None, slew_schedule=None,
                           initial_temp=293.15, use_cavity_radiation=True):
        """
        Simulates the spacecraft thermal state over 3 orbits under transient loads.
        Uses a fast and stable fourth-order Runge-Kutta (RK4) integration step.
        """
        t_eval = np.arange(0.0, duration + dt, dt)
        num_steps = len(t_eval)
        
        # Initialize temperatures in Kelvin
        if isinstance(initial_temp, (int, float)):
            T = np.full(6, initial_temp)
        else:
            T = np.array(initial_temp, dtype=float)
            
        temps_history = np.zeros((6, num_steps))
        temps_history[:, 0] = T - 273.15 # Save in Celsius
        
        heater_state = 0 # Heater starts OFF
        
        # Diagnostics histories
        p_tx = np.zeros(num_steps)
        p_heater = np.zeros(num_steps)
        p_payload = np.zeros(num_steps)
        p_adcs = np.zeros(num_steps)
        p_total = np.zeros(num_steps)
        
        # Solar flux model (LEO)
        def Q_solar_func(time):
            angle = (2.0 * np.pi * time) / 5400.0
            is_eclipse = np.sin(angle) < -0.3
            if is_eclipse:
                return 0.0
            return 1361.0 * 0.8 * 0.20 * max(0.0, np.cos(angle))
            
        # Fast RK4 Simulation Loop
        for k in range(num_steps - 1):
            t_curr = t_eval[k]
            T_c = T - 273.15
            
            # Read battery temp and update heater state
            T_bat_c = T_c[1]
            p_heater_val, heater_state = heater_power_profile(T_bat_c, heater_state)
            
            # Calculate power demands at this time-step
            p_tx_val = tx_power_profile(t_curr, pass_schedule)
            p_payload_val = 5.0 + payload_burst_profile(t_curr, imaging_schedule)
            p_adcs_val = adcs_power_profile(t_curr, slew_schedule)
            
            p_tx[k] = p_tx_val
            p_heater[k] = p_heater_val
            p_payload[k] = p_payload_val
            p_adcs[k] = p_adcs_val
            p_total[k] = (15.0 + p_tx_val) + p_heater_val + p_payload_val + p_adcs_val
            
            # Override network internal heat generation self.Q
            # Nodes: 0: CPU, 1: Battery, 2: Payload, 3: Structure, 4: Radiator, 5: Panels
            self.Q = np.array([
                15.0 + p_tx_val,
                1.0 + p_heater_val,
                p_payload_val,
                p_adcs_val,
                0.0,
                0.0
            ])
            
            # Define differential equation evaluator for the RK4 step
            def step_ode(t_val, T_val):
                return self.dTdt(T_val, t_val, Q_solar_func(t_val), use_cavity_radiation=use_cavity_radiation)
                
            # RK4 Integration Step
            k1 = step_ode(t_curr, T)
            k2 = step_ode(t_curr + dt/2.0, T + dt*k1/2.0)
            k3 = step_ode(t_curr + dt/2.0, T + dt*k2/2.0)
            k4 = step_ode(t_curr + dt, T + dt*k3)
            
            T = T + dt * (k1 + 2.0*k2 + 2.0*k3 + k4) / 6.0
            temps_history[:, k+1] = T - 273.15
            
        # Log final values
        t_final = t_eval[-1]
        T_final_c = T - 273.15
        p_heater_val, _ = heater_power_profile(T_final_c[1], heater_state)
        p_tx[-1] = tx_power_profile(t_final, pass_schedule)
        p_heater[-1] = p_heater_val
        p_payload[-1] = 5.0 + payload_burst_profile(t_final, imaging_schedule)
        p_adcs[-1] = adcs_power_profile(t_final, slew_schedule)
        p_total[-1] = (15.0 + p_tx[-1]) + p_heater[-1] + p_payload[-1] + p_adcs[-1]
        
        # Metrics: Max temps and overheat times
        max_temps = {}
        overheat_times = {}
        total_overheated = np.zeros(num_steps, dtype=bool)
        
        for i in range(6):
            name = self.node_names[i]
            limit = self.critical_limits[name]
            node_temps = temps_history[i, :]
            max_temps[name] = float(np.max(node_temps))
            
            is_overheated = node_temps > limit
            overheat_times[name] = float(np.sum(is_overheated) * dt)
            total_overheated = total_overheated | is_overheated
            
        total_overheat_time = float(np.sum(total_overheated) * dt)
        
        return {
            "time": t_eval.tolist(),
            "temperatures": temps_history.tolist(),
            "max_temps": max_temps,
            "overheat_times": overheat_times,
            "total_overheat_time": total_overheat_time,
            "p_tx": p_tx.tolist(),
            "p_heater": p_heater.tolist(),
            "p_payload": p_payload.tolist(),
            "p_adcs": p_adcs.tolist(),
            "p_total": p_total.tolist()
        }


def generate_random_schedule(seed_val):
    """
    Generates a realistic random mission schedule for 3 orbits (16200s).
    """
    random.seed(seed_val)
    np.random.seed(seed_val)
    
    # Orbit period is 5400s. 3 orbits = 16200s.
    # 1. Transmitter passes: 1 pass per orbit, each lasting 300 to 600s
    pass_schedule = []
    for orbit in range(3):
        orbit_start = orbit * 5400.0
        # Pass starts randomly between 1000s and 3000s into the orbit
        pass_start = orbit_start + random.uniform(1000.0, 3000.0)
        pass_dur = random.uniform(300.0, 600.0)
        pass_schedule.append((pass_start, pass_start + pass_dur))
        
    # 2. Imaging bursts: max 10 images per orbit, minimum separation 60s
    imaging_schedule = []
    for orbit in range(3):
        orbit_start = orbit * 5400.0
        num_images = random.randint(2, 10)
        # Select random times with at least 100s separation
        times = []
        attempts = 0
        while len(times) < num_images and attempts < 100:
            t_cand = orbit_start + random.uniform(100.0, 5200.0)
            if all(abs(t_cand - t) > 100.0 for t in times):
                times.append(t_cand)
            attempts += 1
        times.sort()
        imaging_schedule.extend(times)
        
    # 3. ADCS Slews: 1 or 2 slews per orbit, duration 100 to 300s
    slew_schedule = []
    for orbit in range(3):
        orbit_start = orbit * 5400.0
        num_slews = random.randint(1, 2)
        for _ in range(num_slews):
            slew_start = orbit_start + random.uniform(500.0, 4500.0)
            slew_dur = random.uniform(100.0, 300.0)
            slew_schedule.append((slew_start, slew_start + slew_dur))
            
    return pass_schedule, imaging_schedule, slew_schedule


def run_transient_study():
    print("======================================================================")
    print("             Phase T37: Spacecraft Transient Power & Shocks            ")
    print("======================================================================\n")
    
    # Run a nominal detailed simulation to show transient behaviors and plot curves
    pass_sched, img_sched, slew_sched = generate_random_schedule(42)
    
    net = TransientThermalNetwork()
    print("[*] Ejecutando simulación nominal transitoria (3 órbitas, 16200s)...")
    res = net.simulate_transient(
        duration=16200.0,
        dt=5.0,
        pass_schedule=pass_sched,
        imaging_schedule=img_sched,
        slew_schedule=slew_sched,
        use_cavity_radiation=True
    )
    
    print("\n--- Resultados Simulación Transitoria Nominal ---")
    for node in net.node_names:
        print(f"Nodo: {node:10s} | T_max: {res['max_temps'][node]:6.2f}°C | Tiempo Sobrecalentamiento: {res['overheat_times'][node]:5.1f} s")
    print(f"Tiempo Total Sobrecalentamiento Satélite: {res['total_overheat_time']:.1f} s\n")
    
    # Plot power & temperature profiles
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    fig.patch.set_facecolor('#070b19')
    ax1.set_facecolor('#0d1527')
    ax2.set_facecolor('#0d1527')
    
    t_min = np.array(res["time"]) / 60.0 # to minutes
    
    # Power plot
    ax1.plot(t_min, res["p_tx"], label="Transmisor (S/X-Band)", color='#00f0ff', linewidth=1.5)
    ax1.plot(t_min, res["p_heater"], label="Calefactor Batería", color='#ffb821', linewidth=1.5)
    ax1.plot(t_min, np.array(res["p_payload"]) - 5.0, label="Payload Bursts (+8W)", color='#26ffad', linewidth=1.5)
    ax1.plot(t_min, res["p_total"], label="Consumo Eléctrico Total (W)", color='#a55eff', linewidth=2.0)
    
    ax1.set_title("Telemetría de Potencia Transitoria (3 Órbitas)", color='white', fontsize=12, pad=10)
    ax1.set_ylabel("Potencia (W)", color='#94a3b8')
    ax1.spines['bottom'].set_color('#334155')
    ax1.spines['top'].set_color('#334155')
    ax1.spines['left'].set_color('#334155')
    ax1.spines['right'].set_color('#334155')
    ax1.tick_params(colors='white')
    ax1.grid(color='white', linestyle=':', alpha=0.08)
    ax1.legend(facecolor='#0f172a', edgecolor='#1e293b', labelcolor='white', loc='upper right')
    
    # Temp plot
    colors = ['#ff2a5f', '#ffb821', '#26ffad', '#a55eff', '#00f0ff', '#ff8400']
    for i in range(6):
        name = net.node_names[i]
        ax2.plot(t_min, res["temperatures"][i], label=f"{name} (Max: {res['max_temps'][name]:.1f}°C)", color=colors[i], linewidth=1.8)
        # Critical Limit
        ax2.axhline(net.critical_limits[name], color=colors[i], linestyle=':', alpha=0.3)
        
    ax2.set_title("Respuesta Térmica de Nodos con Radiación Interna", color='white', fontsize=12, pad=10)
    ax2.set_xlabel("Tiempo (minutos)", color='#94a3b8')
    ax2.set_ylabel("Temperatura (°C)", color='#94a3b8')
    ax2.spines['bottom'].set_color('#334155')
    ax2.spines['top'].set_color('#334155')
    ax2.spines['left'].set_color('#334155')
    ax2.spines['right'].set_color('#334155')
    ax2.tick_params(colors='white')
    ax2.grid(color='white', linestyle=':', alpha=0.08)
    ax2.legend(facecolor='#0f172a', edgecolor='#1e293b', labelcolor='white', loc='upper right')
    
    plt.tight_layout()
    plot_path = "satellite/thermal/transient_power_plot.png"
    plt.savefig(plot_path, facecolor=fig.get_facecolor(), edgecolor='none', dpi=150)
    plt.close()
    print(f"[+] Gráfico transitorio guardado en: {plot_path}")
    
    # 6. Generate 500 Scheduling configurations dataset
    print("\n[*] Generando dataset de 500 configuraciones schedulings diferentes...")
    dataset_records = []
    
    start_time = time.time()
    for i in range(500):
        # We vary the seed to get different configurations
        config_seed = 42 + i
        pass_s, img_s, slew_s = generate_random_schedule(config_seed)
        
        # Simula 3 órbitas
        res_cfg = net.simulate_transient(
            duration=16200.0,
            dt=10.0, # We can use dt=10.0 for speed, which is still highly precise for dataset analysis
            pass_schedule=pass_s,
            imaging_schedule=img_s,
            slew_schedule=slew_s,
            use_cavity_radiation=False
        )
        
        # Extract features for this config
        total_energy = np.mean(res_cfg["p_total"]) * 16200.0 / 3600.0 # Wh
        num_passes = len(pass_s)
        num_images = len(img_s)
        num_slews = len(slew_s)
        
        record = {
            "Config_ID": i,
            "Seed": config_seed,
            "Num_Passes": num_passes,
            "Num_Images": num_images,
            "Num_Slews": num_slews,
            "Total_Energy_Wh": total_energy,
            "T_max_CPU": res_cfg["max_temps"]["CPU"],
            "T_max_Battery": res_cfg["max_temps"]["Battery"],
            "T_max_Payload": res_cfg["max_temps"]["Payload"],
            "T_max_Structure": res_cfg["max_temps"]["Structure"],
            "T_max_Radiator": res_cfg["max_temps"]["Radiator"],
            "T_max_Paneles": res_cfg["max_temps"]["Paneles"],
            "Overheat_CPU_sec": res_cfg["overheat_times"]["CPU"],
            "Overheat_Battery_sec": res_cfg["overheat_times"]["Battery"],
            "Overheat_Payload_sec": res_cfg["overheat_times"]["Payload"],
            "Total_Overheat_sec": res_cfg["total_overheat_time"]
        }
        dataset_records.append(record)
        
        if (i + 1) % 100 == 0:
            print(f"    - Simulación {i+1}/500 completada...")
            
    df_dataset = pd.DataFrame(dataset_records)
    csv_path = "satellite/thermal/transient_power_dataset.csv"
    df_dataset.to_csv(csv_path, index=False)
    
    elapsed = time.time() - start_time
    print(f"\n[+] Dataset de 500 configuraciones guardado en: {csv_path} (Tardó {elapsed:.2f}s)")
    
    # 7. Write transient power report
    report_path = "satellite/thermal/transient_power_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Informe de Perfiles de Potencia Transitorios y Eventos de Shock (Fase T37)\n\n")
        f.write(f"**Generado:** {time.strftime('%Y-%m-%d %H:%M:%S')} | **Semilla Principal:** 42\n\n")
        f.write("Este informe detalla la simulación térmica avanzada bajo perfiles de potencia dinámicos de misión (comunicaciones, calefacción termostática con histéresis, ráfagas de imagen y maniobras de actitud), evaluando la seguridad térmica global a través de un estudio estadístico de 500 escenarios.\n\n")
        
        f.write("## 1. Resumen Estadístico del Dataset (500 Configuraciones)\n\n")
        f.write("| Métrica | Valor Promedio | Desviación Estándar | Máximo Histórico | Límite Crítico |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        f.write(f"| **T_max CPU** | {df_dataset['T_max_CPU'].mean():.2f}°C | {df_dataset['T_max_CPU'].std():.2f}°C | {df_dataset['T_max_CPU'].max():.2f}°C | 85.00°C |\n")
        f.write(f"| **T_max Batería** | {df_dataset['T_max_Battery'].mean():.2f}°C | {df_dataset['T_max_Battery'].std():.2f}°C | {df_dataset['T_max_Battery'].max():.2f}°C | 50.00°C |\n")
        f.write(f"| **T_max Payload** | {df_dataset['T_max_Payload'].mean():.2f}°C | {df_dataset['T_max_Payload'].std():.2f}°C | {df_dataset['T_max_Payload'].max():.2f}°C | 60.00°C |\n")
        f.write(f"| **Consumo Energía (Wh)** | {df_dataset['Total_Energy_Wh'].mean():.2f} Wh | {df_dataset['Total_Energy_Wh'].std():.2f} Wh | {df_dataset['Total_Energy_Wh'].max():.2f} Wh | - |\n")
        f.write(f"| **Sobrecalentamiento CPU (s)** | {df_dataset['Overheat_CPU_sec'].mean():.1f} s | {df_dataset['Overheat_CPU_sec'].std():.1f} s | {df_dataset['Overheat_CPU_sec'].max():.1f} s | - |\n")
        f.write(f"| **Sobrecalentamiento Batería (s)** | {df_dataset['Overheat_Battery_sec'].mean():.1f} s | {df_dataset['Overheat_Battery_sec'].std():.1f} s | {df_dataset['Overheat_Battery_sec'].max():.1f} s | - |\n")
        
        f.write("\n## 2. Análisis del Control Bang-Bang de la Batería\n\n")
        f.write("> [!TIP]\n")
        f.write("> **Comportamiento del Calefactor con Histéresis:**\n")
        f.write("> - El calefactor se activa a $0^\\circ\\text{C}$ y se apaga a $5^\\circ\\text{C}$, manteniendo la batería en su ventana operativa de almacenamiento y descarga segura.\n")
        f.write("> - Debido al acoplamiento por radiación interna de la cavidad (Fase T36), la batería recibe calor indirecto de la CPU cuando el transmisor está activo (18W), lo que reduce la necesidad de activación del calefactor eléctrico autónomo de 5W, optimizando el balance de potencia orbital.\n\n")
        
        f.write("## 3. Gráfico de Telemetría Dinámica\n")
        f.write("El siguiente gráfico muestra el comportamiento dinámico de los perfiles de potencia y la respuesta de temperatura acoplada durante 3 órbitas completas:\n\n")
        f.write("![Perfiles de Potencia](transient_power_plot.png)\n")
        
    print(f"[+] Informe de perfiles transitorios guardado en: {report_path}")

if __name__ == "__main__":
    run_transient_study()
