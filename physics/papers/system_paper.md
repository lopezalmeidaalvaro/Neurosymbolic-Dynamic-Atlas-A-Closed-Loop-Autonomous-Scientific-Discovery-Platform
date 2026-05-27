# Neuro-Symbolic Dynamic Atlas: Comprehensive Evaluation Report

**Date:** May 27, 2026
**Version:** Phase 8 — Automated Evaluation Report

> **Disclaimer**: All results are model-specific observations derived from numerical simulations
> of chaotic dynamical systems (Lorenz, Duffing, Van der Pol, Rössler, Logistic Map).
> No claims are made about real physical systems, universal laws, or out-of-domain performance.

---

## Abstract

We present a systematic evaluation of the Neuro-Symbolic Dynamic Atlas pipeline across
63 module-system combinations (Phase 8A).
Reproducibility analysis using Sobol quasi-random seeds and BCa bootstrap confidence intervals
shows 28.6% of evaluations converge within relative CI
width < 5%, with 23.8% classified as stable
(CV < 0.05, median CV = 0.0373).
Ablation analysis (Phase 8B) identifies 0 large-impact
module removals (|d| ≥ 0.8), with the highest impact from `NO_TDA`
(d = 0.0000).
Noise robustness (Phase 8E): mean NRS = -0.3687
(best module: EV3).
Mean OOD generalization gap: 0.0861.

---

## 1. Introduction

Scientific machine learning pipelines require rigorous validation beyond held-out accuracy.
This report evaluates the Neuro-Symbolic Dynamic Atlas along four orthogonal axes:
(1) statistical reproducibility across randomized initializations,
(2) modular ablation sensitivity with DAG-aware dependency resolution,
(3) comparison against SOTA reference implementations,
and (4) robustness under measurement degradation and distribution shift.

---

## 2. Reproducibility Audit (Phase 8A)

### 2.1 Methodology

Seeds are generated via Sobol quasi-random sequence mapped to integers as
$S = \lfloor p \times (2^{31} - 1) \rfloor$.
Confidence intervals use BCa bootstrap (`scipy.stats.bootstrap`, method='BCa',
n_resamples=2000).
Sequential adaptive stopping: $W_{\text{rel}} = (CI_{hi} - CI_{lo}) / |\mu| < 0.05$
(max 50 seeds per combination).
Stability: CV = $\sigma/\mu < 0.05$ AND converged.

### 2.2 Results

| Metric | Value |
|--------|-------|
| Total evaluations | 63 |
| Converged (W_rel < 0.05) | 28.6% |
| Stable (CV < 0.05) | 23.8% |
| Median CV | 0.0373 |
| Peak RAM | 5.6 MB |
| Peak VRAM | 2.3 MB |

**Sample results** (first 20 rows):

| module   | system      |   n_seeds |     mean |   ci_lower |   ci_upper |   rel_width |     cv | converged   | stable   |
|:---------|:------------|----------:|---------:|-----------:|-----------:|------------:|-------:|:------------|:---------|
| EV3      | lorenz      |         4 |   3.1503 |   nan      |   nan      |    inf      | 0.3594 | False       | False    |
| EV3      | duffing     |        50 |   2.0722 |     1.9299 |     2.3211 |      0.1888 | 0.3140 | False       | False    |
| EV3      | van_der_pol |        20 |   1.8409 |     1.8266 |     1.8623 |      0.0194 | 0.0226 | True        | True     |
| EV3      | rossler     |        40 |   2.0769 |     2.0315 |     2.1263 |      0.0456 | 0.0755 | True        | False    |
| EV3      | logistic    |        20 |   2.5362 |     2.5111 |     2.5632 |      0.0205 | 0.0236 | True        | True     |
| EV3      | ECG200      |        20 |   1.5378 |     1.5105 |     1.5602 |      0.0323 | 0.0373 | True        | True     |
| EV3      | ECG5000     |        20 |   1.5378 |     1.5128 |     1.5604 |      0.0310 | 0.0373 | True        | True     |
| EV3_EXT  | lorenz      |        50 | 232.2864 |   218.4023 |   241.8597 |      0.1010 | 0.1749 | False       | False    |
| EV3_EXT  | duffing     |        50 | 285.0265 |   273.4848 |   291.6460 |      0.0637 | 0.1079 | False       | False    |
| EV3_EXT  | van_der_pol |        20 | 299.0672 |   299.0571 |   299.0771 |      0.0001 | 0.0001 | True        | True     |
| EV3_EXT  | rossler     |        20 | 299.5440 |   299.5068 |   299.5629 |      0.0002 | 0.0002 | True        | True     |
| EV3_EXT  | logistic    |        20 |  51.2886 |    50.6892 |    51.9941 |      0.0254 | 0.0298 | True        | True     |
| EV3_EXT  | ECG200      |        50 |  10.4700 |    10.2371 |    10.7629 |      0.0502 | 0.0903 | False       | False    |
| EV3_EXT  | ECG5000     |        50 |  10.4700 |    10.2492 |    10.7540 |      0.0482 | 0.0903 | True        | False    |
| EV3_DEEP | lorenz      |        30 | 330.9726 |   321.5268 |   338.0160 |      0.0498 | 0.0711 | True        | False    |
| EV3_DEEP | duffing     |        50 | 333.1167 |   318.0827 |   343.9607 |      0.0777 | 0.1392 | False       | False    |
| EV3_DEEP | van_der_pol |        20 | 363.3822 |   362.9118 |   363.8399 |      0.0026 | 0.0031 | True        | True     |
| EV3_DEEP | rossler     |        20 | 364.9516 |   364.3368 |   365.6345 |      0.0036 | 0.0041 | True        | True     |
| EV3_DEEP | logistic    |        50 | 229.0171 |   217.7459 |   256.0952 |      0.1675 | 0.2625 | False       | False    |
| EV3_DEEP | ECG200      |        20 | 104.9322 |   103.9435 |   105.8734 |      0.0184 | 0.0215 | True        | True     |

