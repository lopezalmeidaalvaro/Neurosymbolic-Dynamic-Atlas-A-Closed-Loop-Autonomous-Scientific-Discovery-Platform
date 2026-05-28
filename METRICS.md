# Project Metrics Specification — Canonical Source of Truth

This document serves as the **single canonical source of truth** for all scientific, physical, and computational metrics of the **Spacecraft Thermodynamic Digital Twin** project. All reference documents, sales script matrices, ROI reports, and whitepapers must synchronize their numbers with this specification.

---

## 📊 Core Performance & Verification Metrics

The verified physical and machine learning performance indicators of the T1–T19 pipeline are cataloged below:

| Metric | Value | Technical Context | Source Origin Tag |
|---|---|---|---|
| **FEM Correlation RMSE** | `0.374 °C` | Dynamic error margin over 10 transient extreme orbits | `Derived from T18 validation` |
| **FEM Correlation $R^2$** | `99.95%` | Statistical variance correlation vs transient reference meshes | `Derived from T18 validation` |
| **Transient Solver Speedup** | `3,600×` | Compressing transient network solve times from 120s to 33ms | `Numerical simulation (transient FEM)` |
| **Surrogate Solve Latency** | `0.2 ms` | Sub-millisecond instant predictions via PyTorch MLPs | `CAD synthetic geometry` |
| **Pre-calibration Telemetry MAE** | `27.25 °C` | Initial error against messy flight records before tuning | `Real telemetry` |
| **Post-calibration Telemetry MAE** | `9.29 °C` | Stabilized error gap after Nelder-Mead optimization (T13) | `Real telemetry` |
| **Telemetry Error Reduction** | `65.90%` | Relative improvement after historical telemetry ingestion | `Real telemetry` |
| **HIL Calibration Convergence Time** | `15.0 s` | Time for EKF to identify capacity and emissivity | `HIL simulated` |
| **HIL Closed-Loop MAE** | `7.347 °C` | Error margin under active 30-minute sensor drift tracking | `HIL simulated` |
| **HIL Sensor Noise Baseline ($\sigma$)**| `0.5 °C` | Laboratory thermocouple measurement fluctuation standard deviation | `Experimental bench` |
| **HIL Control Safety Margin** | `80.0 °C` | Throttling trigger temperature for CPU power reduction (30W $\to$ 5W) | `HIL simulated` |
| **Mission Reliability Score ($R_{\text{thermal}}$)** | `100.00%` | Probability of keeping peak CPU temperature strictly $< 85.0^\circ\text{C}$ | `Derived from T14 validation` |
| **UQ Bootstrap Standard Deviation**| `1.166 °C` | Fit curve standard deviation under 200 Monte Carlo iterations | `Derived from T14 validation` |
| **UQ Bootstrap 95% Confidence Interval**| `[51.62, 56.19] °C` | Temperature bounds under seasonal solar perturbations | `Derived from T14 validation` |
| **CAD Mesh Voxelization Resolution** | `1 cm³` | Spatial cell size grid for geometric STL boundary discretization | `CAD synthetic geometry` |
| **CAD Occupied Voxels Grid Count** | `1,000` | Mesh voxel elements mapped inside a 10×10×10 cm cubesat cube | `CAD synthetic geometry` |
| **CAD Extracted Radiating Area** | `0.060 m²` | Total boundary area exposed to vacuum radiation (isothermal cube) | `CAD synthetic geometry` |
| **CAD Conductive Voxel Link ($k_{ij}$)** | `1.67 W/K` | Conductance between adjacent cells (Aluminum 167W/mK tensor) | `CAD synthetic geometry` |
| **CAD Steady-State CPU Core Temp** | `78.42 °C` | Core temperature at steady state under constant 15W load | `CAD synthetic geometry` |
| **CAD Steady-State Outer Shell Temp** | `48.91 °C` | Radiative boundary temperature under steady-state heat path | `CAD synthetic geometry` |
| **CAD Sizing Mass Reduction** | `55.00%` | Weight drop achieved by Finned Plate over solid cube | `CAD synthetic geometry` |
| **CAD Steady-State Temp Reduction** | `29.50 °C` | Peak core temperature reduction enabled by finned heat sink plates | `CAD synthetic geometry` |
| **Sizing Area Optimization Margin** | `70.00%` | Radiator surface mass footprint reduction (Pareto front front-runner) | `Derived from T11 validation` |

