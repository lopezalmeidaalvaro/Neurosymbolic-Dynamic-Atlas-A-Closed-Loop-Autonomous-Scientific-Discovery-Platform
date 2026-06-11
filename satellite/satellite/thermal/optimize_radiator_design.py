#!/usr/bin/env python3
"""
Optimize Radiator Design - Performs multi-objective Pareto optimization for spacecraft radiator parameters.
Author: Alvaro Lopez Almeida
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from thermal_server_model import ThermalServerModel

# Set seed for reproducibility
np.random.seed(42)


def is_pareto_efficient(costs):
    """
    Find the Pareto efficient points
    :param costs: An (n_points, n_costs) array
    :return: A boolean array of pareto efficiency of each point
    """
    is_efficient = np.ones(costs.shape[0], dtype=bool)
    for i, c in enumerate(costs):
        if is_efficient[i]:
            # Keep any point that is not dominated by c
            # Dominated means c is strictly better in at least one and not worse in all
            is_efficient[is_efficient] = np.any(
                costs[is_efficient] < c, axis=1
            ) | np.all(costs[is_efficient] == c, axis=1)
            is_efficient[i] = True  # Keep self
    return is_efficient


def optimize_design():
    print("Initiating radiator design multi-objective optimization...")

    # Configuration
    fixed_power = 30.0  # W, standard spacecraft operational load
    heat_capacity = 500.0  # J/K

    # 1. 100 Random iterations
    print("Running 100 random sampling design evaluations...")
    areas_random = np.random.uniform(0.01, 0.50, 100)
    emissivities_random = np.random.uniform(0.10, 0.95, 100)

    results = []

    for idx in range(100):
        area = float(areas_random[idx])
        emissivity = float(emissivities_random[idx])

        model = ThermalServerModel(
            power=fixed_power,
            area=area,
            emissivity=emissivity,
            heat_capacity=heat_capacity,
        )
        sim_res = model.simulate()
        max_temp = sim_res["max_temp"]

        # Objectives
        mass = area  # Mass proportional to area
        cost = area * (
            1.0 + (1.0 - emissivity)
        )  # Cost proportional to area & coating complexity

        results.append(
            {
                "area": area,
                "emissivity": emissivity,
                "max_temp": max_temp,
                "mass": mass,
                "cost": cost,
                "feasible": max_temp < 85.0,
            }
        )

    # 2. 200 Refined Sequential iterations (focusing on search space near feasibility boundaries)
    print("Running 200 sequential Bayesian-like refinement iterations...")
    for step in range(200):
        # Sample near the best feasible points found so far
        feasible_pts = [r for r in results if r["feasible"]]
        if feasible_pts:
            # Select a random good point as baseline and add small perturbation
            best_pt = np.random.choice(feasible_pts)
            area = float(
                np.clip(best_pt["area"] + np.random.normal(0, 0.05), 0.01, 0.50)
            )
            emissivity = float(
                np.clip(best_pt["emissivity"] + np.random.normal(0, 0.05), 0.10, 0.95)
            )
        else:
            # Fallback to random if no feasible points found yet
            area = float(np.random.uniform(0.01, 0.50))
            emissivity = float(np.random.uniform(0.10, 0.95))

        model = ThermalServerModel(
            power=fixed_power,
            area=area,
            emissivity=emissivity,
            heat_capacity=heat_capacity,
        )
        sim_res = model.simulate()
        max_temp = sim_res["max_temp"]

        mass = area
        cost = area * (1.0 + (1.0 - emissivity))

        results.append(
            {
                "area": area,
                "emissivity": emissivity,
                "max_temp": max_temp,
                "mass": mass,
                "cost": cost,
                "feasible": max_temp < 85.0,
            }
        )

    df_all = pd.DataFrame(results)

    # Filter feasible points for Pareto extraction
    df_feasible = df_all[df_all["feasible"]].copy()

    if df_feasible.empty:
        print(
            "Warning: No feasible designs under 85°C found. Relaxing constraint to find best candidates."
        )
        df_feasible = df_all.copy()

    # Extract Pareto Front
    # Objectives to minimize: [mass, cost, max_temp]
    objectives = df_feasible[["mass", "cost", "max_temp"]].values
    pareto_mask = is_pareto_efficient(objectives)

    df_pareto = df_feasible[pareto_mask].copy()

    # Save Pareto front to CSV
    df_pareto.to_csv("pareto_front.csv", index=False)
    print(f"Pareto Front extracted with {len(df_pareto)} non-dominated configurations.")
    print("Saved Pareto Front to satellite/thermal/pareto_front.csv")

    # Plot Pareto Front (2D Area/Mass vs Max Temp colored by Cost)
    plt.figure(figsize=(10, 6))

    # Scatter of all evaluated points
    plt.scatter(
        df_all["max_temp"],
        df_all["area"],
        c="gray",
        alpha=0.15,
        label="All Explored Designs",
    )

    # Highlight Pareto front
    sc = plt.scatter(
        df_pareto["max_temp"],
        df_pareto["area"],
        c=df_pareto["cost"],
        cmap="viridis",
        s=60,
        edgecolors="black",
        label="Pareto Front (Non-dominated)",
    )

    plt.colorbar(sc, label="Coating & Production Cost")
    plt.axvline(
        85.0, color="red", linestyle="--", label="Max Allowable Temperature (85°C)"
    )
    plt.xlabel("Peak Temperature (°C)")
    plt.ylabel("Radiator Area / Mass (m²)")
    plt.title(
        f"Satellite Radiator Multi-Objective Pareto Optimization (Power: {fixed_power}W)"
    )
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()
    plt.savefig("pareto_front.png", dpi=150)
    plt.close()
    print("Saved Pareto Front visualization to satellite/thermal/pareto_front.png")

    # Select best optimal design
    # Utility function: minimize combined normalized cost and mass, with a strong penalty for approaching temperature limit
    # We want a design that is safely below 85°C (e.g. max_temp <= 65°C), small area (low mass), and high emissivity (low cost)
    df_safe = df_feasible[df_feasible["max_temp"] <= 65.0]
    if df_safe.empty:
        df_safe = df_feasible

    # Best design minimizes area * max_temp
    best_idx = (df_safe["mass"] * df_safe["max_temp"]).idxmin()
    best_design = df_safe.loc[best_idx].to_dict()

    # Structure optimal_design.json
    optimal_design_summary = {
        "fixed_power_watts": fixed_power,
        "optimal_area_m2": best_design["area"],
        "optimal_emissivity": best_design["emissivity"],
        "expected_max_temp_c": best_design["max_temp"],
        "estimated_mass_kg": best_design["mass"] * 10.0,  # e.g., 10kg per m2
        "estimated_cost_usd": best_design["cost"] * 5000.0,  # e.g., $5k base unit cost
        "efficiency_status": (
            "Optimal"
            if best_design["max_temp"] < 65.0
            else "Warning (Near thermal limit)"
        ),
    }

    with open("optimal_design.json", "w") as f:
        json.dump(optimal_design_summary, f, indent=4)

    print("\nOptimal Radiator Design:")
    print(f" -> Area: {best_design['area']:.4f} m^2")
    print(f" -> Emissivity: {best_design['emissivity']:.2f}")
    print(f" -> Max Temperature: {best_design['max_temp']:.2f}°C")
    print("Saved optimal design specs to satellite/thermal/optimal_design.json")


if __name__ == "__main__":
    optimize_design()