---

## 3. Ablation Study (Phase 8B)

### 3.1 Methodology

Nine ablation configurations systematically disable pipeline components.
A DAG-aware resolver cascades disabling to all downstream dependents.
When a dependency is missing, an AR(p) fallback metric is used
(`status=DEPENDENCY_BYPASS`).

For each (config, system, module):
- $\Delta\% = (\mu_{\text{base}} - \mu_{\text{abl}}) / |\mu_{\text{base}}| \times 100$
- Cohen's $d = (\mu_{\text{base}} - \mu_{\text{abl}}) / \sigma_{\text{pooled}}$
- BCa CI₉₅ of $\Delta\%$ (1000 resamples)

Impact: Negligible ($|d| < 0.2$), Small, Medium, Large ($|d| \geq 0.8$).

### 3.2 Results

**Large-impact removals: 0**
(Dependency bypass events: 49)

| ablation   | system      | module   |   delta_pct |   cohens_d |   ci95_lower |   ci95_upper | impact     | status   |
|:-----------|:------------|:---------|------------:|-----------:|-------------:|-------------:|:-----------|:---------|
| NO_TDA     | lorenz      | EV3      |       0.000 |      0.000 |       -6.454 |        6.570 | Negligible | OK       |
| NO_TDA     | lorenz      | EV3_EXT  |       0.000 |      0.000 |      -38.879 |       29.838 | Negligible | OK       |
| NO_TDA     | lorenz      | EV3_DEEP |       0.000 |      0.000 |      -13.221 |       11.623 | Negligible | OK       |
| NO_TDA     | lorenz      | EV3_SCI  |       0.000 |      0.000 |       -4.356 |        3.734 | Negligible | OK       |
| NO_TDA     | duffing     | EV3      |       0.000 |      0.000 |      -20.913 |       16.589 | Negligible | OK       |
| NO_TDA     | duffing     | EV3_EXT  |       0.000 |      0.000 |       -4.329 |        4.149 | Negligible | OK       |
| NO_TDA     | duffing     | EV3_DEEP |       0.000 |      0.000 |       -9.680 |        8.920 | Negligible | OK       |
| NO_TDA     | duffing     | EV3_SCI  |       0.000 |      0.000 |     -168.650 |       71.651 | Negligible | OK       |
| NO_TDA     | van_der_pol | EV3      |       0.000 |      0.000 |       -1.902 |        1.632 | Negligible | OK       |
| NO_TDA     | van_der_pol | EV3_EXT  |       0.000 |      0.000 |       -0.008 |        0.008 | Negligible | OK       |
| NO_TDA     | van_der_pol | EV3_DEEP |       0.000 |      0.000 |       -0.257 |        0.274 | Negligible | OK       |
| NO_TDA     | van_der_pol | EV3_SCI  |       0.000 |      0.000 |       -0.145 |        0.155 | Negligible | OK       |
| NO_TDA     | rossler     | EV3      |       0.000 |      0.000 |       -6.313 |        6.275 | Negligible | OK       |
| NO_TDA     | rossler     | EV3_EXT  |       0.000 |      0.000 |       -0.007 |        0.007 | Negligible | OK       |
| NO_TDA     | rossler     | EV3_DEEP |       0.000 |      0.000 |       -0.394 |        0.341 | Negligible | OK       |

See `figures/ablation_heatmap.pdf` for the systems × modules impact matrix.

---

## 4. SOTA Benchmark (Phase 8C)

### 4.1 Methodology

pip install attempted for each missing SOTA package.
If install fails: `status='NOT_EVALUATED'` — **no mock results generated**.
`win_rate_real` = wins vs evaluated baselines only.
`win_rate_total` = wins vs all baselines (NOT_EVALUATED = defeat).

### 4.2 Results

| Metric | Value |
|--------|-------|
| Evaluated baselines (OK) | 14 |
| Not evaluated | 5 |
| Win rate (real) | 0.56 |
| Win rate (total) | 0.36 |

