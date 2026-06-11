# AST-OS Spacecraft Thermal Digital Twin

## 1. Overview
The AST-OS (Aerospace Spacecraft Thermodynamic Operating System) domain focuses on high-fidelity spacecraft thermal digital twin simulations. By coupling CAD meshes, lumped-parameter thermal network modeling, and neural surrogates, AST-OS enables real-time transient orbit thermal prediction, online Extended Kalman Filter (EKF) parameter calibration, and closed-loop hardware-in-the-loop (HIL) safety control.

---

## 2. Core Performance & Validation Metrics (METRICS.md)

All numbers are verified against the canonical [METRICS.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/METRICS.md):
*   **Gilmore-Karam FEM Correlation RMSE**: `0.374 °C` over 10 transient extreme orbits (Correlation $R^2 = 99.95\%$).
*   **Transient Solver Speedup**: `3,600×` compression (transient network solved in `33.3 ms` vs `120 s` for transient FEM mesh).
*   **Steady-State Surrogate Solve Latency**: `0.2 ms` via PyTorch MLP surrogates (`144,000×` speedup).
*   **Real Telemetry Correlation**:
    *   *Pre-calibration MAE*: `27.25 °C` against raw orbital records.
    *   *Post-calibration MAE*: `9.29 °C` (Nelder-Mead optimization reduces error by `65.90%`).
*   **HIL Closed-Loop MAE**: `7.347 °C` (with an thermocouple noise baseline of $\sigma = 0.5 \ ^\circ\text{C}$ and EKF convergence in `15.0 s`).
*   **Mission Thermal Reliability Score ($R_{\text{thermal}}$)**: `100.00%` probability of keeping CPU core temperatures strictly below $85.0 \ ^\circ\text{C}$ (95% CI is `[51.62, 56.19] °C`).

---

## 3. Methodological Warning: Emulated FEM vs Certified FEM
> [!WARNING]
> **COMPUTATIONAL REPRODUCIBILITY LIMITATION**
> The reference Finite Element Method (FEM) transient orbits used as validation targets were computed using an emulated standard solver. To obtain AS9100 or certified flight-readiness clearance, AST-OS must undergo validation against an externally certified FEM solver (e.g. ANSYS Thermal, Thermal Desktop, or ESATAN-TMS) run independently on the same boundary geometry.

---

## 4. Documents in this Folder
*   [INDEX.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/satellite/INDEX.md): Index navigating satellite reports.
*   [TECHNICAL_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/satellite/TECHNICAL_DOSSIER.md): Detailed AST-OS architecture, thermal equations, HIL closed loops, and surrogate details.
