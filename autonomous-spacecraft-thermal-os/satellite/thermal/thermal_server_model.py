#!/usr/bin/env python3
"""
Thermal Server Model - Physics of a server in orbital vacuum.
Author: Alvaro Lopez Almeida
"""

import numpy as np
import matplotlib.pyplot as plt

class ThermalServerModel:
    """
    Simulates the thermal dynamics of a spacecraft server operating in orbital vacuum.
    Uses a lumped capacitance thermal model without duplicating thermal mass.
    """
    
    stefan_boltzmann = 5.67e-8
    ambient_temp_K = 2.7
    critical_temp_K = 85.0 + 273.15  # 85°C in Kelvin (358.15 K)

    def __init__(self, power, area, emissivity, heat_capacity=500.0, initial_temp=293.15):
        """
        Constructor.
        :param power: Heat generation power Q_gen in Watts.
        :param area: Radiative area A in m^2.
        :param emissivity: Surface emissivity ε.
        :param heat_capacity: Total heat capacity in J/K (Default: 500 J/K).
        :param initial_temp: Initial temperature in Kelvin (Default: 20°C = 293.15 K).
        """
        self.power = float(power)
        self.area = float(area)
        self.emissivity = float(emissivity)
        self.heat_capacity = float(heat_capacity)
        self.initial_temp = float(initial_temp)

    def dTdt(self, T, t=0.0):
        """
        Governing ODE: dT/dt = (Q_gen - ε * σ * A * (T^4 - T_amb^4)) / heat_capacity
        :param T: Temperature in Kelvin.
        :param t: Time in seconds (not used in autonomous system).
        :return: Temperature rate of change dT/dt in K/s.
        """
        Q_rad = self.emissivity * self.stefan_boltzmann * self.area * (T**4 - self.ambient_temp_K**4)
        dT_dt = (self.power - Q_rad) / self.heat_capacity
        return float(dT_dt)

    def simulate(self, duration=3600.0, dt=10.0):
        """
        Runs Euler numerical integration to simulate temperature trajectory.
        :param duration: Total simulation time in seconds.
        :param dt: Time step in seconds.
        :return: dict with time, temperature, max_temp, time_to_critical, and temperature_map_2D.
        """
        steps = int(duration / dt) + 1
        times = np.linspace(0.0, duration, steps)
        temps = np.zeros(steps)
        
        T = self.initial_temp
        temps[0] = T
        
        time_to_critical = None
        
        for i in range(1, steps):
            T_prev = T
            T = T + self.dTdt(T) * dt
            temps[i] = T
            
            # Check critical temperature (85°C = 358.15 K)
            if T >= self.critical_temp_K and time_to_critical is None:
                if T_prev < self.critical_temp_K:
                    t_prev = times[i-1]
                    fraction = (self.critical_temp_K - T_prev) / (T - T_prev) if (T - T_prev) != 0 else 0.0
                    time_to_critical = float(t_prev + fraction * dt)
                else:
                    time_to_critical = 0.0
            
        # Final check if the last state reached critical temp
        if T >= self.critical_temp_K and time_to_critical is None:
            time_to_critical = float(times[-1])

        # Temperature in Celsius for analytics and user convenience
        temps_C = temps - 273.15
        max_temp_C = float(np.max(temps_C))
        
        # Calculate 2D Temperature Map (32x32 grid)
        # Center of grid is at (15.5, 15.5) for indices 0 to 31
        grid_size = 32
        temperature_map_2D = np.zeros((grid_size, grid_size))
        
        T_media_C = float(np.mean(temps_C))
        T_max_C = float(np.max(temps_C))
        T_amb_C = self.ambient_temp_K - 273.15
        
        delta_T = 0.1 * (T_max_C - T_amb_C)
        sigma_gauss = 0.3
        
        # Generate stable normal noise using fixed numpy random seed locally if needed
        # Or standard numpy normal distribution
        noise = np.random.normal(0.0, 0.01 * np.abs(T_media_C), size=(grid_size, grid_size))
        
        for i in range(grid_size):
            for j in range(grid_size):
                # Normalized distance to center from [-1, 1]
                x = (i - 15.5) / 15.5
                y = (j - 15.5) / 15.5
                r = np.sqrt(x**2 + y**2)
                
                T_celda = T_media_C + delta_T * np.exp(-r**2 / (sigma_gauss**2)) + noise[i, j]
                temperature_map_2D[i, j] = T_celda
                
        return {
            "time": times.tolist(),
            "temperature": temps_C.tolist(),
            "max_temp": max_temp_C,
            "time_to_critical": time_to_critical,
            "temperature_map_2D": temperature_map_2D.tolist()
        }

    def steady_state_temp(self):
        """
        Analytical steady-state temperature: T_eq = (Q_gen / (ε * σ * A) + T_amb^4)^(1/4)
        :return: T_eq in Kelvin.
        """
        T_eq_K = (self.power / (self.emissivity * self.stefan_boltzmann * self.area) + self.ambient_temp_K**4) ** 0.25
        return float(T_eq_K)

    def plot(self, output_path=None):
        """
        Plots temperature profile and 2D map. Saves to output_path if provided.
        """
        res = self.simulate()
        t = np.array(res["time"]) / 60.0  # minutes
        T = np.array(res["temperature"])
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        ax1.plot(t, T, 'cyan', linewidth=2, label='Simulation')
        ax1.axhline(85.0, color='red', linestyle='--', label='Critical Temp (85°C)')
        ax1.axhline(self.steady_state_temp() - 273.15, color='orange', linestyle=':', label='Steady State (Analytical)')
        ax1.set_xlabel('Time (minutes)')
        ax1.set_ylabel('Temperature (°C)')
        ax1.set_title('Server Temperature Profile')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        im = ax2.imshow(np.array(res["temperature_map_2D"]), cmap='inferno')
        fig.colorbar(im, ax=ax2, label='Temperature (°C)')
        ax2.set_title('2D Thermal Surface Map (32x32)')
        
        plt.tight_layout()
        if output_path:
            plt.savefig(output_path, dpi=150, facecolor='#0e1117')
            plt.close()
        else:
            plt.show()

if __name__ == "__main__":
    # Test simulation
    model = ThermalServerModel(power=20, area=0.1, emissivity=0.8)
    res = model.simulate()
    print("Test run:")
    print(f"Max Temp: {res['max_temp']:.2f}°C")
    print(f"Time to Critical: {res['time_to_critical']} s")
    print(f"Steady State Temp: {model.steady_state_temp() - 273.15:.2f}°C")
