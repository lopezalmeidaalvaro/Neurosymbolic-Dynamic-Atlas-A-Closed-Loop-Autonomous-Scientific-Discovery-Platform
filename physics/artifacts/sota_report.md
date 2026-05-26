# Phase 8C — SOTA Benchmark Report

## Win Rate

| Metric | Value |
|--------|-------|
| win_rate_real (vs evaluated baselines) | 100.00% |
| win_rate_total (NOT_EVALUATED = defeat) | 66.67% |
| Wins vs evaluated | 2 / 2 |
| NOT_EVALUATED losses | 1 |

## Status Summary

| Status | Count |
|--------|-------|
| OK | 3 |
| NOT_EVALUATED | 1 |
| Other | 3 |

## Baseline Summary

| baseline           |   mean_metric |   mean_time_s |   mean_acc_per_sec |   status_ok_pct |   win_rate_real |   win_rate_total |
|:-------------------|--------------:|--------------:|-------------------:|----------------:|----------------:|-----------------:|
| AI_Feynman         |      nan      |      nan      |           nan      |          0.0000 |          1.0000 |           0.6667 |
| OUR_PIPELINE_EV3   |      523.7899 |       73.1908 |             0.0137 |          1.0000 |          1.0000 |           0.6667 |
| OUR_PIPELINE_SINDy |      nan      |        0.0018 |             0.0000 |          0.0000 |          1.0000 |           0.6667 |
| OUR_PIPELINE_TOPO  |      nan      |        0.0000 |           nan      |          0.0000 |          1.0000 |           0.6667 |
| PySINDy            |      nan      |      nan      |           nan      |          0.0000 |          1.0000 |           0.6667 |
| Ripser             |      297.0000 |        0.0228 |           nan      |          1.0000 |          1.0000 |           0.6667 |
| sklearn_RF         |        0.9931 |        0.1447 |             6.8629 |          1.0000 |          1.0000 |           0.6667 |

## NOT_EVALUATED Reasons (no mocks used)

| baseline   | reason                  |
|:-----------|:------------------------|
| AI_Feynman | aifeynman not installed |

## Methodology

- pip install attempted for each missing package before evaluation.
- If a tool fails to install: `status='NOT_EVALUATED'` — **no mock data is generated**.
- Cost-performance: `accuracy_per_second = accuracy / time_s`.
- `win_rate_real` counts wins only against successfully-evaluated baselines.
- `win_rate_total` treats NOT_EVALUATED entries as defeats (conservative).

## Figures

- [`figures/sota_cost_performance.pdf`](../figures/sota_cost_performance.pdf)
- [`figures/sota_radar.pdf`](../figures/sota_radar.pdf)
