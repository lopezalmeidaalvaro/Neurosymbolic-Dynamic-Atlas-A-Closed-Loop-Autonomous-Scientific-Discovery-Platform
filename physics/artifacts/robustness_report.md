# Phase 8E — Robustness Stress Test Report

## Noise Stress Test (NRS)

NRS = −slope of normalized metric vs SNR index. Higher NRS = more robust.

| system      | module   |   val_clean |   val_20dB |   val_10dB |   val_5dB |   val_0dB |      NRS |
|:------------|:---------|------------:|-----------:|-----------:|----------:|----------:|---------:|
| lorenz      | EV3      |      2.0673 |     2.1032 |     2.2253 |    2.2580 |    2.2803 |  -0.0281 |
| lorenz      | EV3_DEEP |    345.8575 |   297.5454 |   458.0579 |  638.1625 |  956.9643 |  -0.4519 |
| lorenz      | SINDy    |    nan      |   nan      |   nan      |  nan      |  nan      | nan      |
| lorenz      | Topology |    nan      |   nan      |   nan      |  nan      |  nan      | nan      |
| lorenz      | Koopman  |    nan      |   nan      |   nan      |  nan      |  nan      | nan      |
| duffing     | EV3      |      2.1274 |    13.4522 |     5.1746 |    3.5655 |    2.5856 |   0.4217 |
| duffing     | EV3_DEEP |    316.1305 |   610.4323 |  1611.3861 | 2725.9613 | 4523.8687 |  -3.3312 |
| duffing     | SINDy    |    nan      |   nan      |   nan      |  nan      |  nan      | nan      |
| duffing     | Topology |    nan      |   nan      |   nan      |  nan      |  nan      | nan      |
| duffing     | Koopman  |    nan      |   nan      |   nan      |  nan      |  nan      | nan      |
| van_der_pol | EV3      |      1.8182 |     2.0640 |     2.1556 |    2.2204 |    2.3295 |  -0.0648 |
| van_der_pol | EV3_DEEP |    362.8379 |   213.9057 |   230.3314 |  246.6582 |  286.7793 |   0.0329 |
| van_der_pol | SINDy    |    nan      |   nan      |   nan      |  nan      |  nan      | nan      |
| van_der_pol | Topology |    nan      |   nan      |   nan      |  nan      |  nan      | nan      |
| van_der_pol | Koopman  |    nan      |   nan      |   nan      |  nan      |  nan      | nan      |
| rossler     | EV3      |      1.9902 |     2.1983 |     2.3219 |    2.3610 |    2.3995 |  -0.0493 |
| rossler     | EV3_DEEP |    363.5976 |   241.1559 |   325.9369 |  424.6046 |  591.4654 |  -0.1758 |
| rossler     | SINDy    |    nan      |   nan      |   nan      |  nan      |  nan      | nan      |
| rossler     | Topology |    nan      |   nan      |   nan      |  nan      |  nan      | nan      |
| rossler     | Koopman  |    nan      |   nan      |   nan      |  nan      |  nan      | nan      |
| logistic    | EV3      |      2.4771 |     2.6528 |     2.5715 |    2.5647 |    2.5969 |  -0.0061 |
| logistic    | EV3_DEEP |    208.6056 |   209.4599 |   224.5256 |  231.3257 |  233.8910 |  -0.0347 |
| logistic    | SINDy    |    nan      |   nan      |   nan      |  nan      |  nan      | nan      |
| logistic    | Topology |    nan      |   nan      |   nan      |  nan      |  nan      | nan      |
| logistic    | Koopman  |    nan      |   nan      |   nan      |  nan      |  nan      | nan      |

---

## Missing Data Tolerance (MDT)

MDT = largest drop rate with <20% relative degradation.

