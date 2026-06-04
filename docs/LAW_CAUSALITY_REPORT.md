# Law Causality Report (Component Q)
 
Detailed validation of causal relationships including feature ablation delta metrics and counterfactual probability drops.
 
## Causal Validation Metrics
 
| ID | Rule | Base F1 | Delta AUC | Counterfactual Effect | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `LAW_001` | `IF (gate_entropy < 0.25) THEN transferability increases` | 1.0000 | 0.5000 | 1.0000 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_002` | `IF (betweenness_centrality <= 0.25) AND (gate_entropy < 0.25) THEN transferability increases` | 0.7589 | 0.3057 | 0.8731 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_003` | `IF (clifford_ratio <= 0.7) AND (gate_entropy < 0.25) THEN transferability increases` | 0.8298 | 0.3546 | 0.9018 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_004` | `IF (gate_entropy < 0.25) AND (noise_resilience_low) THEN transferability increases` | 1.0000 | 0.5000 | 1.0000 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_005` | `IF (gate_entropy < 0.25) AND (novelty_low) THEN transferability increases` | 1.0000 | 0.5000 | 1.0000 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_006` | `IF (gate_entropy < 0.25) AND (stabilizer_overlap > 0.6) THEN transferability increases` | 0.5770 | 0.2027 | 0.8180 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_007` | `IF (gate_entropy < 0.25) AND (synergy_low) THEN transferability increases` | 1.0000 | 0.5000 | 1.0000 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_008` | `IF (gate_entropy < 0.25) AND (tensor_rank >= 3) THEN transferability increases` | 0.9539 | 0.4560 | 0.9681 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_009` | `IF (gate_entropy < 0.25) AND (stabilizer_overlap <= 0.6) THEN transferability increases` | 0.7457 | 0.2973 | 0.8683 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_010` | `IF (clifford_ratio > 0.7) AND (gate_entropy < 0.25) THEN transferability increases` | 0.4506 | 0.1454 | 0.7903 | `CANDIDATE_LAW` |
| `LAW_011` | `IF (betweenness_centrality > 0.25) AND (gate_entropy < 0.25) THEN transferability increases` | 0.5596 | 0.1943 | 0.8138 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_012` | `IF (clifford_ratio > 0.7) THEN noise_resilience increases` | 0.9998 | 0.4998 | 0.9999 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_013` | `IF (betweenness_centrality <= 0.25) AND (clifford_ratio > 0.7) THEN noise_resilience increases` | 0.7677 | 0.3114 | 0.8583 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_014` | `IF (clifford_ratio > 0.7) AND (gate_entropy < 0.25) THEN noise_resilience increases` | 0.4128 | 0.1300 | 0.7553 | `CANDIDATE_LAW` |
| `LAW_015` | `IF (clifford_ratio > 0.7) AND (novelty_low) THEN noise_resilience increases` | 0.9998 | 0.4998 | 0.9999 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_016` | `IF (clifford_ratio > 0.7) AND (stabilizer_overlap > 0.6) THEN noise_resilience increases` | 0.5841 | 0.2062 | 0.7954 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_017` | `IF (clifford_ratio > 0.7) AND (synergy_low) THEN noise_resilience increases` | 0.9998 | 0.4998 | 0.9999 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_018` | `IF (clifford_ratio > 0.7) AND (tensor_rank >= 3) THEN noise_resilience increases` | 0.9500 | 0.4523 | 0.9600 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_019` | `IF (clifford_ratio > 0.7) AND (gate_entropy >= 0.25) THEN noise_resilience increases` | 0.8503 | 0.3697 | 0.8977 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_020` | `IF (clifford_ratio > 0.7) AND (stabilizer_overlap <= 0.6) THEN noise_resilience increases` | 0.7399 | 0.2935 | 0.8469 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_021` | `IF (clifford_ratio > 0.7) AND (transferability_low) THEN noise_resilience increases` | 0.9998 | 0.4998 | 0.9999 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_022` | `IF (betweenness_centrality > 0.25) AND (clifford_ratio > 0.7) THEN noise_resilience increases` | 0.5472 | 0.1883 | 0.7856 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_023` | `IF (betweenness_centrality > 0.25) THEN novelty increases` | 0.9999 | 0.4998 | 0.9998 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_024` | `IF (betweenness_centrality > 0.25) AND (clifford_ratio <= 0.7) THEN novelty increases` | 0.8267 | 0.3522 | 0.8419 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_025` | `IF (betweenness_centrality > 0.25) AND (gate_entropy >= 0.25) THEN novelty increases` | 0.8422 | 0.3637 | 0.8524 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_026` | `IF (betweenness_centrality > 0.25) AND (noise_resilience_low) THEN novelty increases` | 0.9999 | 0.4998 | 0.9998 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_027` | `IF (betweenness_centrality > 0.25) AND (stabilizer_overlap <= 0.6) THEN novelty increases` | 0.7513 | 0.3007 | 0.7980 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_028` | `IF (betweenness_centrality > 0.25) AND (synergy_low) THEN novelty increases` | 0.9999 | 0.4998 | 0.9998 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_029` | `IF (betweenness_centrality > 0.25) AND (tensor_rank >= 3) THEN novelty increases` | 0.9477 | 0.4503 | 0.9406 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_030` | `IF (betweenness_centrality > 0.25) AND (transferability_low) THEN novelty increases` | 0.9999 | 0.4998 | 0.9998 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_031` | `IF (betweenness_centrality > 0.25) AND (stabilizer_overlap > 0.6) THEN novelty increases` | 0.5695 | 0.1990 | 0.7233 | `CAUSALLY_VALIDATED_LAW` |
| `LAW_032` | `IF (betweenness_centrality > 0.25) AND (clifford_ratio > 0.7) THEN novelty increases` | 0.4558 | 0.1475 | 0.6906 | `CANDIDATE_LAW` |
| `LAW_033` | `IF (betweenness_centrality > 0.25) AND (gate_entropy < 0.25) THEN novelty increases` | 0.4280 | 0.1361 | 0.6837 | `CANDIDATE_LAW` |
