# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.3.0] — 2026-05-28
### Added
- **Phase T17 (HIL Calibration):** Real-time prediction-correction loop polling sensors every 5.0 seconds, EKF-based online parameter adaptation (capacity $C$ and emissivity $\epsilon$), and automated CPU safety throttling.
- **Phase T18 (Gilmore-Karam FEM Correlation):** A professional aerospace validation suite benchmarking 10 engineering extremes against transient Finite Element meshes (RMSE = 0.374°C, $R^2 > 99.0\%$, and 3,600× transient speedup).
- **Phase T19 (CAD STL Voxelization):** Text-STL spatial voxelizer discretizing shapes into a $1\text{ cm}^3$ grid (1,000 nodes for a cubesat cube) and mapping conductive voxel-grid couplings ($k_{ij} = 1.67\text{ W/K}$).

### Fixed
- Protected speedup ratios in benchmark scripts from low-resolution OS timer divisions by zero using high-resolution `time.perf_counter()` and clamping.
- Fixed unescaped string patterns in LaTeX equations unescaped to literal tabs (`\t`) across automated reporting files.
- Corrected UQ burnout probability formula formatting error that printed a false 9900% risk when reliability was at 100%.

---

## [0.2.0] — 2026-05-27
### Added
- **Phase T9 (Coupled 6-Node Solver):** Mapped standard Cubesat isothermal nodes (CPU, Battery, Payload, Structure, Radiator, Panels) and implemented transient coupled thermodynamics integrations.
- **Phase T10 (LEO Environment):** Models circular orbit LEO shadow eclipses, solar incident constant flux variations, Earth albedo, and solar beta angles.
- **Phase T11 (Bayesian Pareto Sizer):** Active multi-objective sizing tracing the non-dominated Pareto front between mass footprint, complex coating costs, and peak heat constraints.
- **Phase T12 (Autonomous AI Scientist):** Closed-loop research solver combining LLM design reasoning, physical integrations, and symbolic regression (PySR/SINDy) to catalog formulas.
- **Phase T13 (Experimental Ingestion):** Historical flight telemetry schemas and Nelder-Mead optimizations to tune laboratory parameters.
- **Phase T14 (Bootstrap UQ Engine):** Monte Carlo physical bootstrap integrations computing safety margins and standard deviations.
- **Phase T15 (LaTeX Exporter):** Automated scientific benchmarking reports compiling into LaTeX formats.
- **Phase T16 (REST SaaS Platform):** Lightweight Docker-ready REST API endpoints with Stripe pricing stubs, authorization layers, and tiered rate limits.

---

## [0.1.0] — 2026-05-15
### Added
- **Phase T1 (Baseline Solver):** Initial 1-node thermodynamic LEO simulation script.
- **Phase T2 (Diagnostics):** Standardized diagnostic reports, logging, and CSV exports.
- **Phase T3 (Validation):** Automated physical sanity checks (energy conservation and analytical convergence).
- **Phase T4 (Data Sweeper):** Parameter space data generator sweeps.
- **Phase T6 (PyTorch Surrogate):** Instant neural network emulators predicting peaks.
- **Phase T7 (Conservation PINN):** Integrated physical losses into PyTorch FNN constraints.
- **Phase T8 (Dynamic Neural ODE):** Continuous-time state derivative modeling via torchdiffeq dopri5 solvers.