| baseline           | metric       |   mean_value |   mean_time |
|:-------------------|:-------------|-------------:|------------:|
| OUR_PIPELINE_EV3   | feature_norm |     866.6781 |     42.9059 |
| OUR_PIPELINE_SINDy | r2           |     nan      |      0.0000 |
| OUR_PIPELINE_TOPO  | h0_count     |     nan      |      0.0000 |
| PySINDy            | r2           |     nan      |    nan      |
| Ripser             | h0_count     |     422.2000 |      0.0497 |
| sklearn_RF         | accuracy     |       0.9965 |      0.3559 |

See `figures/sota_radar.pdf` and `figures/sota_cost_performance.pdf`.

---

## 5. Robustness Stress Test (Phase 8E)

### 5.1 Noise Robustness

Gaussian white noise at SNR ∈ {∞, 20, 10, 5, 0} dB.
NRS = negative linear slope of normalized metric vs SNR index.
- **Mean NRS**: -0.3687
- **Best module**: EV3

### 5.2 Missing Data Tolerance

Random dropout at [0%, 10%, 30%, 50%] with linear interpolation.
MDT = max drop rate at < 20% relative degradation.
- **Mean MDT**: 20.0%

### 5.3 Parameter Drift

Physical parameters modulated: σ: 10→14 (Lorenz), γ: 0.3→0.5 (Duffing).
DDL = estimated timestep of first >2σ deviation.

### 5.4 OOD Generalization

Train: {Lorenz, Duffing} → Test: {Rössler, Van der Pol}.
GG = |μ_in − μ_OOD| / |μ_in|.
- **Mean OOD Gap**: 0.0861

---

## 6. Computational Cost

Measured from Phase 8A reproducibility runs (mean across seeds and systems).
Missing values (N/A) indicate profiling was not enabled or module errored.

| module    | Mean Time (s)   | Peak RAM (MB)   | Peak VRAM (MB)   |
|:----------|:----------------|:----------------|:-----------------|
| EV3       | N/A             | N/A             | N/A              |
| EV3_DEEP  | N/A             | N/A             | N/A              |
| EV3_EXT   | N/A             | N/A             | N/A              |
| EV3_SCI   | 34.01           | 3.78            | 2.08             |
| Koopman   | 0.27            | 0.00            | 0.00             |
| NeuralODE | 0.01            | 0.01            | 0.00             |
| PINN      | 0.01            | 0.01            | 0.00             |
| SINDy     | 0.29            | 0.01            | 0.00             |
| Topology  | 0.27            | 0.00            | 0.00             |

> [!NOTE]
> CPU timing measured via `time.perf_counter()`.
> RAM via `tracemalloc`. VRAM via `torch.cuda.max_memory_allocated()` (GPU only).

---

## 7. Threats to Validity

### 7.1 Statistical Reproducibility

The following metrics are reported as N/A due to missing data: benchmark_ok_count, redundancy_n_redundant. 
BCa bootstrap CI validity requires n_resamples ≥ n_data and non-degenerate distributions.
Short dry-run signals (200 steps) may produce wider CIs than production runs.

### 7.2 Synthetic Dataset Bias

All dynamical systems are numerically integrated (RK4 solver).
Real-world sensor data involves non-Gaussian noise, missing channels, multi-scale coupling,
and hardware quantization effects not present in these benchmarks.
Results are **not** expected to generalize directly to empirical time series without re-validation.

### 7.3 Hardware Dependence

Execution times depend heavily on CPU model, GPU presence, RAM bandwidth,
and background process load. Comparisons across different hardware configurations
are not valid without normalization. VRAM measurements assume NVIDIA CUDA ≥ 11.0.

### 7.4 Hyperparameter Sensitivity

SINDy threshold (0.1), PINN architecture depth (default), NeuralODE step-size,
and EV3 embedding dimensionality have **not** been exhaustively tuned per system.
Performance may improve substantially with system-specific hyperparameter search.

### 7.5 Domain Transfer Limitations

The pipeline processes 1-D signal proxies (x-component) of inherently 3-D chaotic attractors.
Full phase-space reconstruction is not attempted. Performance on multi-dimensional,
multi-modal, or non-stationary empirical data may differ significantly from reported values.

### 7.6 Simulator-Reality Gap

All benchmark results derive from numerical integration of idealized ODEs.
The gap between these simulations and experimental measurements constitutes
a fundamental external validity threat. All conclusions in this report are
**model-specific observations** and should not be interpreted as physical laws
or universal properties of the corresponding dynamical phenomena.

---

## 8. Conclusions

This evaluation establishes baseline reproducibility, ablation sensitivity, robustness profiles,
and comparative positioning for the Neuro-Symbolic Dynamic Atlas pipeline.
All reported values are model-specific observations on numerical simulations.
**No claims are made about universal physical laws or real-world systems.**

---

## References

See `papers/references.bib`.

- Chen et al. (2018) — Neural ODEs
- Brunton et al. (2016) — SINDy
- Edelsbrunner & Harer (2008) — Persistent Homology
- Raissi et al. (2019) — PINNs
- Cohen (1988) — Effect sizes
- Efron & Tibshirani (1994) — Bootstrap
- Joe & Kuo (2003) — Sobol sequences
