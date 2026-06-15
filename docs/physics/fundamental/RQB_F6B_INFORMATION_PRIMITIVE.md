# RQB — Primitive Relational Information

## 1. Introduction

To avoid circularity, the calculation of quantum mutual information $I(i:j)$ between defect excitations in the RQB network must be performed without referencing continuous space, distances, or coordinate mappings. 

This document defines **Primitive Relational Information** directly on the discrete pregeometric Hilbert spaces of the qubit-event network. We prove that information-theoretic quantities are fundamental, pregeometric inputs that exist prior to any spatial reconstruction.

---

## 2. Mathematical Formulation

### 2.1 Density Matrix of Events
Let the pregeometric quantum state of the RQB network be represented by the density matrix $\rho(\tau) \in \mathcal{H}_{\text{net}}$, where $\mathcal{H}_{\text{net}} = \bigotimes_{i \in V} \mathcal{H}_i$ is the tensor product of the local 2-dimensional event Hilbert spaces ($\mathcal{H}_i \cong \mathbb{C}^2$).

For any two event nodes $i, j \in V(G)$, we define the reduced density matrix of the subsystem $\{i, j\}$ by taking the partial trace over all other event degrees of freedom:
$$\rho_{ij} = \text{Tr}_{V \setminus \{i, j\}}(\rho)$$

The individual event density matrices are:
$$\rho_i = \text{Tr}_j(\rho_{ij}), \quad \rho_j = \text{Tr}_i(\rho_{ij})$$

### 2.2 Relational Entanglement Entropy
We define the Von Neumann entropy of a subsystem $A$ purely quantum-mechanically, without space:
$$S(A) = -\text{Tr}(\rho_A \log \rho_A)$$

### 2.3 Mutual Information
The mutual information $I(i:j)$ between events $i$ and $j$ measures the total correlation (both classical and quantum) shared between the two nodes:
$$I(i:j) = S(i) + S(j) - S(i, j)$$

Where:
*   $S(i) = -\text{Tr}(\rho_i \log \rho_i)$
*   $S(j) = -\text{Tr}(\rho_j \log \rho_j)$
*   $S(i, j) = -\text{Tr}(\rho_{ij} \log \rho_{ij})$

This mutual information is computed purely from the state vector $|\Psi\rangle$ or density matrix $\rho$ of the RQB network. The calculation is independent of any metric tensor $g_{\mu\nu}$ or physical coordinate $x^\mu$.

---

## 3. Dynamically Generated Correlations

Correlations are generated dynamically by the Lie-Lindblad master equation. The rate of change of mutual information under the pregeometric updates is:
$$\frac{d I(i:j)}{d\tau} = \text{Tr}\left( \log \rho_i \mathcal{L}_i[\rho] \right) + \text{Tr}\left( \log \rho_j \mathcal{L}_j[\rho] \right) - \text{Tr}\left( \log \rho_{ij} \mathcal{L}_{ij}[\rho] \right)$$

Where $\mathcal{L}$ is the Liouvillian generator representing local qubit-interaction bonds. 

Because $\mathcal{L}$ depends only on the network adjacency matrix $A_{ab}$ and qubit coupling operators, the dynamical evolution of $I(i:j)$ is completely coordinate-free.

$$\text{INFORMATION_PREGEOMETRIC} = \text{True}$$
