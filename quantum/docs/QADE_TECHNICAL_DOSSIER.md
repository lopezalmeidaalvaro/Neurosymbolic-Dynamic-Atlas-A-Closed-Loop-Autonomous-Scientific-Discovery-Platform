# QADE Technical Dossier

## 1. Executive Summary
The Quantum Algorithm Discovery Engine (QADE) is a hardware-aware compilation and optimization suite designed to maximize quantum execution fidelity on noisy intermediate-scale quantum (NISQ) processors. By leveraging daily physical calibration parameters, QADE structures its compiler passes—including graph-based qubit placement, evolutionary gate reductions, and SABRE routing—to place active circuits on the highest-performing physical qubits.

## 2. Purpose
Standard compilers transpile quantum circuits using topological graphs and general heuristics, ignoring the physical noise asymmetry of the target QPU. QADE's purpose is to resolve this limitation by implementing a dynamic, calibration-aware optimization loop that significantly improves Hellinger fidelity and reduces physical gate counts on actual quantum processors.

## 3. Architecture
QADE is structured as a multi-stage compilation pipeline:

```
   +------------------+
   | Input OpenQASM   |
   +--------+---------+
            |
            v
   [Stage A: Parsing & Analysis]
            |
            v
   [Stage C: Fidelity-Aware Qubit Placement]  <-- Subgraph search on coupling map
            |
            v
   [Stage E: Evolutionary Optimization]       <-- Guided by quantum statevector sandbox
            |
            v
   [Stage G: Coherence-Aware Routing]         <-- SABRE with dynamic weights
            |
            v
   [Stage H: Final Transpilation & Cleanup]
            |
            v
   +--------+---------+
   | Output OpenQASM  |
   +------------------+
```

### Core Subsystems
*   **Qiskit Adapter (`qiskit_adapter.py`)**: Normalizes input gates (`SX` to `RX(π/2)`, preserving `ECR`, mapping `BARRIER`).
*   **Placement Engine (`qubit_placement.py`)**: Computes layout via Fidelity-Aware Subgraph Search.
*   **Routing Subsystem (`routing_engine.py`)**: Performs coherence-aware SABRE routing.
*   **Genetic Sandbox (`evolution/`)**: Executes evolutionary search for gate simplification on systems $\le 20$ qubits.

## 4. Methodology
*   **Stage C Qubit Placement**: Evaluates physical coupling maps to find high-coherence subgraphs. It bypasses low $T_1$ or high readout error qubits globally rather than greedily.
*   **Stage E Genetic Search**: For active systems of size $\le 20$ qubits, a genetic search is executed in the `QiskitQuantumSandbox` (simulated via statevector targets). Supported gates (`SX`, `ECR`, `BARRIER`, `ID`) are normalized and mutated, testing correctness against the target statevector.
*   **Stage G SABRE Routing**: Autotunes routing weights ($w_d/w_c$) dynamically based on circuit depth (e.g., $w_d = 0.8$, $w_c = 0.2$ for shallow circuits) to minimize swap gate count and coherence decay.
*   **PyZX Clifford+T Reductions**: Translates the circuit into PyZX graph form, simplifies it using rule-based transformations, and translates it back.

## 5. Results
*   **Gate Reduction**: Achieves an average gate reduction of **-85.9%** compared to standard Qiskit L3 transpilation across a 2–30 qubit suite.
*   **Compilation Speed**: Operates with a mean compilation latency of **429 ms** (due to genetic search and equivalence validation steps).

## 6. Validation
*   **Born Rule / Statevector Equivalence**: Unidad and semantic correctness are verified by comparing the final compiled statevector or unitary matrix against the input.
*   **Equivalence Safeguards**: `verify_equivalence_qiskit()` serves as a fallback path. If PyZX optimization or routing introduces a fidelity drop or drops native gates, QADE rejects the optimization and falls back to a safe Level 1 transpiled baseline.
*   **Overhead Audit Filter**: Optimization passes are rejected if they result in an increased gate count compared to the pre-optimization step.

## 7. Limitations
*   **Classical Simulation Limit**: Verifying quantum states classically requires calculating full statevectors, which is memory-constrained to circuits of $\le 20$ qubits. Above this limit, QADE bypasses evolutionary mutation and utilizes pre-validated motif libraries.
*   **Compilation Overhead**: Latency is significantly higher (429 ms) than standard transpilation (37 ms), making it less suitable for real-time interactive workloads.

## 8. Future Work
*   **Dynamic Calibration Feeds**: Implementing real-time API integrations to fetch live QPU calibration parameters immediately prior to compilation.
*   **API-Key SaaS Portal**: Developing a multi-tenant FastAPI REST endpoint with secure X-API-Key header verification for enterprise routing.

## 9. Source Documents
*   [QADE_TECHNICAL_DOSSIER.md (Original)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/docs/QADE_TECHNICAL_DOSSIER.md)
*   [QADE_COMPILER_DOSSIER.md (Original)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/docs/QADE_COMPILER_DOSSIER.md)
*   [PHASE8_CORE_DECOUPLING_REPORT.md (Consolidated)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/docs/archive/PHASE8_CORE_DECOUPLING_REPORT.md)
