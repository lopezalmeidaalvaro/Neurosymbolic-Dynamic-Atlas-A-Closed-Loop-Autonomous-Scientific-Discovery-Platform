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
| `PRED_001` | 0.3694 | 0.3283 | **0.0411** | 0.0731 |
| `PRED_004` | 0.0756 | 0.0345 | **0.0411** | 0.4721 |
| `PRED_005` | 0.0813 | 0.0402 | **0.0411** | 0.4269 |
| `PRED_009` | 0.0651 | 0.0240 | **0.0411** | 0.5866 |
| `PRED_010` | 0.0968 | 0.0557 | **0.0411** | 0.3387 |
| `PRED_011` | 0.1129 | 0.0718 | **0.0411** | 0.2788 |
| `PRED_003` | 0.1233 | 0.0822 | **0.0411** | 0.2502 |
| `PRED_007` | 0.1276 | 0.0865 | **0.0411** | 0.2401 |
| `PRED_008` | 0.0755 | 0.0344 | **0.0411** | 0.4730 |
| `PRED_002` | 0.0746 | 0.0335 | **0.0411** | 0.4811 |

### Device-Specific Residual Heatmap

| Prediction ID | `ibm_brisbane` | `ibm_sherbrooke` | `rigetti_aspen_m3` | `ionq_aria` | `quantinuum_h1` |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `PRED_001` | +0.0576 | +0.0246 | +0.1071 | +0.0111 | +0.0052 |
| `PRED_004` | +0.0576 | +0.0246 | +0.1071 | +0.0111 | +0.0052 |
| `PRED_005` | +0.0576 | +0.0246 | +0.1071 | +0.0111 | +0.0052 |
| `PRED_009` | +0.0576 | +0.0246 | +0.1071 | +0.0111 | +0.0052 |
| `PRED_010` | +0.0576 | +0.0246 | +0.1071 | +0.0111 | +0.0052 |
| `PRED_011` | +0.0576 | +0.0246 | +0.1071 | +0.0111 | +0.0052 |
| `PRED_003` | +0.0576 | +0.0246 | +0.1071 | +0.0111 | +0.0052 |
| `PRED_007` | +0.0576 | +0.0246 | +0.1071 | +0.0111 | +0.0052 |
| `PRED_008` | +0.0576 | +0.0246 | +0.1071 | +0.0111 | +0.0052 |
| `PRED_002` | +0.0576 | +0.0246 | +0.1071 | +0.0111 | +0.0052 |
