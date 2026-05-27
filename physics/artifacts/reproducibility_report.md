# Phase 8A — Reproducibility Audit Report

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total evaluations | 63 |
| Converged (rel_width < 0.05) | 18 / 63 (28.6%) |
| Stable (CV < 0.05 + converged) | 15 / 63 (23.8%) |
| Median CV | 0.0373 |
| Peak RAM (max) | 5.6 MB |

## Methodology

Seeds are generated via **Sobol quasi-random sequence** (1-D, scrambled),
mapped to integers as $S = \lfloor p \times (2^{31}-1) \rfloor$.

Confidence intervals use **BCa bootstrap** (`scipy.stats.bootstrap`, `method='BCa'`,
`n_resamples=2000`). Sequential adaptive stopping halts when:

$$W_{\text{rel}} = \frac{CI_{\text{hi}} - CI_{\text{lo}}}{|\mu|} < 0.05$$

Hard cap: **50 seeds** per (module, system) combination.

CPU tasks use `ProcessPoolExecutor` (max_workers = cpu_count − 2, min 1).
GPU tasks (NeuralODE, PINN) are **serialized** with `torch.cuda.empty_cache()` and
`torch.cuda.amp.autocast` for mixed precision.

## Stability Table

| module    | system      |   n_seeds |      mean |   ci_lower |   ci_upper |   rel_width |       cv | converged   | stable   |
|:----------|:------------|----------:|----------:|-----------:|-----------:|------------:|---------:|:------------|:---------|
| EV3       | lorenz      |         4 |    3.1503 |   nan      |   nan      |    inf      |   0.3594 | False       | False    |
| EV3       | duffing     |        50 |    2.0722 |     1.9299 |     2.3211 |      0.1888 |   0.3140 | False       | False    |
| EV3       | van_der_pol |        20 |    1.8409 |     1.8266 |     1.8623 |      0.0194 |   0.0226 | True        | True     |
| EV3       | rossler     |        40 |    2.0769 |     2.0315 |     2.1263 |      0.0456 |   0.0755 | True        | False    |
| EV3       | logistic    |        20 |    2.5362 |     2.5111 |     2.5632 |      0.0205 |   0.0236 | True        | True     |
| EV3       | ECG200      |        20 |    1.5378 |     1.5105 |     1.5602 |      0.0323 |   0.0373 | True        | True     |
| EV3       | ECG5000     |        20 |    1.5378 |     1.5128 |     1.5604 |      0.0310 |   0.0373 | True        | True     |
| EV3_EXT   | lorenz      |        50 |  232.2864 |   218.4023 |   241.8597 |      0.1010 |   0.1749 | False       | False    |
| EV3_EXT   | duffing     |        50 |  285.0265 |   273.4848 |   291.6460 |      0.0637 |   0.1079 | False       | False    |
| EV3_EXT   | van_der_pol |        20 |  299.0672 |   299.0571 |   299.0771 |      0.0001 |   0.0001 | True        | True     |
| EV3_EXT   | rossler     |        20 |  299.5440 |   299.5068 |   299.5629 |      0.0002 |   0.0002 | True        | True     |
| EV3_EXT   | logistic    |        20 |   51.2886 |    50.6892 |    51.9941 |      0.0254 |   0.0298 | True        | True     |
| EV3_EXT   | ECG200      |        50 |   10.4700 |    10.2371 |    10.7629 |      0.0502 |   0.0903 | False       | False    |
| EV3_EXT   | ECG5000     |        50 |   10.4700 |    10.2492 |    10.7540 |      0.0482 |   0.0903 | True        | False    |
| EV3_DEEP  | lorenz      |        30 |  330.9726 |   321.5268 |   338.0160 |      0.0498 |   0.0711 | True        | False    |
| EV3_DEEP  | duffing     |        50 |  333.1167 |   318.0827 |   343.9607 |      0.0777 |   0.1392 | False       | False    |
| EV3_DEEP  | van_der_pol |        20 |  363.3822 |   362.9118 |   363.8399 |      0.0026 |   0.0031 | True        | True     |
| EV3_DEEP  | rossler     |        20 |  364.9516 |   364.3368 |   365.6345 |      0.0036 |   0.0041 | True        | True     |
| EV3_DEEP  | logistic    |        50 |  229.0171 |   217.7459 |   256.0952 |      0.1675 |   0.2625 | False       | False    |
| EV3_DEEP  | ECG200      |        20 |  104.9322 |   103.9435 |   105.8734 |      0.0184 |   0.0215 | True        | True     |
| EV3_DEEP  | ECG5000     |        20 |  104.9322 |   103.9435 |   105.8734 |      0.0184 |   0.0215 | True        | True     |
| EV3_SCI   | lorenz      |        50 |  506.9472 |   494.2188 |   522.2608 |      0.0553 |   0.1013 | False       | False    |
| EV3_SCI   | duffing     |        50 | 1179.1353 |   930.4518 |  1433.0291 |      0.4262 |   0.7997 | False       | False    |
| EV3_SCI   | van_der_pol |        20 |  484.8914 |   484.5368 |   485.2383 |      0.0014 |   0.0017 | True        | True     |
| EV3_SCI   | rossler     |        20 |  488.8430 |   487.8555 |   490.3969 |      0.0052 |   0.0059 | True        | True     |
| EV3_SCI   | logistic    |        50 |  396.5135 |   388.6368 |   416.0893 |      0.0692 |   0.1086 | False       | False    |
| EV3_SCI   | ECG200      |        20 |  337.7494 |   337.4403 |   338.0388 |      0.0018 |   0.0021 | True        | True     |
| EV3_SCI   | ECG5000     |        20 |  337.7494 |   337.4403 |   338.0388 |      0.0018 |   0.0021 | True        | True     |
| SINDy     | lorenz      |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| SINDy     | duffing     |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| SINDy     | van_der_pol |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| SINDy     | rossler     |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| SINDy     | logistic    |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| SINDy     | ECG200      |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| SINDy     | ECG5000     |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| Topology  | lorenz      |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| Topology  | duffing     |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| Topology  | van_der_pol |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| Topology  | rossler     |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| Topology  | logistic    |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| Topology  | ECG200      |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| Topology  | ECG5000     |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| Koopman   | lorenz      |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| Koopman   | duffing     |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| Koopman   | van_der_pol |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| Koopman   | rossler     |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| Koopman   | logistic    |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| Koopman   | ECG200      |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| Koopman   | ECG5000     |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| NeuralODE | lorenz      |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| NeuralODE | duffing     |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| NeuralODE | van_der_pol |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| NeuralODE | rossler     |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| NeuralODE | logistic    |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| NeuralODE | ECG200      |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| NeuralODE | ECG5000     |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| PINN      | lorenz      |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| PINN      | duffing     |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| PINN      | van_der_pol |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| PINN      | rossler     |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| PINN      | logistic    |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| PINN      | ECG200      |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |
| PINN      | ECG5000     |        50 |  nan      |   nan      |   nan      |    inf      | nan      | False       | False    |

## Violin Plots

See [`figures/reproducibility_violin.pdf`](../figures/reproducibility_violin.pdf)
for metric distribution per module across all Sobol seeds.

## Notes

- `converged=True` indicates rel_width < 0.05 was achieved before the 50-seed cap.
- `stable=True` additionally requires CV < 0.05.
- `N/A` values indicate modules that raised exceptions on all seeds.
