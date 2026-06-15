# Emergent Chirality Framework for Hayward-LQC

## 1. Introduction and Objectives
A defining property of the Standard Model is chirality: the weak interaction ($SU(2)_L$) couples exclusively to left-handed fermions. In continuous field theory, chirality is postulated, while in lattice field theory, the Nielsen-Ninomiya theorem makes chiral fermions difficult to represent (fermion doubling problem). To achieve a complete pregeometric reconstruction, we must derive chiral structure without assuming space-time:
$$I_0 \Longrightarrow SU(2)_L \text{ chiral couplings}$$

This document defines a relational notion of orientation on the RQB network, formulates spontaneous left/right symmetry breaking, derives chiral fermions, and demonstrates compatibility with the Nielsen-Ninomiya theorem.

---

## 2. Relational Orientation and Parity Breaking

In a discrete pregeometric graph, space does not exist, and thus classical left- and right-handedness are undefined. However, we can define a topological equivalent:

### 2.1 Relational Graph Orientation
For a three-stranded braided ribbon representing a fermion (Type III defect), we define chirality using the crossing sign invariant. Let the braid be represented by a generator sequence $B = \sigma_{i_1}^{s_1} \sigma_{i_2}^{s_2} \dots \sigma_{i_k}^{s_k}$, where $s_k \in \{+1, -1\}$ denotes over-crossings and under-crossings.
-   **Chirality ($\chi$)**: Defined as the sum of the crossing signs:
    $$\chi(B) = \sum_{j=1}^{k} s_j$$
    A braid $B$ and its mirror image $B^*$ (obtained by replacing all $s_j \to -s_j$) have opposite chirality ($\chi(B^*) = -\chi(B)$). They are topologically non-isotopic, meaning they cannot be deformed into each other without cutting the ribbons.

### 2.2 Spontaneous Left/Right Symmetry Breaking
The pregeometric Liouvillian $\mathcal{L}_{\text{pre}}$ is parity-symmetric, meaning it is invariant under the mirror reflection of all braids:
$$[\mathcal{P}, \mathcal{L}_{\text{pre}}] = 0$$

However, when the network cools and transitions to its low-energy phase (forming spatial geometry), the vacuum state $\rho_{\text{vac}}$ falls into one of two degenerate configurations that break this parity. The asymmetric vacuum expectation value of the relational bonds creates a chiral background:
$$\langle \chi(B_{\text{vac}}) \rangle = \chi_0 \neq 0$$

This background couples asymmetric gauge fields to the left-handed sector ($SU(2)_L$), while leaving the right-handed sector uncoupled, explaining the parity violation of the weak interaction.

---

## 3. Chiral Fermions and Chiral $SU(2)_L$ Coupling

The emergent Dirac field $\psi(x)$ is decomposed into left-handed and right-handed Weyl spinors:
$$\psi(x) = \psi_L(x) + \psi_R(x)$$

where:
-   $\psi_L = P_L \psi = \frac{1 - \gamma_5}{2} \psi$ corresponds to braids with negative relational chirality ($\chi < 0$).
-   $\psi_R = P_R \psi = \frac{1 + \gamma_5}{2} \psi$ corresponds to braids with positive relational chirality ($\chi > 0$).

Because the $SU(2)$ weak gauge bosons emerge from the spin-rotation automorphisms of the $\mathbb{C}^2$ qubit state spaces, and the chiral vacuum $\chi_0$ alters the transport properties of the connections, only the left-handed Weyl spinors $\psi_L$ participate in the weak gauge transitions. The right-handed spinors $\psi_R$ are sterile with respect to $SU(2)$ weak interactions.

---

## 4. Compatibility with Nielsen-Ninomiya Theorem

The **Nielsen-Ninomiya Theorem** states that any local, hermitian, translationally invariant fermion theory on a regular spatial lattice must contain an equal number of left-handed and right-handed species (fermion doubling), preventing a pure chiral gauge theory.

### 4.1 Bypassing the Doubling Problem on RQB Graphs
The RQB-Event substrate naturally bypasses the theorem because it violates its core mathematical assumptions:
1.  **Lack of translational symmetry**: The RQB network is a dynamic, random relational graph, not a regular translationally invariant lattice. The concept of a continuous Brillouin zone (momentum torus $T^3$) does not exist at the pregeometric level.
2.  **Locality violations in pregeometry**: Although the interactions in the pregeometric Liouvillian are relationally local (acting on adjacent nodes), the emergent spatial embedding can map relationally adjacent nodes to distant spatial points (non-locality in the emergent space).

Since the theorem's topological requirements are violated, chiral fermions can propagate stably on the RQB network without generating doublers, allowing the weak force to couple exclusively to $\psi_L$.

---

## 5. Evaluation and Verdict

To Deliverable 1 Question: *¿Cómo surge la quiralidad $SU(2)_L$ y cómo se evade el teorema de Nielsen-Ninomiya en la red RQB?*

**Verdict**:
**Chirality arises from the crossing signs of braided ribbons, and parity is spontaneously broken by the asymmetric vacuum state of the network connections. The Nielsen-Ninomiya theorem is bypassed because the RQB graph is dynamic and lacks translational lattice symmetry, preventing the formation of fermion doublers**. This allows a consistent representation of chiral $SU(2)_L$ weak interactions directly from information-theoretic structures.

---

## 6. Metrics and Score

*   **CHIRALITY_SCORE**: `74`

The score of `74/100` reflects that the ribbon braid model provides a highly consistent topological definition of chirality and evades the doubling problem. The remaining challenge is to show how the spontaneous parity breaking occurs dynamically in numerical simulations of graph updates.
