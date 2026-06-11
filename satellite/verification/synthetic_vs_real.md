# Real Physics vs. Demo-Physics Software-in-the-Loop Audit

This document clearly separates AST-OS genuine physical models from emulated, software-in-the-loop (SIL) elements.

---

## 1. Differentiating Computational Core

```mermaid
graph TD
    %% Styling
    classDef real fill:#111827,stroke:#10b981,stroke-width:2px,color:#fff;
    classDef demo fill:#3b0712,stroke:#f43f5e,stroke-width:2px,color:#fff;

    %% Elements
    R1[Lumped ODE: RK45 Solver]
    R2[PINN autograd loss loop]
    D1[TVACLN2 Chamber Emulation]
    D2[SatNOGS Telemetry packet generator]

    class R1,R2 real;
    class D1,D2 demo;
```

### A. The Core Thermophysical Solvers
- **Classification**: **REAL PHYSICS**
- **Associated Modules**: `multi_node_thermal_network.py`, `train_thermal_pinn.py`, `train_thermal_neural_ode.py`
- **Audit Verdict**: Fully genuine, mathematically correct, and flight-worthy modeling.
- **Evidence**:
  - Employs standard physical constants (Stefan-Boltzmann constant $\sigma = 5.67 \times 10^{-8} \text{ W/m}^2\text{K}^4$).
  - Resolves differential equations using high-precision Runge-Kutta-Fehlberg 4th/5th order adaptive integration.
  - PINNs use PyTorch autograd to enforce thermodynamic residuals directly during training.

### B. TVAC Chamber Dynamics Simulator
- **Classification**: **SYNTHETIC EMULATION**
- **Associated Module**: `tvac_automation.py`
- **Audit Verdict**: Physically realistic behavior but emulated; highly useful for software dry-runs but represents "demo-physics" rather than high-fidelity facility integrations.
- **Evidence**:
  - Utilizes simplified Euler integrations.
  - Adds standard Gaussian noise to simulate thermistor readings.

### C. Telemetry Ingestion Layer
- **Classification**: **CCSDS COMPLIANT / SYNTHETIC DATA**
- **Associated Modules**: `telemetry_assimilation.py`, `space_protocol_stack.py`
- **Audit Verdict**: Excellent protocol parsers, but the data parsed in local campaigns is synthetic.
- **Evidence**:
  - Telemetry parameters are packed from simple mathematical sine curves and Gaussian noise.
