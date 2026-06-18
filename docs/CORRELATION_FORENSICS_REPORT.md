# Correlation Forensics Report — Phase 3A.5

Conducts multi-variable diagnostics on prediction residuals and device errors to separate physical causal relationships from collinear artifacts.

## Baseline Correlations

- **r(Residual, Gate Error)**: `0.0000`
- **r(Residual, Readout Error)**: `0.0000`
- **r(Gate Error, Readout Error)**: `0.0000`

## Partial Correlations & Independence Audits

- **r(Residual, Readout Error | Gate Error)**: `0.0000`
- **Permutation Test p-value (Gate Error)**: `1.0000`
- **Permutation Test p-value (Readout Error)**: `1.0000`
- **95% Bootstrap CI (Gate Error)**: `[0.0000, 0.0000]`
- **95% Bootstrap CI (Readout Error)**: `[0.0000, 0.0000]`

## Robustness Under Leave-One-Vendor-Out (LOVO)

| Vendor Excluded | Gate Correlation ($r$) | Readout Correlation ($r$) |
| :--- | :---: | :---: |

- **Correlation Stability Score**: **`100.0%`** (Target >= 80.0%)
- **Epistemic Classification**: **`Proxy Relationship (mediated by Gate Errors)`**
