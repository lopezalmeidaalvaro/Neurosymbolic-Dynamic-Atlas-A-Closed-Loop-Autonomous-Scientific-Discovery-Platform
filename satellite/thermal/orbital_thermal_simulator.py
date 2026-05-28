#!/usr/bin/env python3
"""
Orbital Thermal Simulator for LEO Spacecraft (Cubesat 1-Node Model)
Author: Alvaro Lopez Almeida
"""

import os
import sys
import math
import argparse
import csv

# Add current dir to path to ensure imports
sys.path.insert(0, os.path.dirname(__file__))

# Physical Constants
C_THERMAL = 135000.0  # J/K (Aluminum thermal mass)
G_SOL = 1361.0        # W/m2 (Solar constant in LEO)
SIGMA = 5.67e-8       # W/m2K4 (Stefan-Boltzmann constant)
T_ORBIT = 5677.0      # seconds (Orbit period ~94.6 mins)
STEP_SIZE = 10.0      # seconds per integration step

def run_simulation(power, area, absorptivity, emissivity, num_orbits=3):
    """
    Solves the spacecraft thermal balance equation numerically.
    m * Cp * dT/dt = Q_solar(t) + Q_earth(t) + P_internal - sigma * eps * A * T^4
    """
    print(f"[*] Starting thermal simulation: P={power}W, A={area}m2, alpha={absorptivity}, eps={emissivity}")
    
    T = 293.15  # Initial temperature 20°C in Kelvin
    steps_per_orbit = int(T_ORBIT / STEP_SIZE)
    total_steps = steps_per_orbit * num_orbits
    
    telemetry = []
    
    for step in range(total_steps):
        time_sec = step * STEP_SIZE
        angle = (2.0 * math.pi * time_sec) / T_ORBIT
        
        # Shadow modeling (LEO Eclipse)
        is_eclipse = math.sin(angle) < -0.3
        
        Q_solar = 0.0
        if not is_eclipse:
            cos_factor = max(0.0, math.cos(angle))
            Q_solar = absorptivity * area * G_SOL * cos_factor
            
        Q_earth = emissivity * area * 230.0  # Earth IR constant (230 W/m2)
        Q_in = Q_solar + Q_earth + power
        
        # Radiator output to deep space (3K)
        Q_out = SIGMA * emissivity * area * (T ** 4)
        
        # Euler integration step
        dT = ((Q_in - Q_out) / C_THERMAL) * STEP_SIZE
        T = T + dT
        
        temp_deg_c = T - 273.15
        
        # Record all points in the final orbit
        if step >= (total_steps - steps_per_orbit):
            orbit_time_min = ((step - (total_steps - steps_per_orbit)) * STEP_SIZE) / 60.0
            telemetry.append({
                'Time_Min': round(orbit_time_min, 2),
                'Temp_C': round(temp_deg_c, 2),
                'Q_Solar_W': round(Q_solar, 2),
                'Q_Rad_Out_W': round(Q_out, 2),
                'Is_Eclipse': int(is_eclipse)
            })
            
    print("[+] Numerical simulation completed successfully.")
    return telemetry

