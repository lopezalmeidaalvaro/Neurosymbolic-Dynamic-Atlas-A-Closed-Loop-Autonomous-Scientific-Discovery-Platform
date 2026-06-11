#!/usr/bin/env python3
"""
Generate Thermal Dataset - Samples configuration parameters and generates simulated thermal profiles.
Author: Alvaro Lopez Almeida
"""

import os
import json
import numpy as np
import pandas as pd
from thermal_server_model import ThermalServerModel


def generate_dataset(
    n_configs=500, output_path="satellite/thermal/thermal_dataset.csv"
):
    """
    Generates thermal dataset by simulating random physical configurations.
    :param n_configs: Number of configurations to generate.
    :param output_path: CSV path to save the dataset.
    :return: DataFrame of the generated dataset.
    """
    # Set seed for reproducibility
    np.random.seed(42)

    # Uniform sampling of physical parameters
    powers = np.random.uniform(5.0, 50.0, n_configs)
    areas = np.random.uniform(0.01, 0.50, n_configs)
    emissivities = np.random.uniform(0.10, 0.95, n_configs)
    heat_capacity = 500.0  # Fixed at 500 J/K

    data = []

    print(f"Generating {n_configs} thermal simulations...")
    for idx in range(n_configs):
        power = float(powers[idx])
        area = float(areas[idx])
        emissivity = float(emissivities[idx])

        # Instantiate and run model
        model = ThermalServerModel(
            power=power, area=area, emissivity=emissivity, heat_capacity=heat_capacity
        )

        # Run standard 3600 second LEO simulation
        sim_res = model.simulate(duration=3600.0, dt=10.0)

        # Save as JSON-serializable strings
        row = {
            "config_id": int(idx),
            "power": power,
            "area": area,
            "emissivity": emissivity,
            "heat_capacity": heat_capacity,
            "max_temp": sim_res["max_temp"],
            "time_to_critical": (
                sim_res["time_to_critical"]
                if sim_res["time_to_critical"] is not None
                else -1.0
            ),
            "temperature_profile": json.dumps(sim_res["temperature"]),
            "time_profile": json.dumps(sim_res["time"]),
            "temperature_map_2D": json.dumps(sim_res["temperature_map_2D"]),
        }
        data.append(row)

        if (idx + 1) % 100 == 0:
            print(f" -> Completed {idx + 1}/{n_configs} simulations")

    df = pd.DataFrame(data)

    # Ensure directory exists
    dir_name = os.path.dirname(output_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)

    df.to_csv(output_path, index=False)
    print(f"Dataset successfully saved to {output_path}")
    return df


if __name__ == "__main__":
    # Generate the main dataset (500 configurations)
    main_path = "thermal_dataset.csv"
    print("Generating main dataset (500 configs)...")
    generate_dataset(n_configs=500, output_path=main_path)

    # Also generate the 20 test configurations and plot the first as required
    test_path = "thermal_dataset_test.csv"
    print("\nGenerating test dataset (20 configs)...")
    df = generate_dataset(n_configs=20, output_path=test_path)

    # Plot first configuration
    first_row = df.iloc[0]
    print(f"\nPlotting config_id 0:")
    print(
        f"Power: {first_row['power']:.2f} W, Area: {first_row['area']:.4f} m^2, Emissivity: {first_row['emissivity']:.2f}"
    )
    print(
        f"Max Temp: {first_row['max_temp']:.2f}°C, Time to Critical: {first_row['time_to_critical']}"
    )

    model = ThermalServerModel(
        power=first_row["power"],
        area=first_row["area"],
        emissivity=first_row["emissivity"],
        heat_capacity=first_row["heat_capacity"],
    )
    plot_path = "test_plot.png"
    model.plot(output_path=plot_path)
    print(f"Saved test simulation plot to {plot_path}")
