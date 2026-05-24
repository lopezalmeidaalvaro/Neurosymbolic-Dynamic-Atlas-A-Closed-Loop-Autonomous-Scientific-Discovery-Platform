# Threats to Validity

This document outlines the current limitations of the Neurosymbolic Automated Discovery Engine.

## 1. Geometric and Topological Proxies

- **Heuristic Geometry:** The terms "manifold", "geodesic", "metric tensor", and "curvature" used in earlier iterations and certain artifacts are used strictly as **heuristic proxies**. They refer to graph-based shortest paths and Euclidean distance variations within PCA-projected spaces, not to formally defined Riemannian manifolds.
- **Absence of Formal TDA:** The current pipeline relies on classical statistical moments and dynamical invariants (e.g., Lyapunov exponents, kurtosis) mapped into a Euclidean vector space. It does not yet implement formal Topological Data Analysis (TDA) methods such as persistent homology or Betti number extraction.

## 2. Hypothesis Generation and Autonomy

- **Hardcoded Falsification:** The current automated statistical pipeline uses pre-programmed statistical thresholds (e.g., Pearson correlation constraints and fixed noise perturbations). It does not autonomously design the mathematical logic of the statistical tests.
- **Human-in-the-Loop:** While the execution, artifact generation, and SQLite tracking are automated, the initial feature selection and the interpretation of the semantic `meta_insights` rely heavily on human design and prompting.

## 3. Benchmarking and Baselines

- **Lack of SOTA Comparison:** The structural embedding space (Embedding v2) has not yet been benchmarked against state-of-the-art (SOTA) time-series classification algorithms (such as ROCKET, catch22, or DTW).
- **Clustering Bias:** The separation between continuous and discrete dynamics observed in the PCA projections is empirical and highly sensitive to the scaling and specific selection of the 8 handcrafted features.

## 4. Predictability Modeling

- **Gaussian Process Failure:** The observed failure of Gaussian Process regression in the latent space indicates high non-linearity and sensitivity (referred to heuristically as "caustics"). However, this has not been subjected to rigorous hyperparameter optimization or alternative kernel testing.

*These limitations define the immediate roadmap for the project, prioritizing rigorous benchmarking (vs. catch22/ROCKET) and the integration of true Persistent Homology (giotto-tda).*
