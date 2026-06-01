# Spacecraft Thermal OS (AST-OS) — Verification Requirements Dashboard
**Document ID**: AST-V&V-DASH-005  
**Authority**: Lead Verification & Validation Engineer (ESA/NASA)  
**Date**: 2026-05-30 (Updated after FAIL resolution)

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
| **REQ-EKF-01**: Extended Kalman Filter Convergence Accuracy | `<= 2.0 °C` | `UNKNOWN` | **UNKNOWN** |

## 2. Status Scorecard
- **Total Audited Requirements**: **`18`**  
- **PASS**: **`17`** (94.4%)  
- **FAIL**: **`0`** (0.0%) ← Resolved  
- **UNKNOWN**: **`1`** (5.6%)  

> [!IMPORTANT]
> **All four FAIL requirements resolved.** See [`fail_resolution_report.md`](file:///C:/Users/Alvaro/.gemini/antigravity/brain/7b243eda-09c0-4d63-9478-00317473a170/fail_resolution_report.md) for root cause analysis and parametric fix details. **13/13 unit tests pass with zero regressions.**

> [!NOTE]
> **OPEN_RISK — REQ-EKF-01**: No standalone EKF residual CSV log file exists. The Kalman filter convergence residuals are computed inline within the autonomy pipeline without persistent output. This requirement cannot be verified until a dedicated `ekf_residuals.csv` logging sink is implemented.
