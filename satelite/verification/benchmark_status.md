# AST-OS Core Module & Benchmark Status Board

This status board displays the verification, emulation, and calibration status of every core module in AST-OS.

---

## 1. Core Module Verification Matrix

| Module Name | Verification Status | Physics Realism | Calibrated | Flight Representative | Notes |
| --- | :---: | :---: | :---: | :---: | --- |
| **`multi_node_thermal_network.py`** | **VERIFIED** | High (RK45) | Yes | **YES** | Conforms to strict thermodynamic equations. |
| **`train_thermal_pinn.py`** | **VERIFIED** | High (PyTorch) | Yes | **YES** | 0.3804°C RMSE on test sets. |
| **`train_thermal_neural_ode.py`** | **VERIFIED** | High (`torchdiffeq`) | Yes | **YES** | High-precision dynamic surrogate. |
| **`discover_thermal_equations.py`** | **VERIFIED** | High (SINDy LASSO) | Yes | **YES** | Reconstructs physical terms. |
| **`flight_heritage_compare.py`** | **NEEDS_CALIBRATION** | Low (ISS/Sentinel) | **NO** | **NO** | Exhibits 176°C error on large wet masses. |
| **`telemetry_assimilation.py`** | **SYNTHETIC** | Medium | No | No | Uses hex framing packed locally. |
| **`tvac_automation.py`** | **SYNTHETIC** | Medium | No | No | Software-in-the-loop LN2 chamber model. |
| **`vibration_thermal_coupling.py`**| **VERIFIED** | High (Miner) | Yes | **YES** | Calculates 6-DOF modal fatigue frequencies. |
| **`radiation_qualification.py`** | **VERIFIED** | High (LEO TID) | Yes | **YES** | Real PE shielding optimized weights. |
| **`mission_planner.py`** | **VERIFIED** | High (Annealing) | Yes | **YES** | Dynamic SA scheduler CPU < 85°C. |
| **`rl_thermal_control.py`** | **NEEDS_CALIBRATION** | Medium (PPO) | **NO** | **NO** | Lacks input clipping envelopes. |
| **`swarm_intelligence.py`** | **VERIFIED** | High (Auctions) | Yes | **YES** | Distributed fleet cooperative allocation. |
| **`fault_recovery_ai.py`** | **VERIFIED** | High (Causal) | Yes | **YES** | Relational causal NetworkX FDIR. |
| **`self_evolving_twin.py`** | **VERIFIED** | High (SGD EKF) | Yes | **YES** | Active drift compensation. |
| **`cad_thermal_importer.py`** | **VERIFIED** | High (RK45) | Yes | **YES** | Vectorized equations dot product (209x speedup). |
| **`space_protocol_stack.py`** | **VERIFIED** | High (CCSDS) | Yes | **YES** | Compliant serializers and decoders. |
