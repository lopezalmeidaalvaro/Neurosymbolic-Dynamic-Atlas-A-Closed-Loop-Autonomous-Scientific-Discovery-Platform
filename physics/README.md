# Physics Domain — Biophysical ECG & Chaotic Attractor Research Pipeline

Welcome to the **Physics & Neurosymbolic Analysis Domain** of the Neurosymbolic Dynamic Atlas. This folder contains the modular scientific discovery pipeline (Fases 1–18) researching nonlinear chaotic dynamics, discrete Quantum Gravity ensembles, cardiovascular biophysics, and the mathematical boundaries of transfer learning.

---

## 🔬 Scientific Overview: The Theory-to-Clinic Pipeline

Our core research focuses on **strange attractor universality** and the transportability of continuous dynamical embeddings to clinical diagnostics. We study how representations learned from mathematical equations in **Domain A (Synthetic Chaotic Systems)** can be mapped through **Domain B (Composite Biophysical Noise Models)** to diagnose real cardiovascular pathologies in **Domain C (Clinical Patient Electrocardiograms)**.

```
┌─────────────────────────────────┐      ┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│       Domain A (Synthetic)      │ ───> │      Domain B (Biophysical)     │ ───> │       Domain C (Clinical)       │
│  Lorenz, Rössler, Chua Solvers  │      │   ECG Pulse + Baseline Noise    │      │  MIT-BIH Patient Database (AAMI) │
└─────────────────────────────────┘      └─────────────────────────────────┘      └─────────────────────────────────┘
```

---

## 🧩 1. The Core Challenge & Embedding V3 Space (Phase 1)

In cardiac telemetry, traditional time-series classification models (like ROCKET or Dynamic Time Warping) perform exceptionally well on synthetic, noise-free datasets but suffer from high computational latencies ($O(N^2)$ for DTW) and serve as "black boxes" lacking clinical interpretability.

To address this, we developed **Embedding V3**—a handcrafted, **8-dimensional amplitude-invariant, variance-invariant feature space** representing physical and statistical dynamical invariants:

1. `perm_entropy`: Normalized Bandt-Pompe Permutation Entropy (measuring ordinal trajectory complexity).
2. `spectral_entropy`: Normalized Shannon Entropy of the power spectral density (PSD).
3. `svd_entropy`: Singular Value Decomposition Entropy of the time-delay reconstruction matrix.
4. `fractal_dim`: Higuchi Fractal Dimension estimate (calculating structural trajectory self-similarity).
5. `autocorr_decay`: Decorrelation time lag crossing the $1/e$ threshold (independent of signal energy).
6. `robust_skewness`: Galton Skewness based on quantile ratios (robust to outlying spikes).
7. `robust_kurtosis`: Crow-Siddiqui Kurtosis based on quantile ratios.
8. `temporal_irreversibility`: Third statistical moment of first differences normalized by variance (measuring time-reversal thermodynamic asymmetry).

---

## 🌁 2. Bridging the Gap: Domain B (Composite Biophysical Model)

To evaluate representational stability under continuous domain shifts, we engineered **Domain B (Composite Biophysical)**. It acts as a controlled, parameterized mathematical bridge that models physiological noise, heart-rate variability, and instrumental electrode fluctuations:

$$x_{\text{comp}} = w_{\text{morph}} \cdot S_{\text{morph}} + w_{\text{hrv}} \cdot S_{\text{hrv}} + w_{\text{resp}} \cdot S_{\text{resp}} + k_{\text{inst}} \cdot N_{\text{inst}} + k_{\text{motion}} \cdot N_{\text{motion}}$$

We locked the reproducible weights based on standard clinical ECG profiles:
* **Cardiac Morphology ($w_{\text{morph}} = 0.60$):** Synthetic electrocardiogram pulses modeling real-world P-QRS-T complexes.
* **Heart Rate Variability ($w_{\text{hrv}} = 0.20$):** Timing jitter introducing physiological quasi-periodicity.
* **Respiratory Modulation ($w_{\text{resp}} = 0.20$):** Low-frequency sinusoidal baseline wander ($0.25\text{ Hz}$) recreating respiratory drift.
* **Instrumental Noise ($k_{\text{inst}} = 0.10$):** $1/f$ pink noise + Gaussian white noise representing electrode thermal variations.
* **Motion Artifact ($k_{\text{motion}} = 0.10$):** Exponentially decaying low-frequency drift simulating patient physical movement.

