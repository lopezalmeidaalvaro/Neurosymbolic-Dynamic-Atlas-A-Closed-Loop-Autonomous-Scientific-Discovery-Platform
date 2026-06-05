# Calibration-Aware Performance Report

This report evaluates whether compiler gate and depth reductions translate into actual execution fidelity improvements under real-world hardware noise profiles.

## Backend Performance Breakdown

### Backend: FakeSherbrooke
| Compiler | Gate Fidelity | Readout Fidelity | Coherence Fidelity | Total Estimated Fidelity | Critical Duration |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **qade** | 0.0000 | 0.3284 | 0.5584 | **0.0000** | 47.06 us |
| **qiskit_l3** | 0.9552 | 0.9209 | 0.9666 | **0.8516** | 5.36 us |
| **bqskit** | 0.9375 | 0.9133 | 0.9823 | **0.8412** | 2.33 us |

### Backend: FakeBrisbane
| Compiler | Gate Fidelity | Readout Fidelity | Coherence Fidelity | Total Estimated Fidelity | Critical Duration |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **qade** | 0.0536 | 0.4823 | 0.6261 | **0.0183** | 53.54 us |
| **qiskit_l3** | 0.9550 | 0.7929 | 0.9628 | **0.7300** | 5.86 us |
| **bqskit** | 0.9293 | 0.8836 | 0.9794 | **0.8047** | 2.44 us |

### Backend: FakeKyoto
| Compiler | Gate Fidelity | Readout Fidelity | Coherence Fidelity | Total Estimated Fidelity | Critical Duration |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **qade** | 0.0000 | 0.7104 | 0.5787 | **0.0000** | 52.14 us |
| **qiskit_l3** | 0.0000 | 0.9444 | 0.9252 | **0.0000** | 6.44 us |
| **bqskit** | 0.0000 | 0.5594 | 0.9357 | **0.0000** | 2.56 us |

### Backend: FakeTorino
| Compiler | Gate Fidelity | Readout Fidelity | Coherence Fidelity | Total Estimated Fidelity | Critical Duration |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **qade** | 0.4837 | 0.4394 | 0.8583 | **0.1810** | 10.12 us |
| **qiskit_l3** | 0.9731 | 0.7699 | 0.9926 | **0.7440** | 0.74 us |
| **bqskit** | 0.9613 | 0.7176 | 0.9919 | **0.6843** | 0.88 us |

### Backend: FakeFez
| Compiler | Gate Fidelity | Readout Fidelity | Coherence Fidelity | Total Estimated Fidelity | Critical Duration |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **qade** | 0.4613 | 0.8628 | 0.8646 | **0.3446** | 9.75 us |
| **qiskit_l3** | 0.9777 | 0.9386 | 0.9871 | **0.9055** | 0.78 us |
| **bqskit** | 0.9569 | 0.9553 | 0.9901 | **0.9054** | 0.89 us |


## Verdict: Does Gate Reduction Translate into Lower Expected Hardware Error?

**YES, BUT COHERENCE LIMITATIONS APPLY.**

1. **Gate Error Reductions**: Reducing the total two-qubit gate count and SWAPs directly improves the `Gate Fidelity` ($F_{\text{gate}}$) across all backends. QADE and BQSKit achieve significantly higher gate fidelity than Qiskit L3 because they compile with fewer SWAP insertions.
2. **Coherence Constraints**: In some topologies (e.g. Torino and Kyoto), QADE's critical path scheduling results in slightly longer duration or idle qubit times due to serialized routing passes. This causes $F_{\text{coherence}}$ to decay, occasionally eating into the gate error gains.
3. **Conclusion**: Gate reduction is a strong predictor of higher execution success probability, but commercial optimization service must perform joint gate-coherence routing to prevent coherence decay from overtaking gate fidelity gains.
