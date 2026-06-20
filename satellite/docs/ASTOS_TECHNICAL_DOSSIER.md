# AST-OS Technical Dossier

## 1. Executive Summary
The Aerospace Spacecraft Thermal Operating System (AST-OS) is a high-fidelity digital twin framework designed to model, simulate, and monitor spacecraft thermal dynamics. By translating CAD models into nodal network grids, AST-OS solves conductive and radiative transfer equations to predict thermal transients and detect anomalies in real time.

## 2. Purpose
The purpose of AST-OS is to provide real-time spacecraft thermal telemetry validation, fault detection, isolation, and recovery (FDIR) during orbital missions, ensuring instrument thermal safety and operational continuity.

## 3. Architecture
The digital twin pipeline translates geometric representations into physical simulation networks:

```
   +-----------------------+
   | Spacecraft CAD Model  |
   +-----------+-----------+
               |
               v
   [Voxelization & Node Mapping]
               |
               v
   [Thermal Resistance Solver]  <-- Conductive & radiative node networks
               |
               v
   [Hardware-in-the-Loop]       <-- Runs SIL/HIL simulation cycles
```

### Core Subsystems
*   **Voxelization Module**: Discretizes complex CAD geometries into network nodes.
*   **Thermal Network Solver**: Solves transient heat transfer equations across the node graph.
*   **FDIR Interface**: Monitors sensor feeds against twin state predictions to identify discrepancies (residuals).

## 4. Methodology
*   **Conductive & Radiative Heat Transfer**: Resolves node-to-node conductive resistance based on material tensors. Radiative exchanges are computed dynamically using view-factor matrices derived from the spatial orientations of the spacecraft facets.
*   **Transient State Integration**: Solves the heat balance differential equations:
    $$C_i \frac{dT_i}{dt} = Q_i + \sum_j K_{ji}(T_j - T_i) + \sum_j R_{ji}(T_j^4 - T_i^4)$$
    where $C_i$ is thermal capacity, $Q_i$ is internal heat generation, $K$ is conduction, and $R$ is radiation.
*   **Residual-Based Fault Isolation**: The FDIR system computes difference residuals between physical sensor telemetry and transient digital twin predictions.

## 5. Results
*   **Simulation Loop Latency**: Conductive-radiative transient solver runs in **$<8.5\text{ ms}$** on target ARM Cortex-M processors, permitting real-time synchronization.
*   **Thermal Vacuum Chamber Alignment**: Temperature predictions correspond to empirical vacuum chamber testing results within **$\pm 0.8^\circ\text{C}$**.

## 6. Validation
*   **FDIR Verification**: Tested by injecting radiator blockages, battery runway scenarios, and sensor failures. The system isolated **$97.8\%$** of heater failures within $15$ seconds.
*   **ECSS Compliance**: Telemetry frame encoding and safety command execution follow the ECSS-compliant space packet protocol codecs (PUS standards).

## 7. Limitations
*   **Geometric Resolution Constraints**: High-density CAD models must undergo decimation and voxel limit constraints (typically capping nodes at $\le 1000$) to run within the memory boundaries of embedded spacecraft computer systems.
*   **MLI Degradation Uncertainty**: The conductive solver assumes isotropic multi-layer insulation (MLI) degradation, which may diverge from local physical tearing.

## 8. Future Work
*   **Orbital Ray-Tracing Acceleration**: Offloading view-factor calculations to hardware-accelerated GPUs for complex articulated payload sweeps.
*   **Physics-Informed Neural Networks (PINNs)**: Training surrogate ML models to bypass numerical integration loops on ultra-low-power microcontrollers.

## 9. Source Documents
*   [ASTOS_TECHNICAL_DOSSIER.md (Original)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/ASTOS_TECHNICAL_DOSSIER.md)
*   [satellite/ARCHITECTURE.md (Consolidated)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/ARCHITECTURE.md)
