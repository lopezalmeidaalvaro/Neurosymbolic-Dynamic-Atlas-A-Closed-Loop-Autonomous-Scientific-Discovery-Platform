# Out-of-Sample Theory Tournament Report — Phase 3B.1

Comparative tournament pitting simulator-derived theories against the reality-native theory on independent hardware data.

## Theory Tournament Leaderboard

| Rank | ID | Name | MAE | RMSE | Median Error | Calibration Error | Status |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `RTHEORY_001` | Reality-Native Noise-Decoupled Theory | `0.000099` | `0.000106` | `0.000101` | `0.019901` | **`CONFIRMED`** |
| 2 | `SIM_THEORY` | Simulator-Derived Baseline Theories | `0.017454` | `0.019086` | `0.016655` | `0.482546` | `FALSIFIED` |

## Measured Generalization Comparison

- **Relative Error Reduction**: `99.43%` improvement in MAE over the baseline simulator model.
- **Median Deviation Reduction**: `99.39%` reduction in median error.
