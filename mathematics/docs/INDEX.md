# Mathematics Domain Knowledge Index

Welcome to the Mathematics Domain documentation hub. This index serves as the navigation hub for all formal verification and Lean theorem validation dossiers.

---

## 1. Directory Structure

All files under `mathematics/docs/` are listed below:

| File Name | Purpose | Ownership |
| :--- | :--- | :--- |
| [INDEX.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/mathematics/docs/INDEX.md) | Central navigation hub. | `mathematics` team |
| [FORMAL_VERIFICATION_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/mathematics/docs/FORMAL_VERIFICATION_DOSSIER.md) | Lean formalization strategies, circuit unitary proofs, and MCTS tactic search systems. | `formal_methods` leads |
| [THEOREM_VALIDATION_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/mathematics/docs/THEOREM_VALIDATION_DOSSIER.md) | Lean compiler integration, state parsing, and preference alignment (DPO) dataset generation. | `verification` leads |

---

## 2. Dependencies

The mathematics proof core is located under `mathematics/` and has the following dependencies:
*   **External dependencies**: Local Lean 4 installation, Mathlib package manager (`elan` and `lake` configurations).
*   **Compiler Interface**: Relies on direct filesystem shell execution bounds to run target verification tasks.

---

## 3. Recommended Reading Order

For formal verification specialists and proof systems developers, we recommend the following traversal:
1.  **Formalization Foundations**: Read [FORMAL_VERIFICATION_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/mathematics/docs/FORMAL_VERIFICATION_DOSSIER.md) to understand Lean-adapter mappings.
2.  **Verification Pipeline**: Read [THEOREM_VALIDATION_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/mathematics/docs/THEOREM_VALIDATION_DOSSIER.md) to understand tactic checks and dataset metrics collection.
