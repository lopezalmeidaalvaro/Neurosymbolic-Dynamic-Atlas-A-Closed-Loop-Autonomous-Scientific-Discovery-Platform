# Law Tournament Report (Component Q)
 
Scientific leaderboard ranking discovered rules and baseline laws based on precision, coverage, generalization, causality, and robustness.
 
## Tournament Leaderboard
 
| Rank | ID | Rule | Type | Tournament Score | Robustness |
| :---: | :--- | :--- | :---: | :---: | :---: |
| 1 | `LAW_012` | `IF (clifford_ratio > 0.7) THEN noise_resilience increases` | `DISCOVERED` | **0.9671** | 0.8359 |
| 2 | `LAW_021` | `IF (clifford_ratio > 0.7) AND (transferability_low) THEN noise_resilience increases` | `DISCOVERED` | **0.9670** | 0.8356 |
| 3 | `LAW_015` | `IF (clifford_ratio > 0.7) AND (novelty_low) THEN noise_resilience increases` | `DISCOVERED` | **0.9669** | 0.8351 |
| 4 | `LAW_001` | `IF (gate_entropy < 0.25) THEN transferability increases` | `DISCOVERED` | **0.9638** | 0.8191 |
| 5 | `LAW_023` | `IF (betweenness_centrality > 0.25) THEN novelty increases` | `DISCOVERED` | **0.9504** | 0.7527 |
| 6 | `LAW_030` | `IF (betweenness_centrality > 0.25) AND (transferability_low) THEN novelty increases` | `DISCOVERED` | **0.9500** | 0.7507 |
| 7 | `LAW_008` | `IF (gate_entropy < 0.25) AND (tensor_rank >= 3) THEN transferability increases` | `DISCOVERED` | **0.9363** | 0.8202 |
| 8 | `LAW_018` | `IF (clifford_ratio > 0.7) AND (tensor_rank >= 3) THEN noise_resilience increases` | `DISCOVERED` | **0.9349** | 0.8324 |
| 9 | `LAW_029` | `IF (betweenness_centrality > 0.25) AND (tensor_rank >= 3) THEN novelty increases` | `DISCOVERED` | **0.9121** | 0.7517 |
| 10 | `LAW_019` | `IF (clifford_ratio > 0.7) AND (gate_entropy >= 0.25) THEN noise_resilience increases` | `DISCOVERED` | **0.8794** | 0.8343 |
| 11 | `LAW_003` | `IF (clifford_ratio <= 0.7) AND (gate_entropy < 0.25) THEN transferability increases` | `DISCOVERED` | **0.8691** | 0.8143 |
| 12 | `LAW_025` | `IF (betweenness_centrality > 0.25) AND (gate_entropy >= 0.25) THEN novelty increases` | `DISCOVERED` | **0.8464** | 0.7500 |
| 13 | `LAW_024` | `IF (betweenness_centrality > 0.25) AND (clifford_ratio <= 0.7) THEN novelty increases` | `DISCOVERED` | **0.8381** | 0.7516 |
| 14 | `LAW_013` | `IF (betweenness_centrality <= 0.25) AND (clifford_ratio > 0.7) THEN noise_resilience increases` | `DISCOVERED` | **0.8376** | 0.8309 |
| 15 | `LAW_002` | `IF (betweenness_centrality <= 0.25) AND (gate_entropy < 0.25) THEN transferability increases` | `DISCOVERED` | **0.8361** | 0.8178 |
| 16 | `LAW_009` | `IF (gate_entropy < 0.25) AND (stabilizer_overlap <= 0.6) THEN transferability increases` | `DISCOVERED` | **0.8309** | 0.8218 |
| 17 | `LAW_020` | `IF (clifford_ratio > 0.7) AND (stabilizer_overlap <= 0.6) THEN noise_resilience increases` | `DISCOVERED` | **0.8251** | 0.8333 |
| 18 | `LAW_027` | `IF (betweenness_centrality > 0.25) AND (stabilizer_overlap <= 0.6) THEN novelty increases` | `DISCOVERED` | **0.7985** | 0.7501 |
| 19 | `LAW_005` | `IF (gate_entropy < 0.25) AND (novelty_low) THEN transferability increases` | `DISCOVERED` | **0.7710** | 0.4652 |
| 20 | `LAW_006` | `IF (gate_entropy < 0.25) AND (stabilizer_overlap > 0.6) THEN transferability increases` | `DISCOVERED` | **0.7584** | 0.8211 |
| 21 | `LAW_016` | `IF (clifford_ratio > 0.7) AND (stabilizer_overlap > 0.6) THEN noise_resilience increases` | `DISCOVERED` | **0.7576** | 0.8356 |
| 22 | `LAW_011` | `IF (betweenness_centrality > 0.25) AND (gate_entropy < 0.25) THEN transferability increases` | `DISCOVERED` | **0.7514** | 0.8215 |
| 23 | `LAW_004` | `IF (gate_entropy < 0.25) AND (noise_resilience_low) THEN transferability increases` | `DISCOVERED` | **0.7477** | 0.4341 |
| 24 | `LAW_026` | `IF (betweenness_centrality > 0.25) AND (noise_resilience_low) THEN novelty increases` | `DISCOVERED` | **0.7444** | 0.4295 |
| 25 | `LAW_022` | `IF (betweenness_centrality > 0.25) AND (clifford_ratio > 0.7) THEN noise_resilience increases` | `DISCOVERED` | **0.7425** | 0.8356 |
| 26 | `LAW_031` | `IF (betweenness_centrality > 0.25) AND (stabilizer_overlap > 0.6) THEN novelty increases` | `DISCOVERED` | **0.7143** | 0.7421 |
| 27 | `LAW_010` | `IF (clifford_ratio > 0.7) AND (gate_entropy < 0.25) THEN transferability increases` | `DISCOVERED` | **0.7071** | 0.8153 |
| 28 | `LAW_014` | `IF (clifford_ratio > 0.7) AND (gate_entropy < 0.25) THEN noise_resilience increases` | `DISCOVERED` | **0.6890** | 0.8335 |
| 29 | `LAW_028` | `IF (betweenness_centrality > 0.25) AND (synergy_low) THEN novelty increases` | `DISCOVERED` | **0.6803** | 0.3504 |
| 30 | `LAW_007` | `IF (gate_entropy < 0.25) AND (synergy_low) THEN transferability increases` | `DISCOVERED` | **0.6766** | 0.3455 |
| 31 | `LAW_017` | `IF (clifford_ratio > 0.7) AND (synergy_low) THEN noise_resilience increases` | `DISCOVERED` | **0.6752** | 0.3436 |
| 32 | `LAW_032` | `IF (betweenness_centrality > 0.25) AND (clifford_ratio > 0.7) THEN novelty increases` | `DISCOVERED` | **0.6668** | 0.7359 |
| 33 | `LAW_033` | `IF (betweenness_centrality > 0.25) AND (gate_entropy < 0.25) THEN novelty increases` | `DISCOVERED` | **0.6582** | 0.7480 |
| 34 | `BASE_001` | `IF topology_similarity >= 0.6 THEN transfer_success = True` | `BASELINE` | **0.5360** | 0.5800 |
| 35 | `BASE_003` | `IF gate_distribution_distance >= 0.5 THEN transfer_success = False` | `BASELINE` | **0.5360** | 0.5800 |
| 36 | `BASE_002` | `IF qubit_count_difference >= 1.0 THEN transfer_success = False` | `BASELINE` | **0.4360** | 0.5800 |
