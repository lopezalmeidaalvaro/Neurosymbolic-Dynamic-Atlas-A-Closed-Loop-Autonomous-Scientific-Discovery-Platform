# QADE Phase VI Economic Impact Report

## Hardware Savings

* IBM-style saved two-qubit operations: **166.0**
* IBM-style saved execution time: **157.22 us**
* Estimated saved shots required: **5284.0**

## Workload Economics

| Workload Family | Data Source | Avg Motif Gate Benefit | Avg Fidelity Gain | Cost Savings Per Job | Savings % |
| :--- | :--- | ---: | ---: | ---: | ---: |
| Quantum Kernel | observed_transfer | 46.00 | 2.002e-05 | $0.00 | 0.0% |
| QFT | mapped_transfer | 24.00 | -5.423e-05 | $0.00 | 0.0% |
| QAOA | mapped_transfer | 46.00 | 3.271e-05 | $0.00 | 0.0% |
| VQE | mapped_transfer | 24.00 | -5.423e-05 | $0.00 | 0.0% |
| ADAPT-VQE | mapped_transfer | 28.00 | 3.128e-04 | $45.09 | 6.4% |
| Knapsack | mapped_transfer | 46.00 | 3.271e-05 | $0.00 | 0.0% |
| Randomized Compiling | mapped_transfer | 28.00 | 3.128e-04 | $45.09 | 6.4% |
| Data Re-uploading | mapped_transfer | 28.00 | 3.128e-04 | $45.09 | 6.4% |

## Final Questions

* Hardware cost saved: **166.0 two-qubit-equivalent operations** and **157.22 us** per observed motif portfolio application set.
* Execution cost saved: **$135.28 per representative workload portfolio** under conservative shot/runtime assumptions.
* Highest-value family: **ADAPT-VQE**.