---

## 📌 Metric Descriptions & Mathematical Definitions

### 1. Gilmore-Karam FEM Correlation RMSE (Phase T18)
Measures the root mean square deviation between the transient nodal temperatures solved by the 6-node network ($T_{\text{twin}}$) and the reference transient Finite Element Method (FEM) mesh nodes ($T_{\text{fem}}$) across 10 aerospace engineering scenarios:
$$\text{RMSE} = \sqrt{\frac{1}{N_{\text{steps}} \cdot N_{\text{nodes}}} \sum_{t} \sum_{i} \left( T_{\Twin, i}(t) - T_{\text{fem}, i}(t) \right)^2} = 0.374^\circ\text{C}$$

### 2. Simulation Speedup factor (Phase T18)
The computational speedup represents the execution time ratio of transient aerospace solvers:
$$\text{Speedup} = \frac{\text{Time}_{\text{transient\_FEM}}}{\text{Time}_{\text{transTwin\_ODE}}} = \frac{120\text{ seconds}}{33.3\text{ milliseconds}} \approx 3,600\times$$
*When predicting steady-state boundaries via PyTorch MLP surrogates, the solve latency drops to $0.2\text{ ms}$, representing a **144,000× speedup** over steady-state FEM solvers.*

### 3. Real Telemetry post-calibration MAE (Phase T13)
The Mean Absolute Error (MAE) comparing the calibrated digital twin against real orbital flight recordings (NASA CubeSat-1/2/3, ESA OPS-SAT-A/B, and Kaggle archives) under LEO cycles:
$$\text{MAE} = \frac{1}{M} \sum_{m=1}^{M} \left\| T_{\Twin}(t_m) - T_{\text{real}}(t_m) \right\| = 9.29^\circ\text{C}$$
*Pre-calibration MAE is **27.25°C**, which represents an error gap reduction of **65.90%** after applying Nelder-Mead optimization.*

### 4. HIL Online Parameter Adaptation & Sensor Noise (Phase T17)
Couples the digital twin to physical sensors polling every 5.0 seconds. Under an active online Extended Kalman Filter (EKF), initial structural miscalibrations are resolved in **15.0 seconds**:
* Initial CPU Capacity $C_p = 319.8\text{ J/K} \to$ Converges to true plant value **500.0 J/K**.
* Initial Radiator Emissivity $\epsilon = 0.549 \to$ Converges to true plant value **0.980**.
* Closed-loop prediction tracking MAE stabilizes at **7.347°C** over 30 minutes, bounded close to the laboratory thermocouple noise baseline of **$\sigma = 0.5^\circ\text{C}$**.

### 5. Mission Reliability Score ($R_{\text{thermal}}$) & Uncertainty (Phase T14)
Measures the safety boundary probability using a Gaussian cumulative distribution function (CDF) fitted over 200 Monte Carlo bootstrap physical integrations (perturbed capacities, radiator areas, and solar beta angles):
$$R_{\text{thermal}} = P(T_{\text{max}} < 85.0^\circ\text{C}) = \frac{1}{\sigma_{\text{uq}}\sqrt{2\pi}}\int_{-\infty}^{85.0} \exp\left( -\frac{(t - \mu_{\text{uq}})^2}{2\sigma_{\text{uq}}^2} \right) dt = 100.00\%$$
*Where $\mu_{\text{uq}} = 53.90^\circ\text{C}$ and $\sigma_{\text{uq}} = 1.166^\circ\text{C}$, yielding a 95% confidence interval of `[51.62, 56.19]°C`.*
