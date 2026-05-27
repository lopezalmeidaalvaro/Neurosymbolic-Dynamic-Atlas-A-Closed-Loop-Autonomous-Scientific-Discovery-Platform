# Phase 8B — Ablation Study Report

## Summary

- Total ablation rows: 560
- Large-impact removals (|d| ≥ 0.8): **0**
- Dependency-bypass events (AR(p) fallback): 49

## Per-Config Summary

| module_removed       |   delta_pct |   cohens_d |   ci95_lower |   ci95_upper | interpretation   |
|:---------------------|------------:|-----------:|-------------:|-------------:|:-----------------|
| NO_GEOMETRY          |       0.000 |      0.000 |      -14.200 |        9.189 | Negligible       |
| NO_KOOPMAN           |       0.000 |      0.000 |      -14.200 |        9.189 | Negligible       |
| NO_NEURAL_ODE        |       0.000 |      0.000 |      -14.200 |        9.189 | Negligible       |
| NO_PINN              |       0.000 |      0.000 |      -14.200 |        9.189 | Negligible       |
| NO_PYSR              |       0.000 |      0.000 |      -14.200 |        9.189 | Negligible       |
| NO_SINDY             |       0.000 |      0.000 |      -14.200 |        9.189 | Negligible       |
| NO_TDA               |       0.000 |      0.000 |      -14.200 |        9.189 | Negligible       |
| NO_TOPOLOGY_GEOMETRY |       0.000 |      0.000 |      -14.200 |        9.189 | Negligible       |

## Top 5 Highest-Impact Ablations (by Cohen's d)

| ablation   | system   | module   |   delta_pct |   cohens_d |   ci95_lower |   ci95_upper | impact     |
|:-----------|:---------|:---------|------------:|-----------:|-------------:|-------------:|:-----------|
| NO_TDA     | lorenz   | EV3      |       0.000 |      0.000 |       -6.454 |        6.570 | Negligible |
| NO_TDA     | lorenz   | EV3_EXT  |       0.000 |      0.000 |      -38.879 |       29.838 | Negligible |
| NO_TDA     | lorenz   | EV3_DEEP |       0.000 |      0.000 |      -13.221 |       11.623 | Negligible |
| NO_TDA     | lorenz   | EV3_SCI  |       0.000 |      0.000 |       -4.356 |        3.734 | Negligible |
| NO_TDA     | duffing  | EV3      |       0.000 |      0.000 |      -20.913 |       16.589 | Negligible |

## Methodology

- Dependency DAG: cascade disabling of downstream modules.
- Fallback: when a dependent module is missing, AR(p) AIC metric is used
  and row is marked `status=DEPENDENCY_BYPASS`.
- Δ% = (baseline_mean − ablated_mean) / |baseline_mean| × 100
- Cohen's d: pooled standard deviation formula.
- CI95: BCa bootstrap, 1000 resamples (`scipy.stats.bootstrap, method='BCa'`).
- Impact: Negligible (|d|<0.2), Small, Medium, Large (|d|≥0.8).

## Heatmap

See [`figures/ablation_heatmap.pdf`](../figures/ablation_heatmap.pdf).
