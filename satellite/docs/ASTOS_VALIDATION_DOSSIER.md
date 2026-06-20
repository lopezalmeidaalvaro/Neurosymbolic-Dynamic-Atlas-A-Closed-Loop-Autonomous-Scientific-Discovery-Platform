# AST-OS Validation Dossier

## 1. Executive Summary
This document summarizes the validation benchmarks, Hardware-in-the-Loop (HIL) test suites, and empirical sensor comparisons for the AST-OS digital twin. Real-time executions on embedded target processors verify compliance with ECSS latency and precision requirements.

## 2. Purpose
The purpose of the validation suite is to certify AST-OS for integration into onboard spacecraft computer architectures, verifying numerical accuracy against physical vacuum chamber experimental data.

## 3. Architecture
The HIL verification test bench is structured as follows:

```
   [Host PC: CAD Simulator] 
          |
          v (Ethernet / CAN Bridge)
   [Embedded ARM Cortex-M]  <-- Runs AST-OS Solver
          |
          v (Telemetry Compare)
   [TVAC Empirical Datasets]
```

*   **Host PC**: Injects virtual orbital solar fluxes and telemetry configurations.
*   **Embedded Target**: ARM Cortex-M microprocessor running the compiled C-based AST-OS solver.
*   **Comparator**: Measures prediction residuals against physical Thermal Vacuum Chamber (TVAC) data.

## 4. Methodology
*   **Voxel Grid Discretization Check**: Geometric validation measuring volume mismatch errors of voxel grids against original high-resolution CAD files.
*   **Thermal Vacuum Chamber (TVAC) Runs**: Feeds identical physical profiles from a physical TVAC test campaign and measures solver temperature divergence.
*   **FDIR Scenario Injector**: Injects simulated fault events (radiator blockages, sensor drift, heater failure) to measure detection rate and isolation latency.

## 5. Results
*   **Voxel Grid Accuracy**: The discretization engine maps complex geometric shapes with a volume mismatch error of **$<0.12\%$**.
*   **HIL Simulation Latency**: AST-OS executes its complete conductive-radiative solver step in **$<8.5\text{ ms}$** on target ARM Cortex-M processors. This is well below the **$20.0\text{ ms}$** ECSS operations boundary.
*   **Solver Accuracy**: Temperature predictions align with TVAC chamber measurement profiles within **$\pm 0.8^\circ\text{C}$** at steady state.

## 6. Validation
*   **FDIR Anomaly Isolation**: The residual detector isolated **$97.8\%$** of heater failures within **$15$ seconds** of drift onset.
*   **Adversarial Sensor Drifts**: Isolated sensor faults from physical line noise with zero false-alarm mode changes.

## 7. Limitations
*   **Embedded RAM Constraints**: Node graphs with $>1200$ nodes exhaust microcontroller stack memory, causing execution errors.
*   **Transient Spikes**: Fast-changing power switches can introduce transient simulation prediction errors up to $\pm 1.5^\circ\text{C}$ for short durations ($<10$ seconds) before re-stabilizing.

## 8. Future Work
*   **LEON Processor Target Validation**: Validating the compiled solver on space-grade radiation-hardened LEON processors.
*   **Dual-Core Execution**: Splitting radiative view-factor solving and conductive matrix inversion across separate embedded cores to support denser node graphs.

## 9. Source Documents
*   [ASTOS_VALIDATION_DOSSIER.md (Original)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/ASTOS_VALIDATION_DOSSIER.md)
*   [satellite/VALIDATION_REPORT.md (Consolidated)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/VALIDATION_REPORT.md)
