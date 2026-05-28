#!/usr/bin/env python3
"""
Phase T9: Multi-Node Thermal Network Solver for LEO Cubesat
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import numpy as np
import scipy.integrate
import matplotlib.pyplot as plt

# Ensure reproducible simulations
np.random.seed(42)

# Physical Constants
SIGMA = 5.67e-8  # W/(m2 K4) - Stefan-Boltzmann constant
T_SPACE = 2.7    # K - Temperature of deep space

class ThermalNetwork:
    """
    Solves the 6-node coupled thermodynamic heat balance equations for a Cubesat.
    Nodes:
      0: CPU (Main heat source)
      1: Battery
      2: Payload
      3: Structure (Bus)
      4: Radiator (Space dissipation)
      5: Solar Panels (Solar absorption)
    """
    
    def __init__(self, config_dict=None):
        """
        Initializes the 6 nodes with their thermal capacity, surface properties,
        internal power generation, and coupling conductances.
        """
        # Load default parameters
        self.node_names = ["CPU", "Battery", "Payload", "Structure", "Radiator", "Paneles"]
        
        # Default configuration
        self.C = np.array([200.0, 500.0, 300.0, 1000.0, 200.0, 300.0]) # J/K
        self.Q = np.array([15.0, 1.0, 5.0, 0.0, 0.0, 0.0])             # W (Internal generation)
        self.eps = np.array([0.1, 0.1, 0.1, 0.2, 0.85, 0.1])           # Emissivity
        self.A = np.array([0.01, 0.02, 0.01, 0.10, 0.15, 0.20])        # Radiating Area (m2)
        
        # Conductance matrix (k_ij in W/K)
        # Symmetrical matrix of connections
        self.k = np.zeros((6, 6))
        self.k[0, 3] = self.k[3, 0] = 2.0  # CPU-Structure
        self.k[1, 3] = self.k[3, 1] = 0.5  # Battery-Structure
        self.k[2, 3] = self.k[3, 2] = 1.5  # Payload-Structure
        self.k[4, 3] = self.k[3, 4] = 5.0  # Radiator-Structure
        self.k[5, 3] = self.k[3, 5] = 0.8  # Panels-Structure
        
        # Override with custom config if provided
        if config_dict:
            if "C" in config_dict: self.C = np.array(config_dict["C"])
            if "Q" in config_dict: self.Q = np.array(config_dict["Q"])
            if "eps" in config_dict: self.eps = np.array(config_dict["eps"])
            if "A" in config_dict: self.A = np.array(config_dict["A"])
            if "k" in config_dict: self.k = np.array(config_dict["k"])
            
        # Critical temperatures limits in Celsius
        self.critical_limits = {
            "CPU": 85.0,
            "Battery": 50.0,
            "Payload": 60.0,
            "Structure": 80.0,
            "Radiator": 100.0,
            "Paneles": 120.0
        }

    def dTdt(self, T_vector, t, Q_solar):
        """
        Computes the temperature derivatives for all 6 nodes.
        Equation:
          C_i * dT_i/dt = Q_internal_i + Q_solar_i + Sum_j k_ij * (T_j - T_i) - eps_i * sigma * A_i * (T_i^4 - T_space^4)
        """
        dT = np.zeros(6)
        for i in range(6):
            # Internal heat generation
            Q_in = self.Q[i]
            
            # Solar panels absorb the direct external solar input Q_solar
            if i == 5:
                Q_in += Q_solar
                
            # Conduction coupling terms Sum_j k_ij * (T_j - T_i)
            Q_cond = 0.0
            for j in range(6):
                if self.k[i, j] > 0.0:
                    Q_cond += self.k[i, j] * (T_vector[j] - T_vector[i])
                    
            # Radiative heat rejection to space: eps_i * sigma * A_i * (T_i^4 - T_space^4)
            Q_rad = self.eps[i] * SIGMA * self.A[i] * (T_vector[i]**4 - T_SPACE**4)
            
            # Rate of temperature change
            dT[i] = (Q_in + Q_cond - Q_rad) / self.C[i]
            
        return dT

    def simulate(self, duration=5400, dt=5.0, orbit_period=5400, initial_temp=293.15, Q_solar_func=None, solver_method='Radau'):
        """
        Simulates the thermal network over the specified duration.
        Uses solve_ivp to integrate the coupled ODE system.
        """
        # Ensure that t_eval contains values strictly within [0, duration] to satisfy solve_ivp
        t_eval = np.arange(0.0, duration, dt)
        if len(t_eval) == 0 or t_eval[-1] < duration:
            t_eval = np.append(t_eval, duration)
        
        # Initial state: 20 degrees Celsius for all nodes unless specified
        if isinstance(initial_temp, (int, float)):
            T0 = np.full(6, initial_temp)
        else:
            T0 = np.array(initial_temp)
            
        # Default Solar flux model (Eclipse/Sun cycle) if no custom function is provided
        if Q_solar_func is None:
            # Let's model a standard eclipse fraction ~35%
            # Solar panel area = 0.20 m2, absorptivity = 0.8, flux = 1361 W/m2 -> Max solar power ~217 W
            def default_solar_flux(time):
                angle = (2.0 * np.pi * time) / orbit_period
                is_eclipse = np.sin(angle) < -0.3
                if is_eclipse:
                    return 0.0
                return 1361.0 * 0.8 * 0.20 * max(0.0, np.cos(angle))
            Q_solar_func = default_solar_flux

        # ODE system wrapper to match solve_ivp format
        def ode_system(t, y):
            q_solar_val = Q_solar_func(t)
            return self.dTdt(y, t, q_solar_val)

        # Integrate using Radau/RK45/BDF
        sol = scipy.integrate.solve_ivp(
            ode_system,
            (0.0, duration),
            T0,
            t_eval=t_eval,
            method=solver_method,
            rtol=1e-6,
            atol=1e-6
        )
        
        # Convert Kelvin back to Celsius for metrics and visualization
        temps_k = sol.y
        temps_c = temps_k - 273.15
        
        # Calculate max temperatures per node
        max_temps = {}
        for i in range(6):
            max_temps[self.node_names[i]] = float(np.max(temps_c[i]))
            
        # Calculate time_to_critical per node
        time_to_critical = {}
        for i in range(6):
            name = self.node_names[i]
            limit = self.critical_limits[name]
            # Find first index where limit is crossed
            crossed_indices = np.where(temps_c[i] >= limit)[0]
            if len(crossed_indices) > 0:
                time_to_critical[name] = float(sol.t[crossed_indices[0]])
            else:
                time_to_critical[name] = -1.0 # Safe or never reached
                
        result = {
            "time": sol.t.tolist(),
            "temperatures": temps_c.tolist(),
            "temperatures_k": temps_k.tolist(),
            "max_temps": max_temps,
            "time_to_critical": time_to_critical
        }
        return result

    def detect_hotspots(self, result):
        """
        Identifies nodes that exceed their thermal critical thresholds.
        """
        hotspots = []
        for i, name in enumerate(self.node_names):
            limit = self.critical_limits[name]
            max_t = result["max_temps"][name]
            if max_t > limit:
                hotspots.append({
                    "node": name,
                    "max_temp": max_t,
                    "limit": limit,
                    "exceeded_by": max_t - limit
                })
        return hotspots

    def compute_thermal_gradients(self, result):
        """
        Computes the maximum thermal gradient (T_i - T_j) for all coupled nodes.
        """
        gradients = {}
        temps = np.array(result["temperatures"])
        
        # Track connections with non-zero conductances
        for i in range(6):
            for j in range(i+1, 6):
                if self.k[i, j] > 0.0:
                    grad_profile = np.abs(temps[i] - temps[j])
                    max_grad = float(np.max(grad_profile))
                    gradients[f"{self.node_names[i]}-{self.node_names[j]}"] = max_grad
        return gradients

    def plot_network(self, result, output_path=None):
        """
        Renders a highly styled professional dark-mode thermal telemetry plot.
        """
        times = np.array(result["time"]) / 60.0 # to minutes
        temps = np.array(result["temperatures"])
        
        fig, ax = plt.subplots(figsize=(11, 6))
        fig.patch.set_facecolor('#070b19')
        ax.set_facecolor('#0d1527')
        
        colors = ['#ff2a5f', '#ffb821', '#26ffad', '#a55eff', '#00f0ff', '#ff8400']
        styles = ['-', '--', '-.', ':', '-', '--']
        
        for i in range(6):
            name = self.node_names[i]
            limit = self.critical_limits[name]
            ax.plot(times, temps[i], label=f"{name} (Max: {result['max_temps'][name]:.1f}°C)", 
                    color=colors[i], linestyle=styles[i], linewidth=2.0)
            # Add subtle dotted critical limit lines
            ax.axhline(limit, color=colors[i], linestyle=':', alpha=0.3)
            
        ax.set_title("LEO Cubesat Multi-Node Thermal Network Simulation", color='white', fontsize=14, pad=15)
        ax.set_xlabel("Time (minutes)", color='#94a3b8', fontsize=11)
        ax.set_ylabel("Temperature (°C)", color='#94a3b8', fontsize=11)
        
        ax.spines['bottom'].set_color('#334155')
        ax.spines['top'].set_color('#334155')
        ax.spines['left'].set_color('#334155')
        ax.spines['right'].set_color('#334155')
        ax.tick_params(colors='white')
        ax.grid(color='white', linestyle=':', alpha=0.08)
        
        leg = ax.legend(facecolor='#0f172a', edgecolor='#1e293b', labelcolor='white', loc='upper right')
        
        plt.tight_layout()
        
        if output_path:
            dir_name = os.path.dirname(output_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', dpi=150)
            print(f"[+] Saved multi-node network plot to: {output_path}")
        plt.close()

def run_baselines():
    """
    Runs default configuration scenarios:
      1. Nominal: CPU=15W, payload=5W, radiator=0.15m2
      2. High Load: CPU=30W, payload=10W, radiator=0.15m2
      3. Eclipse: CPU=15W, payload=5W, solar=0 for 35 minutes
    """
    print("[*] Running Baseline Configurations...")
    
    # 1. Nominal scenario
    net_nominal = ThermalNetwork()
    res_nominal = net_nominal.simulate(duration=5400)
    net_nominal.plot_network(res_nominal, "thermal_network_nominal.png")
    
    # 2. High Load scenario
    config_high = {
        "Q": [30.0, 1.0, 10.0, 0.0, 0.0, 0.0]
    }
    net_high = ThermalNetwork(config_high)
    res_high = net_high.simulate(duration=5400)
    net_high.plot_network(res_high, "thermal_network_high_load.png")
    
    # 3. Eclipse scenario
    # Q_solar is 0 during 35min (2100s) out of 90min (5400s) orbit cycle
    def eclipse_solar_flux(time):
        t_mod = time % 5400
        if t_mod < 2100: # First 35 minutes in shadow
            return 0.0
        # Normal sun flux
        angle = (2.0 * np.pi * t_mod) / 5400
        return 1361.0 * 0.8 * 0.20 * max(0.0, np.cos(angle))
        
    net_eclipse = ThermalNetwork()
    res_eclipse = net_eclipse.simulate(duration=5400, Q_solar_func=eclipse_solar_flux)
    net_eclipse.plot_network(res_eclipse, "thermal_network_eclipse.png")
    
    # Simple report print
    print("\n=== BASELINE SIMULATION DIAGNOSTICS ===")
    for name, res in [("Nominal", res_nominal), ("High Load", res_high), ("Eclipse", res_eclipse)]:
        print(f"\n[{name} Scenario]")
        for node in ["CPU", "Battery", "Structure"]:
            print(f" -> {node} Max Temp: {res['max_temps'][node]:.2f}°C, Time to Critical: {res['time_to_critical'][node]}")
        hotspots = net_nominal.detect_hotspots(res)
        if hotspots:
            print(f" [CRITICAL] Hotspots detected: {hotspots}")
        else:
            print(" [SAFE] All nodes within safety margins.")
            
if __name__ == '__main__':
    run_baselines()
