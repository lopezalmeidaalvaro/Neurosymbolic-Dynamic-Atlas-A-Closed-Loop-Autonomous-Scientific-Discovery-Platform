# Mathematics Domain

This domain is structured as an isolated, deterministic formal verification assembly line. It handles intermediate representations, deterministic and LLM-guided translations to Lean 4, tree-search proving (MCTS), and database persistence of verified theorems.

## Assembly Line Architecture

```text
   +------------------------------+
   |  Empirical Discovery Engine  |
   +--------------+---------------+
                  |
                  v
       [ir_core: Pydantic IR]
                  |
                  v
       [orchestrator: Chain]
                  |
         +--------+--------+
         |                 |
         v                 v
   [Deterministic]    [LLM-Guided]
         |                 |
         v                 v
     [leanlib]    [prover: MCTS Tactics]
         |                 |
         +--------+--------+
                  |
                  v
      [verifier: Lean 4 runtime]
                  |
                  v
      [knowledge_base: SQLite]
```

## Folder Structure

- **`ir_core/`**: Immutable Intermediate Representations.
- **`translator/`**: Deterministic rule-based translation engine.
- **`llm_translator/`**: Probabilistic translator and iterative repair loop.
- **`prover/`**: Monte Carlo Tree Search prover.
- **`orchestrator/`**: Chain of Responsibility coordinator.
- **`verifier/`**: Lean 4 proof assembly & runtime.
- **`knowledge_base/`**: Relational SQLite formal library.
- **`leanlib/`**: Lean 4 base definitions and proof axioms.
- **`docs/`**: Consolidated dossiers and reports.
- **`tests/`**: Unit test suites.

## Consolidated Dossiers

Refer to the domain documentation under `mathematics/docs/`:
- **[Knowledge Index](docs/INDEX.md)**: Navigation hub for the domain.
- **[FORMAL_VERIFICATION_DOSSIER](docs/FORMAL_VERIFICATION_DOSSIER.md)**: Proof system configurations, Lean 4 representations, and LLM guidance architecture.
- **[THEOREM_VALIDATION_DOSSIER](docs/THEOREM_VALIDATION_DOSSIER.md)**: Lean compiler integration, AST parsing, and preference alignment preference alignment datasets generation.
