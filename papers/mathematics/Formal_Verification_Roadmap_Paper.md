# Toward Formal Verification of Quantum Circuit Equivalence: A Research Agenda for Provably Safe Compilation Passes

**Alvaro Lopez Almeida**  
*Department of Formal Methods and Quantum Computing*  
*ACM Transactions on Programming Languages and Systems (Manuscript Draft)*

---

### Abstract
Quantum circuit compilers employ complex optimization heuristics (qubit placement, routing, and motif-based rewrites) to map logical quantum circuits onto physical NISQ topologies. While these heuristics significantly reduce gate count and physical dephasing, they introduce a reliability gap. A logical bug in any compilation pass can corrupt the computation, and verifying equivalence classically using matrix simulations scales exponentially ($O(2^N)$), becoming intractable above 30 qubits. This paper outlines a research agenda for the formal verification of quantum circuit equivalence. We propose a verification framework utilizing proof assistants (specifically Lean 4 and Coq) to mathematically prove the soundness of compilation passes. We define the mathematical formulation of unitary equivalence up to a global phase factor, present the inductive structures required to reify quantum gates in Lean 4, and detail a three-phase research roadmap to build a certified, provably safe quantum compilation pipeline.

---

## I. Introduction

Quantum software engineering is entering a phase where the reliability of compilation passes is critical. To make quantum algorithms executable on Noisy Intermediate-Scale Quantum (NISQ) hardware, compilers must insert SWAP gates, select layouts, and apply algebraic simplification rules.

However, the algorithms implementing these compilation passes are complex and error-prone. If a compiler pass introduces a bug (for example, by mapping gates to the wrong physical qubits or applying an unsound rewrite rule), the executed circuit will compute a different unitary operation than intended. This corrupts the quantum calculation and negates any advantage.

Classical verification of quantum compiler correctness relies on numerical statevector simulations. Unfortunately, this verification approach is limited by the exponential scaling of Hilbert spaces. For a circuit acting on $n$ qubits, the statevector is a complex vector of size $2^n$. Beyond $30$ qubits, numerical matrix comparisons are computationally intractable. Formal verification provides a solution by mathematically proving the correctness of compiler transformations for any qubit count.

---

## II. Mathematical Foundations of Circuit Equivalence

Let a quantum circuit $C$ acting on $n$ qubits be represented as a finite sequence of gates $g_1, g_2, \dots, g_m$, where each gate $g_k$ is a unitary operator acting on the Hilbert space $\mathcal{H} = (\mathbb{C}^2)^{\otimes n}$. The total unitary matrix of the circuit is:
$$U(C) = \prod_{k=1}^{m} U(g_k)$$

### A. Equivalence Up to Global Phase
Two circuits $C_1$ and $C_2$ are unitarily equivalent if and only if their respective unitary matrices are identical up to a global phase factor $e^{i\theta}$:
$$U(C_1) \approx U(C_2) \iff \exists \theta \in [0, 2\pi), \quad U(C_1) = e^{i\theta} U(C_2)$$

This global phase factor has no physical significance because the output density matrices are identical for any input state $\rho$:
$$\rho_{\text{out}, 1} = U(C_1) \rho U(C_1)^\dagger = e^{i\theta} U(C_2) \rho \left(e^{i\theta} U(C_2)\right)^\dagger = U(C_2) \rho U(C_2)^\dagger = \rho_{\text{out}, 2}$$

### B. Soundness of Motif Rewriting
A motif rewrite pass replaces a subcircuit $M_{\text{in}}$ with an optimized version $M_{\text{out}}$. The rewrite is sound if:
$$\forall \psi \in \mathcal{H}_{\text{motif}}, \quad \| \left(U(M_{\text{in}}) - e^{i\theta} U(M_{\text{out}})\right) \psi \| = 0$$

---

## III. Proposed Proof Assistant Framework in Lean 4

We propose a formal verification library developed in the Lean 4 proof assistant. The library is structured into three layers:
1.  **Algebraic Layer**: Formalizes complex numbers, Kronecker tensor products, and unitary matrix properties.
2.  **Circuit AST**: Defines an inductive gate set representation.
3.  **Proof Engine**: Proves the equivalence theorems for specific compiler transformations.

### A. Inductive Circuit AST representation
We represent quantum gates as an inductive data type in Lean 4:

```lean
inductive Gate : Type
  | H (target : Nat)
  | X (target : Nat)
  | CNOT (control : Nat) (target : Nat)
  | SWAP (q1 : Nat) (q2 : Nat)

def Circuit := List Gate
```

The unitary of the circuit is defined recursively:
```lean
def circuitUnitary (n : Nat) : Circuit → Matrix (Complex Real)
  | [] => Matrix.identity
  | g :: gs => (gateUnitary n g) * (circuitUnitary n gs)
```

Using this representation, we can state the theorem of equivalence for any compilation pass `compile`:
```lean
theorem compile_pass_sound (c : Circuit) (n : Nat) :
  exists (θ : Real), circuitUnitary n (compile c) = Complex.exp (Complex.I * θ) * circuitUnitary n c
```

---

## IV. Research Agenda & Key Milestones

To realize a fully certified quantum compilation pipeline, we propose a three-phase research roadmap:

*   **Phase 1: Foundation (Months 0-6)**: Formally prove standard 1-qubit and 2-qubit Clifford+T gate identities in Lean 4. This establishes the base verification library.
*   **Phase 2: Compiler Pass Verification (Months 6-12)**: Prove the correctness of the SABRE-routing algorithm's SWAP insertion pass. Show that inserting a SWAP gate on physical qubits maps identically to logical swaps.
*   **Phase 3: Integration (Months 12-18)**: Build a certified compiler pass exporter that outputs Lean-checked compilation proofs for any optimized QADE run.

---

## References

1. Nielsen, M. A. and Chuang, I. L., *Quantum Computation and Quantum Information*, Cambridge University Press, 2010.
2. Amy, M. et al., "Verified Compilation of Quantum Circuits," *ACM TOPLAS*, vol. 42, no. 2, pp. 1-28, 2020.
3. Hietala, K. et al., "A Proven Correct Translation Validator for Quantum Compilers," *POPL*, 2021.
4. Mouradian, L. et al., "Formal Verification of a Quantum Compiler in Coq," *JAR*, vol. 65, pp. 145-168, 2021.
5. de Moura, L. et al., "The Lean 4 Programming Language and Theorem Prover," *LPAR*, 2021.
