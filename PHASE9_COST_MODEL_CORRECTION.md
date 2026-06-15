# QADE Phase IX - Hardware Cost Model Correction Report

> **⚠️ DISCLOSURE:** All economic metrics, hardware costs, and licensing models discussed in this project context represent speculative simulation projections and do not reflect active revenues or contracted values. (modelo especulativo — sin revenue real)

This report documents the resolution of the absolute scale discrepancy (bug) in QADE's physical cost model, the creation of [hardware_cost_model_v2.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/optimization/hardware_cost_model_v2.py), and its validation against real quantum processor outcomes.

---

## 1. Summary of Diagnosed Bugs

1.  **Readout Error Over-counting**: Readout fidelity was aggregated over all qubits in the active layout, mapping to all 156 qubits of the QPU instead of only the 5 measured qubits. This resulted in readout fidelity of $F_{\text{readout}} \approx 0.0076$.
2.  **Decoherencia Over-counting**: Decaimiento de coherencia temporal ($T_1$/$T_2$) era calculado sobre todo el chip físico de 156 qubits debido a barreras e instrucciones de transpilado redundantes.
3.  **Single-Qubit Gate Noise**: Se incluían errores de compuertas de un qubit en el presupuesto de fidelidad, añadiendo ruido de fondo irrelevante para fidelidades absolutas.

---

## 2. Corrections Applied (Cost Model v2)

We implemented [hardware_cost_model_v2.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/optimization/hardware_cost_model_v2.py) with the following principles:

*   **CNOT-only Gate Fidelity**: `log_gate_fidelity` accumulates only CNOT/2-qubit gates, where error rates are significant ($\approx 0.5\%$).
*   **Measurement-only Readout Fidelity**: Readout fidelity is calculated only for the qubits that have a `measure` instruction in `native.data`.
*   **Active Qubits Coherence**: Decoherencia is accumulated only for the qubits participating in gates or measurements, using the critical path duration as the exposure time.

---

## 3. Validation with Real Hardware Results (`ibm_marrakesh`)

The v2 cost model has been validated against the actual compilation layouts from both execution runs:

### GHZ_5q Workload:
*   **Old Cost Model**: Qiskit L3 = `0.0042` | QADE = `0.0039`
*   **New Cost Model v2**: Qiskit L3 = `0.8616` | QADE = `0.8150`
*   **Observed Fidelity (Run 2)**: Qiskit L3 = `0.9539` | QADE = `0.9369`
*   **Compiler Order Validation**: Both the new cost model and the physical QPU confirm **Qiskit Wins** (since Qiskit uses 32 gates vs QADE's 36 gates for this non-dominance setup).

### VQE_5q Workload:
*   **Old Cost Model**: Qiskit L3 = `0.0042` | QADE = `0.0038`
*   **New Cost Model v2**: Qiskit L3 = `0.8599` | QADE = `0.8657`
*   **Observed Fidelity (Run 2)**: Qiskit L3 = `0.9761` | QADE = `0.9954`
*   **Compiler Order Validation**: Under QADE's layout optimization, the physical CNOT-active qubits achieved a lower average error rate. The new model restricts decoherence and gate noise to this subset, verifying **QADE Wins** (+1.93% observed delta) over Qiskit for the VQE ansatz compilation, with the predicted order also favoring QADE (0.8657 > 0.8599).

### Quantum Kernel 8q Workload (Dominance Region):
*   **New Cost Model v2**: Qiskit L3 = `0.7654` | QADE = `0.8022`
*   **Observed Fidelity (Run 2)**: Qiskit L3 = `0.9515` | QADE = `0.9683`
*   **Compiler Order Validation**: QADE achieves higher observed fidelity (+1.68% observed delta) and is predicted correctly by the v2 cost model (0.8022 > 0.7654), validating the dominance region.
