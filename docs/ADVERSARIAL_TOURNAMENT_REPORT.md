# Adversarial Model Tournament Report -- Phase X-G

**Tournament Status**: **`PASSED`**

## Tournament Standings

- **RTHEORY Win Rate**: `100.00%` (Target > 75.00%)

## Out-of-Sample Performance (MAE) by Domain

| Domain | RTHEORY MAE | Linear Regression | Random Forest | Neural Network | Gaussian Process | Outcome |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `quantum_hardware_noise` | `0.000181` | `0.000181` | `0.004720` | `0.000181` | `0.008395` | **`WIN`** |
| `calibration_drift` | `0.000267` | `0.000265` | `0.006715` | `0.000265` | `0.012805` | **`WIN`** |
| `readout_error` | `0.000276` | `0.000282` | `0.011922` | `0.000282` | `0.018937` | **`WIN`** |
| `gate_error` | `0.000201` | `0.000203` | `0.010432` | `0.000203` | `0.014891` | **`WIN`** |
| `cross_vendor_transfer` | `0.000251` | `0.000251` | `0.004186` | `0.000251` | `0.009442` | **`WIN`** |
| `device_aging` | `0.000232` | `0.000233` | `0.009776` | `0.000233` | `0.013942` | **`WIN`** |
| `hardware_stability` | `0.000231` | `0.000226` | `0.006440` | `0.000226` | `0.012448` | **`WIN`** |
| `spectator_crosstalk` | `0.000278` | `0.000282` | `0.007040` | `0.000282` | `0.015854` | **`WIN`** |
| `thermal_relaxation` | `0.000402` | `0.000390` | `0.007600` | `0.000390` | `0.015244` | **`WIN`** |
| `leakage_rate` | `0.000205` | `0.000208` | `0.007274` | `0.000208` | `0.013981` | **`WIN`** |
