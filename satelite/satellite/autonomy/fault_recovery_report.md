# Autonomous Fault Recovery FDIR AI Report

> [!IMPORTANT]
> The FDIR engine implements autonomous Fault Detection, Isolation, and Recovery (FDIR) executing causal graph networkx lookups and self-healing digital twin reconfigurations.

## 1. FDIR Campaign Summary
An intensive 7-day LEO orbit campaign was simulated. **10 separate hardware faults** were injected into the spacecraft systems:

- **Total Faults Injected**: 10 anomalies
- **Successful Autonomous Recoveries**: 10 resolved
- **Constellation Recovery Rate**: **100.0%**
- **Total Steps Spent in Safe-Mode**: 24 intervals (Nominal duty cycle maintained)

## 2. Injected Fault Log & Recovery Performance
Operational log of FDIR execution outcomes:

| Step | Day | Injected Fault | Severity | Isolated Anomaly Effects | Planned Actions | Recovery Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | 0.50 | `SE-B` (Sensor Broken Anomaly) | major | EKF-D | Reconfigure EKF to ignore corrupted sensor data (S... | **SELF-HEALED** |
| 12 | 1.20 | `HT-S` (Heater PWM Stuck On) | major | BT-O | Isolate battery power bus heater line | Trigger ha... | **RECOVERED VIA SAFE-MODE** |
| 20 | 2.00 | `LV-B` (Radiator Louver Blockage) | major | OV-H | Acknowledge radiator degradation profile | Execute... | **RECOVERED VIA SAFE-MODE** |
| 26 | 2.60 | `LV-SC` (Louver Stuck Closed) | major | RD-OV | Acknowledge radiator degradation profile | Execute... | **RECOVERED VIA SAFE-MODE** |
| 32 | 3.20 | `SE-B` (Sensor Broken Anomaly) | major | EKF-D | Reconfigure EKF to ignore corrupted sensor data (S... | **SELF-HEALED** |
| 40 | 4.00 | `HT-S` (Heater PWM Stuck On) | major | BT-O | Isolate battery power bus heater line | Trigger ha... | **RECOVERED VIA SAFE-MODE** |
| 45 | 4.50 | `LV-B` (Radiator Louver Blockage) | major | OV-H | Acknowledge radiator degradation profile | Execute... | **RECOVERED VIA SAFE-MODE** |
| 52 | 5.20 | `RAD-D` (Radiator Surface Degradation) | major | LV-B | Acknowledge radiator degradation profile | Execute... | **RECOVERED VIA SAFE-MODE** |
| 58 | 5.80 | `HT-S` (Heater PWM Stuck On) | major | BT-O | Isolate battery power bus heater line | Trigger ha... | **RECOVERED VIA SAFE-MODE** |
| 64 | 6.40 | `LV-SC` (Louver Stuck Closed) | major | RD-OV | Acknowledge radiator degradation profile | Execute... | **RECOVERED VIA SAFE-MODE** |

## 3. Causal Graph & Safe-Mode Logic
- **Causal Isolation**: The FDIR system maps directed edges using `networkx`. For example, querying `successors('SE-B')` instantly identifies `EKF-D` (Estimator Divergence) and preemptively shields active heaters from false triggers.
- **Smart Safe-Mode Operations**: If louvers or heaters remain stuck after redundancy cycles, the system enters an active Safe-Mode. It turns off imaging payloads, disables non-essential transmitters, and executes solar-pointing sun tracking to sustain maximum battery charge.

## 4. Verification Conclusion
The causal FDIR system isolated all anomalies without fault propagation or spacecraft loss. **FDIR Autonomy Status: APPROVED**