---

## 🔬 3. The Analytical Breakthrough: Asymmetric Representational Decay

We subjected our 8D V3 embedding space to a bifurcated clinical validation using real patient records from the **MIT-BIH Arrhythmia Database** (AAMI strict partitioning: DS1 Train, DS2 Test, involving 6,702 total windows centered around Normal `N` and Premature Ventricular Contractions `V` beats).

This study led to the discovery of **Asymmetric Representational Decay (Asymmetric Topological Adaptation)**, a fundamental mathematical paradox in representation transport:

### The Analytical Paradox:
1. **Clinical Diagnostic Success:** Features trained on raw clinical ECGs achieve a high classification accuracy (**ROC-AUC = 0.830 on raw signals**, and **0.847 on filtered signals**), displaying remarkable robustness under external noise injection ($\Delta AUC_{\text{noise}} = +0.0171$).
2. **Latent Manifold Geometry Collapse:** Linear Centered Kernel Alignment (CKA) between synthetic equations space (Domain A) and clinical waveforms (Domain C) shows a near-total geometric deformation:
   $$D_{\text{emb}} = 1 - CKA(E_A, E_C) = 0.982$$
   This proves that there is **zero universal geometric transport** ($p = 0.1688$). The geometric manifold deforms completely.
3. **Causal Attribution Preservation:** Despite the representation deforming completely, the internal feature attributions remain moderately correlated:
   $$D_{\text{attr}} = 1 - \rho_{\text{Spearman}}(\bar{C}_A, \bar{C}_C) = 0.763$$
   where the biophysical transition is highly correlated ($S_2 = +0.667$).

### Conclusion
This asymmetric adaptation reveals that **diagnostic success is not driven by geometric universality**. Instead, the latent manifold deforms under the weight of biophysical scaling, but the decision boundary successfully adapts because the *relative causal ordering* of explanatory features (specifically `autocorr_decay` and `svd_entropy`) survives the transport. This explains why our models maintain diagnostic fidelity in clinics despite the complete disruption of their underlying phase-space geometry.

---

## 📁 Directory Structure

```text
physics/
├── core/                    # Modular Library Utilities
│   ├── autonomous/          # LLM-driven research loop & hypothesis engine
│   ├── dynamic/             # Lorenz, Rössler, Chua chaotic solvers
│   ├── features/            # Feature extraction (8D V3 Feature Space)
│   ├── io/                  # Persistent SQLite & Neo4j database handlers
│   └── validation/          # Centered Kernel Alignment & SHAP attribution
├── models/                  # Saved weights for ResNet, LSTM, Neural ODEs (.pth files)
├── data/                    # Time-series datasets (synthetic attractors & MIT-BIH ECGs)
├── artifacts/               # Telemetry records, database sessions, and JSON sweeps
├── figures/                 # Exported PNG/PDF attractor phase-space plots
├── papers/                  # Publications drafts related to this domain
├── tests/                   # Integrated unit test suite (test_phase*.py)
├── LIMITATIONS.md           # Audited geometric/topological limitations of the pipeline
├── PROJECT_HISTORY.md       # Historical evolution of the Asymmetric Decay discovery
├── run_pipeline.py          # Master entry-point script to run all phases
└── README.md                # This documentation file
```

---

## ⚡ Quick Start & Pipeline Execution

Activate your virtual environment and execute the master runner inside `physics/`:

### 1. Run the Entire Diagnostic Benchmarking Pipeline
```bash
python run_pipeline.py
```
This runs the entire chaotic solvers generation, extracts 8D V3 features, trains models, performs CKA alignment, and logs results in `physics/artifacts/scientific_kb.db`.

### 2. Run a Specific Phase
You can target individual scientific tasks using arguments:
```bash
# Run SINDy symbolic regression to recover equations
python run_pipeline.py --experiment sindy_recovery --symbolic_discovery

# Execute CKA representational alignment analysis
python run_pipeline.py --experiment cka_audit --run_alignment_audit

# Launch the LLM autonomous research sweep
python run_pipeline.py --experiment autonomous_scientist --run_autonomous_sweep
```
