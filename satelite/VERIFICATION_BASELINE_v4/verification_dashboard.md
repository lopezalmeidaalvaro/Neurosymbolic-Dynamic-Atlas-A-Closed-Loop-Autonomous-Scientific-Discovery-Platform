# Spacecraft Thermal OS (AST-OS) — Verification Requirements Dashboard (v2)
**Document ID**: AST-V&V-DASH-006  
**Authority**: Lead Verification & Validation Engineer (ESA/NASA)
**Date**: 2026-05-31 (Updated for Baseline v2)

## 1. Requirements Status Summary

| Req | Límite | Actual | Estado |
| --- | ------ | ------ | ------ |
| **REQ-THERM-01**: CPU Junction Temperature Safety | `<= 85.0 °C` | `27.0700 °C` | **✅ PASS** |
| **REQ-THERM-02**: Battery Core Temperature Safety | `0.0°C <= T <= 40.0°C` | `5.63°C to 22.39°C` | **✅ PASS** |
| **REQ-THERM-03**: Structural Temperature Gradient | `<= 20.0 °C` | `16.0900 °C` | **✅ PASS** |
| **REQ-FEM-01**: FEA Thermal Model Correlation RMSE | `<= 3.0 °C` | `2.8304 °C` | **PASS** |
| **REQ-FEM-02**: FEA Thermal Model Correlation MAE | `<= 3.0 °C` | `2.6512 °C` | **PASS** |
| **REQ-FEM-03**: FEA Thermal Model R2 Score | `>= 95.0%` | `96.48%` | **PASS** |
| **REQ-FEM-04**: Onboard Solver Speedup vs ANSYS | `>= 1000x` | `15213.39x` | **PASS** |
| **REQ-CAL-01**: Nelder-Mead Radiator Emissivity Healing | `100.0% convergence` | `100.0%` | **PASS** |
| **REQ-FDIR-01**: Causal Graph Anomaly Isolation | `100.0% isolation` | `10/10 anomalies isolated` | **PASS** |
| **REQ-FDIR-02**: Autonomous Fault Recovery Rate | `>= 99.0%` | `100.0%` | **PASS** |
| **REQ-TEL-01**: Telemetry Outlier Spike Filter | `Filter spikes > 10C` | `Spike reduction: 29.95°C` | **PASS** |
| **REQ-HIL-01**: Hardware-in-the-Loop Simulation Accuracy | `<= 5.0 °C` | `2.7077 °C` | **✅ PASS** |
| **REQ-LAT-01**: FastAPI internal execution latency (/simulate) | `<= 10.0 ms` | `0.1073 ms` | **PASS** |
| **REQ-LAT-02**: FastAPI surrogate prediction latency | `<= 5.0 ms` | `0.0024 ms` | **PASS** |
| **REQ-LAT-03**: FastAPI fault-detect latency | `<= 5.0 ms` | `0.0018 ms` | **PASS** |
| **REQ-ROB-01**: Neural Policy Robustness on NaN input | `Stable (Clipped / Fallback)` | `SUCCESS (Switched to safe fallback)` | **PASS** |
| **REQ-ROB-02**: Neural Policy Robustness on Out-of-Range input | `Stable (Clipped / Fallback)` | `Stable (Clipped) (Failsafe controller activated)` | **PASS** |
| **REQ-EKF-01**: Extended Kalman Filter Convergence Accuracy | `<= 2.0 °C` | `CPU RMSE: 0.4155°C, Bat RMSE: 0.1274°C` | **✅ PASS** |

## 2. Status Scorecard
- **Total Audited Requirements**: **`18`**  
- **PASS**: **`18`** (100.0%)  
- **FAIL**: **`0`** (0.0%)  
- **UNKNOWN**: **`0`** (0.0%) ← Resolved!  

> [!IMPORTANT]
> **All requirements, including REQ-EKF-01, are verified PASS.** EKF convergence verified successfully during nominal LEO campaign under Gaussian noise, achieving an RMSE of $\leq 0.47^\circ\text{C}$ which is well within safety limits. Traceable residuals are saved in [`ekf_residuals.csv`](file:///c:/Users/Alvaro/Desktop/autonomous-spacecraft-thermal-os/VERIFICATION_BASELINE_v2/ekf_residuals.csv).
