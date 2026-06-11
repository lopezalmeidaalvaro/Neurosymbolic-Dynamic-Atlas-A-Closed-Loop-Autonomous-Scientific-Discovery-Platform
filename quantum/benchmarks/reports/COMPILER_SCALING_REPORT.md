# Compiler Scaling Report

This report defines the qubit capacity tiers and limits for the compilers integrated into the QADE benchmarking pipeline.

## Qubit Capacity Tiers

- **Tier 1:** 1–5 qubits
- **Tier 2:** 6–10 qubits
- **Tier 3:** 11–20 qubits
- **Tier 4:** 21–50 qubits

## Compiler Scaling Capabilities

| Compiler | Max Qubits | Supported Tiers |
| :--- | :---: | :--- |
| **Qiskit** | 127 | Tier 1, Tier 2, Tier 3, Tier 4 |
| **TKET** | 100 | Tier 1, Tier 2, Tier 3, Tier 4 |
| **BQSKit** | 20 | Tier 1, Tier 2, Tier 3 |
| **Cirq** | 50 | Tier 1, Tier 2, Tier 3, Tier 4 |
| **PyZX** | 100 | Tier 1, Tier 2, Tier 3, Tier 4 |

---

*Note: Compilers are dynamically queried for their capabilities. Benchmarks will automatically filter out and mark as "NOT_AVAILABLE" any circuits exceeding a compiler's maximum qubit capacity.*
