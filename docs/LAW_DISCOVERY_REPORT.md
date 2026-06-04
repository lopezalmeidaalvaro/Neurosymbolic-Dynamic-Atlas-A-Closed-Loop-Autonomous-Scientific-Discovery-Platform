# Law Discovery Report (Component Q)
 
This report logs all candidate symbolic laws discovered by mining frequent structural patterns from quantum circuit compositions.
 
## Candidate Laws
 
| ID | Symbolic Rule | Precision | Coverage | Lift |
| :--- | :--- | :---: | :---: | :---: |
| `LAW_001` | `IF (gate_entropy < 0.25) THEN transferability increases` | 1.0000 | 0.2723 | 3.6724 |
| `LAW_002` | `IF (betweenness_centrality <= 0.25) AND (gate_entropy < 0.25) THEN transferability increases` | 1.0000 | 0.1665 | 3.6724 |
| `LAW_003` | `IF (clifford_ratio <= 0.7) AND (gate_entropy < 0.25) THEN transferability increases` | 1.0000 | 0.1931 | 3.6724 |
| `LAW_004` | `IF (gate_entropy < 0.25) AND (noise_resilience_low) THEN transferability increases` | 1.0000 | 0.1930 | 3.6724 |
| `LAW_005` | `IF (gate_entropy < 0.25) AND (novelty_low) THEN transferability increases` | 1.0000 | 0.1664 | 3.6724 |
| `LAW_006` | `IF (gate_entropy < 0.25) AND (stabilizer_overlap > 0.6) THEN transferability increases` | 1.0000 | 0.1104 | 3.6724 |
| `LAW_007` | `IF (gate_entropy < 0.25) AND (synergy_low) THEN transferability increases` | 1.0000 | 0.2632 | 3.6724 |
| `LAW_008` | `IF (gate_entropy < 0.25) AND (tensor_rank >= 3) THEN transferability increases` | 1.0000 | 0.2483 | 3.6724 |
| `LAW_009` | `IF (gate_entropy < 0.25) AND (stabilizer_overlap <= 0.6) THEN transferability increases` | 1.0000 | 0.1619 | 3.6724 |
| `LAW_010` | `IF (clifford_ratio > 0.7) AND (gate_entropy < 0.25) THEN transferability increases` | 1.0000 | 0.0792 | 3.6724 |
| `LAW_011` | `IF (betweenness_centrality > 0.25) AND (gate_entropy < 0.25) THEN transferability increases` | 1.0000 | 0.1058 | 3.6724 |
| `LAW_012` | `IF (clifford_ratio > 0.7) THEN noise_resilience increases` | 1.0000 | 0.3044 | 3.2841 |
| `LAW_013` | `IF (betweenness_centrality <= 0.25) AND (clifford_ratio > 0.7) THEN noise_resilience increases` | 1.0000 | 0.1897 | 3.2841 |
| `LAW_014` | `IF (clifford_ratio > 0.7) AND (gate_entropy < 0.25) THEN noise_resilience increases` | 1.0000 | 0.0792 | 3.2841 |
| `LAW_015` | `IF (clifford_ratio > 0.7) AND (novelty_low) THEN noise_resilience increases` | 1.0000 | 0.1897 | 3.2841 |
| `LAW_016` | `IF (clifford_ratio > 0.7) AND (stabilizer_overlap > 0.6) THEN noise_resilience increases` | 1.0000 | 0.1256 | 3.2841 |
| `LAW_017` | `IF (clifford_ratio > 0.7) AND (synergy_low) THEN noise_resilience increases` | 1.0000 | 0.2932 | 3.2841 |
| `LAW_018` | `IF (clifford_ratio > 0.7) AND (tensor_rank >= 3) THEN noise_resilience increases` | 1.0000 | 0.2755 | 3.2841 |
| `LAW_019` | `IF (clifford_ratio > 0.7) AND (gate_entropy >= 0.25) THEN noise_resilience increases` | 1.0000 | 0.2252 | 3.2841 |
| `LAW_020` | `IF (clifford_ratio > 0.7) AND (stabilizer_overlap <= 0.6) THEN noise_resilience increases` | 1.0000 | 0.1788 | 3.2841 |
| `LAW_021` | `IF (clifford_ratio > 0.7) AND (transferability_low) THEN noise_resilience increases` | 1.0000 | 0.2252 | 3.2841 |
| `LAW_022` | `IF (betweenness_centrality > 0.25) AND (clifford_ratio > 0.7) THEN noise_resilience increases` | 1.0000 | 0.1147 | 3.2841 |
| `LAW_023` | `IF (betweenness_centrality > 0.25) THEN novelty increases` | 1.0000 | 0.3885 | 2.5733 |
| `LAW_024` | `IF (betweenness_centrality > 0.25) AND (clifford_ratio <= 0.7) THEN novelty increases` | 1.0000 | 0.2738 | 2.5733 |
| `LAW_025` | `IF (betweenness_centrality > 0.25) AND (gate_entropy >= 0.25) THEN novelty increases` | 1.0000 | 0.2827 | 2.5733 |
| `LAW_026` | `IF (betweenness_centrality > 0.25) AND (noise_resilience_low) THEN novelty increases` | 1.0000 | 0.2738 | 2.5733 |
| `LAW_027` | `IF (betweenness_centrality > 0.25) AND (stabilizer_overlap <= 0.6) THEN novelty increases` | 1.0000 | 0.2338 | 2.5733 |
| `LAW_028` | `IF (betweenness_centrality > 0.25) AND (synergy_low) THEN novelty increases` | 1.0000 | 0.3725 | 2.5733 |
| `LAW_029` | `IF (betweenness_centrality > 0.25) AND (tensor_rank >= 3) THEN novelty increases` | 1.0000 | 0.3500 | 2.5733 |
| `LAW_030` | `IF (betweenness_centrality > 0.25) AND (transferability_low) THEN novelty increases` | 1.0000 | 0.2827 | 2.5733 |
| `LAW_031` | `IF (betweenness_centrality > 0.25) AND (stabilizer_overlap > 0.6) THEN novelty increases` | 1.0000 | 0.1547 | 2.5733 |
| `LAW_032` | `IF (betweenness_centrality > 0.25) AND (clifford_ratio > 0.7) THEN novelty increases` | 1.0000 | 0.1147 | 2.5733 |
| `LAW_033` | `IF (betweenness_centrality > 0.25) AND (gate_entropy < 0.25) THEN novelty increases` | 1.0000 | 0.1058 | 2.5733 |
