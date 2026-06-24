# Placement Score Diagnosis: Run 8 Qubit Groups

- **Backend**: FakeFez (156 qubits)
- **max_t1**: 274.4 us  |  **max_t2**: 302.8 us
- **Scoring weights**: w_T1=0.225, w_T2=0.225, w_readout=0.3, w_gate=0.25, w_degree=0.01

## WINNERS (QFT worked): qubits [19, 35, 15, 13, 14]

| Qubit | T1 (µs) | T2 (µs) | T1/max | T2/max | Readout Err | Avg Gate Err | Degree | **Score** | Rank/156 |
|------:|--------:|--------:|-------:|-------:|------------:|-------------:|-------:|----------:|-------:|
|    19 |   184.4 |   120.7 |  0.672 |  0.399 |     0.00732 |      0.00157 |      2 |   0.25838 |    28 |
|    35 |   175.0 |    48.1 |  0.638 |  0.159 |     0.00684 |      0.00169 |      2 |   0.19683 |    83 |
|    15 |   233.0 |   146.2 |  0.849 |  0.483 |     0.03296 |      0.00233 |      2 |   0.30927 |     9 |
|    13 |   262.3 |   204.6 |  0.956 |  0.676 |     0.01050 |      0.00181 |      2 |   0.38349 |     2 |
|    14 |   225.3 |    45.9 |  0.821 |  0.152 |     0.00366 |      0.00246 |      2 |   0.23715 |    43 |

**Group avg score: 0.27702**

## LOSERS  (GHZ failed): qubits [131, 132, 133, 134, 135]

| Qubit | T1 (µs) | T2 (µs) | T1/max | T2/max | Readout Err | Avg Gate Err | Degree | **Score** | Rank/156 |
|------:|--------:|--------:|-------:|-------:|------------:|-------------:|-------:|----------:|-------:|
|   131 |   141.2 |   201.5 |  0.515 |  0.665 |     0.05542 |      0.00175 |      3 |   0.27842 |    20 |
|   132 |   137.0 |   161.6 |  0.499 |  0.534 |     0.01343 |      0.00167 |      2 |   0.24799 |    33 |
|   133 |   195.3 |    47.9 |  0.712 |  0.158 |     0.01636 |      0.00267 |      3 |   0.22017 |    60 |
|   134 |   151.3 |    22.7 |  0.551 |  0.075 |     0.00537 |      0.00220 |      2 |   0.15876 |   120 |
|   135 |   179.6 |    92.5 |  0.655 |  0.305 |     0.06006 |      0.00277 |      2 |   0.21728 |    61 |

**Group avg score: 0.22452**

## TRIVIAL (0..4): qubits [0, 1, 2, 3, 4]

| Qubit | T1 (µs) | T2 (µs) | T1/max | T2/max | Readout Err | Avg Gate Err | Degree | **Score** | Rank/156 |
|------:|--------:|--------:|-------:|-------:|------------:|-------------:|-------:|----------:|-------:|
|     0 |    48.8 |    42.4 |  0.178 |  0.140 |     0.01147 |      0.00384 |      1 |   0.07711 |   153 |
|     1 |   255.7 |   302.8 |  0.932 |  1.000 |     0.01172 |      0.00353 |      2 |   0.45028 |     1 |
|     2 |   274.4 |   100.0 |  1.000 |  0.330 |     0.00488 |      0.00179 |      2 |   0.31739 |     8 |
|     3 |   219.7 |   215.5 |  0.801 |  0.712 |     0.01587 |      0.00240 |      3 |   0.36498 |     3 |
|     4 |   190.9 |   161.9 |  0.696 |  0.535 |     0.00146 |      0.00188 |      2 |   0.29595 |    15 |

**Group avg score: 0.30114**

---
## Direct Comparison: Key Metrics

| Metric | LOSERS (131-135) avg | TRIVIAL (0-4) avg | WINNERS (19,35,15,13,14) avg |
|--------|---------------------:|------------------:|-----------------------------:|
| T1 (µs) | 160.9 | 197.9 | 216.0 |
| T2 (µs) | 105.2 | 164.5 | 113.1 |
| Readout Err | 0.03013 | 0.00908 | 0.01226 |
| Avg Gate Err | 0.00221 | 0.00269 | 0.00197 |
| Score | 0.22452 | 0.30114 | 0.27702 |

---
## Verdict

### Q: Do qubits 131-135 have higher T1/T2 than 0-4 in FakeFez?
- **T1**: LOSERS avg = 160.9 us vs TRIVIAL avg = 197.9 us -> **NO** (-18.7%)
- **T2**: LOSERS avg = 105.2 us vs TRIVIAL avg = 164.5 us -> **NO** (-36.0%)

### Q: Do they also have worse noise metrics?
- **Readout Error**: LOSERS = 0.03013 vs TRIVIAL = 0.00908 -> **WORSE** (+231.7%)
- **Gate Error**: LOSERS = 0.00221 vs TRIVIAL = 0.00269 -> **BETTER** (-17.8%)

### Q: Does Stage C score the LOSERS higher than TRIVIAL?
- **Score**: LOSERS = 0.22452 vs TRIVIAL = 0.30114 -> **NO**

> [!NOTE]
> In FakeFez, qubits 131-135 do NOT score higher than 0-4. The real
> ibm_fez calibration must have different T1/T2 values on the day of Run 8.
> The fallback mechanism is still essential as a safety net against
> future calibration drift.
