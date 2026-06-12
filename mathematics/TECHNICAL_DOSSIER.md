# TECHNICAL DOSSIER: Formal Verification Pipeline & Relational Knowledge Base

This document presents the architectural design, technical rationale, and intellectual property protection features of the `mathematics` formal verification engine (Phases 1, 2, 3 & 4).

---

## 1. Paradigm Shift: From Empirical AI to Deterministic Verification

Classical Deep Learning models and LLMs proposes solutions based on probabilistic approximations. In physics, quantum chemistry, and mathematics, these approximations are not sufficient. Hallucinations can lead to catastrophic failures.

Our architecture transitions from a **heuristic proposal engine** to a **deterministic validation system**. The AI model acts as a *hypothesis generator*, proposing candidates, laws, or equivalence relations. The `mathematics` pipeline translates these suggestions into proof goals in the **Lean 4 interactive theorem prover**. Once the Lean 4 compiler verifies the proof script without warnings or unsolved goals, the hypothesis is mathematically certified.

```
+-----------------------------------+
|      AI Hypothesis Generator      |  --> Probabilistic / Heuristic
+-----------------------------------+
                  |
                  v  (ProofGoalIR / data contracts)
+-----------------------------------+
|      Lean 4 Verification Engine   |  --> Deterministic / Absolute Proof
+-----------------------------------+
```

---

## 2. Decoupled Processing: Runtime Execution vs Semantic Parsing

To avoid compiling-environment pollution and code injection risks, the pipeline isolates compilation from semantic interpretation:

- **Process Sandboxing (`LeanRuntime`)**: `LocalLeanRuntime` operates as an independent execution boundary. It manages process lifecycles, resource consumption timeouts, and platform-specific subprocess invocations, writing scripts to volatile temporary files.
- **Decoupled Parser (`LeanOutputParser`)**: Assigning verification states solely based on process exit codes is fragile. Lean 4 may exit with code 0 while outputting warnings or `sorry` placeholders. Conversely, minor syntax discrepancies or warning outputs might return non-zero codes. The `LeanOutputParser` reads the exact stream output (`stdout` and `stderr`) to identify the presence of unresolved logical goals or skipped assumptions.

This isolation guarantees that changes to Lean compiler internals will only require updates to the parser layer, leaving the runtimes completely untouched.

---

## 3. Relational Knowledge Normalization & Cascade Invalidation Analysis

Our knowledge base replaces loosely-structured JSON structures with a fully normalized SQLite schema:
- **`theorems`**: Contains immutable metadata, logical declarations, raw proof scripts, and validation states.
- **`theorem_dependencies`**: Maps many-to-many dependency graphs.

### Invalidation and Cascade Analysis
In a formal library, theorems are built on top of other theorems. If an upstream theorem is modified or found to have an unsound axiom, all downstream theorems that depend on it are immediately suspect. 
By maintaining a normalized `theorem_dependencies` table, we can instantly trace the dependency tree:
- Finding dependents: A simple query `SELECT theorem_id FROM theorem_dependencies WHERE dependency_id = ?` returns the immediate dependents of a theorem.
- Recursive traversal: We can query the transitive closure to perform impact analysis, invalidate downstream verified flags in cascade, or flag them for automatic re-evaluation by the verifier.

---

## 4. Cryptographic Proof Sealing & Intellectual Property Protection

To establish a defensible, audit-ready chain of custody for discovered formulas, each proof is cryptographically sealed:

1. **SHA-256 Content Hashing**: The `FormalKnowledgeBase` automatically computes a SHA-256 hash of the verification script (`proof_hash`).
2. **Immutable Seal**: Once a proof is compiled and marked as `verified = 1`, its hash represents a unique fingerprint of the mathematical certificate.
3. **Auditability**: Any tampering with the local proof script or theorem statement immediately invalidates the hash consistency check. This seal provides concrete, mathematically certified proof of discovery that can be stamped on a distributed ledger or submitted to patent/copyright authorities to secure deep-tech intellectual property.

---

## 5. Rule-Based Translation: Deterministic Strategy Pattern (Phase 2)

Generating proof scripts and theorem declarations directly from empirical heuristics introduces high variance and execution instability. Phase 2 introduces a **deterministic, rule-based Strategy pattern translation layer**:

