# Phase 41.1 - Microscopic Degrees of Freedom Reconstruction

## Scope
This document identifies and reconstructs the minimal fundamental degrees of freedom (DOF) capable of reproducing the effective regular Hayward-LQC geometry under the fixed cutoff scale $L \simeq 0.866$.

---

## Candidates for Fundamental Degrees of Freedom

We evaluate the following five quantum-gravitational frameworks to determine the minimal set of microscopic variables:

### 1. Loop Quantum Gravity (LQG) Spin Networks
In canonical LQG, space is represented by spin network states $|\Gamma, j_e, i_v\rangle$ defined on a graph $\Gamma$:
- **Edges ($e$):** Carry $SU(2)$ representations (spins $j_e \in \mathbb{N}/2$), which quantize area:
  $$\hat{A}_S |\Gamma, j_e, i_v\rangle = 8\pi \gamma l_P^2 \sum_{e \cap S} \sqrt{j_e(j_e+1)} |\Gamma, j_e, i_v\rangle$$
- **Nodes ($v$):** Carry intertwiners $i_v$, which quantize volume:
  $$\hat{V}_R |\Gamma, j_e, i_v\rangle = \sum_{v \in R} V_v |\Gamma, j_e, i_v\rangle$$
- **Boundary Punctures:** The black hole horizon is a 2-surface punctured by spin network edges carrying spins $j_p$, giving rise to horizon area and boundary Hilbert space states.

### 2. Loop Quantum Cosmology (LQC) Polymer States
In the homogeneous and isotropic sector (and its spherically symmetric extensions), the connection variables are polymer-quantized:
- The configuration variable $c$ (connection) is not represented as an operator; only its holonomies $\widehat{e^{i\mu c}}$ are well-defined.
- The Hilbert space is $\mathcal{H}_{poly} = L^2(\mathbb{R}_{Bohr}, d\mu_{Bohr})$.
- The basis is composed of discrete volume eigenstates $\{|v\rangle\}$.

### 3. Effective Quantum Geometry
Effective variables are classical fields modified by quantum corrections (e.g. holonomies and inverse triad corrections):
- Holonomy corrections modify the Hamiltonian constraint via the substitution:
  $$c \to \frac{\sin(\bar{\mu} c)}{\bar{\mu}}$$
- This smooths out the singularity at $r \to 0$, replacing it with a de Sitter core of density $\rho_{crit} \approx 0.41 \rho_P$.

### 4. Tensor Structures (Spin Foams & Networks)
Quantum spacetime can be represented covariant-wise by Spin Foam amplitudes (e.g., the EPRL model) or tensor networks:
- Entanglement of bulk states across the horizon boundary dictates the geometry.
- Boundary states represent the microscopic states of the black hole.

### 5. Discrete Lattices and Triangulations
Discrete approximations (such as Regge calculus or Causal Dynamical Triangulations) replace continuous manifolds with discrete simplices.

---

## Q1: What are the minimal candidates for the fundamental degrees of freedom?
The minimal candidates are **LQG spin network states** carrying discrete area and volume eigenvalues, combined with **polymerized LQC variables** representing the radial and volume degrees of freedom in the spherically symmetric sector. The effective regular core of Hayward-LQC is not a collection of point-like particles or field modes, but rather a quantum-geometric state of polymerized space where the radial coordinate has a minimum discrete step matched to the LQG area gap:
$$\Delta = 4\sqrt{3}\pi \gamma l_P^2 \approx 5.17 l_P^2$$

---

## Conclusion
```python
FUNDAMENTAL_DOF_CANDIDATE = "LQG_SPIN_NETWORKS_AND_POLYMERIC_VOLUME_STATES"
```
The fundamental microscopic degrees of freedom are the discrete quanta of area (spins) and volume (intertwiners/polymer states) originating from canonical Loop Quantum Gravity and Loop Quantum Cosmology.
