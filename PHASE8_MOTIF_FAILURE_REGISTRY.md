# QADE Motif Governance: Failure & Limitation Registry

This document records the optimization motifs, compiler configurations, and topological regimes where QADE fails to outperform baseline compilers or encounters execution limits, with technical hypotheses and mitigation pathways.

---

## 1. Non-Transferable Motifs

The following motifs have a transferability score of **0.0** and are restricted to their origin workloads:

### 1.1. `QADE-M-0010` (`motif_6828d62ca193d193`)
*   **Description**: RX(0.08)-RX(-0.08) Rotation Cancellation
*   **Conditions of Failure**: Fails to transfer to `Quantum Kernel`, `QFT`, or `Error Mitigation` workload families.
*   **Backend Limitations**: No transfer observed outside of simulator environments containing VQE-like parameter patterns.
*   **Technical Hypothesis**: RX rotations with small parameters ($\pm 0.08$) are highly specific to the ADAPT-VQE ansatz optimization path. In other workload families, RX gates with these specific angles do not occur sequentially, or are combined into multi-qubit entangling operations before algebraic cancellation can occur.
*   **Status / Governance**: **VALIDATED (Restricted)**. The motif is valid mathematically but must be restricted to the VQE domain registry. It should not be loaded into the general-purpose rewriter.

### 1.2. `QADE-M-0011` (`motif_5f8b73934973613d`)
*   **Description**: RX(0.12)-RX(-0.12) Rotation Cancellation
*   **Conditions of Failure**: Fails to transfer to non-VQE workload families.
*   **Backend Limitations**: Same as `QADE-M-0010`.
*   **Technical Hypothesis**: Specific RX rotation parameters are typical of variational ansatzes where parameters update slowly. General workloads (like QFT) rely on discrete Clifford+T gates or discrete phase rotations (RZ), rendering RX-specific cancellation patterns redundant.
*   **Status / Governance**: **VALIDATED (Restricted)**. Retained in the database with a restricted domain classification.

---

## 2. Compiler Scaling and Topology Failures

### 2.1. Classical Verification Ceiling (> 20 Qubits)
*   **Failure Regime**: Circuits with qubit counts $N > 20$.
*   **Mechanism**: Motif validation relies on classical statevector simulation to verify unitary equivalence:
    $$U(M_{\text{in}})^\dagger U(M_{\text{out}}) \approx I$$
*   **Technical Cause**: The memory required to store the statevector scales exponentially as $O(2^N)$. At 20 qubits, a single statevector requires 16 MB. At 30 qubits, it requires 16 GB, causing memory allocation errors on standard validation nodes.
*   **Mitigation Strategy**: **Recoverable**. For $N > 20$ qubits, QADE bypasses dynamic validator checks and relies exclusively on pre-validated motif databases. Future updates (Phase IX) plan to integrate Tensor Network contraction solvers (e.g. cuTensorNet) to support validation up to 40 qubits.

### 2.2. Large-Circuit Routing Overhead (e.g. QFT-20q, GHZ-20q)
*   **Failure Regime**: Sequential routing of multi-qubit gates on complex networks.
*   **Observed Degradation**: For QFT-20q on Heavy-Hex topologies, QADE increases the two-qubit gate count and depth compared to Qiskit Level 3.
*   **Technical Hypothesis**: QADE's `route_circuit` pass performs sequential look-ahead routing. When the qubit count is large ($N \ge 20$) and connectivity is sparse, sequential BFS routing of single gates creates long SWAP chains that propagate errors. Since the evolutionary search population size is small (n=4) due to compile-time constraints, the optimizer fails to find the global optimum in the routing search space.
*   **Mitigation Strategy**: Implement global placement constraints and partition the circuit into smaller, independently routeable blocks.

### 2.3. Sparser Topological Constraints (Heavy-Hex)
*   **Failure Regime**: Sparsely connected backends (e.g., IBM Brisbane, average degree $\approx 2.0$).
*   **Observed Degradation**: QADE uses more physical gates than Qiskit L3 to compile identical workloads on Heavy-Hex maps.
*   **Technical Hypothesis**: In Heavy-Hex layouts, physical connectivity is extremely constrained. Routing a multi-qubit gate between distant qubits requires routing along rigid linear paths. QADE's routing cost function heavily penalizes bad qubits (coherence decay), forcing the router to choose longer physical paths over higher-quality qubits. While this improves estimated physical fidelity on small circuits, on large circuits the accumulated gate error of extra SWAP operations outweighs the coherence benefit.
*   **Mitigation Strategy**: Dynamically adjust routing weights ($w_d$ and $w_c$) based on circuit depth. If the estimated gate depth exceeds a threshold, the router should shift weight toward gate-count minimization ($w_d$).
