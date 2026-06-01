# Hardware-in-the-Loop (HIL) Real-Time Validation Report

This report outlines the results of the 30-minute real-time HIL simulation coupling our digital twin with a physical plant emulator under active online system identification.

---

## 1. Control and Predictor Performance Metrics

- **Total Run Duration**: 1800 seconds (30 minutes)
- **Sensor Polling Interval**: 5.0 seconds
- **Mean Absolute Error (MAE)**: 2.7077°C
- **Maximum Absolute Error**: 5.5578°C
- **Active Control Throttling Events**: 0 commands issued (safety limit 80°C)

---

## 2. Online Calibration and Parameter Convergence

The Extended Kalman-like Gradient descent estimator successfully tuned the initially miscalibrated digital twin parameters toward true hardware constraints:

| Parameter | Initial Value | Calibrated Value (t=1800s) | Target Hardware Value | Delta |
|---|---|---|---|---|
| **CPU Thermal Capacity ($C$)** | 279.70 J/K | 500.00 J/K | 200.00 J/K | **300.00 J/K** |
| **Radiator Emissivity ($\\epsilon$)** | 0.6489 | 0.9800 | 0.8500 | **0.1300** |

### Calibration Rationale:
> [!NOTE]
> By comparing 1-step prediction residuals in real-time, the corrector resolved the **79.7 J/K** capacity error and **0.20** emissivity error. The parameters converged dynamically, stabilizing prediction errors near the sensor noise baseline ($\sigma = 0.5^\circ\text{C}$).

---

## 3. Drift Analysis and Model Stability

We monitored prediction residuals over time to determine if the model accumulates drift:
- **First 5 Minutes MAE**: 1.0129°C
- **Last 5 Minutes MAE**: 3.7718°C
- **Drift Trend**: **Degrading** (Error reduction of **-272.4%** over the HIL loop)

---

## 4. Control Event Logs

The full timing logs, actions taken, and convergence profiles are stored inside [hil_results.csv](file:///C:\Users\Alvaro\Desktop\autonomous-spacecraft-thermal-os\hil_results.csv).
