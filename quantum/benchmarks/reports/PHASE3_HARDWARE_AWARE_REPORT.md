# QADE Phase III Hardware-Aware Validation Report

## Competitive Leaderboard

| Compiler | Gate Count | Two-Qubit Count | SWAP Count | Depth | Critical Duration (us) | Total Estimated Fidelity | Compile Time (ms) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **bqskit** | 383.7 | 45.0 | 0.0 | 72.5 | 16.32 | 5.513e-03 | 158.2 |
| **qade_phase2** | 13051.4 | 11795.9 | 10735.0 | 9475.0 | 15695.82 | 7.901e-12 | 13364.5 |
| **qade_phase3** | 23506.3 | 1615.6 | 0.0 | 2323.0 | 352.25 | 6.396e-03 | 3540.1 |
| **qiskit_l3** | 23641.0 | 1886.4 | 0.0 | 2597.0 | 394.53 | 6.348e-03 | 871.1 |
| **tket** | 325.0 | 45.0 | 0.0 | 91.0 | 18.12 | 5.016e-03 | 1388.8 |

## QADE Phase III vs Qiskit L3

* Win rate by `total_estimated_fidelity`: **28.0%** (7/25 matched cases).
* Mean relative fidelity improvement on non-underflow baselines: **10.20%**.
* Median log10 fidelity ratio vs Qiskit L3: **0.00**.
* Mean gate-count advantage: **0.52%**.
* Mean critical-duration reduction vs QADE Phase II: **98.95%**.

## Routing and Placement Ablation

Best observed combination: **fidelity_aware** placement with **sabre** routing.

| Placement | Routing | Gate Count | SWAP Count | Critical Duration (us) | Total Estimated Fidelity |
| :--- | :--- | ---: | ---: | ---: | ---: |
| fidelity_aware | sabre | 400 | 0 | 21.66 | 1.899e-03 |
| fidelity_aware | beam | 400 | 0 | 21.66 | 1.899e-03 |
| fidelity_aware | hybrid | 400 | 0 | 21.66 | 1.899e-03 |
| fidelity_aware | coherence_aware_sabre | 400 | 0 | 21.66 | 1.899e-03 |
| trivial | sabre | 400 | 0 | 21.66 | 5.857e-04 |
| trivial | beam | 400 | 0 | 21.66 | 5.857e-04 |
| trivial | hybrid | 400 | 0 | 21.66 | 5.857e-04 |
| trivial | coherence_aware_sabre | 400 | 0 | 21.66 | 5.857e-04 |
| distance | sabre | 400 | 0 | 21.66 | 1.977e-04 |
| distance | beam | 400 | 0 | 21.66 | 1.977e-04 |
| distance | hybrid | 400 | 0 | 21.66 | 1.977e-04 |
| distance | coherence_aware_sabre | 400 | 0 | 21.66 | 1.977e-04 |
| interaction | beam | 405 | 5 | 52.14 | 7.281e-05 |
| interaction | sabre | 416 | 16 | 56.34 | 1.662e-05 |
| interaction | hybrid | 417 | 17 | 51.96 | 8.680e-06 |
| interaction | coherence_aware_sabre | 416 | 16 | 59.22 | 2.408e-50 |

## Success Criteria

| Criterion | Result | Observed |
| :--- | :---: | :--- |
| Win rate vs Qiskit L3 > 60% | FAIL | 28.0% |
| Mean critical duration reduction vs Phase II >= 20% | PASS | 98.9% |
| Logical fidelity >= 0.999 on verifiable circuits | PASS | maintained by QADE equivalence path for <=12q |
| Positive gate-count advantage vs Qiskit L3 | PASS | 0.5% |

Overall Phase III result: **3/4 criteria passed**.
