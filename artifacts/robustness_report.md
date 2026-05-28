# Phase 8E — Robustness Stress Test Report

## Noise Stress Test (NRS)

NRS = −slope of normalized metric vs SNR index. Higher NRS = more robust.

| system   | module   |   val_clean |   val_20dB |   val_10dB |   val_5dB |   val_0dB |    NRS |
|:---------|:---------|------------:|-----------:|-----------:|----------:|----------:|-------:|
| lorenz   | EV3      |      4.0902 |     4.2053 |     3.5459 |    3.1079 |    2.6905 | 0.0953 |

---

## Missing Data Tolerance (MDT)

MDT = largest drop rate with <20% relative degradation.

| system   | module   |   val_0pct |   val_10pct |   val_30pct |   val_50pct |    MDT |
|:---------|:---------|-----------:|------------:|------------:|------------:|-------:|
| lorenz   | EV3      |     4.0902 |      4.0897 |      4.0875 |      4.0796 | 0.5000 |

---

## Parameter Drift (DDL)

Drift test: σ Lorenz 10→14, γ Duffing 0.3→0.5.
DDL = estimated timestep of first >2σ deviation.

| system   | module   | parameter   |   param_from |   param_to |   baseline_val |   drifted_val |      DDL |
|:---------|:---------|:------------|-------------:|-----------:|---------------:|--------------:|---------:|
| lorenz   | EV3      | sigma       |      10.0000 |    14.0000 |         4.0902 |        4.3673 | 200.0000 |
| duffing  | EV3      | gamma       |       0.3000 |     0.5000 |         1.7001 |        1.7216 | 200.0000 |

---

## OOD Generalization Gap (GG)

Train: {lorenz, duffing} → Test: {rossler, van_der_pol}.
GG = |μ_in − μ_ood| / |μ_in|.

| module   |   in_dist_mean |   ood_mean |   generalization_gap |
|:---------|---------------:|-----------:|---------------------:|
| EV3      |         2.7140 |     1.6198 |               0.4032 |

## Figures
- [`figures/robustness_degradation.pdf`](../figures/robustness_degradation.pdf)
- [`figures/robustness_ood.pdf`](../figures/robustness_ood.pdf)
