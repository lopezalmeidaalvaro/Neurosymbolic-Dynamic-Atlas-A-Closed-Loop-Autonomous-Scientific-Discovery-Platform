# Correlation Forensics Report — Phase 3A.5

Conducts multi-variable diagnostics on prediction residuals and device errors to separate physical causal relationships from collinear artifacts.

## Baseline Correlations

- **r(Residual, Gate Error)**: `0.9990`
- **r(Residual, Readout Error)**: `0.9997`
- **r(Gate Error, Readout Error)**: `0.9976`

## Partial Correlations & Independence Audits

- **r(Residual, Readout Error | Gate Error)**: `0.9999`
- **Permutation Test p-value (Gate Error)**: `0.0110`
- **Permutation Test p-value (Readout Error)**: `0.0100`
- **95% Bootstrap CI (Gate Error)**: `[0.9925, 1.0000]`
- **95% Bootstrap CI (Readout Error)**: `[0.9974, 1.0000]`

## Robustness Under Leave-One-Vendor-Out (LOVO)

| Vendor Excluded | Gate Correlation ($r$) | Readout Correlation ($r$) |
| :--- | :---: | :---: |
| `IonQ` | 0.9990 | 0.9997 |
| `Rigetti` | 0.9976 | 0.9993 |
| `IBM` | 0.9998 | 0.9999 |
| `Quantinuum` | 0.9989 | 0.9996 |

- **Correlation Stability Score**: **`100.0%`** (Target >= 80.0%)
- **Epistemic Classification**: **`Real Relationship`**
