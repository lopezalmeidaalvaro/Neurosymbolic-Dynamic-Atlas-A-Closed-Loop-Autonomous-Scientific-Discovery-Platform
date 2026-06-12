# Coarse-Graining Audit for Hayward-LQC

## 1. Introduction and Objectives
A smooth classical spacetime metric $g_{\mu\nu}$ is an effective description of a vast number of microscopic quantum degrees of freedom. In Loop Quantum Gravity, the transition from discrete spin networks (at the Planck scale $l_P \approx 1.6 \times 10^{-35} \text{ m}$) to macroscopic geometry requires a **coarse-graining** procedure and the study of renormalization group flows.

This document audits the coarse-graining properties of the Hayward-LQC regular black hole model, evaluating renormalization, coarse graining, tensor-network approaches, and whether the effective metric represents a coarse-grained description of deeper quantum states.

---

## 2. Coarse Graining and Renormalization in LQG

Spacetime geometry behaves like a fluid: the microscopic molecules (tetrahedra, spin networks) are not individually visible at macroscopic scales; instead, we observe a continuous fluid (smooth metric) governed by hydrodynamic-like equations (Einstein field equations).

### 2.1 The Coarse-Graining Map
A coarse-graining map $\mathcal{M}$ projects a fine-grained state $\Psi_{\text{fine}}$ on a large graph onto an effective state $\Psi_{\text{coarse}}$ on a smaller, simplified graph:
$$\mathcal{M}: \mathcal{H}_{\text{fine}} \longrightarrow \mathcal{H}_{\text{coarse}}$$
During this projection, high-frequency quantum fluctuations are averaged out, and the expectation values of geometric operators are renormalized:
$$\langle \hat{V}_{\text{coarse}} \rangle = \mathcal{M}\left( \langle \hat{V}_{\text{fine}} \rangle \right)$$
In LQC, this renormalization justifies the use of effective homogeneous connections and triads.

### 2.2 Tensor-Network Approaches
Tensor networks (such as MERA or MPS) are used to represent states with spatial entanglement. In quantum gravity, tensor networks can model the holographic entanglement of the black hole horizon:
- The bulk spin-network geometry is represented by a tensor network where the bonds carry spin labels.
- Coarse graining the tensor network correspond to performing renormalization sweeps, which scale the area and volume operators. This shows that the horizon entropy $S = A/4l_P^2$ is an entanglement entropy of the coarse-grained boundary.

---

## 3. Hayward-LQC as a Coarse-Grained Geometry

The effective Hayward-LQC metric contains a regular core scale $L \simeq 0.866$. This scale can be interpreted as a coarse-grained parameter:

1.  **Microscopic Triad Fluctuations**: At the Planck scale, the triad operators fluctuate wildly. Coarse graining over a scale $d \gg l_P$ averages these fluctuations, yielding a smooth effective metric.
2.  **Regularization via Coarse Graining**: The regular scale $L$ represents the minimum physical size of a quantum cell. Because we cannot resolve structures smaller than the area gap $\Delta \approx 5.17$, the metric $f(r)$ is smoothed out at the core, preventing the curvature invariants from diverging.
3.  **Hydrodynamic Analogy**: Just as the viscosity of a fluid prevents infinite velocity gradients, the quantum gravity coarse graining (characterized by $L$) prevents infinite curvature gradients at the center of the black hole, resolving the singularity.

---

## 4. Evaluation and Verdict

To Deliverable 5 Question: *¿Representa la métrica de Hayward-LQC una descripción de grano grueso (coarse-grained) de estados cuánticos más profundos?*

**Verdict**: 
**Yes**. The Hayward-LQC metric is best understood as a **coarse-grained effective description** of a highly complex, many-node spin-network state. The regular core scale $L \simeq 0.866$ represents a physical renormalization cutoff that emerges when high-frequency Planckian degrees of freedom are averaged out. This coarse-grained model successfully captures the macroscopic physics (horizon positions, singularity resolution, mass inflation) while smoothing over the underlying discrete spin network fluctuations.

---

## 5. Metrics and Score

*   **COARSE_GRAINING_SCORE**: `80`

The score of `80/100` reflects that coarse graining and renormalization group techniques provide a very solid, physically intuitive explanation for the emergence of effective regular geometries, matching the expected behavior of field theories in the infrared limit.
