# Formal Verification of Quantum Circuits: Technical Dossier & Research Agenda

Audience: Funding bodies (EIC Accelerator, CDTI, NEOTEC), academic quantum computing groups, and formal methods researchers.

---

## 1. Executive Summary

This dossier outlines the research agenda and formal formulation of a verification framework designed to guarantee the equivalence of quantum circuits before and after compilation. 

As quantum compilers (such as QADE, Qiskit, and TKET) implement increasingly aggressive heuristic optimization passes (e.g. qubit routing, placement, and motif rewriting), checking correctness via classical simulation becomes computationally intractable ($O(2^N)$ space complexity). 

We propose a formal verification roadmap utilizing proof assistants (such as Lean 4 or Coq) to mathematically prove the soundness of compilation passes, ensuring that optimized circuits are structurally and unitarily equivalent to their original specifications.

---

## 2. Problem Statement: The Compilation Reliability Gap

Quantum compilation involves mapping an idealized, layout-independent quantum circuit to physical hardware constraints. This process consists of three major steps:
1.  **Logical Simplification**: Applying algebraic rules (e.g. ZX-calculus reductions, motif substitution) to decrease gate count.
2.  **Physical Placement**: Selecting a subset of physical qubits on the hardware coupling graph to map the logical qubits.
3.  **Physical Routing**: Inserting SWAP gates to satisfy physical adjacency requirements for two-qubit gates.

If any of these passes contains a logical bug, the compiled circuit will execute a different unitary operation than intended, corrupting the computation. 

Since verifying unitary equivalence classical-simulations is limited to $\approx 30$ qubits, formal verification provides the only path to guarantee correctness for large-scale circuits.

---

## 3. Mathematical Formulation of Circuit Equivalence

Let a quantum circuit $C$ acting on $n$ qubits be represented as a sequence of gates $g_1, g_2, \dots, g_m$, where each gate $g_k$ is a unitary operator acting on the Hilbert space $\mathcal{H} = (\mathbb{C}^2)^{\otimes n}$. The total unitary representation of the circuit is:
$$U(C) = \prod_{k=1}^{m} U(g_k)$$

### 3.1 Unitary Equivalence Up to Global Phase
Two circuits $C_1$ and $C_2$ are unitarily equivalent if and only if their respective unitary matrices are identical up to a global phase factor $e^{i\theta}$:
$$U(C_1) \approx U(C_2) \iff \exists \theta \in [0, 2\pi), \quad U(C_1) = e^{i\theta} U(C_2)$$

In terms of density matrices, for any initial state $\rho$, the output states must be identical:
$$\rho_{\text{out}, 1} = U(C_1) \rho U(C_1)^\dagger = e^{i\theta} U(C_2) \rho \left(e^{i\theta} U(C_2)\right)^\dagger = U(C_2) \rho U(C_2)^\dagger = \rho_{\text{out}, 2}$$

### 3.2 Verification of Motif Rewriting
A motif rewrite replaces a subcircuit $M_{\text{in}}$ with an optimized version $M_{\text{out}}$. The rewrite pass is proven sound if:
$$\forall \psi \in \mathcal{H}_{\text{motif}}, \quad \| \left(U(M_{\text{in}}) - e^{i\theta} U(M_{\text{out}})\right) \psi \| < \epsilon$$
For exact compilers, we require $\epsilon = 0$. For approximate compilers (which trade small amounts of fidelity for significant gate reduction), $\epsilon > 0$ defines the error bound.

---

## 4. Formal Verification Architecture in Lean 4

The proposed research roadmap targets the implementation of a Lean 4 library containing:
1.  **Formal Hilbert Space Model**: Reifying complex vector spaces, Kronecker tensor products, and unitary operators.
2.  **Circuit AST**: Representing quantum circuits as an inductive data type in Lean.
3.  **Pass Soundness Theorems**: Proving that if $C_{\text{opt}} = \text{compile}(C)$, then $U(C) \approx U(C_{\text{opt}})$.

```
+-------------------------------------------------------------+
|                     Lean 4 Proof Assistant                  |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| 1. Hilbert Space Theories: Complex Matrices, Kronecker   |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| 2. Circuit AST: Inductive Gate Set (X, Y, Z, H, CNOT, SWAP) |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| 3. Proof of Pass Equivalence: compile(C) =~= C              |
+-------------------------------------------------------------+
```

### 4.1 Example Inductive Definition of Circuits in Lean 4
```lean
inductive Gate : Type
  | H (target : Nat)
  | X (target : Nat)
  | CNOT (control : Nat) (target : Nat)
  | SWAP (q1 : Nat) (q2 : Nat)

def Circuit := List Gate

def gateUnitary (n : Nat) : Gate → Matrix (Complex Real)
  | Gate.H t => tensorPowerH n t
  | Gate.X t => tensorPowerX n t
  | Gate.CNOT c t => tensorPowerCNOT n c t
  | Gate.SWAP q1 q2 => tensorPowerSWAP n q1 q2

def circuitUnitary (n : Nat) : Circuit → Matrix (Complex Real)
  | [] => Matrix.identity
  | g :: gs => (gateUnitary n g) * (circuitUnitary n gs)
```

---

## 5. Research Roadmap & Key Milestones

*   **Milestone 1 (Month 0-6)**: Formally prove equivalence of 1-qubit and 2-qubit Clifford+T gate identities in Lean 4.
*   **Milestone 2 (Month 6-12)**: Prove the correctness of the SABRE-routing algorithm's SWAP insertion pass. Show that inserting a SWAP gate on physical qubits maps identically to logical swaps.
*   **Milestone 3 (Month 12-18)**: Build a certified compiler pass exporter that outputs Lean-checked compilation proofs for any optimized QADE run.
