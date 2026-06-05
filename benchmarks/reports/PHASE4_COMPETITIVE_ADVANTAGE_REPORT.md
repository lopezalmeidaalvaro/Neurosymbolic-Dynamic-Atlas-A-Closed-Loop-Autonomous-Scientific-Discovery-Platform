# QADE Phase IV Competitive Advantage Report

Phase IV searches for dominance regions rather than average compiler rank. QADE is compared against the best available industrial baseline per case: Qiskit Level 3, TKET, or BQSKit.

## Category Dominance

| Category | Cases | Fidelity Win Rate vs Best Industrial | Gate Improvement vs Best Industrial | Fidelity Improvement | Median log10 Fidelity Ratio | Commercial Label |
| :--- | ---: | :---: | ---: | ---: | ---: | :--- |
| controls | 15 | 60.0% [34.3%, 85.7%] | -171.1% | 10.9% | 0.01 | neutral |
| qml | 12 | 58.3% [29.2%, 87.5%] | -94.6% | 18.3% | 0.06 | neutral |
| error_mitigation | 9 | 33.3% [0.7%, 66.0%] | -200.1% | -0.0% | 0.00 | loss_region |
| optimization | 15 | 26.7% [3.5%, 49.8%] | -53.3% | -0.9% | 0.00 | loss_region |
| quantum_chemistry | 12 | 16.7% [0.0%, 38.7%] | -101.0% | 4.1% | 0.00 | neutral |

## Dominance Signals

* Categories where QADE wins >60%: **none**.
* Categories where QADE wins >20% on gate count: **none**.
* Categories where QADE wins >20% on estimated fidelity: **none**.
* Categories where QADE loses: **error_mitigation, optimization**.

## Workload Family Dominance

| Family | Cases | Fidelity Win Rate vs Best Industrial | Gate Improvement vs Best Industrial | Fidelity Improvement | Median log10 Fidelity Ratio | Commercial Label |
| :--- | ---: | :---: | ---: | ---: | ---: | :--- |
| Quantum Kernel | 3 | 100.0% [100.0%, 100.0%] | -102.8% | 53.1% | 0.19 | dominance_region |
| QFT | 3 | 100.0% [100.0%, 100.0%] | -282.6% | 29.9% | 0.11 | dominance_region |
| QAOA | 3 | 66.7% [1.3%, 100.0%] | -15.7% | 19.1% | 0.00 | dominance_region |
| ADAPT-VQE | 3 | 66.7% [1.3%, 100.0%] | -72.5% | 16.3% | 0.08 | dominance_region |
| VQE | 3 | 66.7% [1.3%, 100.0%] | -97.4% | 3.1% | 0.01 | dominance_region |
| Knapsack | 3 | 66.7% [1.3%, 100.0%] | -83.9% | -0.1% | 0.00 | dominance_region |
| Data Re-uploading | 3 | 66.7% [1.3%, 100.0%] | -170.0% | -5.3% | 0.04 | dominance_region |
| Randomized Compiling | 3 | 66.7% [1.3%, 100.0%] | -424.9% | -15.1% | 0.00 | dominance_region |
| Feature Map | 3 | 33.3% [0.0%, 98.7%] | -9.6% | 18.8% | 0.00 | neutral |
| Zero Noise Extrapolation | 3 | 33.3% [0.0%, 98.7%] | -53.8% | 17.1% | 0.00 | neutral |
| Variational Classifier | 3 | 33.3% [0.0%, 98.7%] | -96.0% | 6.7% | 0.00 | neutral |
| Vehicle Routing | 3 | 33.3% [0.0%, 98.7%] | -52.0% | 3.1% | 0.00 | neutral |
| Quantum Volume | 3 | 33.3% [0.0%, 98.7%] | -21.0% | 1.8% | 0.00 | neutral |
| GHZ | 3 | 33.3% [0.0%, 98.7%] | -438.9% | 0.4% | 0.00 | neutral |
| MaxCut | 3 | 33.3% [0.0%, 98.7%] | -16.8% | -7.6% | -0.06 | loss_region |
| Molecular Hamiltonian | 3 | 0.0% [0.0%, 0.0%] | -21.1% | 0.0% | 0.00 | neutral |
| Portfolio | 3 | 0.0% [0.0%, 0.0%] | -53.9% | 0.0% | 0.00 | neutral |
| Scheduling | 3 | 0.0% [0.0%, 0.0%] | -59.9% | 0.0% | 0.00 | neutral |
| UCCSD | 6 | 0.0% [0.0%, 0.0%] | -155.2% | 0.0% | 0.00 | neutral |
| Probabilistic Error Cancellation | 3 | 0.0% [0.0%, 0.0%] | -121.8% | -2.0% | 0.00 | loss_region |

