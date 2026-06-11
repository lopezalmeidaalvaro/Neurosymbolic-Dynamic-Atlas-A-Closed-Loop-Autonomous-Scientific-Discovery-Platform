#!/usr/bin/env python3
"""
Phase T10: Orbital Environment and Physics Engine
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Add current dir to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_node_thermal_network import ThermalNetwork

# Physical constants
R_EARTH = 6371.0e3  # m - Earth radius
MU_EARTH = 3.986e14  # m3/s2 - Earth gravitational parameter
G_SOL = 1361.0  # W/m2 - Solar constant
SIGMA = 5.67e-8  # W/(m2 K4) - Stefan-Boltzmann constant


def compute_orbit_params(altitude_km=400):
    """
    Computes standard orbital parameters for a circular Low Earth Orbit (LEO).
    """
    altitude = altitude_km * 1.0e3  # convert to meters
    a = R_EARTH + altitude

    # Orbital period: T = 2 * pi * sqrt(a^3 / mu)
    period = 2.0 * math.pi * math.sqrt(a**3 / MU_EARTH)

    # Orbital velocity: v = sqrt(mu / a)
    velocity = math.sqrt(MU_EARTH / a)

    # Eclipse angle and fraction: f_eclipse = (1 / pi) * arcsin(R_Earth / a)
    eclipse_ratio = math.asin(R_EARTH / a)
    eclipse_fraction = eclipse_ratio / math.pi

    return {
        "altitude_km": altitude_km,
        "semi_major_axis_m": a,
        "period_sec": period,
        "velocity_m_s": velocity,
        "eclipse_fraction": eclipse_fraction,
        "eclipse_angle_rad": eclipse_ratio,
    }


def solar_flux(t, orbit_params, beta_angle=0):
    """
    Calculates direct incident solar flux on the panels in W/m2.
    Takes into account the orbit angle theta(t) and solar beta angle.
    """
    period = orbit_params["period_sec"]
    eclipse_angle = orbit_params["eclipse_angle_rad"]

    # Orbit position angle (0 is noon, pi is midnight)
    theta = (2.0 * math.pi * t) / period
    theta_mod = theta % (2.0 * math.pi)

    # Shadow check: centered around midnight (pi)
    is_eclipse = (math.pi - eclipse_angle) <= theta_mod <= (math.pi + eclipse_angle)

    if is_eclipse:
        return 0.0, True

    # Sunlit phase
    # Q = Q0 * max(0, cos(theta)) * cos(beta)
    # We model solar incidence angle on panels
    cos_theta = math.cos(theta_mod)
    cos_beta = math.cos(math.radians(beta_angle))

    flux = G_SOL * max(0.0, cos_theta) * cos_beta
    return flux, False


def albedo_flux(t, orbit_params, beta_angle=0):
    """
    Calculates Earth albedo reflected radiation flux in W/m2.
    Reflected sunlight is proportional to incident solar flux and distance-attenuated.
    """
    a_albedo = 0.3  # albedo coefficient of Earth
    a = orbit_params["semi_major_axis_m"]

    # Base solar flux at this instant (without shadow since it is albedo)
    flux_sol, is_eclipse = solar_flux(t, orbit_params, beta_angle)

    if is_eclipse:
        return 0.0

    # Reflected flux: a_albedo * Q_solar * (R_Earth / a)^2
    attenuation = (R_EARTH / a) ** 2
    flux_alb = a_albedo * flux_sol * attenuation
    return flux_alb


def earth_ir_flux(altitude_km=400):
    """
    Returns constant Earth IR outbound flux in LEO (W/m2).
    """
    return 240.0


def total_environmental_flux(t, orbit_params, beta_angle=0):
    """
    Sums all three environmental heat flux sources.
    Returns (total_flux, is_eclipse).
    """
    sol_f, is_eclipse = solar_flux(t, orbit_params, beta_angle)
    alb_f = albedo_flux(t, orbit_params, beta_angle)
    ir_f = earth_ir_flux(orbit_params["altitude_km"])

    total = sol_f + alb_f + ir_f
    return total, is_eclipse


def simulate_with_orbit(network, altitude=400, beta=0, duration=3 * 5400):
    """
    Couples the ThermalNetwork with the LEO orbital environmental flux simulator.
    Runs simulation over specified duration and logs results to a CSV.
    """
    print(f"[*] Starting coupled orbital simulation: Alt={altitude}km, Beta={beta}deg")
    orbit_params = compute_orbit_params(altitude)
    period = orbit_params["period_sec"]

    # Custom solar input function to feed into Node 5 (Solar Panels)
    # The panels absorb solar + albedo + Earth IR
    # Node 5: area=0.20, solar absorptivity=0.8, IR emissivity=0.1
    # Total heat input on Node 5 panels: Q_panels = A_5 * (alpha * (flux_solar + flux_albedo) + eps * flux_IR)
    alpha_solar = 0.8
    eps_panels = network.eps[5]
    A_panels = network.A[5]

    def orbital_heat_func(time):
        sol_f, is_eclipse = solar_flux(time, orbit_params, beta)
        alb_f = albedo_flux(time, orbit_params, beta)
        ir_f = earth_ir_flux(altitude)

        Q_total = A_panels * (alpha_solar * (sol_f + alb_f) + eps_panels * ir_f)
        return Q_total

    # Execute network simulation
    res = network.simulate(
        duration=duration,
        dt=5.0,
        orbit_period=period,
        initial_temp=293.15,
        Q_solar_func=orbital_heat_func,
    )

    # Generate CSV dataset
    time_steps = res["time"]
    temps = res["temperatures"]

    # Compile telemetry structure
    telemetry_rows = []
    for idx, t in enumerate(time_steps):
        sol_f, is_eclipse = solar_flux(t, orbit_params, beta)
        alb_f = albedo_flux(t, orbit_params, beta)
        ir_f = earth_ir_flux(altitude)
        total_f = sol_f + alb_f + ir_f

        row = {
            "Time_s": t,
            "Time_Min": round(t / 60.0, 2),
            "Solar_Flux_W_m2": round(sol_f, 2),
            "Albedo_Flux_W_m2": round(alb_f, 2),
            "Earth_IR_Flux_W_m2": round(ir_f, 2),
            "Total_Flux_W_m2": round(total_f, 2),
            "Is_Eclipse": int(is_eclipse),
            "T_CPU_C": round(temps[0][idx], 2),
            "T_Battery_C": round(temps[1][idx], 2),
            "T_Payload_C": round(temps[2][idx], 2),
            "T_Structure_C": round(temps[3][idx], 2),
            "T_Radiator_C": round(temps[4][idx], 2),
            "T_Panels_C": round(temps[5][idx], 2),
        }
        telemetry_rows.append(row)

    df = pd.DataFrame(telemetry_rows)
    csv_path = "orbital_simulation_results.csv"
    df.to_csv(csv_path, index=False)
    print(f"[+] Saved orbital simulation telemetry to: {csv_path}")

    # Draw a professional orbital thermal telemetry plot
    plot_orbital_results(df, "orbital_simulation_plot.png")

    return res


def plot_orbital_results(df, output_path):
    """
    Generates a premium telemetry plot showing the coupled orbital parameters and temperatures.
    """
    times = df["Time_Min"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    fig.patch.set_facecolor("#070b19")

    # Plot 1: Environmental Heat Fluxes
    ax1.set_facecolor("#0d1527")
    ax1.plot(
        times, df["Solar_Flux_W_m2"], label="Solar Flux", color="#e0f2fe", linewidth=1.8
    )
    ax1.plot(
        times,
        df["Albedo_Flux_W_m2"],
        label="Earth Albedo",
        color="#38bdf8",
        linewidth=1.5,
    )
    ax1.plot(
        times,
        df["Earth_IR_Flux_W_m2"],
        label="Earth IR",
        color="#fb7185",
        linewidth=1.5,
    )
    ax1.plot(
        times,
        df["Total_Flux_W_m2"],
        label="Total Env Flux",
        color="#26ffad",
        linewidth=2.0,
        linestyle="--",
    )

    # Shadow zones
    shadows = df["Is_Eclipse"].values
    for i in range(len(times) - 1):
        if shadows[i] == 1:
            ax1.axvspan(times[i], times[i + 1], color="midnightblue", alpha=0.15)
            ax2.axvspan(times[i], times[i + 1], color="midnightblue", alpha=0.15)

    ax1.set_title(
        "LEO Cubesat Orbital Environment Heat Fluxes",
        color="white",
        fontsize=12,
        pad=10,
    )
    ax1.set_ylabel("Heat Flux (W/m²)", color="#94a3b8")
    ax1.tick_params(colors="white")
    ax1.grid(color="white", linestyle=":", alpha=0.08)
    ax1.legend(facecolor="#0f172a", edgecolor="#1e293b", labelcolor="white")

    # Plot 2: Node Temperatures
    ax2.set_facecolor("#0d1527")
    nodes = ["CPU", "Battery", "Payload", "Structure", "Radiator", "Panels"]
    cols = ["#ff2a5f", "#ffb821", "#26ffad", "#a55eff", "#00f0ff", "#ff8400"]
    keys = [
        "T_CPU_C",
        "T_Battery_C",
        "T_Payload_C",
        "T_Structure_C",
        "T_Radiator_C",
        "T_Panels_C",
    ]

    for idx, key in enumerate(keys):
        ax2.plot(times, df[key], label=nodes[idx], color=cols[idx], linewidth=2.0)

    ax2.set_title(
        "Coupled Multi-Node Telemetry Temperature Curves",
        color="white",
        fontsize=12,
        pad=10,
    )
    ax2.set_xlabel("Time (minutes)", color="#94a3b8")
    ax2.set_ylabel("Temperature (°C)", color="#94a3b8")
    ax2.tick_params(colors="white")
    ax2.grid(color="white", linestyle=":", alpha=0.08)
    ax2.legend(
        facecolor="#0f172a", edgecolor="#1e293b", labelcolor="white", loc="upper right"
    )

    for ax in [ax1, ax2]:
        ax.spines["bottom"].set_color("#334155")
        ax.spines["top"].set_color("#334155")
        ax.spines["left"].set_color("#334155")
        ax.spines["right"].set_color("#334155")

    plt.tight_layout()
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none", dpi=150)
    plt.close()
    print(f"[+] Saved orbital coupled plots to: {output_path}")


def main():
    print("[*] Launching Orbital Environment Simulation (LEO 400km)...")
    network = ThermalNetwork()
    simulate_with_orbit(network, altitude=400, beta=15, duration=3 * 5554)


if __name__ == "__main__":
    main()
