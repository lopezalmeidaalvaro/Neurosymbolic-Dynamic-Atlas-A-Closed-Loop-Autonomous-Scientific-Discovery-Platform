# Discovery Engine Dossier

## 1. Executive Summary
The AI-for-Science physics discovery engine implements a neurosymbolic pipeline to extract closed-form physical equations, coordinate manifolds, and dynamical representations from raw spatiotemporal observation data. By integrating symbolic regression, sparse dynamics identification, and causal guardians, the engine discovers predictive physical laws that are robust to noise and out-of-sample variations.

## 2. Purpose
The purpose of the discovery engine is to accelerate the scientific method by autonomously discovering conservation laws, vector fields, and dynamical equations from complex physical trajectories without human-engineered prior assumptions.

## 3. Architecture
The engine runs an Autonomous Scientist Loop structured as follows:

```
   +-------------------+
   | Raw Observations  |
   +---------+---------+
             |
             v
   [Causal Mechanism Discovery]  <-- Identifies independent physical variables
             |
             v
   [Symbolic Regression (PySR)]  <-- Generates candidate equations
             |
             v
   [Scientific Guard Auditing]   <-- Falsifies and constrains equations
             |
             v
   [Relational Memory Storage]   <-- Registers canonical laws (SQLite)
```

*   **Causal Discovery Block**: Uses autoencoders and latent-space projections (PCA/UMAP) to isolate physical degrees of freedom.
*   **Symbolic Regression Engine**: Executes evolutionary symbolic searches (PySR) alongside Sparse Identification of Non-linear Dynamics (SINDy).
*   **Scientific Guard**: Evaluates candidates against physical dimensional integrity and boundaries.
*   **Epistemic Memory**: Logs validated laws into `scientific_kb.db`.

## 4. Methodology
*   **Symbolic Representation & SINDy**: Chaotic trajectories are analyzed using library-based sparse identification to match numerical derivatives to polynomials and trigonometric functions.
*   **Fisher Information Complexity Metric**: Used to evaluate candidate equations:
    $$\text{Objective} = \text{Loss} + \kappa \cdot \text{Complexity}$$
    This balances reconstruction accuracy against equation complexity to avoid overfitting.
*   **Epistemic Hardening Engine**: Subjects discovered relations to cross-validation and perturbation sweeps to ensure physical correctness under out-of-sample bounds.

## 5. Results
*   **Lorenz Attractor Reconstruction**: SINDy successfully reconstructs true Lorenz system coefficients with under **$0.05\%$** parameter error.
*   **Duffing Oscillator State Transitions**: Neural ODE modules model state transitions under varying external force amplitudes, maintaining a Hellinger distance error of **$<10^{-4}$**.

## 6. Validation
*   **Gaussian Noise Perturbations**: Candidate equations are validated under randomized label shuffles and noise injections. Discovered systems maintain a survival rate of **$>85\%$** under $5\%$ Gaussian noise.
*   **Anti-Fitting Audits**: The system runs cross-checks against pre-catalogued physical baselines to ensure discovered laws represent genuine scientific discoveries rather than random data fits.

## 7. Limitations
*   **Dimensionality Scaling**: The symbolic search space scales exponentially with the number of variables, limiting the engine's primary discovery loop to systems with $\le 10$ active degrees of freedom.
*   **High-Noise Convergence**: In highly chaotic regimes with signal-to-noise ratios (SNR) $< 15\text{ dB}$, SINDy convergence rates drop below $50\%$.

## 8. Future Work
*   **Fourier Neural Operator (FNO) Integration**: Expanding the discovery loop to partial differential equations (PDEs) for fluid dynamics and electromagnetic field theories.
*   **Multi-Agent Collaborative Discovery**: Implementing multiple autonomous scientist loops working in parallel on distinct subsets of observational data, exchanging candidate models via a shared memory registry.

## 9. Source Documents
*   [DISCOVERY_ENGINE_DOSSIER.md (Original)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/physics/docs/DISCOVERY_ENGINE_DOSSIER.md)
*   [RQB_P1_MANIFOLD_RECONSTRUCTION.md (Consolidated)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/physics/fundamental/RQB_P1_MANIFOLD_RECONSTRUCTION.md)
*   [RQB_P1_CONTINUUM_LIMIT.md (Consolidated)](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/physics/fundamental/RQB_P1_CONTINUUM_LIMIT.md)
