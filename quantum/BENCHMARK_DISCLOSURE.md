# QADE Benchmark Disclosure

This document discloses the execution policy, performance parameters, and key limitations of the Quantum Algorithm Discovery Engine (QADE) real-hardware compilation benchmarks.

---

## 1. Compiler Execution Policy

All benchmarks are evaluated using a strict **real-or-exclude** execution policy:
*   **No emulation**: Comparative compilers (Qiskit Level 3, TKET, BQSKit, Cirq-native, PyZX) run their real native transpilation/compilation passes.
*   **No emulation of backends**: High-fidelity estimations are generated using daily calibration parameters (T1/T2 times, gate errors, readout errors) from live quantum backends.
*   **No silent substitutions**: If a compiler is not available or fails on a given circuit configuration (such as BQSKit for circuits $>20$ qubits), it is marked as `NOT_AVAILABLE` and excluded from that configuration's scoring metrics.
*   **Benchmark Configuration**: 5 compilers evaluated across 5 backends and 5 circuit types (2 to 30 qubits), with 30 runs per configuration (totaling $n=780$ configurations per compiler).

---

## 2. Verified Benchmark Performance

Based on the verified results stored in [COMPILER_COMPARISON_REAL.csv](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/results/COMPILER_COMPARISON_REAL.csv):

*   **Mean Fidelity**: QADE achieved a mean fidelity of **0.9228** (p < 0.0001, Cliff's $d = 0.33$, $n = 780$), which is statistically superior to the Qiskit L3 baseline of **0.8544**.
*   **Mean Gate Reduction**: QADE achieved an average gate reduction of **-85.9%** compared to Qiskit L3 on circuits across the 2-30 qubit range. Note that this gate reduction factor reflects the mixed distribution; the effect is highly pronounced on smaller circuits where compiler routines converge to minimal physical layouts.
*   **Highest Benchmark Fidelity**: Cirq-native achieved the highest overall average fidelity of **0.9262** ($p < 0.0001$ vs Qiskit L3), primarily due to its efficient native simplifications on small-scale circuits (2-5 qubits).
*   **BQSKit Performance**: BQSKit achieved a mean fidelity of **0.9185** ($p < 0.0001$ vs Qiskit L3) but was excluded for circuits $>20$ qubits (`NOT_AVAILABLE`).

---

## 3. Disclosures & Known Limitations

1.  **Classical Validation Limits**: Validating optimization motifs requires calculating the full classical statevector. This step is memory-constrained and restricted to $\le 20$ qubits. For larger circuits ($>20$ qubits), QADE relies on pre-validated motif libraries.
2.  **Compilation Latency**: QADE's evolutionary sandbox and validation pipeline require a mean compile time of **429 ms**, compared to **37 ms** for the Qiskit L3 baseline.
3.  **No Live Hardware Execution**: The benchmark scores are computed using physical cost models parameterized by live hardware calibration parameters. They represent predicted physical execution success probabilities, not direct measurements of quantum processors.
