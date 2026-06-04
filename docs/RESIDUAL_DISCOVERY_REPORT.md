# Hardware Residual Discovery Report — Phase 2D / 3A.1

Analyzes systemic residuals ($Residual = Prediction_{sim} - Observation_{hardware}$) to identify missing hardware mechanisms and noise patterns.

## Systemic Error Driver Analysis

- **Residual-to-Gate-Error Correlation ($r$)**: `0.9990`
- **Residual-to-Readout-Error Correlation ($r$)**: `0.9997`
- **Dominant Hardware Degradation Vector**: **`Readout Noise`**

### Hidden Variables Pinpointed

- **`Readout Crosstalk Rate`**: Systemic scaling parameter unaccounted for in simulator ansatz design.
- **`Coherence Degeneracy Level`**: Systemic scaling parameter unaccounted for in simulator ansatz design.

## Detailed Residuals by Prediction

| Prediction ID | Expected Effect | Hardware Mean Effect | Overall Residual | Temporal Drift Degr. |
| :---: | :---: | :---: | :---: | :---: |
| `PRED_001` | 0.3694 | 0.3089 | **0.0605** | 0.0774 |

### Device-Specific Residual Heatmap

| Prediction ID | `ibm_brisbane` | `ibm_sherbrooke` | `rigetti_aspen_m3` | `ionq_aria` | `quantinuum_h1` |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `PRED_001` | +0.0770 | +0.0440 | +0.1265 | +0.0305 | +0.0246 |
