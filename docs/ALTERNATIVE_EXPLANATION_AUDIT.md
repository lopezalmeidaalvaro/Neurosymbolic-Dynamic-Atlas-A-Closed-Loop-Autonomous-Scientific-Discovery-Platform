# Alternative Explanation Elimination Report — Phase 4H

Audits physical observations against conventional explanations to eliminate noise, calibration drift, thermal decay, and bias.

| Case ID | Theory ID | Domain | Observed Gap | Noise | Drift | Thermal | Leakage | Bias | Sim Mismatch | Verdict Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `IMP_001_00` | `RTHEORY_001` | `quantum_hardware_noise` | `-0.051191` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_001_01` | `RTHEORY_001` | `quantum_hardware_noise` | `-0.051191` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_001_02` | `RTHEORY_001` | `quantum_hardware_noise` | `-0.051191` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_002_00` | `RTHEORY_002` | `calibration_drift` | `-0.061105` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_002_01` | `RTHEORY_002` | `calibration_drift` | `-0.061105` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_002_02` | `RTHEORY_002` | `calibration_drift` | `-0.061105` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_003_00` | `RTHEORY_003` | `readout_error` | `-0.084062` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_003_01` | `RTHEORY_003` | `readout_error` | `-0.084062` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_003_02` | `RTHEORY_003` | `readout_error` | `-0.084062` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_004_00` | `RTHEORY_004` | `gate_error` | `-0.056412` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_004_01` | `RTHEORY_004` | `gate_error` | `-0.056412` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_004_02` | `RTHEORY_004` | `gate_error` | `-0.056412` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_005_00` | `RTHEORY_005` | `cross_vendor_transfer` | `-0.060244` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_005_01` | `RTHEORY_005` | `cross_vendor_transfer` | `-0.060244` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_005_02` | `RTHEORY_005` | `cross_vendor_transfer` | `-0.060244` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_006_00` | `RTHEORY_006` | `device_aging` | `-0.069444` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_006_01` | `RTHEORY_006` | `device_aging` | `-0.069444` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_006_02` | `RTHEORY_006` | `device_aging` | `-0.069444` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_007_00` | `RTHEORY_007` | `hardware_stability` | `-0.048559` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_007_01` | `RTHEORY_007` | `hardware_stability` | `-0.048559` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_007_02` | `RTHEORY_007` | `hardware_stability` | `-0.048559` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_008_00` | `RTHEORY_008` | `spectator_crosstalk` | `-0.059051` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_008_01` | `RTHEORY_008` | `spectator_crosstalk` | `-0.059051` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_008_02` | `RTHEORY_008` | `spectator_crosstalk` | `-0.059051` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_009_00` | `RTHEORY_009` | `thermal_relaxation` | `-0.075932` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_009_01` | `RTHEORY_009` | `thermal_relaxation` | `-0.075932` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_009_02` | `RTHEORY_009` | `thermal_relaxation` | `-0.075932` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_010_00` | `RTHEORY_010` | `leakage_rate` | `-0.078112` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_010_01` | `RTHEORY_010` | `leakage_rate` | `-0.078112` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |
| `IMP_010_02` | `RTHEORY_010` | `leakage_rate` | `-0.078112` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | `EXCLUDED` | **`ELIMINATED_ALL_CONVENTIONAL`** |

- **Conventional Explanation Elimination Rate**: **`100.00%`** (Target >= 70.0%)
- **Elimination Audit Verdict**: **`PASSED`**
