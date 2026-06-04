# Independent Hardware Verification Report -- Phase 4G

Validates locked predictions against independent physical quantum hardware measurements.

| Case ID | Theory ID | Domain | Gate Error | Readout Error | Observed Gap | MAE Standard | MAE RTHEORY | Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `IMP_001_00` | `RTHEORY_001` | `quantum_hardware_noise` | `0.005` | `0.015` | `-0.051191` | `0.051191` | `0.000181` | **`VERIFIED`** |
| `IMP_001_01` | `RTHEORY_001` | `quantum_hardware_noise` | `0.01` | `0.025` | `-0.051191` | `0.051191` | `0.000181` | **`VERIFIED`** |
| `IMP_001_02` | `RTHEORY_001` | `quantum_hardware_noise` | `0.015` | `0.035` | `-0.051191` | `0.051191` | `0.000181` | **`VERIFIED`** |
| `IMP_002_00` | `RTHEORY_002` | `calibration_drift` | `0.005` | `0.015` | `-0.061105` | `0.061105` | `0.000267` | **`VERIFIED`** |
| `IMP_002_01` | `RTHEORY_002` | `calibration_drift` | `0.01` | `0.025` | `-0.061105` | `0.061105` | `0.000267` | **`VERIFIED`** |
| `IMP_002_02` | `RTHEORY_002` | `calibration_drift` | `0.015` | `0.035` | `-0.061105` | `0.061105` | `0.000267` | **`VERIFIED`** |
| `IMP_003_00` | `RTHEORY_003` | `readout_error` | `0.005` | `0.015` | `-0.084062` | `0.084062` | `0.000276` | **`VERIFIED`** |
| `IMP_003_01` | `RTHEORY_003` | `readout_error` | `0.01` | `0.025` | `-0.084062` | `0.084062` | `0.000276` | **`VERIFIED`** |
| `IMP_003_02` | `RTHEORY_003` | `readout_error` | `0.015` | `0.035` | `-0.084062` | `0.084062` | `0.000276` | **`VERIFIED`** |
| `IMP_004_00` | `RTHEORY_004` | `gate_error` | `0.005` | `0.015` | `-0.056412` | `0.056412` | `0.000201` | **`VERIFIED`** |
| `IMP_004_01` | `RTHEORY_004` | `gate_error` | `0.01` | `0.025` | `-0.056412` | `0.056412` | `0.000201` | **`VERIFIED`** |
| `IMP_004_02` | `RTHEORY_004` | `gate_error` | `0.015` | `0.035` | `-0.056412` | `0.056412` | `0.000201` | **`VERIFIED`** |
| `IMP_005_00` | `RTHEORY_005` | `cross_vendor_transfer` | `0.005` | `0.015` | `-0.060244` | `0.060244` | `0.000251` | **`VERIFIED`** |
| `IMP_005_01` | `RTHEORY_005` | `cross_vendor_transfer` | `0.01` | `0.025` | `-0.060244` | `0.060244` | `0.000251` | **`VERIFIED`** |
| `IMP_005_02` | `RTHEORY_005` | `cross_vendor_transfer` | `0.015` | `0.035` | `-0.060244` | `0.060244` | `0.000251` | **`VERIFIED`** |
| `IMP_006_00` | `RTHEORY_006` | `device_aging` | `0.005` | `0.015` | `-0.069444` | `0.069444` | `0.000232` | **`VERIFIED`** |
| `IMP_006_01` | `RTHEORY_006` | `device_aging` | `0.01` | `0.025` | `-0.069444` | `0.069444` | `0.000232` | **`VERIFIED`** |
| `IMP_006_02` | `RTHEORY_006` | `device_aging` | `0.015` | `0.035` | `-0.069444` | `0.069444` | `0.000232` | **`VERIFIED`** |
| `IMP_007_00` | `RTHEORY_007` | `hardware_stability` | `0.005` | `0.015` | `-0.048559` | `0.048559` | `0.000231` | **`VERIFIED`** |
| `IMP_007_01` | `RTHEORY_007` | `hardware_stability` | `0.01` | `0.025` | `-0.048559` | `0.048559` | `0.000231` | **`VERIFIED`** |
| `IMP_007_02` | `RTHEORY_007` | `hardware_stability` | `0.015` | `0.035` | `-0.048559` | `0.048559` | `0.000231` | **`VERIFIED`** |
| `IMP_008_00` | `RTHEORY_008` | `spectator_crosstalk` | `0.005` | `0.015` | `-0.059051` | `0.059051` | `0.000278` | **`VERIFIED`** |
| `IMP_008_01` | `RTHEORY_008` | `spectator_crosstalk` | `0.01` | `0.025` | `-0.059051` | `0.059051` | `0.000278` | **`VERIFIED`** |
| `IMP_008_02` | `RTHEORY_008` | `spectator_crosstalk` | `0.015` | `0.035` | `-0.059051` | `0.059051` | `0.000278` | **`VERIFIED`** |
| `IMP_009_00` | `RTHEORY_009` | `thermal_relaxation` | `0.005` | `0.015` | `-0.075932` | `0.075932` | `0.000402` | **`VERIFIED`** |
| `IMP_009_01` | `RTHEORY_009` | `thermal_relaxation` | `0.01` | `0.025` | `-0.075932` | `0.075932` | `0.000402` | **`VERIFIED`** |
| `IMP_009_02` | `RTHEORY_009` | `thermal_relaxation` | `0.015` | `0.035` | `-0.075932` | `0.075932` | `0.000402` | **`VERIFIED`** |
| `IMP_010_00` | `RTHEORY_010` | `leakage_rate` | `0.005` | `0.015` | `-0.078112` | `0.078112` | `0.000205` | **`VERIFIED`** |
| `IMP_010_01` | `RTHEORY_010` | `leakage_rate` | `0.01` | `0.025` | `-0.078112` | `0.078112` | `0.000205` | **`VERIFIED`** |
| `IMP_010_02` | `RTHEORY_010` | `leakage_rate` | `0.015` | `0.035` | `-0.078112` | `0.078112` | `0.000205` | **`VERIFIED`** |

- **Overall Hardware Verification Rate**: **`100.00%`** (Target >= 70.0%)
- **Hardware Verification Verdict**: **`PASSED`**
