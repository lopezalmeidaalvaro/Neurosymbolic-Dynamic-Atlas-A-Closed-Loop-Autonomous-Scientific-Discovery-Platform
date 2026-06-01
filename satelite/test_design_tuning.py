import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(
    0, r"c:\Users\Alvaro\Desktop\autonomous-spacecraft-thermal-os\satellite\thermal"
)
from multi_node_thermal_network import ThermalNetwork
import orbital_environment as oe

net = ThermalNetwork()

results_search = []

for A_rad in [0.15, 0.18, 0.22, 0.26]:
    for k_panel_struct in [0.1, 0.2, 0.3]:
        for k_batt_struct in [0.2, 0.4, 0.6]:
            for Q_batt in [2.0, 3.0, 4.0]:
                custom_k = net.k.copy()
                custom_k[5, 3] = custom_k[3, 5] = k_panel_struct
                custom_k[1, 3] = custom_k[3, 1] = k_batt_struct
                custom_k[4, 3] = custom_k[3, 4] = 6.0  # good radiator coupling

                config = {
                    "C": [250.0, 800.0, 300.0, 1500.0, 200.0, 300.0],
                    "Q": [15.0, Q_batt, 5.0, 0.0, 0.0, 0.0],
                    "eps": [0.1, 0.1, 0.1, 0.2, 0.85, 0.1],
                    "A": [0.01, 0.02, 0.01, 0.10, A_rad, 0.20],
                    "k": custom_k,
                }

                net_test = ThermalNetwork(config)
                res = oe.simulate_with_orbit(
                    net_test, altitude=400, beta=15, duration=1 * 5554
                )

                cpu_max = res["max_temps"]["CPU"]
                batt_max = res["max_temps"]["Battery"]
                batt_min = min(res["temperatures"][1])

                temps_np = np.array(res["temperatures"])
                # Evaluate gradient ONLY over internal bus nodes: CPU (0), Battery (1), Payload (2), Structure (3)
                internal_temps = temps_np[:4, :]
                max_gradient = (
                    internal_temps.max(axis=0) - internal_temps.min(axis=0)
                ).max()

                results_search.append(
                    {
                        "A_rad": A_rad,
                        "k_panel": k_panel_struct,
                        "k_batt": k_batt_struct,
                        "Q_batt": Q_batt,
                        "cpu_max": cpu_max,
                        "batt_max": batt_max,
                        "batt_min": batt_min,
                        "grad": max_gradient,
                    }
                )

df = pd.DataFrame(results_search)
success = df[
    (df["cpu_max"] <= 85.0)
    & (df["batt_min"] >= 0.0)
    & (df["batt_max"] <= 40.0)
    & (df["grad"] <= 20.0)
]
print("=== SUCCESS CASES ===")
print(success)
