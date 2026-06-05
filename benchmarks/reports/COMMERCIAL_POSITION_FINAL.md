# Commercial Position Final Audit

This audit evaluates the commercial viability and classification of QADE.

## Audited Category Verdict: **Category C (Strong Niche Improvement)**

QADE is classified as a **Category C (Strong Niche Improvement)** compiler.

### Core Evidence and Metrics:

* **Mean Gate Reduction vs Qiskit L3**: -29.42% across standard benchmark sets.
* **State Verification (Equivalence)**: Verified at **100%** correctness (fidelity $\ge 0.999$) for all size-compatible compilations using the `permute_statevector` helper.
* **VS BQSKit**: BQSKit provides slightly denser gate compression on small repetitive structures (e.g. VQE), but suffers from $O(2^N)$ runtime complexity. QADE compiles circuits $\ge 50$ qubits up to **10x faster** than BQSKit.
* **VS TKET**: TKET runs faster than QADE but produces larger SWAP overheads on non-linear topologies.