def save_csv(telemetry, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Time_Min', 'Temp_C', 'Q_Solar_W', 'Q_Rad_Out_W', 'Is_Eclipse'])
        writer.writeheader()
        writer.writerows(telemetry)
    print(f"[+] Saved telemetry data to: {file_path}")

def plot_telemetry(telemetry, plot_path, p, a, alpha, eps):
    try:
        import matplotlib.pyplot as plt
        
        times = [pt['Time_Min'] for pt in telemetry]
        temps = [pt['Temp_C'] for pt in telemetry]
        shadows = [pt['Is_Eclipse'] for pt in telemetry]
        
        fig, ax1 = plt.subplots(figsize=(10, 5))
        
        # Draw shadow zones
        for i in range(len(times) - 1):
            if shadows[i] == 1:
                ax1.axvspan(times[i], times[i+1], color='midnightblue', alpha=0.15)
                
        # Plot temperature
        color = 'tab:cyan'
        ax1.set_xlabel('Orbit Time (minutes)', color='white')
        ax1.set_ylabel('Temperature (°C)', color=color)
        ax1.plot(times, temps, color=color, linewidth=2.5, label='Telemetry Temp (°C)')
        ax1.tick_params(axis='y', labelcolor=color)
        
        # Reference limits
        ax1.axhline(85.0, color='red', linestyle='--', alpha=0.6, label='Burnout Limit (85°C)')
        ax1.axhline(-40.0, color='blue', linestyle='--', alpha=0.6, label='Freeze Limit (-40°C)')
        
        # Styles
        fig.patch.set_facecolor('#070b19')
        ax1.set_facecolor('#0d1527')
        ax1.spines['bottom'].set_color('#334155')
        ax1.spines['top'].set_color('#334155')
        ax1.spines['left'].set_color('#334155')
        ax1.tick_params(colors='white')
        ax1.grid(color='white', linestyle=':', alpha=0.05)
        
        plt.title(f"LEO Spacecraft Orbit Thermal Cycle\n(P={p}W, A={a}m2, alpha={alpha}, eps={eps})", color='white', pad=15)
        
        os.makedirs(os.path.dirname(plot_path), exist_ok=True)
        plt.savefig(plot_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
        plt.close()
        print(f"[+] Saved thermal cycle plot to: {plot_path}")
    except ImportError:
        print("[!] matplotlib not installed. Skipping PNG plot generation (CSV generated successfully).")

def main():
    parser = argparse.ArgumentParser(description="Orbital Thermal Simulator for LEO Satellites")
    parser.add_argument("--power", type=float, default=220.0, help="Internal Electrical Power (W)")
    parser.add_argument("--area", type=float, default=2.2, help="Radiator Surface Area (m2)")
    parser.add_argument("--absorptivity", type=float, default=0.28, help="Solar Absorptivity (alpha)")
    parser.add_argument("--emissivity", type=float, default=0.78, help="Infrared Emissivity (epsilon)")
    parser.add_argument("--orbits", type=int, default=3, help="Number of simulated orbits")
    parser.add_argument("--output", type=str, default=None, help="Output CSV path")
    parser.add_argument("--plot", type=str, default=None, help="Output PNG plot path")
    
    args = parser.parse_args()
    
    # Enforce strict physical validation bounds
    if not (0.0 <= args.power <= 1000.0):
        parser.error("Physical bound exceeded: Power must be within [0.0, 1000.0] W.")
    if not (0.01 <= args.area <= 100.0):
        parser.error("Physical bound exceeded: Radiator area must be within [0.01, 100.0] m2.")
    if not (0.01 <= args.absorptivity <= 1.0):
        parser.error("Physical bound exceeded: Solar absorptivity must be within [0.01, 1.0].")
    if not (0.01 <= args.emissivity <= 1.0):
        parser.error("Physical bound exceeded: Infrared emissivity must be within [0.01, 1.0].")
    if not (1 <= args.orbits <= 100):
        parser.error("Boundary exceeded: Orbits count must be within [1, 100].")
        
    # Setup default paths relative to script parent
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_csv = args.output or os.path.join(script_dir, "..", "models", "telemetry.csv")
    output_plot = args.plot or os.path.join(script_dir, "..", "models", "thermal_simulation.png")
    
    # Run simulation
    telemetry = run_simulation(args.power, args.area, args.absorptivity, args.emissivity, args.orbits)
    
    # Save results
    save_csv(telemetry, output_csv)
    plot_telemetry(telemetry, output_plot, args.power, args.area, args.absorptivity, args.emissivity)
    
    # Diagnostic report
    temps = [p['Temp_C'] for p in telemetry]
    min_t, max_t = min(temps), max(temps)
    print(f"\n[Simulation Report]")
    print(f" -> Peak Temperature: {max_t} C")
    print(f" -> Minimum Temperature: {min_t} C")
    
    if max_t > 85.0 or min_t < -40.0:
        print(" [CRITICAL ALERT] Spacecraft exceeds safety limits! Check radiator configurations.")
    elif max_t > 65.0 or min_t < -20.0:
        print(" [WARNING] Moderate thermal stress detected.")
    else:
        print(" [OPTIMAL] Thermal bounds are completely stable.")

if __name__ == '__main__':
    main()
