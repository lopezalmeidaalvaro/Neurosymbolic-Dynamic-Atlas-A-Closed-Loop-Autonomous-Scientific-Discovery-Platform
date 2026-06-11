# Statistical Validation Report

This report evaluates the statistical significance of QADE compiling performance compared to Qiskit L3.

## 1. Statistical Significance Table (Fidelity)

| Compiler Workflow | N | Mean Fidelity | Median Fidelity | 95% Confidence Interval | p-value vs Qiskit L3 | Cliff's Delta | Significance |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **PyZX** | 810 | 0.7237 | 0.8777 | [0.7022, 0.7428] | 8.2256e-09 | -0.1654 | Significativo (p < 0.05) |
| **TKET** | 780 | 0.8931 | 0.9159 | [0.8873, 0.8993] | 1.4407e-06 | 0.1396 | Significativo (p < 0.05) |
| **BQSKit** | 780 | 0.9185 | 0.9224 | [0.9154, 0.9217] | 1.1248e-23 | 0.2906 | Significativo (p < 0.05) |
| **Cirq-native** | 780 | 0.9262 | 0.9293 | [0.9235, 0.9288] | 3.4779e-35 | 0.3585 | Significativo (p < 0.05) |
| **QADE** | 780 | 0.9228 | 0.9275 | [0.9200, 0.9254] | 7.8304e-30 | 0.3286 | Significativo (p < 0.05) |
| **QADE + PyZX** | 780 | 0.7987 | 0.8905 | [0.7825, 0.8147] | 7.2623e-02 | -0.0520 | No Significativo |
| **QADE + Knowledge Graph** | 780 | 0.7508 | 0.8795 | [0.7327, 0.7699] | 4.2046e-06 | -0.1333 | Significativo (p < 0.05) |
| **QADE + Evolution + PyZX** | 780 | 0.7628 | 0.8813 | [0.7445, 0.7814] | 1.3095e-04 | -0.1108 | Significativo (p < 0.05) |

## 2. Statistical Significance Table (Gate Count)

| Compiler Workflow | N | Mean Gates | Median Gates | 95% Confidence Interval | p-value vs Qiskit L3 | Cliff's Delta | Significance |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **PyZX** | 810 | 56.4 | 28.0 | [52.3, 61.3] | 3.2707e-02 | -0.0613 | Significativo (p < 0.05) |
| **TKET** | 780 | 25.9 | 17.5 | [24.5, 27.3] | 1.1219e-27 | -0.3157 | Significativo (p < 0.05) |
| **BQSKit** | 780 | 12.4 | 9.5 | [11.7, 13.0] | 1.3205e-116 | -0.6646 | Significativo (p < 0.05) |
| **Cirq-native** | 780 | 12.4 | 9.5 | [11.7, 13.0] | 1.3205e-116 | -0.6646 | Significativo (p < 0.05) |
| **QADE** | 780 | 10.6 | 8.0 | [10.1, 11.2] | 5.6509e-134 | -0.7131 | Significativo (p < 0.05) |
| **QADE + PyZX** | 780 | 40.6 | 23.0 | [37.5, 43.8] | 2.3491e-09 | -0.1729 | Significativo (p < 0.05) |
| **QADE + Knowledge Graph** | 780 | 47.3 | 26.0 | [43.9, 50.6] | 8.7470e-04 | -0.0964 | Significativo (p < 0.05) |
| **QADE + Evolution + PyZX** | 780 | 47.0 | 24.0 | [43.1, 50.9] | 1.1642e-04 | -0.1116 | Significativo (p < 0.05) |

## 3. Results with Insufficient Statistical Power

No workflows have insufficient statistical power in this test (all n >= 30).