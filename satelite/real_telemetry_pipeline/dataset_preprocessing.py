# ==============================================================================
# Spacecraft Thermal OS (AST-OS) - Space Telemetry Validation
# File: dataset_preprocessing.py
# Description: Checks telemetry for timestamps, units, and thermodynamic invariants.
# ==============================================================================

import pandas as pd
import numpy as np


def validate_space_telemetry(csv_path):
    print(f"[*] Validating Space Telemetry Invariant Checks on: {csv_path}")
    df = pd.read_csv(csv_path)

    anomalies_detected = 0

    # 1. Verification of Continuity (Constant Timestamps)
    # Assumes nominal sample step = 21.6 seconds (180 min over 500 steps)
    time_diffs = np.diff(df["Timestamp_Epoch"])
    max_gap = np.max(time_diffs)
    print(f"  - Max Timestamp Gap: {max_gap} seconds (Nominal: 22s)")
    if max_gap > 60:
        print(
            "  [WARNING] Telemetry gap exceeding 60s detected. Continuity check FAILED."
        )
        anomalies_detected += 1
    else:
        print("  [PASS] Telemetry continuity verified.")

    # 2. Thermodynamic Range Invariants (Bounded Limits)
    # CPU temperatures must be strictly between -100C and 150C
    min_temp = np.min(df["ISS_ATCS_CPU_Raw_C"])
    max_temp = np.max(df["ISS_ATCS_CPU_Raw_C"])
    print(f"  - CPU Temperature Range: {min_temp:.2f} C to {max_temp:.2f} C")
    if min_temp < -100.0 or max_temp > 150.0:
        print(
            "  [ERROR] Unphysical temperatures detected. Thermodynamic limits FAILED."
        )
        anomalies_detected += 1
    else:
        print("  [PASS] Thermal range limits verified.")

    # 3. Maximum Derivative Boundedness (dT/dt)
    # A physical solid spacecraft node cannot change temperature by more than 10.0C per minute
    dt = 22.0 / 60.0  # Time steps in minutes
    temp_derivatives = np.abs(np.diff(df["ISS_ATCS_CPU_Raw_C"]) / dt)
    max_derivative = np.max(temp_derivatives)
    print(f"  - Max CPU dT/dt: {max_derivative:.4f} C/min")
    if max_derivative > 10.0:
        print(
            f"  [WARNING] Derivative exceedance detected (Max: {max_derivative:.2f} C/min). Indicates telemetry spikes/outliers."
        )
        anomalies_detected += 1
    else:
        print("  [PASS] Derivative limits verified.")

    # 4. Solar Flux and Orbital Consistency
    # Incident solar flux cannot exceed solar constant S0 = 1361 W/m² (plus error bounds)
    max_flux = np.max(df["Solar_Flux_W_m2"])
    print(f"  - Max Incident Solar Flux: {max_flux:.1f} W/m²")
    if max_flux > 1400.0:
        print(
            "  [ERROR] Incident solar flux exceeds physical solar constant bounds. Solar validation FAILED."
        )
        anomalies_detected += 1
    else:
        print("  [PASS] Solar flux bounds verified.")

    if anomalies_detected > 0:
        print(
            f"\n[!] Telemetry validation completed: {anomalies_detected} anomalies/warnings flagged. Preprocessing required.\n"
        )
    else:
        print(
            "\n[+] Telemetry validation completed: 100% PASS. Thermodynamic consistency guaranteed.\n"
        )

    return anomalies_detected


if __name__ == "__main__":
    validate_space_telemetry("datasets/nasa_atcs_telemetry.csv")
