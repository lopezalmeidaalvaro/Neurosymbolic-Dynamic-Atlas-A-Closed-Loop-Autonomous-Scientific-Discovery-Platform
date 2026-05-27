# Phase 8C — SOTA Benchmark Report

## Win Rate

| Metric | Value |
|--------|-------|
| win_rate_real (vs evaluated baselines) | 55.56% |
| win_rate_total (NOT_EVALUATED = defeat) | 35.71% |
| Wins vs evaluated | 5 / 9 |
| NOT_EVALUATED losses | 5 |

## Status Summary

| Status | Count |
|--------|-------|
| OK | 14 |
| NOT_EVALUATED | 5 |
| Other | 16 |

## Baseline Summary

| baseline           |   mean_metric |   mean_time_s |   mean_acc_per_sec |   status_ok_pct |   win_rate_real |   win_rate_total |
|:-------------------|--------------:|--------------:|-------------------:|----------------:|----------------:|-----------------:|
| AI_Feynman         |      nan      |      nan      |           nan      |          0.0000 |          0.5556 |           0.3571 |
| OUR_PIPELINE_EV3   |      866.6781 |       42.9059 |             0.0233 |          1.0000 |          0.5556 |           0.3571 |
| OUR_PIPELINE_SINDy |      nan      |        0.0000 |             0.0000 |          0.0000 |          0.5556 |           0.3571 |
| OUR_PIPELINE_TOPO  |      nan      |        0.0000 |           nan      |          0.0000 |          0.5556 |           0.3571 |
| PySINDy            |      nan      |      nan      |           nan      |          0.0000 |          0.5556 |           0.3571 |
| Ripser             |      422.2000 |        0.0497 |           nan      |          1.0000 |          0.5556 |           0.3571 |
| sklearn_RF         |        0.9965 |        0.3559 |             2.8653 |          0.8000 |          0.5556 |           0.3571 |

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
