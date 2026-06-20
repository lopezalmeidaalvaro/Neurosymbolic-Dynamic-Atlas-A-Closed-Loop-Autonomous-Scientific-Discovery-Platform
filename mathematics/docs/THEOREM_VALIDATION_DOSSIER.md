# Theorem Validation Dossier

## 1. Executive Summary
This dossier outlines the theorem validation loops, metrics tracking systems, and preference alignment dataset generation workflows in the mathematics domain. It details the Lean 4 compiler feedback integration that validates proof scripts and parses proof goal states.

## 2. Purpose
The purpose of the theorem validation pipeline is to provide a programmatic interface to the Lean 4 compiler, enabling autonomous proof search agents to receive compile-time errors, goal statuses, and tactic verification verdicts.

## 3. Architecture
The validation system monitors compile-time execution metrics:

```
   [Tactic Input stream]
             |
             v
   [Lean 4 AST Parser]
             |
             v
  [Goal State Extractor]
             |
             v
    [Metrics Collector] ---> [DPO Preferences JSONL]
```

*   **Compiler Interface**: Runs Lean 4 checks on generated `.lean` source files.
*   **AST Parser**: Parses Lean compiler outputs to inspect unresolved goals or error locations.
*   **Metrics Collector**: Records MCTS depth, compilation latencies, and tactical success metrics.

## 4. Methodology
*   **Lean 4 Compiler Checks**: Programmatically invokes `lean --run` or interactive server interfaces to compile proof scripts.
*   **Proof State Extraction**: Evaluates the Lean compiler goal state to confirm that the `theorem` declaration has been successfully closed (signified by "no goals" and zero compiler warnings).
*   **Tactic Preference Metrics**: Compiles chosen tactic trajectories alongside rejected branches to train policy models using Direct Preference Optimization (DPO).

## 5. Results
*   **Dataset Output**: Created versioned preference alignment datasets (JSONL format) containing verified proof trajectories, serving as the training baseline for auto-formalization models.
*   **Verification Classification**: Proves theorems under a binary verdict schema: `PROVEN` (closed proof) vs. `UNPROVEN` (parse error, type mismatch, or open goals).

## 6. Validation
*   **AST Integrity Verification**: Lean AST parser outputs are validated against formal mock files to ensure no goals are bypassed by `sorry` or `admit` tactics.
*   **Type-checking Soundness**: The Lean kernel validates the syntactic correctness of the proof transitions.

## 7. Limitations
*   **Compiler Timeout Sensitivity**: Heavy proofs with deeply nested algebraic expansions can trigger compiler timeouts, falsely classifying correct tactics as unproven.
*   **Concurrency Overhead**: Running multiple parallel Lean 4 compilation processes during MCTS loops introduces significant CPU and file-system I/O overhead.

## 8. Future Work
*   **Lean Server Session Caching**: Implementing interactive Lean server sessions (`lean --server`) to bypass the startup latency of invoking the compiler executable for every step.
*   **Adversarial Tactic Generation**: Generating synthetic invalid proofs to train the policy model's error rejection capability.

## 9. Source Documents
*   [THEOREM_VALIDATION_DOSSIER.md (Original)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/mathematics/docs/THEOREM_VALIDATION_DOSSIER.md)
*   [task_history.md (Consolidated)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/task_history.md)
