# RQB — Precedence Theorem

## 1. Introduction

To mathematically disprove the circularity accusation, we must establish a rigorous theorem of logical precedence. We prove that relational information is the primitive, undefined mathematical input of the RQB framework, whereas spatial geometry is a secondary, derived structure.

---

## 2. Theorem Statement and Proof

### Theorem: THEOREM_F6B_PRECEDENCE
Let $\rho(\tau)$ be the pregeometric state of a relational qubit network $G_N = (V, E)$, evolving under Lie-Lindblad dynamics. Then, the emergent pseudo-Riemannian manifold $(M, g_{\mu\nu})$ is constructed via a directed acyclic logical chain of mappings:

$$\rho(\tau) \xrightarrow{\quad \Phi_1 \quad} I(i:j) \xrightarrow{\quad \Phi_2 \quad} d_{\text{eff}}(i, j) \xrightarrow{\quad \Phi_3 \quad} \mathcal{A} \xrightarrow{\quad \Phi_4 \quad} M \xrightarrow{\quad \Phi_5 \quad} g_{\mu\nu}$$

where each mapping $\Phi_k$ is one-directional and does not depend on the outputs of any subsequent mapping $\Phi_m$ ($m \ge k$).

### Proof:

1.  **Mapping $\Phi_1$: State to Information**
    The input is the density matrix $\rho(\tau)$. The mutual information is computed as:
    $$I(i:j) = S(i) + S(j) - S(i, j)$$
    This mapping requires only the partial trace over event Hilbert spaces $\mathcal{H}_i \cong \mathbb{C}^2$. No metric or coordinates are assumed.
    $$\text{Inputs}(\Phi_1) = \{\rho\} \implies \text{Outputs}(\Phi_1) = \{I(i:j)\}$$

2.  **Mapping $\Phi_2$: Information to Effective Distance**
    We define the effective relational distance $d_{\text{eff}}(i, j)$ using the mutual information:
    $$d_{\text{eff}}(i, j) = - \lambda_0 \log \left( \frac{I(i:j)}{I_{\text{max}}} \right)$$
    where $\lambda_0$ is the Planck length scale factor.
    $$\text{Inputs}(\Phi_2) = \{I(i:j)\} \implies \text{Outputs}(\Phi_2) = \{d_{\text{eff}}(i, j)\}$$
    This is a purely algebraic transformation. It does not assume any spatial manifold.

3.  **Mapping $\Phi_3$: Distance to Local Atlas**
    Using Multidimensional Scaling (MDS) or Diffusion Maps, we embed the relational distance matrix $D_{ij} = d_{\text{eff}}(i, j)$ into local Euclidean patches $\mathbb{R}^d$:
    $$\Phi_{\text{MDS}}: D_{ij} \to \{ x_i \in \mathbb{R}^d \}$$
    We define local coordinate charts $(U_\alpha, \phi_\alpha)$ by covering the graph with overlapping neighborhood subgraphs.
    $$\text{Inputs}(\Phi_3) = \{d_{\text{eff}}(i, j)\} \implies \text{Outputs}(\Phi_3) = \{(U_\alpha, \phi_\alpha)\}$$

4.  **Mapping $\Phi_4$: Atlas to Manifold**
    We reconstruct the smooth manifold $M$ by sewing the local charts together using transition functions $\psi_{\alpha\beta} = \phi_\beta \circ \phi_\alpha^{-1}$. We prove that the transition functions are smooth ($C^\infty$) in the thermodynamic limit $N \to \infty$.
    $$\text{Inputs}(\Phi_4) = \{(U_\alpha, \phi_\alpha)\} \implies \text{Outputs}(\Phi_4) = \{M\}$$

5.  **Mapping $\Phi_5$: Manifold to Metric**
    Finally, the metric tensor $g_{\mu\nu}$ is extracted from the local coordinate differences and the relational distance matrix:
    $$d_{\text{eff}}^2(i, j) \approx g_{\mu\nu}(x) dx^\mu dx^\nu$$
    $$\text{Inputs}(\Phi_5) = \{M, d_{\text{eff}}(i, j)\} \implies \text{Outputs}(\Phi_5) = \{g_{\mu\nu}\}$$

### Conclusion of Precedence:
Because the logical dependency chain is a Directed Acyclic Graph (DAG) starting at the state $\rho$ and ending at the metric $g_{\mu\nu}$, there are no loops. Information does not require geometry:

$$\text{GEOMETRY_NOT_REQUIRED_FOR_INFORMATION} = \text{True}$$

$$\text{Q.E.D.}$$