- **Strategy Pattern (`TranslationRule`)**: Individual conversion strategies (e.g. `DoubleHadamardRule`) are isolated as rule objects inheriting from `TranslationRule`. This guarantees 100% reproducibility since translation is fully deterministic and independent of model temperatures or hallucination boundaries.
- **Rule Registry (`RuleRegistry`)**: Rules are dynamically registered, allowing the translation mapper to match incoming intermediate representations to the appropriate proof script template.
- **Traceable Linage Mapping**: By copying the unique `motif_id` of the empirical quantum representation into the `source_reference` field of the resulting `ProofGoalIR`, the translator preserves the direct logical linkage from heuristic discovery to compiler validation.
- **Deferred Heuristics**: Direct LLM tactic-generation is intentionally postponed until a closed, deterministic library of axioms and structures has been verified. Establishing this rule-based baseline guarantees a solid foundation before introducing probabilistic tactic search agents.

---

## 6. Hybrid Translation Chain: Chain of Responsibility Pattern (Phase 3)

In Phase 3, we implement a **Chain of Responsibility** orchestration pipeline to combine the speed/predictability of deterministic rules with the flexibility of generative models:

- **`DeterministicHandler` (First Link)**: Resolves the goal immediately if there is a registered strategy rule (e.g. `DoubleHadamardRule`). This guarantees that known equivalence classes are validated instantaneously with zero LLM inference cost.
- **`LLMHandler` (Fallback Link)**: If the registry yields a mismatch (`NoMatchingRuleError`), the request falls back to the generative translator. This handler runs the `AutoFormalizationLoop` implementing **Test-Time Compute** (iterative compiler-feedback repair), querying the LLM and passing Lean compiler trace tracebacks as correction prompts up to a maximum number of attempts.
- **Provenance Auditing**: Verified proofs are persisted in the database with their respective source lineage metadata (`DETERMINISTIC_RULE` or `AUTO_FORMALIZED`), allowing deep audits on which patents/theorems are backed by hard translation rules versus heuristic search.

---

## 7. Robust JSON Extraction & RL Trajectory Collection

Generative models often wrap outputs inside markdown fences or add explanatory conversational preambles. To ensure data exchange stability:

- **Regex-based Parser**: The `extract_json_object` parser uses regular expression patterns to isolate the JSON string block from raw text, resolving decoding issues dynamically.
- **RL Trajectory Logs**: Every formalization attempt is recorded as a structured `FormalizationAttempt` containing the generated script, status, and compiler feedback. This collection of attempts serves as a **dataset of repair trajectories**. These trajectories can be directly ingested by a Reinforcement Learning from Compiler Feedback (RLCF) pipeline in Phase 4 to fine-tune the generator, teaching it how to learn from Lean error logs.

---

## 8. Heuristic Tree Search: Monte Carlo Tree Search Prover (Phase 4)

For complex theorems that cannot be solved in a single generative step, Phase 4 integrates a **Monte Carlo Tree Search (MCTS)** prover utilizing compiler feedback loop diagnostics:

### PUCT Selection Algorithm
During tree traversal, next states are selected by balancing exploitation (estimated reward) and exploration (LLM prior probabilities) using the **PUCT (Predictor Upper Confidence bounds applied to Trees)** formula:

$$U(s, a) = Q(s, a) + c_{puct} \cdot P(s, a) \cdot \frac{\sqrt{N(s)}}{1 + N(s, a)}$$

Where:
- $Q(s, a) = \frac{W(s, a)}{N(s, a)}$ is the action value (estimated reward).
- $P(s, a)$ is the prior probability of tactic $a$ at state $s$ predicted by the LLM.
- $N(s)$ is the visit count of the parent node.
- $N(s, a)$ is the visit count of the child node.
- $c_{puct}$ is a constant scaling exploration (defaults to 1.4).

### Strict Compiler-Feedback Rewards
Unlike standard game-playing MCTS where rewards are only given at terminal game states, our prover assigns strict, compiler-driven intermediate rewards:
- **`VERIFIED` (Success)**: $+1.0$ (early termination threshold).
- **`UNSOLVED_GOALS` (Logical progress)**: $+0.1$ (incentivizes paths that compile successfully but leave open sub-goals).
- **`COMPILATION_ERROR` / `TIMEOUT` / `INTERNAL_ERROR` (Syntactic/semantic crash)**: $-1.0$ (heavily penalizes nodes generating invalid tactics, pruning those branches immediately).

### RL Search Telemetry Database (`mcts_runs`)
Offline reinforcement learning requires high-fidelity search trajectories. The pipeline persists every MCTS search campaign into the `mcts_runs` table. Recording both successful and failed simulation trees (`total_simulations`, `success`, `nodes_explored`) provides the telemetry logs necessary to train downstream policy models (Fase 5) using policy-gradient or value-estimation techniques.
