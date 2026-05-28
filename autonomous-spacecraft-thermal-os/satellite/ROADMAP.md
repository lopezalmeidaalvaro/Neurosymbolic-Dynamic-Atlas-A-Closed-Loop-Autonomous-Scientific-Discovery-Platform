# Roadmap — Orbital Thermal Digital Twin

This document outlines the development lifecycle of the **Spacecraft Thermodynamic Digital Twin**, tracking completed milestones, in-progress integrations, and upcoming architectural extensions.

---

## 🟢 Completed (T1–T16)

The initial core design and surrogate modeling layers are fully stable and verified:

### 1. Core Physics & Telemetry Ingestion (T1–T5)
* **T1 — Baseline Simulator:** Implemented the 1-node thermodynamic Euler solver modeling LEO cycles.
* **T2 — Diagnostic Logger:** Set up structured telemetry CSV reporting and automated temperature warnings.
* **T3 — Physical Validation:** Verified energy conservation ($<0.05\%$) and steady-state analytical convergence ($<0.5\%$).
* **T4 — Data Generator:** Automated dataset generation sweeps across parameter bounds.
* **T5 — Telemetry Ingestion:** Mapped historical mission telemetry schemas from NASA, ESA, and Kaggle.

### 2. Machine Learning Surrogate Emulation (T6–T8)
* **T6 — PyTorch Surrogate:** Trained an MLP emulator to predict peak temperatures in microseconds.
* **T7 — Physics-Informed NN (PINN):** Constrained neural training using thermodynamic conservation losses.
* **T8 — Continuous Neural ODE:** Modeled continuous-time state derivatives via adaptive `dopri5` ODE solvers.

### 3. Red Térmica Multi-Nodo & Sizing Optimization (T9–T11)
* **T9 — Multi-Node Network:** Transitioned from a single bulk node to a 6-node coupled thermodynamic solver.
* **T10 — Orbital Environment:** Integrated LEO eclipse shadow formulas, Earth albedo, and solar beta angles.
* **T11 — Bayesian Pareto Sizer:** Designed active-learning loops to extract non-dominated area/emissivity design specs.

### 4. Autonomous Science & Monetization (T12–T16)
* **T12 — AI Scientist:** Combined LLM hypotheses, sandbox runs, and symbolic regression to discover thermodynamic equations.
* **T13 — Laboratory Calibration:** Implemented Nelder-Mead optimization to tune coefficients against laboratory telemetry.
* **T14 — Bootstrap UQ Engine:** Constructed Monte Carlo physical perturbation bounds and calculated reliability scores.
* **T15 — LaTeX Exporter:** Automated scientific correlation report compiling and LaTeX document generation.
* **T16 — SaaS REST API:** Designed lightweight Docker-ready REST microservice endpoints with API key rate-limiting.

---

## 🟡 In Progress / Recently Completed (T17–T19)

We are finalizing the validation of edge hardware interfaces and geometric mesh integrations:

* **T17 — Hardware-in-the-Loop (HIL) Loop:** Connecting the digital twin to physical sensors (ESP32 / Raspberry Pi) in real-time, executing Online Calibration via Extended Kalman Filters (EKF) and active cooling throttling.
* **T18 — Gilmore-Karam FEM Correlation:** Standardizing accuracy benchmarks against Transient Finite Element meshes across 10 evaluation extreme scenarios, achieving RMSE $< 0.4^\circ\text{C}$ and $3,600\times$ speedups.
* **T19 — CAD-Aware 3D Voxelizer:** Importing raw text-STL 3D geometry models, voxelizing boundaries, and extracting conductive thermal coupling networks.

---

## 🔵 Planned (T20–T23)

The upcoming milestones focus on spaceflight control, federated architectures, and advanced compute systems:

### T20 — Deep Reinforcement Learning for Active Attitude & Thermal Steering
* Train a DRL agent (PPO/SAC) to dynamically control satellite orientation (yaw/pitch/roll) to optimize solar panel absorption while shielding delicate payloads, minimizing battery heater power consumption in deep eclipse phases.

### T21 — Multi-Spacecraft Constellation Federated Learning
* Implement a federated learning framework allowing a constellation of distinct cubesats to collaborate on updating neural surrogate weights without transferring raw thermal sensor telemetry to ground stations.

### T22 — Quantum-Accelerated Finite Element Surrogates
* Explore NISQ-era Quantum Reservoir Computing (QRC) and Parametric Quantum Circuits (VQE) to accelerate high-fidelity spatial gradient solves of localized PCB hot-spots.

### T23 — Fully Autonomous On-Orbit Self-Healing Calibration
* Design a decentralized, low-compute calibration loop that runs natively on microcontrollers, dynamically detecting sensor drift or coating degradation, and automatically rewriting flight control parameters on the fly.

---

## 🚀 Future Exploration

* **Rad-Hardened Hardware Deployments:** Testing the compiled surrogates on radiation-hardened microprocessors (such as ARM Cortex-R52 or RISC-V spaceboards) to evaluate transient gate ionization errors.
* **Deep Space Radiative Decay Modeling:** Extending the LEO environmental engine to support interplanetary deep-space profiles, incorporating solar wind thermal flux and cosmic dust micro-collisions coating erosion.
