# Spacecraft Thermo-Avionics Numerical Stiffness Report

**Compiled:** 2026-05-28 16:42:41

This document outlines the comparative performance and stability bounds of standard integration solvers (RK45, Radau, BDF) when solving the transient spacecraft thermal 6-node network under rapid eclipse transitions.

## 1. Experimental Setup
- **Physical Nodes**: 6 coupled nodes (CPU, Battery, Payload, Structure, Radiator, Panels)
- **Stiff Stimulus**: Low CPU thermal mass ($C_{\text{cpu}} = 10\text{ J/K}$) and high heating power ($Q_{\text{cpu}} = 50\text{ W}$)
- **Rapid Orbit**: 10 minutes (600s) period with a 3-minute eclipse shadow shadow transitions ($1361\text{ W/m}^2$ to $0\text{ W/m}^2$)
- **Simulation Duration**: 1800 seconds (30 minutes)

## 2. Solver Evaluation Matrix

| Solver | Status | Runtime (s) | Min CPU Temp (°C) | Max CPU Temp (°C) |
| :--- | :---: | :---: | :---: | :---: |
| **RK45** | SUCCESS | 0.0261s | 20.00°C | 54.08°C |
| **Radau** | SUCCESS | 0.0545s | 20.00°C | 54.08°C |
| **BDF** | SUCCESS | 0.0426s | 20.00°C | 54.07°C |

## 3. Scientific Discussion & Guidelines

### Numerical Stiffness Phenomenon
> [!IMPORTANT]
> **What is Stiffness in Spacecraft Thermal Networks?**
> Spacecraft digital twins combine elements with highly contrasting thermal timescales. A CPU is extremely small and dissipates or gathers heat rapidly (seconds), whereas the structural aluminum mass is heavy and absorbs heat over hours. This massive difference in time constants creates **stiff ordinary differential equations (ODEs)**.

### Solver Selection Guidelines:
1. **Non-Stiff Scenarios (Nominal Cubesats):**
   - **RK45 (Runge-Kutta 4th/5th order)** is highly efficient and standard. It provides fast execution with moderate steps.
2. **Stiff Scenarios (Avionics Throttling, Swift Eclipses, Small Nodes):**
   - **Radau (implicit Runge-Kutta of Radau IIA family)** is the canonical choice. It maintains perfect stability without requiring step sizes near zero, preventing infinite loops or silent divergences.
   - **BDF (Backward Differentiation Formula)** is extremely reliable for stiff systems, utilizing implicit backward integrations to guarantee convergence in stiff regimes.