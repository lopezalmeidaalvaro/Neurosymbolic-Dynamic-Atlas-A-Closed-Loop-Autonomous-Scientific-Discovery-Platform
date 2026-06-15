# RQB — Spacetime Geometry Failure Cases

## 1. Introduction

Spacetime geometry does not emerge from just any arbitrary quantum state or graph structure. To establish a robust, falsifiable theory, we must define the boundaries of geometric emergence.

This document identifies **Geometry Failure Cases**—classes of graphs and quantum states where entanglement information is well-defined but fails to reconstruct a smooth, low-dimensional manifold. We derive the minimal necessary pregeometric properties for successful spacetime emergence.

---

## 2. Pathological Classes (Failure Cases)

### 2.1 Expander Graphs
An expander graph is a sparse graph that has strong connectivity properties. For any subset $S \subset V$ with $|S| \le N/2$, the boundary $\partial S$ satisfies:
$$|\partial S| \ge h |S|$$
where $h > 0$ is the Cheeger constant.
*   **Failure Mechanism**: The volume-to-boundary ratio remains constant, meaning the spectral dimension $d_S \to \infty$ as $N \to \infty$. MDS cannot embed the relational distances into any finite-dimensional Euclidean space $\mathbb{R}^d$ without infinite coordinate stress.
*   **Result**: No low-dimensional spacetime manifold emerges.

### 2.2 Scale-Free Networks
Scale-free networks have a degree distribution following a power law: $P(k) \propto k^{-\gamma}$.
*   **Failure Mechanism**: The presence of "hubs" (highly connected nodes) collapses the relational distance between arbitrary nodes to $d_{\text{eff}} \approx 2$ steps (ultra-small world property).
*   **Result**: The space collapses to a single point in the continuum limit.

### 2.3 Global GHZ States
Consider the Greenberger-Horne-Zeilinger state of the network:
$$|\Psi_{\text{GHZ}}\rangle = \frac{|00\dots0\rangle + |11\dots1\rangle}{\sqrt{2}}$$
*   **Failure Mechanism**: For any two events $i, j$, the reduced density matrix $\rho_{ij}$ is diagonal:
    $$\rho_{ij} = \frac{|00\rangle\langle00| + |11\rangle\langle11|}{2}$$
    The Von Neumann entropy of any single node is $S(i) = 1$, and the joint entropy is $S(i, j) = 1$. The mutual information is:
    $$I(i:j) = S(i) + S(j) - S(i, j) = 1 + 1 - 1 = 1$$
    Every single pair of nodes has identical mutual information, regardless of connectivity.
*   **Result**: Relational distance $d_{\text{eff}}(i, j)$ is constant for all pairs, representing a simplex. Reconstructed dimension collapses or is infinite.

### 2.4 Volume-Law Entangled States
States with high entanglement, such as random page states, follow a volume law: $S(A) \propto |A|$.
*   **Failure Mechanism**: The mutual information between small regions does not decay with distance but remains high due to global entangling.
*   **Result**: The relational distance matrix has uniform entries, preventing the formation of localized charts.

---

## 3. Minimal Necessary Conditions

For a smooth $4D$ Lorentzian manifold to emerge from the RQB network, the state $\rho$ and graph $G$ must satisfy:

1.  **Area Law Entanglement**: For any localized region $A$, the entropy must scale with the boundary size:
    $$S(A) \propto |\partial A|$$
2.  **Spectral Dimension Decay**: The spectral dimension computed from the heat kernel trace must converge to a finite value:
    $$\lim_{t \to \infty} d_S(t) = d \approx 4.0$$
3.  **Local Flatness**: The coordinate stress of MDS embedding on localized subgraphs must be small:
    $$\sigma_{\text{local}} = \frac{\sum_{i,j \in U} (\|x_i - x_j\| - D_{ij})^2}{\sum D_{ij}^2} \ll 1$$

These conditions define the boundaries of `GEOMETRY_EMERGENCE_CONDITIONS`.
