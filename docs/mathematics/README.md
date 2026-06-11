# Mathematics: Formal Verification of Quantum Equivalences

## 1. Overview
The Mathematics domain centers on formal verification methods applied to quantum compilers. As compilers grow in complexity and utilize stochastic search heuristics (such as QADE's evolutionary algorithms and SABRE routing), verifying compilation correctness becomes critical. 

This research agenda focuses on building formal proofs of equivalence between the input quantum circuit ($C_{\text{in}}$) and the output compiled circuit ($C_{\text{out}}$), establishing provably correct compilation passes that guarantee preservation of the underlying quantum state vector.

---

## 2. Research Focus & Methods
*   **Symbolic Equivalence Proofs**: Developing algebraic simplification rules for ZX-Calculus and proving their soundness using formal proof assistants (such as Coq or Lean).
*   **Equivalence Checking Latency**: Constructing scalable algorithms for checking state-vector equivalence ($F \ge 0.9999$) that scale sub-exponentially for structured circuits.
*   **Motif Rewrite Verification**: Formally proving that motif translation libraries do not introduce phase errors or relative state deviations.

---

## 3. Documents in this Folder
*   [INDEX.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/mathematics/INDEX.md): Index navigating mathematics research papers.
*   [TECHNICAL_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/mathematics/TECHNICAL_DOSSIER.md): Technical position dossier on quantum formal verification.