| system      | module   |   val_0pct |   val_10pct |   val_30pct |   val_50pct |    MDT |
|:------------|:---------|-----------:|------------:|------------:|------------:|-------:|
| lorenz      | EV3      |     2.0673 |      2.0674 |      2.0666 |      2.0592 | 0.5000 |
| lorenz      | EV3_DEEP |   345.8575 |    345.9263 |    345.8493 |    345.4176 | 0.5000 |
| lorenz      | SINDy    |   nan      |    nan      |    nan      |    nan      | 0.0000 |
| lorenz      | Topology |   nan      |    nan      |    nan      |    nan      | 0.0000 |
| lorenz      | Koopman  |   nan      |    nan      |    nan      |    nan      | 0.0000 |
| duffing     | EV3      |     2.1274 |      2.1274 |      2.1371 |      2.1370 | 0.5000 |
| duffing     | EV3_DEEP |   316.1305 |    316.0411 |    315.7039 |    315.4483 | 0.5000 |
| duffing     | SINDy    |   nan      |    nan      |    nan      |    nan      | 0.0000 |
| duffing     | Topology |   nan      |    nan      |    nan      |    nan      | 0.0000 |
| duffing     | Koopman  |   nan      |    nan      |    nan      |    nan      | 0.0000 |
| van_der_pol | EV3      |     1.8182 |      1.8182 |      1.8182 |      1.8183 | 0.5000 |
| van_der_pol | EV3_DEEP |   362.8379 |    362.8335 |    362.8396 |    362.8487 | 0.5000 |
| van_der_pol | SINDy    |   nan      |    nan      |    nan      |    nan      | 0.0000 |
| van_der_pol | Topology |   nan      |    nan      |    nan      |    nan      | 0.0000 |
| van_der_pol | Koopman  |   nan      |    nan      |    nan      |    nan      | 0.0000 |
| rossler     | EV3      |     1.9902 |      1.9902 |      1.9903 |      1.9903 | 0.5000 |
| rossler     | EV3_DEEP |   363.5976 |    363.5880 |    363.5886 |    363.5938 | 0.5000 |
| rossler     | SINDy    |   nan      |    nan      |    nan      |    nan      | 0.0000 |
| rossler     | Topology |   nan      |    nan      |    nan      |    nan      | 0.0000 |
| rossler     | Koopman  |   nan      |    nan      |    nan      |    nan      | 0.0000 |
| logistic    | EV3      |     2.4771 |      2.8561 |      2.5393 |      2.3288 | 0.5000 |
| logistic    | EV3_DEEP |   208.6056 |    225.3534 |    232.2333 |    207.2079 | 0.5000 |
| logistic    | SINDy    |   nan      |    nan      |    nan      |    nan      | 0.0000 |
| logistic    | Topology |   nan      |    nan      |    nan      |    nan      | 0.0000 |
| logistic    | Koopman  |   nan      |    nan      |    nan      |    nan      | 0.0000 |

---

## Parameter Drift (DDL)

Drift test: σ Lorenz 10→14, γ Duffing 0.3→0.5.
DDL = estimated timestep of first >2σ deviation.

| system   | module   | parameter   |   param_from |   param_to |   baseline_val |   drifted_val |       DDL |
|:---------|:---------|:------------|-------------:|-----------:|---------------:|--------------:|----------:|
| lorenz   | EV3      | sigma       |      10.0000 |    14.0000 |         2.0673 |        2.1264 | 2000.0000 |
| lorenz   | EV3_DEEP | sigma       |      10.0000 |    14.0000 |       345.8575 |      355.3286 | 2000.0000 |
| lorenz   | SINDy    | sigma       |      10.0000 |    14.0000 |       nan      |      nan      |  nan      |
| lorenz   | Topology | sigma       |      10.0000 |    14.0000 |       nan      |      nan      |  nan      |
| lorenz   | Koopman  | sigma       |      10.0000 |    14.0000 |       nan      |      nan      |  nan      |
| duffing  | EV3      | gamma       |       0.3000 |     0.5000 |         2.1274 |        1.9120 |  600.0000 |
| duffing  | EV3_DEEP | gamma       |       0.3000 |     0.5000 |       316.1305 |      293.0538 | 2000.0000 |
| duffing  | SINDy    | gamma       |       0.3000 |     0.5000 |       nan      |      nan      |  nan      |
| duffing  | Topology | gamma       |       0.3000 |     0.5000 |       nan      |      nan      |  nan      |
| duffing  | Koopman  | gamma       |       0.3000 |     0.5000 |       nan      |      nan      |  nan      |

---

## OOD Generalization Gap (GG)

Train: {lorenz, duffing} → Test: {rossler, van_der_pol}.
GG = |μ_in − μ_ood| / |μ_in|.

| module   |   in_dist_mean |   ood_mean |   generalization_gap |
|:---------|---------------:|-----------:|---------------------:|
| EV3      |         2.1234 |     1.9439 |               0.0846 |
| EV3_DEEP |       334.4163 |   363.7179 |               0.0876 |
| SINDy    |       nan      |   nan      |             nan      |
| Topology |       nan      |   nan      |             nan      |
| Koopman  |       nan      |   nan      |             nan      |

## Figures
- [`figures/robustness_degradation.pdf`](../figures/robustness_degradation.pdf)
- [`figures/robustness_ood.pdf`](../figures/robustness_ood.pdf)
