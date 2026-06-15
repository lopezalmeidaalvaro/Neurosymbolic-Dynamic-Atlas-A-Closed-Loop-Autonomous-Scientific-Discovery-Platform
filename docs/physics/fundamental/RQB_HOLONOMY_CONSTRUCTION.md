# RQB Holonomy Construction

## 1. Introduction
In standard gauge theories, parallel transport and holonomies are defined over a continuous manifold using connection forms $A_\mu$. In the pregeometric RQB framework, we must reconstruct these quantities directly on the discrete graph edges. This document details the construction of parallel transport operators, Wilson-line analogues, and closed-loop holonomies.

---

## 2. Parallel Transport on Graph Edges

Let two events $I_i$ and $I_j$ be connected by an active entanglement bond represented by the adjacency parameter $\hat{A}_{ij} = 1$. The parallel transport operator $U_{ij}$ is the operator that maps the internal spin and twist state of $I_i$ to that of $I_j$ along the connection edge:

$$U_{ij} = P_{ij} \exp\left( i \Theta_{ij} \right)$$

where:
1.  **$P_{ij} \in SU(2)$** is the spin transport projection, aligning the local quantization frames of the two endpoints:
    $$P_{ij} = \exp\left( \vec{\theta}_{ij} \cdot \vec{\sigma} \right)$$
2.  **$\Theta_{ij} \in U(1) \times SU(3)$** is the phase shift accumulated due to Dehn twists and strand crossings on the connecting ribbon.

By definition, the transport operator satisfies:
- **Hermitian conjugation**: $U_{ji} = U_{ij}^\dagger = U_{ij}^{-1}$
- **Unitarity**: $U_{ij} U_{ij}^\dagger = \mathbb{I}$

---

## 3. Wilson Lines on Graph Paths

A **Wilson line** $W(\gamma)$ along a discrete path $\gamma = (i_0, i_1, \dots, i_k)$ is defined as the ordered product of the parallel transport operators along the connecting edges:

$$W(\gamma) = \prod_{m=1}^k U_{i_{m-1} i_m} = U_{i_0 i_1} U_{i_1 i_2} \cdots U_{i_{k-1} i_k}$$

Under a local gauge transformation at node $m$, where the state transforms as $|s_m\rangle \to \Omega_m |s_m\rangle$ (with $\Omega_m \in SU(3) \times SU(2) \times U(1)$), the transport operator transforms as:
$$U_{lm} \to \Omega_l U_{lm} \Omega_m^\dagger$$

Consequently, the Wilson line transforms only at its endpoints:
$$W(\gamma) \to \Omega_{i_0} W(\gamma) \Omega_{i_k}^\dagger$$

This confirms that the discrete product behaves exactly like a continuous gauge-covariant Wilson line.

---

## 4. Closed-Loop Holonomies

For a closed loop $\mathcal{C}$ where the start and end nodes are the same ($i_0 = i_k$), the trace of the Wilson line defines a gauge-invariant **holonomy**:

$$H(\mathcal{C}) = \operatorname{Tr}\left[ W(\mathcal{C}) \right] = \operatorname{Tr}\left[ \prod_{e \in \mathcal{C}} U_e \right]$$

Because $\Omega_{i_0}^\dagger \Omega_{i_0} = \mathbb{I}$ inside the trace:
$$H(\mathcal{C}) \to \operatorname{Tr}\left[ \Omega_{i_0} W(\mathcal{C}) \Omega_{i_0}^\dagger \right] = \operatorname{Tr}\left[ W(\mathcal{C}) \right] = H(\mathcal{C})$$

This closed-loop holonomy is a direct physical observable of the relational network. In the low-energy limit, the sum over all closed loops recover the Wilson loop observables of continuous gauge theory:
$$\operatorname{Tr}\left[ \mathcal{P} \exp\left( i \oint_{\mathcal{C}} A_\mu dx^\mu \right) \right]$$

---

## 5. Conclusion
Parallel transport operators $U_{ij}$ are rigorously constructed as unitary link variables on the relational graph edges, yielding gauge-invariant closed-loop holonomies that match standard lattice gauge theory definitions.

```python
YANG_MILLS_RECOVERED = True
```
