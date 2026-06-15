# RQB Edge Holonomies

## 1. Introduction
In standard continuum gauge field theories, parallel transport and holonomies are defined over a smooth differential manifold using a connection form $A$. In the pregeometric Relational Quantum Bit-Event (RQB) framework, these continuous concepts are reconstructed starting from discrete relational properties on the graph edges. This document establishes the mathematical definition of parallel transport, edge operators, discrete Wilson lines, and gauge-invariant closed Wilson loops.

---

## 2. Edge Transport Operators
Let two events $I_i$ and $I_j$ be connected by an active entanglement bond represented by the adjacency parameter $A_{ij} = 1$. The discrete parallel transport operator $U_{ij}$ is a unitary link variable mapping the internal Hilbert space $\mathcal{H}_i$ of event $I_i$ to $\mathcal{H}_j$ of event $I_j$:

$$U_{ij} = P_{ij} \exp\left( i \Theta_{ij} \right)$$

where:
1. **$P_{ij} \in SU(2)$** is the spin transport operator, aligning the local spin frames (quantization axes) of the two endpoints:
   $$P_{ij} = \exp\left( \vec{\theta}_{ij} \cdot \vec{\sigma} \right)$$
   where $\vec{\sigma}$ are the Pauli matrices and $\vec{\theta}_{ij}$ is the relative orientation angle vector.
2. **$\Theta_{ij} \in U(1) \times SU(3)$** is the phase shift operator accumulated from ribbon Dehn twists and strand crossings:
   $$\Theta_{ij} = \theta_{ij}^Y \mathbb{I} + \sum_{a=1}^8 \phi_{ij}^a \lambda^a$$
   where $\theta_{ij}^Y$ is the Dehn twist hypercharge phase, $\lambda^a$ are the Gell-Mann matrices, and $\phi_{ij}^a$ are the strand permutation phases.

By definition, the transport operator satisfies the key relations:
- **Hermitian Conjugation**: $U_{ji} = U_{ij}^\dagger = U_{ij}^{-1}$
- **Unitarity**: $U_{ij} U_{ij}^\dagger = \mathbb{I}$

---

## 3. Parallel Transport and Wilson Lines
For a discrete path $\gamma = (i_0, i_1, \dots, i_k)$ on the relational graph, the transport of an internal state $|\psi(i_0)\rangle$ to the endpoint $i_k$ is mediated by the ordered product of link variables, defining a discrete **Wilson line** $W(\gamma)$:

$$|\psi(i_k)\rangle = W(\gamma) |\psi(i_0)\rangle$$

where the Wilson line operator is:

$$W(\gamma) = \prod_{m=1}^k U_{i_m i_{m-1}} = U_{i_k i_{k-1}} \cdots U_{i_2 i_1} U_{i_1 i_0}$$

---

## 4. Local Gauge Covariance
Under a local change of basis (local gauge transformation) at vertex $i$, the state transforms as:

$$|\psi(i)\rangle \to \Omega_i |\psi(i)\rangle$$

where $\Omega_i \in SU(3) \times SU(2) \times U(1)$ is a unitary operator representing local frame rotations, permuting color strands, or shifting twist phases.

To preserve the transport relation $|\psi(j)\rangle = U_{ji} |\psi(i)\rangle$, the edge transport operator must transform covariantly:

$$U_{ji} \to \Omega_j U_{ji} \Omega_i^\dagger$$

Applying this transformation rule to the Wilson line $W(\gamma)$ along path $\gamma$, we find:

$$W(\gamma) \to \Omega_{i_k} W(\gamma) \Omega_{i_0}^\dagger$$

Thus, the discrete Wilson line is gauge-covariant and depends only on the gauge transformations at its endpoints.

---

## 5. Closed-Loop Wilson Loops
For a closed path $\mathcal{C}$ where the start and end vertices are identical ($i_0 = i_k$), the trace of the Wilson line defines the **Wilson loop** observable $H(\mathcal{C})$:

$$H(\mathcal{C}) = \operatorname{Tr}\left[ W(\mathcal{C}) \right] = \operatorname{Tr}\left[ \prod_{e \in \mathcal{C}} U_e \right]$$

Under local gauge transformations, the Wilson loop transforms as:

$$H(\mathcal{C}) \to \operatorname{Tr}\left[ \Omega_{i_0} W(\mathcal{C}) \Omega_{i_0}^\dagger \right] = \operatorname{Tr}\left[ W(\mathcal{C}) \right] = H(\mathcal{C})$$

Because of the cyclic property of the trace, $H(\mathcal{C})$ is strictly gauge-invariant under all local frame rotations, ribbon twist shifts, and strand permutations. These Wilson loops represent the fundamental gauge-invariant physical observables of the discrete RQB pregeometric network.

---

## 6. Conclusion
Gauge-invariant observables emerge on discrete graph edges in the form of parallel transport operators and Wilson loops without any continuum assumptions.

```python
GAUGE_FIELDS_EMERGENT = True
```
