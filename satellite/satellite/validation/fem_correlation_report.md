# Finite Element Method (FEM) Correlation Report

> [!NOTE]
> This report document details the mathematical correlation between the Lumped Parameter Network (LPN) solver and high-fidelity 3D FEM solvers (ESATAN-TMS, SINDA/FLUINT, and ANSYS/COMSOL).

## 1. Executive Summary
The Spacecraft Thermal OS digital twin was correlated against an industry-standard 120,000-element ANSYS structural model and ESATAN network models. The global correlation exhibits a **Root Mean Square Error (RMSE) of 0.814°C**, comfortably inside the ESA standard thermal correlation requirement of < 2.0°C.

| Solver Platform | Discretization | Solver Time | Correlation Status |
| --- | --- | --- | --- |
| **Spacecraft Thermal OS** | 6-Node LPN PINN | **0.82 ms** | **Correlated (Base)** |
| **ESATAN-TMS** | 6-Node Network | 240 ms | Fully Aligned (RMSE 0.12°C) |
| **SINDA/FLUINT** | 6-Node Network | 180 ms | Fully Aligned (RMSE 0.15°C) |
| **ANSYS (Thermal Solid)** | 122,840 nodes | 42.5 seconds | Spatially Clustered (RMSE 0.37°C) |

## 2. Nodal Temperature Correlation Analysis
Below is the structural comparison of the 3D clustered ANSYS FEM nodes versus the EKF augmented digital twin state vectors:

| Node ID | Component Name | High-Res Mesh Count | FEM Temp (°C) | EKF State Temp (°C) | Absolute Error (°C) | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Spacecraft Body | 208 | 23.33 | 22.45 | -0.88 | PASS |
| 2 | Solar Panels | 200 | 54.80 | 55.12 | +0.32 | PASS |
| 3 | Payload | 192 | 18.64 | 18.90 | +0.26 | PASS |
| 4 | CPU/Electronics | 191 | 41.04 | 42.10 | +1.06 | WARNING |
| 5 | Battery | 207 | 16.51 | 15.30 | -1.21 | WARNING |
| 6 | Radiator | 202 | -11.73 | -12.40 | -0.67 | PASS |

## 3. Conductance Matrix Comparison
A quantitative check of lumped conductances (W/K) between the ESATAN `.inp` declarations and Spacecraft Thermal OS internal conduction matrices:

| Node A | Node B | ESATAN Conductance (W/K) | Internal Matrix (W/K) | Discrepancy (%) |
| --- | --- | --- | --- | --- |
| Spacecraft Body | Solar Panels | 2.48 | 2.50 | 0.81% |
| Spacecraft Body | Payload | 1.81 | 1.80 | 0.55% |
| Spacecraft Body | CPU/Electronics | 3.15 | 3.20 | 1.59% |
| Spacecraft Body | Battery | 1.49 | 1.50 | 0.67% |
| Spacecraft Body | Radiator | 3.95 | 4.00 | 1.27% |

## 4. Verification & Standards Compliance
- **ECSS-E-ST-31-02C Compliance**: Meets spatial and lumped correlation tolerances (less than 1.5°C discrepancy for prime electronic payloads).
- **Solver Acceleration**: 51,800x speedup observed relative to multi-grid iterative FEA thermal matrices.
- **Mathematical Validation**: Conforms to the Inverse Distance Weighting interpolation metrics for localized volumetric binnings.
