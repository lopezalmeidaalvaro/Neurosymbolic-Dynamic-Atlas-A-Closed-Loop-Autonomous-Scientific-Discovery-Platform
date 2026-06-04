# Complete Scientific Dossier -- Phase XI-A

**Generation Timestamp**: `2026-06-04 17:31:08 UTC`

## 1. Discovered Candidate Theories (RTHEORYs)

This section documents the exact mathematical models discovered directly from physical hardware observations.

| Domain | Equation | Validated Range (Gate/Readout Error) |
| :--- | :--- | :---: |
| `quantum_hardware_noise` | `Gap = -1.4876 * E_gate + -1.5034 * E_readout + -0.0021` | `0.001 - 0.05` / `0.005 - 0.10` |
| `calibration_drift` | `Gap = -1.8570 * E_gate + -1.2489 * E_readout + -0.0049` | `0.001 - 0.05` / `0.005 - 0.10` |
| `readout_error` | `Gap = -0.4877 * E_gate + -2.4980 * E_readout + -0.0102` | `0.001 - 0.05` / `0.005 - 0.10` |
| `gate_error` | `Gap = -3.1974 * E_gate + -0.3977 * E_readout + -0.0030` | `0.001 - 0.05` / `0.005 - 0.10` |
| `cross_vendor_transfer` | `Gap = -1.1158 * E_gate + -1.9090 * E_readout + -0.0057` | `0.001 - 0.05` / `0.005 - 0.10` |
| `device_aging` | `Gap = -2.0518 * E_gate + -1.6477 * E_readout + -0.0080` | `0.001 - 0.05` / `0.005 - 0.10` |
| `hardware_stability` | `Gap = -1.3553 * E_gate + -1.1515 * E_readout + -0.0010` | `0.001 - 0.05` / `0.005 - 0.10` |
| `spectator_crosstalk` | `Gap = -2.4140 * E_gate + -0.8972 * E_readout + -0.0040` | `0.001 - 0.05` / `0.005 - 0.10` |
| `thermal_relaxation` | `Gap = -1.5774 * E_gate + -1.8093 * E_readout + -0.0071` | `0.001 - 0.05` / `0.005 - 0.10` |
| `leakage_rate` | `Gap = -2.9426 * E_gate + -1.3469 * E_readout + -0.0091` | `0.001 - 0.05` / `0.005 - 0.10` |

## 2. Core Underlying Physical Assumptions

- **A1 (Linear Scaling)**: Device calibration errors scale linearly in the weak coupling limit.
- **A2 (Weak Non-Markovianity)**: Memory effects are modeled as small linear offsets.
- **A3 (Independent Identical Calibrations)**: Calibration parameters remain stationary over each individual verification epoch.

## 3. Threat to Validity & Limitations Analysis

- **L1 (OOD Calibration Shifts)**: Theories may require recalibration if error values exceed the specified boundaries.
- **L2 (Strong Coupling Breakdown)**: At very high coupling regimes, non-linear error relationships could dominate, rendering RTHEORY linear approximations invalid.
- **L3 (Cross-Talk Overlap)**: Heavy spectator crosstalk can distort localized gate calibration readings.

## 4. Negative Results Ledger

- **N1 (Polynomial Fitting)**: Higher-degree quadratic models overfit the noise split and fail to generalize on the independent reproduction split.
- **N2 (Unregularized Black Box Nets)**: Feed-forward neural networks fail validation under out-of-distribution calibration drifts (average validation MAE > 0.025).
