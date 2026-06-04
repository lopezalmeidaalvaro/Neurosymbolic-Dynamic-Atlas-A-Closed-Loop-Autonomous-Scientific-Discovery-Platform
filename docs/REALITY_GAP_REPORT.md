# Reality Gap Quantification Report — Phase 2D / 3A.1

Measures the divergence between simulated expectations and hardware realities ($RealityGap = Score_{sim} - Score_{hardware}$) across all scientific layers.

## Executive Summary

- **Mean Law Reality Gap**: `0.8030`
- **Mean Theory Reality Gap**: `-0.1583`
- **Mean Mechanism Reality Gap**: `0.0160`
- **Mean Prediction Reality Gap**: `0.0605`

## 1. Laws Reality Gap

| Law ID | Simulation Score | Hardware Score | Reality Gap |
| :---: | :---: | :---: | :---: |
| `LAW_001` | 1.0000 | 0.7600 | **0.2400** |
| `LAW_005` | 1.0000 | 0.7600 | **0.2400** |
| `LAW_009` | 1.0000 | 0.7600 | **0.2400** |
| `LAW_013` | 1.0000 | 0.7600 | **0.2400** |
| `LAW_017` | 1.0000 | 0.7600 | **0.2400** |
| `LAW_021` | 1.0000 | 0.7600 | **0.2400** |
| `LAW_025` | 1.0000 | 0.7600 | **0.2400** |
| `LAW_002` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_006` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_010` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_014` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_018` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_022` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_026` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_004` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_008` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_012` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_016` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_020` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_024` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_003` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_007` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_011` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_015` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_019` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_023` | 1.0000 | 0.0000 | **1.0000** |
| `LAW_027` | 1.0000 | 0.0000 | **1.0000** |

## 2. Theories Reality Gap

| Theory ID | Simulation Score | Hardware Score | Reality Gap |
| :--- | :---: | :---: | :---: |
| `THEORY_001` | 0.1270 | 0.7600 | **-0.6330** |
| `THEORY_002` | 0.0000 | 0.0000 | **0.0000** |
| `THEORY_004` | 0.0000 | 0.0000 | **0.0000** |
| `THEORY_003` | 0.0000 | 0.0000 | **0.0000** |

## 3. Mechanisms Reality Gap

| Theory ID | Causal Pathway Edge | Simulation Weight | Hardware Correlation | Reality Gap |
| :--- | :--- | :---: | :---: | :---: |
| `THEORY_001` | `gate_entropy -> structural_coherence` | 0.8000 | 0.7667 | **0.0333** |
| `THEORY_001` | `structural_coherence -> transferability` | 0.8500 | 0.8513 | **-0.0013** |

## 4. Predictions Reality Gap

| Prediction ID | Simulation Expected Effect | Hardware Mean Observed | Reality Gap |
| :---: | :---: | :---: | :---: |
| `PRED_001` | 0.3694 | 0.3089 | **0.0605** |
