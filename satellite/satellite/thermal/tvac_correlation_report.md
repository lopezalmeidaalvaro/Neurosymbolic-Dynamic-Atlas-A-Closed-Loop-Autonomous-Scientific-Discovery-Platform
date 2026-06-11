# TVAC Thermal Telemetry Correlation & Calibration Report

**Date Generated:** 2026-05-28 15:22:10
**Evaluated TVAC File:** `tvac_results.csv`
**ESA Reference Standard:** ECSS-E-ST-31C (Spacecraft Thermal Control)

---

## 📊 Conformity Evaluation

⚠️ **CONFORMITY STATUS: NON-COMPLIANT**
Certain nodes exceed the standard temperature deviations allowed by **ECSS-E-ST-31C**. Recalibration of parameters is required.

### ECSS Deviation Limits Reference
* **Steady State Allowed Margin:** $\pm 3.0^\circ\text{C}$
* **Transient State Allowed Margin:** $\pm 5.0^\circ\text{C}$

---

## 📈 Nodal Correlation Metrics

| Thermal Node | RMSE (°C) | MAE / Steady SS (°C) | Max Error / Transient (°C) | ECSS Compliance Status |
|--------------|-----------|----------------------|---------------------------|------------------------|
| CPU          |   14.1976 |              12.2689 |                   21.0936 | NON_COMPLIANT          |
| Battery      |   14.3638 |              11.3890 |                   24.7439 | NON_COMPLIANT          |
| Payload      |   14.5365 |              12.1041 |                   22.5152 | NON_COMPLIANT          |
| Structure    |   13.7110 |              11.6032 |                   21.0227 | NON_COMPLIANT          |
| Radiator     |   12.6304 |              10.7412 |                   20.6227 | NON_COMPLIANT          |
| Panels       |   14.0188 |              12.2301 |                   23.1247 | NON_COMPLIANT          |

---

## 🔬 Experimental Setup & Emulation Parameters

* **Gauge Vacuum Pressure:** {AVG_PRESSURE:.2e} mbar (convection negligible: verified)
* **Active Shroud Cooling Sink:** 80.00 K (-193.15°C LN2 shroud simulation)
* **Sensor Thermal Mass Delay (Lag):** $\tau_{sensor} = 15.0\text{ s}$
* **Precision Sensor Noise Floor:** $\sigma_{PT100} = 0.20^\circ\text{C}$
* **Infrared Sensor Noise Floor:** $\sigma_{IR} = 1.00^\circ\text{C}$

### Sensor Lag Formulation
A first-order thermal mass filter is applied to model physical thermocouple response delays inside the chamber:
$$T_{sensor}(t) = (1 - \alpha) \cdot T_{sensor}(t-dt) + \alpha \cdot T_{real}(t)$$
Where $\alpha = \frac{dt}{dt + \tau_{sensor}}$.

---

## 📊 TVAC Diagnostic Visualization

The thermal correlations are exported to diagnostic figures showing the heating, passive cooling, and stabilization cycles inside the TVAC cold shroud environment.

![TVAC Calibration Plots](tvac_correlation_plots.png)

---
*DEMONSTRATION ONLY — Certified placeholder. Requires hardware DAQ connection.*
