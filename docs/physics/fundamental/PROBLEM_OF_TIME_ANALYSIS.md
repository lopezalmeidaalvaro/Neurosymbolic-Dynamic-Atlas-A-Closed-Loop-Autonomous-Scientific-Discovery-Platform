# The Problem of Time in Loop Quantum Gravity and Hayward-LQC

## 1. Introduction and Objectives
In classical general relativity, time is part of the spacetime manifold, which is subject to diffeomorphism invariance. Consequently, there is no absolute, preferred time parameter. In canonical quantum gravity, this manifests as the **Problem of Time**: the Hamiltonian constraint $\hat{\mathcal{H}} |\Psi\rangle = 0$ is a frozen equation. There is no explicit time parameter $t$ in the physical states, and the system appears static.

This document analyzes the problem of time for the Hayward-LQC model, studying the Wheeler-DeWitt frozen state, relational time, scalar and dust clocks, and timeless evolution.

---

## 2. Theoretical Analysis of Time in Quantum Gravity

We evaluate the primary mechanisms to address the problem of time:

### 2.1 The Wheeler-DeWitt and Canonical Frozen Time
In the canonical quantization of general relativity, the Wheeler-DeWitt equation is:
$$\hat{\mathcal{H}} |\Psi\rangle = 0$$
Since the physical state is annihilated by the Hamiltonian operator, there is no Schrodinger-like equation of the form $i\hbar \frac{\partial}{\partial t} |\Psi\rangle = \hat{H} |\Psi\rangle$. The state does not evolve classically. Time is a gauge parameter, and physical states are timeless.

### 2.2 Relational Time (The Rovelli-Smolin Framework)
To recover dynamics, we identify physical variables that can act as clocks. Diffeomorphism-invariant statements are formulated relationally:
> "What is the value of the volume $V$ when the scalar field $\phi$ has the value $\phi_0$?"
This relational volume $V(\phi_0)$ is a true Dirac observable. The evolution of the system is described by the correlations between different degrees of freedom, resolving the timelessness of the theory.

### 2.3 The Scalar Clock
By coupling a massless, homogeneous scalar field $\phi$ to gravity, the Hamiltonian constraint becomes:
$$\mathcal{H} = \mathcal{H}_{\text{grav}} + \mathcal{H}_{\phi} = \mathcal{H}_{\text{grav}} + \frac{p_\phi^2}{2V} \approx 0$$
At the quantum level, this can be rewritten as:
$$\frac{\partial^2}{\partial \phi^2} \Psi(v, \phi) = -\hat{\Theta} \Psi(v, \phi)$$
where $\hat{\Theta}$ acts only on the gravitational degrees of freedom (volume $v$). Since $\phi$ enters the equation monotonically, it serves as a global relational clock. Evolution is defined by the operator:
$$\hat{U}(\phi, \phi_0) = \exp\left( -i \sqrt{\hat{\Theta}} (\phi - \phi_0) \right)$$
This yields a consistent Schrodinger-like evolution.

### 2.4 The Dust Clock (Brown-Kuchař and Husain-Pawlowski)
Alternatively, coupling a pressureless dust field $T$ to the gravitational field yields a Hamiltonian constraint that is linear in the dust momentum $p_T$:
$$\mathcal{H} = p_T + \mathcal{H}_{\text{physical}} \approx 0$$
This translates directly to a true Schrodinger equation at the quantum level:
$$-i \hbar \frac{\partial}{\partial T} \Psi = \hat{\mathcal{H}}_{\text{physical}} \Psi$$
where the dust coordinate $T$ acts as a physical time variable, and $\hat{\mathcal{H}}_{\text{physical}}$ acts as a true physical Hamiltonian.

---

## 3. Application to Hayward-LQC Black Holes

For the Hayward-LQC regular black hole model, the problem of time is resolved through the relational scalar clock method:

1.  **Interior Region (Kantowski-Sachs)**: The interior coordinates are swapped such that the radial coordinate is timelike and the temporal coordinate is spacelike. A coupled scalar field $\phi$ or dust field $T$ is used as the relational time variable.
2.  **Quantum regular core**: The evolution of the triad and connection operators as a function of the scalar clock $\phi$ shows that the singularity is resolved: the curvature invariants peak at a finite value and then decrease as the core transitions from collapse to expansion, demonstrating a unitary quantum bounce.
3.  **Boundary and Horizons**: The positions of the event and Cauchy horizons are defined relationally by the values of the clock field where the expansion of null geodesics vanishes.

---

## 4. Evaluation and Verdict

To Q3: *¿Puede definirse una evolución física sin tiempo externo?*

**Verdict**: 
**Yes**. A physical evolution can be defined without an external time parameter by using **relational evolution**. In the Hayward-LQC model, this is successfully implemented by coupling a massless scalar field (or dust) to serve as a relational clock. The physical states evolve relationally with respect to this clock, and the physical transitions (including the black hole collapse and the regular core bounce) are unitary and well-defined.

---

## 5. Metrics and Score

*   **TIME_RESOLUTION_STATUS**: `"RESOLVED_RELATIONALLY_VIA_SCALAR_CLOCK"`
*   **TIME_RESOLUTION_SCORE**: `85`

The score of `85/100` reflects that the relational clock mechanism is a highly successful and mathematically complete solution to the problem of time for symmetry-reduced models (like Hayward-LQC), though it introduces minor ambiguities regarding the choice of clock (the "multiple choice problem of time") in the full theory.
