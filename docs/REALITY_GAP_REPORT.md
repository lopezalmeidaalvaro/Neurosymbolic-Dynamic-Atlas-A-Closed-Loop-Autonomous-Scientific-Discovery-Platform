# Reality Gap Quantification Report — Phase 2D / 3A.1

Measures the divergence between simulated expectations and hardware realities ($RealityGap = Score_{sim} - Score_{hardware}$) across all scientific layers.

## Executive Summary

- **Mean Law Reality Gap**: `0.7988`
- **Mean Theory Reality Gap**: `-0.1809`
- **Mean Mechanism Reality Gap**: `0.0157`
- **Mean Prediction Reality Gap**: `0.0411`

## 1. Laws Reality Gap

| Law ID | Simulation Score | Hardware Score | Reality Gap |
| :---: | :---: | :---: | :---: |
| `LAW_001` | 1.0000 | 0.2965 | **0.7035** |
| `LAW_005` | 1.0000 | 0.2965 | **0.7035** |
| `LAW_009` | 1.0000 | 0.2965 | **0.7035** |
| `LAW_013` | 1.0000 | 0.2965 | **0.7035** |
| `LAW_017` | 1.0000 | 0.2965 | **0.7035** |
| `LAW_021` | 1.0000 | 0.2965 | **0.7035** |
| `LAW_025` | 1.0000 | 0.2965 | **0.7035** |
| `LAW_002` | 1.0000 | 0.2750 | **0.7250** |
| `LAW_006` | 1.0000 | 0.2750 | **0.7250** |
| `LAW_010` | 1.0000 | 0.2750 | **0.7250** |
| `LAW_014` | 1.0000 | 0.2750 | **0.7250** |
| `LAW_018` | 1.0000 | 0.2750 | **0.7250** |
| `LAW_022` | 1.0000 | 0.2750 | **0.7250** |
| `LAW_026` | 1.0000 | 0.2750 | **0.7250** |
| `LAW_004` | 1.0000 | 0.2190 | **0.7810** |
| `LAW_008` | 1.0000 | 0.2190 | **0.7810** |
| `LAW_012` | 1.0000 | 0.2190 | **0.7810** |
| `LAW_016` | 1.0000 | 0.2190 | **0.7810** |
| `LAW_020` | 1.0000 | 0.2190 | **0.7810** |
| `LAW_024` | 1.0000 | 0.2190 | **0.7810** |
| `LAW_003` | 1.0000 | 0.0170 | **0.9830** |
| `LAW_007` | 1.0000 | 0.0170 | **0.9830** |
| `LAW_011` | 1.0000 | 0.0170 | **0.9830** |
| `LAW_015` | 1.0000 | 0.0170 | **0.9830** |
| `LAW_019` | 1.0000 | 0.0170 | **0.9830** |
| `LAW_023` | 1.0000 | 0.0170 | **0.9830** |
| `LAW_027` | 1.0000 | 0.0170 | **0.9830** |

## 2. Theories Reality Gap

| Theory ID | Simulation Score | Hardware Score | Reality Gap |
| :--- | :---: | :---: | :---: |
| `THEORY_001` | 0.0409 | 0.2965 | **-0.2556** |
| `THEORY_002` | 0.0311 | 0.2750 | **-0.2439** |
| `THEORY_004` | 0.0120 | 0.2190 | **-0.2070** |
| `THEORY_003` | 0.0000 | 0.0170 | **-0.0170** |

## 3. Mechanisms Reality Gap

| Theory ID | Causal Pathway Edge | Simulation Weight | Hardware Correlation | Reality Gap |
| :--- | :--- | :---: | :---: | :---: |
| `THEORY_003` | `clifford_ratio -> stabilizer_compatibility` | 0.7978 | 0.7958 | **0.0020** |
| `THEORY_003` | `stabilizer_compatibility -> error_mitigation` | 1.0000 | 0.9920 | **0.0080** |
| `THEORY_003` | `error_mitigation -> noise_resilience` | 0.8063 | 0.8025 | **0.0038** |
| `THEORY_001` | `gate_entropy -> structural_coherence` | 0.7698 | 0.7667 | **0.0031** |
| `THEORY_001` | `structural_coherence -> domain_similarity` | 1.0000 | 0.9910 | **0.0090** |
| `THEORY_001` | `domain_similarity -> transferability` | 0.8532 | 0.8467 | **0.0065** |
| `THEORY_004` | `betweenness_centrality -> reuse_bottleneck` | 0.8402 | 0.8369 | **0.0033** |
| `THEORY_004` | `reuse_bottleneck -> module_recombination` | 1.0000 | 0.9857 | **0.0143** |
| `THEORY_004` | `module_recombination -> novelty` | 0.8992 | 0.8911 | **0.0081** |
| `THEORY_002` | `stabilizer_overlap -> algebraic_symmetry` | 0.8596 | 0.8495 | **0.0101** |
| `THEORY_002` | `algebraic_symmetry -> state_preservation` | 0.2681 | 0.2376 | **0.0305** |
| `THEORY_002` | `tensor_rank -> computation_complexity` | 0.4722 | 0.4729 | **-0.0007** |
| `THEORY_002` | `computation_complexity -> state_preservation` | 0.3461 | 0.3879 | **-0.0418** |
| `THEORY_002` | `state_preservation -> synergy` | 0.9816 | 0.8177 | **0.1639** |

## 4. Predictions Reality Gap

| Prediction ID | Simulation Expected Effect | Hardware Mean Observed | Reality Gap |
| :---: | :---: | :---: | :---: |
| `PRED_001` | 0.3694 | 0.3283 | **0.0411** |
| `PRED_004` | 0.0756 | 0.0345 | **0.0411** |
| `PRED_005` | 0.0813 | 0.0402 | **0.0411** |
| `PRED_009` | 0.0651 | 0.0240 | **0.0411** |
| `PRED_010` | 0.0968 | 0.0557 | **0.0411** |
| `PRED_011` | 0.1129 | 0.0718 | **0.0411** |
| `PRED_003` | 0.1233 | 0.0822 | **0.0411** |
| `PRED_007` | 0.1276 | 0.0865 | **0.0411** |
| `PRED_008` | 0.0755 | 0.0344 | **0.0411** |
| `PRED_002` | 0.0746 | 0.0335 | **0.0411** |
