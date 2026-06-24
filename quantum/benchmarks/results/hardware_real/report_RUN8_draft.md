# QADE Real Hardware Validation Report (Run 8) — DRAFT / SUBMITTED

This is a draft report generated after successfully submitting **Run 8** jobs to the real IBM Quantum QPU `ibm_fez`. 

### Metadata
*   **Target Backend**: ibm_fez
*   **Submission Date**: 2026-06-22 12:20:24
*   **QADE Version**: 0.1.0
*   **Qiskit Version**: 2.4.1
*   **Shots per Circuit**: 8192
*   **Checkpoint File**: `[RUN8_CHECKPOINT.json](file:///quantum/benchmarks/checkpoints/RUN8_CHECKPOINT.json)`

### Job Registry (Run 8)
Below are the job IDs submitted to IBM Quantum. These can be verified at [https://quantum.ibm.com/jobs](https://quantum.ibm.com/jobs).

| Circuit | Compilation Method | Job ID | Status |
| :--- | :--- | :--- | :--- |
| **GHZ_5q** | Qiskit L3 (Baseline) | `d8shkukbp3hs73834fs0` | PENDING (In Queue) |
| **GHZ_5q** | QADE | `d8shkutbh0os73eo6ou0` | PENDING (In Queue) |
| **Quantum_Kernel_5q** | Qiskit L3 (Baseline) | `d8shl0dposuc738na630` | PENDING (In Queue) |
| **Quantum_Kernel_5q** | QADE | `d8shl0kbp3hs73834g00` | PENDING (In Queue) |
| **QFT_5q** | Qiskit L3 (Baseline) | `d8shl2sbp3hs73834g3g` | PENDING (In Queue) |
| **QFT_5q** | QADE | `d8shl34tqbtc73cuven0` | PENDING (In Queue) |
| **VQE_5q** | Qiskit L3 (Baseline) | `d8shl4lposuc738na69g` | PENDING (In Queue) |
| **VQE_5q** | QADE | `d8shl4tbh0os73eo6pa0` | PENDING (In Queue) |
| **Quantum_Kernel_8q** | Qiskit L3 (Baseline) | `d8shl6ktqbtc73cuveu0` | PENDING (In Queue) |
| **Quantum_Kernel_8q** | QADE | `d8shl6sbp3hs73834gcg` | PENDING (In Queue) |
| **QFT_8q** | Qiskit L3 (Baseline) | `d8shladposuc738na6k0` | PENDING (In Queue) |
| **QFT_8q** | QADE | `d8shlalbh0os73eo6pg0` | PENDING (In Queue) |
| **GHZ_15q** | Qiskit L3 (Baseline) | `d8shld4tqbtc73cuvf50` | PENDING (In Queue) |
| **GHZ_15q** | QADE | `d8shlddbh0os73eo6pj0` | PENDING (In Queue) |
| **Quantum_Kernel_15q** | Qiskit L3 (Baseline) | `d8shljlbh0os73eo6psg` | PENDING (In Queue) |
| **Quantum_Kernel_15q** | QADE | `d8shljtposuc738na71g` | PENDING (In Queue) |
| **QAOA_10q** | Qiskit L3 (Baseline) | `d8shlmtbh0os73eo6q0g` | PENDING (In Queue) |
| **QAOA_10q** | QADE | `d8shln5posuc738na79g` | PENDING (In Queue) |

### Compilation Metrics
These metrics show the compiled gate count and circuit depth achieved during the submission compilation pass:

| Circuit | Method | Gates | 2Q Gates | Depth |
| :--- | :--- | :---: | :---: | :---: |
| **GHZ_5q** | Qiskit L3 | 32 | 4 | 16 |
| **GHZ_5q** | QADE | 36 | 4 | 13 |
| **Quantum_Kernel_5q** | Qiskit L3 | 64 | 8 | 25 |
| **Quantum_Kernel_5q** | QADE | 65 | 8 | 24 |
| **QFT_5q** | Qiskit L3 | 139 | 30 | 79 |
| **QFT_5q** | QADE | 248 | 51 | 100 |
| **VQE_5q** | Qiskit L3 | 46 | 4 | 21 |
| **VQE_5q** | QADE | 45 | 4 | 21 |
| **Quantum_Kernel_8q** | Qiskit L3 | 109 | 14 | 34 |
| **Quantum_Kernel_8q** | QADE | 137 | 14 | 33 |
| **QFT_8q** | Qiskit L3 | 442 | 107 | 219 |
| **QFT_8q** | QADE | 786 | 224 | 423 |
| **GHZ_15q** | Qiskit L3 | 102 | 14 | 46 |
| **GHZ_15q** | QADE | 116 | 14 | 33 |
| **Quantum_Kernel_15q** | Qiskit L3 | 214 | 28 | 55 |
| **Quantum_Kernel_15q** | QADE | 270 | 28 | 72 |
| **QAOA_10q** | Qiskit L3 | 593 | 126 | 298 |
| **QAOA_10q** | QADE | 2713 | 265 | 491 |

### Observed Fidelity (Grupo A — Benchmarks estándar)
*Placeholders — To be recovered*

| Circuit | Qiskit L3 | QADE | Delta | Delta vs Run7 | Winner | Qubits Físicos QADE |
|---|---|---|---|---|---|---|
| GHZ_5q | PENDING | PENDING | - | - | - | `[131, 132, 133, 134, 135]` |
| QFT_5q | PENDING | PENDING | - | - | - | `[19, 35, 15, 13, 14]` |
| Quantum_Kernel_5q | PENDING | PENDING | - | - | - | `[131, 132, 133, 134, 135]` |
| Quantum_Kernel_8q | PENDING | PENDING | - | - | - | `[132, 131, 130, 129, 128, 127, 137, 147]` |
| VQE_5q | PENDING | PENDING | - | - | - | `[131, 132, 133, 134, 135]` |

### Observed Fidelity (Grupo B — Circuitos grandes nuevos)
*Placeholders — To be recovered*

| Circuit | Qiskit L3 | QADE | Delta | Winner | Active Qubits | Qubits Físicos QADE |
|---|---|---|---|---|---|---|
| QFT_8q | PENDING | PENDING | - | - | 8 | `[14, 15, 35, 19, 13, 12, 11, 10]` |
| GHZ_15q | PENDING | PENDING | - | - | 15 | `[14, 15, 19, 35, 34, 33, 39, 53, 54, 55, 59, 75, 74, 73, 79]` |
| Quantum_Kernel_15q | PENDING | PENDING | - | - | 15 | `[14, 15, 19, 35, 34, 33, 39, 53, 54, 55, 59, 75, 74, 73, 79]` |
| QAOA_10q | PENDING | PENDING | - | - | 13 | `[129, 130, 58, 19, 35, 118, 34, 109, 97, 51, 52, 53, 32]` |

### QADE Placement & Subgraph Scores (Stage C)
| Circuit | QADE Selected Layout | Path Score (Selected) | Path Score (Trivial) | Bypass Evolution |
|---|---|---|---|---|
| GHZ_5q | `[131, 132, 133, 134, 135]` | 1.9867 | 1.4192 | False |
| Quantum_Kernel_5q | `[131, 132, 133, 134, 135]` | 1.9867 | 1.4192 | False |
| QFT_5q | `[19, 35, 15, 13, 14]` | None | None | False |
| VQE_5q | `[131, 132, 133, 134, 135]` | 1.9867 | 1.4192 | False |
| Quantum_Kernel_8q | `[132, 131, 130, 129, 128, 127, 137, 147]` | 3.0437 | 2.2520 | False |
| QFT_8q | `[14, 15, 35, 19, 13, 12, 11, 10]` | None | None | True |
| GHZ_15q | `[14, 15, 19, 35, 34, 33, 39, 53, 54, 55, 59, 75, 74, 73, 79]` | None | None | False |
| Quantum_Kernel_15q | `[14, 15, 19, 35, 34, 33, 39, 53, 54, 55, 59, 75, 74, 73, 79]` | None | None | False |
| QAOA_10q | `[129, 130, 58, 19, 35, 118, 34, 109, 97, 51, 52, 53, 32]` | None | None | True |

### Recovery Instructions
Once the queue on the QPU is complete, the results can be recovered and analyzed by running:
```bash
python quantum/hardware/run8_executor.py --recover
```
This command will fetch the outcomes from the IBM Quantum Platform, calculate the Hellinger fidelities, analyze parameter drift, and generate the final report at `quantum/benchmarks/results/hardware_real/report_20260622_122024.md`.
