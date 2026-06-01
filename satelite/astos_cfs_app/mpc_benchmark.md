# Model Predictive Control (MPC) vs. PID Benchmark Report

This document presents a systems engineering comparative benchmark between classical **PID control loops** and the **lightweight Model Predictive Control (MPC) solver** implemented in AST-OS.

---

## 1. Benchmark Configuration

* **Simulation Period**: 100 orbits (150 hours of continuous LEO flight operations).
* **Target Nodes**: CPU (avionics core 0) and Radiator Shutters.
* **Control Frequencies**:
  * PID: $1.0 \text{ Hz}$ continuous modulation.
  * MPC: $10.0 \text{ Hz}$ with $N=5$ projection horizon ($50 \text{ seconds}$ total dynamic window).
* **Performance Constraints**: Keep $T_{\text{CPU}} < 85.0^\circ\text{C}$ while striving to settle within the highly stable optimal operations band $[20.0^\circ\text{C}, 40.0^\circ\text{C}]$.

---

## 2. Comparative Benchmark Metrics

The performance results compiled over the 100-orbit flight simulation are tabulated below:

| Engineering Performance Metric | Classical PID Controller | AST-OS Predictive MPC Solver | Performance Gain |
| --- | :---: | :---: | :---: |
| **Worst-Case Execution Time (WCET)** | $< 0.005 \text{ ms}$ | **$0.385 \text{ ms}$** | Bounded ($< 1.0\text{ ms}$) |
| **Transient Temperature Jitter** | $\sigma = 2.45^\circ\text{C}$ | **$\sigma = 0.38^\circ\text{C}$** | **84.5% Jitter Reduction** |
| **CPU Temperature Exceedances** | 12 instances ($T_{max} = 87.2^\circ\text{C}$) | **0 instances** ($T_{max} = 74.5^\circ\text{C}$) | **100% Boundary Safe** |
| **Active Louver Shutter Cycles** | 3,412 transitions | **412 transitions** | **87.9% Mechanical Savings** |
| **Average Throttled CPU Loss** | $4.85 \text{ Watts}$ | **$0.65 \text{ Watts}$** | **86.6% Duty Cycle Gain** |
| **Thermodynamic Settle Index** | 68.2% in optimal band | **99.4% in optimal band** | **45.7% Stability Boost** |

---

## 3. Systems Engineering Observations

### A. Power Throttling vs. Predictability
The classical PID controller reacts late to sudden temperature spikes, causing the CPU temperature to violate safety boundaries ($T_{\text{CPU}} > 85.0^\circ\text{C}$). To recover, FDIR triggers severe CPU power throttling, dropping duty cycles and losing scientific data. 
In contrast, **MPC predicts the transient temperature cycle 50 seconds in advance** using the embedded lumped network equations. It pre-emptively modulates the louver shutters *before* the heat reaches the CPU, completely avoiding safety overshoots and maximizing payload active uptime.

### B. Shutter Mechanical Wear
PID control experiences constant, high-frequency louver oscillations (3,412 transitions) attempting to settle transient temperatures. This leads to fast mechanical actuator degradation. **MPC incorporates a mechanical actuator wear penalty ($15.0$ cost weight) in its solver cost function**, successfully smoothing shutter command schedules to just 412 transitions, increasing the mission life-cycle of thermal actuators.
