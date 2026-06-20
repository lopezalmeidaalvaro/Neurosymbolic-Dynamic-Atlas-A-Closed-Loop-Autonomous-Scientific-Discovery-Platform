# Formal Verification Dossier

## 1. Executive Summary
This dossier outlines the formal mathematical verification architecture, Lean 4 compiler integrations, and LLM-guided tactic search systems within the mathematics domain. The engine formally verifies the semantic equivalence of quantum compiler transformations, guaranteeing correctness up to a global phase.

## 2. Purpose
The purpose of the formal verification system is to eliminate compilation compiler errors by checking transpilation passes against formal proofs in Lean 4, providing absolute guarantees of unitary equivalence.

## 3. Architecture
The proof generation and verification pipeline is structured as follows:

```
   [Abstract Quantum Circuit]
              |
              v (Auto-formalization)
   [Lean Theorem Definition]
              |
              v (MCTS / LLM Tactic Generator)
     [Lean 4 Compiler Loop] <-- Verification feedback
              |
              v (Proof Found)
    [Verified Safe Theorem]
```

### Core Subsystems
*   **Theorem Prover Orchestrator (`orchestrator/`)**: Coordinates input definitions and LLM tactic queries.
*   **Lean 4 Compiler Interface**: Invokes the local Lean 4 executable and extracts AST and goal state telemetry.
*   **MCTS Search Engine**: Traverses the proof state graph to find closing tactic sequences.

## 4. Methodology
*   **Auto-Formalization**: Translates circuit matrices and gate sequences into Lean 4 inductive types and theorem statements.
*   **Tree Search Exploration**: Utilizes Monte Carlo Tree Search (MCTS) guided by a language model policy to explore valid proof tactics (e.g., `simp`, `ring`, custom Clifford lemmas).
*   **AST Goal Parsing**: Deconstructs intermediate Lean compiler outputs to update active goal contexts for the prover agent.

## 5. Results
*   **Proof Trajectory Dataset**: Generated DPO preference datasets (JSONL format) logging successful vs. failed tactic decisions to align LLM policy networks.
*   **Lean Compiler Latency**: Single-proof verification loops complete within **$<1.2\text{ s}$** for basic equivalence transformations.

## 6. Validation
*   **Lean Compiler Verdict**: Proofs are validated exclusively by the local Lean 4 type-checker, ensuring no unproven assumptions or errors exist.
*   **Equivalence Soundness**: Lean theorems guarantee that the physical unitary matrix is preserved up to a global phase factor $e^{i\theta}$.

## 7. Limitations
*   **Toolchain Installation Dependency**: The system requires a local Lean 4 and Mathlib environment, making it environment-dependent.
*   **Search Space Explosion**: Proof search for non-Clifford circuits (e.g., arbitrary rotation angles) often exceeds maximum MCTS depth limits, resulting in `TIMEOUT` errors.

## 8. Future Work
*   **Full Mathlib Integration**: Moving custom matrix representations to canonical Mathlib matrix libraries.
*   **Inductive Proof Generalization**: Automatically proving general $N$-qubit scaling theorems for recursive circuits (e.g., QFT).

## 9. Source Documents
*   [FORMAL_VERIFICATION_DOSSIER.md (Original)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/mathematics/docs/FORMAL_VERIFICATION_DOSSIER.md)
*   [walkthrough_history.md (Consolidated)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/walkthrough_history.md)
