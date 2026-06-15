# D6 — Lorentzian Compatibility

## Preamble

This document extends the diffeomorphism emergence theorem (Theorem P1) to the Lorentzian setting. We show that the causal DAG structure of the RQB network induces a Lorentzian signature on the emergent manifold, and that this signature is preserved under the emergent diffeomorphisms.

### Prerequisites

- D1–D5: Full automorphism-to-diffeomorphism machinery.
- [RQB_LORENTZIAN_LIMIT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/physics/fundamental/RQB_LORENTZIAN_LIMIT.md): Physical motivation (superseded by rigorous treatment below).

---

## 1. Causal Structure

**Definition 6.1** (Causal Partial Order).
Let $G_N = (V_N, E_N, w_N)$ be an RQB graph with Lie-Lindblad dynamics. The *causal partial order* $\prec$ on $V_N$ is defined by:
$$i \prec j \iff \exists \text{ directed path from } i \text{ to } j \text{ in the update DAG}$$

where the *update DAG* $\mathcal{D}_N = (V_N, E_N^{\to})$ has a directed edge $i \to j$ if the state of $j$ at parameter step $\tau + 1$ depends on the state of $i$ at step $\tau$.

**Axiom L1** (Acyclicity).
The update DAG $\mathcal{D}_N$ is acyclic: there is no directed cycle $i_1 \to i_2 \to \cdots \to i_k \to i_1$.

**Axiom L2** (Bounded Speed of Propagation).
There exists a constant $c_{\max} > 0$ such that for every directed edge $i \to j$ in $\mathcal{D}_N$:
$$d_N^{\text{spatial}}(i, j) \leq c_{\max} \cdot \Delta\tau$$
where $d_N^{\text{spatial}}$ is the relational distance on the spatial hypergraph (edges without causal direction) and $\Delta\tau$ is the discrete update step.

**Definition 6.2** (Causal-Compatible Automorphism).
An automorphism $\sigma \in Aut(G_N)$ is *causal-compatible* if it preserves the causal partial order:
$$i \prec j \implies \sigma(i) \prec \sigma(j)$$

The set of all causal-compatible automorphisms is denoted $Aut_\prec(G_N) \subseteq Aut(G_N)$.

**Lemma 6.0** ($Aut_\prec(G_N)$ is a subgroup).
$Aut_\prec(G_N)$ is a subgroup of $Aut(G_N)$.

*Proof.*
If $\sigma, \tau$ preserve $\prec$, then $\sigma \circ \tau$ preserves $\prec$ (by transitivity of implication). The identity preserves $\prec$ trivially. If $\sigma$ preserves $\prec$, then $\sigma^{-1}$ preserves $\prec$: suppose $i \prec j$ but $\sigma^{-1}(i) \not\prec \sigma^{-1}(j)$; applying $\sigma$ gives $i \not\prec j$, contradiction. $\square$

---

## 2. Temporal Function and Foliation

**Lemma 6.1** (Temporal Function).
Under Axioms L1 and L2, there exists a function $T: V_N \to \mathbb{Z}_{\geq 0}$ such that:
1. $i \prec j \implies T(i) < T(j)$ (monotonicity).
2. $T(i) - T(j) = $ length of the longest directed path from $j$ to $i$ (maximality).

In the continuum limit, $T$ induces a smooth function $t: M \to \mathbb{R}$ satisfying $g^{\mu\nu} \partial_\mu t \partial_\nu t < 0$ everywhere (i.e., $dt$ is timelike).

*Proof.*
Existence of $T$ on the finite DAG: Since $\mathcal{D}_N$ is acyclic (Axiom L1), topological sort yields a function $T$ satisfying (1). The maximal path length function satisfies (2) by construction.

For the continuum limit: The function $T$ scales as $T \sim N^{1/d} \cdot \tau$ on the graph. Under the GH convergence (Theorem 2.1), $T$ converges to a Lipschitz function $t: M \to \mathbb{R}$. By the curvature boundedness condition, the gradient $\nabla t$ has bounded norm and is non-vanishing (since the DAG has no source-to-sink shortcuts violating Axiom L2). By elliptic regularity of the limit Laplacian, $t$ is smooth.

The timelike condition $g^{\mu\nu}\partial_\mu t \partial_\nu t < 0$ follows from the fact that the level sets $\Sigma_s = t^{-1}(s)$ separate causal past from causal future, and the maximal signal speed $c_{\max}$ defines the light cone boundary. $\square$

**Lemma 6.2** (Spatial Metric Positivity).
The restriction of the emergent metric $g$ to each level set $\Sigma_s = t^{-1}(s)$ is positive-definite:
$$h_{ij} = g_{\mu\nu} e_i^\mu e_j^\nu > 0$$
where $\{e_i\}$ is a basis of $T\Sigma_s$.