## Family-Level Signals

* Families where QADE wins >60%: **ADAPT-VQE, Data Re-uploading, Knapsack, QAOA, QFT, Quantum Kernel, Randomized Compiling, VQE**.
* Families where QADE wins >20% on gate count: **none**.
* Families where QADE wins >20% on estimated fidelity: **QFT, Quantum Kernel**.
* Families where QADE loses: **MaxCut, Probabilistic Error Cancellation**.

## Case-Level Detail

| Category | Backend | Workload | Fidelity Result | Best Industrial | Gate Improvement | Fidelity Improvement | log10 Fidelity Ratio |
| :--- | :--- | :--- | :---: | :--- | ---: | ---: | ---: |
| controls | FakeBrisbane | GHZ_10q | win | qiskit_l3 | -566.7% | 1.3% | 0.01 |
| controls | FakeBrisbane | QAOA_10q | win | bqskit | -46.1% | 56.6% | 0.19 |
| controls | FakeBrisbane | QFT_8q | win | qiskit_l3 | -457.1% | 28.7% | 0.11 |
| controls | FakeBrisbane | QV_10q | win | qiskit_l3 | -32.3% | 5.3% | 0.02 |
| controls | FakeBrisbane | VQE_10q | win | qiskit_l3 | -148.7% | 8.1% | 0.03 |
| controls | FakeFez | GHZ_10q | loss | qiskit_l3 | -375.0% | 0.0% | 0.00 |
| controls | FakeFez | QAOA_10q | win | bqskit | 53.9% | 0.8% | 0.00 |
| controls | FakeFez | QFT_8q | win | qiskit_l3 | -200.0% | 49.4% | 0.17 |
| controls | FakeFez | QV_10q | loss | qiskit_l3 | -15.4% | 0.0% | 0.00 |
| controls | FakeFez | VQE_10q | win | qiskit_l3 | -71.8% | 1.4% | 0.01 |
| controls | FakeTorino | GHZ_10q | loss | qiskit_l3 | -375.0% | 0.0% | 0.00 |
| controls | FakeTorino | QAOA_10q | loss | qiskit_l3 | -54.9% | 0.0% | 0.00 |
| controls | FakeTorino | QFT_8q | win | bqskit | -190.8% | 11.5% | 0.05 |
| controls | FakeTorino | QV_10q | loss | qiskit_l3 | -15.4% | 0.0% | 0.00 |
| controls | FakeTorino | VQE_10q | loss | qiskit_l3 | -71.8% | 0.0% | 0.00 |
| error_mitigation | FakeBrisbane | PEC_8q | loss | tket | -365.3% | -6.1% | -0.03 |
| error_mitigation | FakeBrisbane | RC_10q | win | qiskit_l3 | -629.9% | 22.6% | 0.09 |
| error_mitigation | FakeBrisbane | ZNE_QAOA_8q | win | qiskit_l3 | -47.5% | 51.3% | 0.18 |
| error_mitigation | FakeFez | PEC_8q | loss | qiskit_l3 | 0.0% | 0.0% | 0.00 |
| error_mitigation | FakeFez | RC_10q | win | qiskit_l3 | -314.5% | 0.9% | 0.00 |
| error_mitigation | FakeFez | ZNE_QAOA_8q | loss | qiskit_l3 | -57.5% | 0.0% | 0.00 |
| error_mitigation | FakeTorino | PEC_8q | loss | qiskit_l3 | 0.0% | 0.0% | 0.00 |
| error_mitigation | FakeTorino | RC_10q | loss | tket | -330.4% | -68.7% | -0.50 |
| error_mitigation | FakeTorino | ZNE_QAOA_8q | loss | qiskit_l3 | -56.2% | 0.0% | 0.00 |
| optimization | FakeBrisbane | Knapsack_8q | win | tket | -103.2% | 0.7% | 0.00 |
| optimization | FakeBrisbane | MaxCut_10q_3regular | loss | qiskit_l3 | 38.7% | -86.5% | -0.87 |
| optimization | FakeBrisbane | Portfolio_8q | loss | qiskit_l3 | -59.7% | 0.0% | 0.00 |
| optimization | FakeBrisbane | Scheduling_9q | loss | qiskit_l3 | -59.4% | 0.0% | 0.00 |
| optimization | FakeBrisbane | VRP_10q | win | qiskit_l3 | -53.0% | 13.2% | 0.05 |
| optimization | FakeFez | Knapsack_8q | win | qiskit_l3 | -64.5% | 3.7% | 0.02 |
| optimization | FakeFez | MaxCut_10q_3regular | loss | qiskit_l3 | 37.4% | -12.4% | -0.06 |
| optimization | FakeFez | Portfolio_8q | loss | qiskit_l3 | -50.3% | 0.0% | 0.00 |
| optimization | FakeFez | Scheduling_9q | loss | qiskit_l3 | -60.2% | 0.0% | 0.00 |
| optimization | FakeFez | VRP_10q | loss | bqskit | -50.6% | -3.8% | -0.02 |
| optimization | FakeTorino | Knapsack_8q | loss | tket | -83.9% | -4.6% | -0.02 |
| optimization | FakeTorino | MaxCut_10q_3regular | win | qiskit_l3 | -126.5% | 76.2% | 0.25 |
| optimization | FakeTorino | Portfolio_8q | loss | qiskit_l3 | -51.7% | 0.0% | 0.00 |
| optimization | FakeTorino | Scheduling_9q | loss | qiskit_l3 | -60.2% | 0.0% | 0.00 |
| optimization | FakeTorino | VRP_10q | loss | qiskit_l3 | -52.4% | 0.0% | 0.00 |
| qml | FakeBrisbane | Classifier_10q_l3 | win | qiskit_l3 | -125.6% | 20.1% | 0.08 |
| qml | FakeBrisbane | FeatureMap_12q_r2 | win | qiskit_l3 | -28.9% | 56.3% | 0.19 |
| qml | FakeBrisbane | Kernel_8q_l2 | win | tket | -130.2% | 73.6% | 0.24 |
| qml | FakeBrisbane | Reuploading_8q_l4 | loss | tket | 2.1% | -97.2% | -1.55 |
| qml | FakeFez | Classifier_10q_l3 | loss | qiskit_l3 | -81.2% | 0.0% | 0.00 |
| qml | FakeFez | FeatureMap_12q_r2 | loss | qiskit_l3 | 0.0% | 0.0% | 0.00 |
| qml | FakeFez | Kernel_8q_l2 | win | qiskit_l3 | -95.1% | 55.9% | 0.19 |
| qml | FakeFez | Reuploading_8q_l4 | win | qiskit_l3 | -334.6% | 72.3% | 0.24 |
| qml | FakeTorino | Classifier_10q_l3 | loss | qiskit_l3 | -81.2% | 0.0% | 0.00 |
| qml | FakeTorino | FeatureMap_12q_r2 | loss | qiskit_l3 | 0.0% | 0.0% | 0.00 |
| qml | FakeTorino | Kernel_8q_l2 | win | bqskit | -83.2% | 29.7% | 0.11 |
| qml | FakeTorino | Reuploading_8q_l4 | win | qiskit_l3 | -177.4% | 9.0% | 0.04 |
| quantum_chemistry | FakeBrisbane | BeH2_ADAPT_10q | win | qiskit_l3 | -85.5% | 29.8% | 0.11 |
| quantum_chemistry | FakeBrisbane | H2_UCCSD_4q | loss | qiskit_l3 | -245.5% | 0.0% | 0.00 |
| quantum_chemistry | FakeBrisbane | LiH_Hamiltonian_8q | loss | qiskit_l3 | -21.1% | 0.0% | 0.00 |
| quantum_chemistry | FakeBrisbane | LiH_UCCSD_8q | loss | qiskit_l3 | -88.3% | 0.0% | 0.00 |
| quantum_chemistry | FakeFez | BeH2_ADAPT_10q | win | qiskit_l3 | -57.3% | 21.3% | 0.08 |
| quantum_chemistry | FakeFez | H2_UCCSD_4q | loss | qiskit_l3 | -222.7% | 0.0% | 0.00 |
| quantum_chemistry | FakeFez | LiH_Hamiltonian_8q | loss | qiskit_l3 | -19.1% | 0.0% | 0.00 |
| quantum_chemistry | FakeFez | LiH_UCCSD_8q | loss | qiskit_l3 | -76.1% | 0.0% | 0.00 |
| quantum_chemistry | FakeTorino | BeH2_ADAPT_10q | loss | qiskit_l3 | -74.8% | -2.3% | -0.01 |
| quantum_chemistry | FakeTorino | H2_UCCSD_4q | loss | qiskit_l3 | -222.7% | 0.0% | 0.00 |
| quantum_chemistry | FakeTorino | LiH_Hamiltonian_8q | loss | qiskit_l3 | -23.0% | 0.0% | 0.00 |
| quantum_chemistry | FakeTorino | LiH_UCCSD_8q | loss | qiskit_l3 | -76.1% | 0.0% | 0.00 |

## Answer

QADE is commercially strongest at the broad category level in **controls**, where the observed fidelity win rate is **60.0%** and mean fidelity improvement is **10.9%**. At the workload-family level, the strongest region is **Quantum Kernel** with **100.0%** win rate and **53.1%** mean fidelity improvement. It is weakest in **quantum_chemistry**, where the observed fidelity win rate is **16.7%**.
