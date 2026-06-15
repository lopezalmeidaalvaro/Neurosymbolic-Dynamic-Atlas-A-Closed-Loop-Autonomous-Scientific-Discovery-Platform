# Phase IX: QFT Circuit Destruction Bug Report

## 1. Executive Summary
During validation Run 2 on `ibm_fez` (2026-06-15), QADE compiled the 5-qubit Quantum Fourier Transform (`QFT_5q`) to a trivial layout containing only 11 gates and 1 two-qubit CNOT gate. In contrast, the baseline Qiskit L3 compiler generated 139 gates and 30 two-qubit gates. The physical run yielded a Hellinger fidelity of **0.0451** (equivalent to random output), confirming that the compiled circuit was semantically incorrect.

## 2. Gate Count Comparison
- **Qiskit L3 (Baseline)**: 139 gates, 30 two-qubit gates, Depth: 79
- **QADE (Optimized)**: 11 gates, 1 two-qubit gate, Depth: 3
- **Reduction**: -92.1% gate count (unphysical reduction for QFT)

## 3. Semantic Equivalence Verification
Classical simulation of the unitary matrices (without measurements) of the original transpiled circuit and the QADE-compiled circuit yielded:
- **Direct Equivalence**: `False`
- **Unitary Operator Fidelity (up to global phase)**: **0.1768** (well below the correctness threshold of $>0.999$)
- **Verdict**: **BUG CONFIRMED**. QADE produced a semantically incorrect circuit.

## 4. Root Cause Analysis & Supporting Evidence

### Hypothesis
**A) PyZX optimizer eliminated too many gates due to unsupported gate drops.**

### Supporting Evidence & Technical Breakdown
1.  **Unsupported Basis Gates**: The transpiled input circuit from `transpile(..., optimization_level=1)` contains `sx` (square-root-of-X) gates because they are part of the native basis gates of `ibm_fez` and `GenericBackendV2`.
2.  **Silently Ignored Gates in PyZX Translation**: When QADE converts the transpiled circuit to the PyZX format using `qade_json_to_pyzx` (in `pyzx_adapter.py`), there is no translation mapping for the `SX` gate. 
3.  **Circuit Destruction**: The `SX` gates were silently ignored and dropped from the PyZX graph representation before running `zx.simplify.full_reduce`. Because a major portion of the gate structure was missing, PyZX interpreted the remaining gates as algebraically redundant and simplified them aggressively to an incorrect 11-gate circuit.
4.  **No Fallback Check**: Because `pyzx_optimizer.py` lacked post-optimization semantic validation or gate count reduction checks, it silently accepted the incorrect circuit and passed it to the physical QPU.