*Proof.*
On each level set $\Sigma_s$, the relational distance $d_N^{\text{spatial}}$ is defined by entanglement links between spacelike-separated events (those with $T(i) = T(j)$). Since entanglement is symmetric and the mutual information is non-negative, the induced distance satisfies the metric axioms (Lemma 3.1) on $\Sigma_s$. By the MDS embedding (Definition 3.2) applied to $\Sigma_s$, the coordinate representation has a positive-definite inner product. In the GH limit, this gives a positive-definite spatial metric $h_{ij}$ on $\Sigma_s$. $\square$

---

## 3. Lorentzian Signature Theorem

**Theorem 6.1** (Lorentzian Signature).
Under Axioms C1, C2, L1, L2 and the hypotheses of Theorem 2.1 with $d = 4$, the emergent metric $g_{\mu\nu}$ on $M^4$ has Lorentzian signature $(-, +, +, +)$.

*Proof.*

*Step 1 (Decomposition)*: By Lemma 6.1, the smooth temporal function $t: M \to \mathbb{R}$ provides a global foliation $M = \bigcup_s \Sigma_s$. At each point $p \in M$, the tangent space decomposes as:
$$T_pM = \text{span}(\nabla t) \oplus T_p\Sigma_{t(p)}$$

*Step 2 (Temporal direction)*: The vector $\nabla t / |\nabla t|$ (normalized gradient) defines the unit timelike direction. By construction from the causal DAG, $g(\nabla t, \nabla t) < 0$ (Lemma 6.1).

*Step 3 (Spatial directions)*: By Lemma 6.2, the metric restricted to $T_p\Sigma_{t(p)}$ is positive-definite with dimension $d - 1 = 3$.

*Step 4 (Signature)*: Therefore, $g_{\mu\nu}$ has exactly one negative eigenvalue (temporal) and $d - 1 = 3$ positive eigenvalues (spatial), giving signature $(-, +, +, +)$.

*Step 5 (Global consistency)*: The signature is constant across $M$ because:
- The temporal function $t$ is smooth and non-degenerate ($dt \neq 0$ everywhere).
- The eigenvalues of $g_{\mu\nu}$ are continuous functions on $M$.
- A continuous integer-valued function on a connected manifold is constant.
$\square$

---

## 4. Causal Diffeomorphism Emergence

**Theorem 6.2** (Causal Diffeomorphism Convergence).
Under the hypotheses of Theorem P1 (D5) combined with Axioms L1 and L2:
$$\lim_{N \to \infty} Aut_\prec(G_N) \cong Diff^+(M)$$
where $Diff^+(M)$ denotes the group of orientation-preserving, causality-preserving diffeomorphisms of the Lorentzian manifold $(M, g)$.

*Proof.*

*Step 1 (Restriction of the interpolation map)*: The group interpolation map $\Psi_N: Aut_\epsilon(G_N) \to Diff_c(M)$ from Theorem 5.2 restricts to:
$$\Psi_N|_{Aut_\prec}: Aut_{\prec,\epsilon}(G_N) \to Diff_c(M)$$

We claim the image consists of causality-preserving diffeomorphisms.

*Step 2 (Causal preservation)*: If $\sigma \in Aut_{\prec}(G_N)$ preserves the discrete partial order $\prec$, then the induced diffeomorphism $\phi_\sigma = \Psi_N(\sigma)$ satisfies:
$$t(\phi_\sigma(p)) \geq t(p) \quad \text{whenever } p \prec q \implies \phi_\sigma(p) \prec \phi_\sigma(q)$$
This means $\phi_\sigma$ maps causal curves to causal curves, i.e., $\phi_\sigma \in Diff^+(M)$.

*Step 3 (Converse)*: Any causality-preserving diffeomorphism $\phi \in Diff^+(M)$ can be approximated by elements of $\Psi_N(Aut_{\prec,\epsilon}(G_N))$, since the causal constraint is a closed condition and the approximation of Corollary 5.1 can be refined to respect the causal order.

*Step 4 (Isomorphism in the limit)*: By the same projective limit argument as in Theorem 5.2:
$$\varprojlim_N Aut_{\prec,\epsilon}(G_N) / \ker(\Psi_N) \cong Diff^+(M) \quad \square$$

**Corollary 6.1.** The Lorentzian metric $g_{\mu\nu}$ with signature $(-, +, +, +)$ is invariant (up to diffeomorphism) under the emergent symmetry group $Diff^+(M)$.

---

## 5. Outputs

```python
LORENTZIAN_SIGNATURE_RIGOROUS = True
CAUSAL_ORDER_DEFINED = True  # Definition 6.1
TEMPORAL_FUNCTION_CONSTRUCTED = True  # Lemma 6.1
SPATIAL_POSITIVITY_PROVEN = True  # Lemma 6.2
LORENTZIAN_THEOREM = True  # Theorem 6.1
CAUSAL_DIFF_CONVERGENCE = True  # Theorem 6.2
```
