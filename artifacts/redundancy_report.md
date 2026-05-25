# Feature Redundancy & Dimensional Pruning Report

## Overview
We audited the 84-dimensional `EV3_SCIENTIFIC` feature matrix across 7 systems (Lorenz, Duffing, Van der Pol, R"ossler, Logistic, ECG200, ECG5000) using Pearson correlation, PCA variance, Mutual Information (MI), and RandomForest Gini importances.

## Redundancy Summary
- **Redundant features** ($|r| > 0.95$): 39 features.
- **PCA Cumulative Variance**:
  * 95% variance explained by: 3 components.
  * 99% variance explained by: 5 components.

## Optimal Feature Selection
- **Baseline Accuracy (84D)**: 88.10%
- **Optimal Pruned Feature Count**: 10 features.
- **Optimal Accuracy**: 87.38%
- **Optimal Indices**: [16, 22, 23, 24, 27, 71, 72, 78, 80, 81]

## Verdict
Applying dimensional pruning dramatically reduces model computational weight while retaining robust dynamical discriminative capabilities.
