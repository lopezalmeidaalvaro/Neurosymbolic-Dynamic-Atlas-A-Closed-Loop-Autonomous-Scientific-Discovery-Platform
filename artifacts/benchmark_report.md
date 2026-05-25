# Unified Scientific Pipeline Performance Benchmark Report

## Overview
This report presents a unified mathematical representation evaluation across all 9 representation and identification modules on 7 representative dynamical systems.

## Metrics Matrix Table

| System | Module | Metric Name | Value | Status | Error Details |
| :--- | :--- | :--- | :---: | :---: | :--- |
| lorenz | **EV3 (8D)** | Classification Accuracy/AUC | 1.0000 | OK |  |
| lorenz | **EV3_DEEP (68D)** | Classification Accuracy/AUC | 1.0000 | OK |  |
| lorenz | **EV3_SCIENTIFIC (84D)** | Classification Accuracy/AUC | 1.0000 | OK |  |
| lorenz | **SINDy** | Jaccard Term Match | 0.0000 | OK |  |
| lorenz | **PySR** | Symbolic Jaccard > 0.5 Match | 0.0000 | OK |  |
| lorenz | **Topología** | Wasserstein Stability | 0.0000 | OK |  |
| lorenz | **Koopman** | Invariant mode survival rate | 0.3333 | OK |  |
| lorenz | **Neural ODE** | Relative forecasting L2 score | 0.7848 | OK |  |
| lorenz | **PINN** | Parameter estimation accuracy | 0.6658 | OK |  |
| lorenz | **Autonomous Loop** | Normalized Epistemic Gain | 0.5295 | OK |  |
| duffing | **EV3 (8D)** | Classification Accuracy/AUC | 1.0000 | OK |  |
| duffing | **EV3_DEEP (68D)** | Classification Accuracy/AUC | 1.0000 | OK |  |
| duffing | **EV3_SCIENTIFIC (84D)** | Classification Accuracy/AUC | 1.0000 | OK |  |
| duffing | **SINDy** | Jaccard Term Match | 0.0000 | OK |  |
| duffing | **PySR** | Symbolic Jaccard > 0.5 Match | 0.0000 | OK |  |
| duffing | **Topología** | Wasserstein Stability | 0.0000 | OK |  |
| duffing | **Koopman** | Invariant mode survival rate | 1.0000 | OK |  |
| duffing | **Neural ODE** | Relative forecasting L2 score | 0.8580 | OK |  |
| duffing | **PINN** | Parameter estimation accuracy | 1.0000 | OK |  |
| duffing | **Autonomous Loop** | Normalized Epistemic Gain | 0.5295 | OK |  |
| van_der_pol | **EV3 (8D)** | Classification Accuracy/AUC | 1.0000 | OK |  |
| van_der_pol | **EV3_DEEP (68D)** | Classification Accuracy/AUC | 1.0000 | OK |  |
| van_der_pol | **EV3_SCIENTIFIC (84D)** | Classification Accuracy/AUC | 1.0000 | OK |  |
| van_der_pol | **SINDy** | Jaccard Term Match | 0.0000 | OK |  |
| van_der_pol | **PySR** | Symbolic Jaccard > 0.5 Match | 0.0000 | OK |  |
| van_der_pol | **Topología** | Wasserstein Stability | 0.0000 | OK |  |
| van_der_pol | **Koopman** | Invariant mode survival rate | 1.0000 | OK |  |
| van_der_pol | **Neural ODE** | Relative forecasting L2 score | 0.7064 | OK |  |
| van_der_pol | **PINN** | Parameter estimation accuracy | 1.0000 | OK |  |
| van_der_pol | **Autonomous Loop** | Normalized Epistemic Gain | 0.5295 | OK |  |
| rossler | **EV3 (8D)** | Classification Accuracy/AUC | 1.0000 | OK |  |
| rossler | **EV3_DEEP (68D)** | Classification Accuracy/AUC | 1.0000 | OK |  |
| rossler | **EV3_SCIENTIFIC (84D)** | Classification Accuracy/AUC | 1.0000 | OK |  |
| rossler | **SINDy** | Jaccard Term Match | 0.0000 | OK |  |
| rossler | **PySR** | Symbolic Jaccard > 0.5 Match | 0.0000 | OK |  |
| rossler | **Topología** | Wasserstein Stability | 0.0000 | OK |  |
| rossler | **Koopman** | Invariant mode survival rate | 1.0000 | OK |  |
| rossler | **Neural ODE** | Relative forecasting L2 score | 0.6358 | OK |  |
| rossler | **PINN** | Parameter estimation accuracy | 1.0000 | OK |  |
| rossler | **Autonomous Loop** | Normalized Epistemic Gain | 0.5295 | OK |  |
| logistic | **EV3 (8D)** | Classification Accuracy/AUC | 0.5000 | OK |  |
| logistic | **EV3_DEEP (68D)** | Classification Accuracy/AUC | 1.0000 | OK |  |
| logistic | **EV3_SCIENTIFIC (84D)** | Classification Accuracy/AUC | 1.0000 | OK |  |
| logistic | **SINDy** | Jaccard Term Match | 0.0000 | OK |  |
| logistic | **PySR** | Symbolic Jaccard > 0.5 Match | 0.0000 | OK |  |
| logistic | **Topología** | Wasserstein Stability | 0.0000 | OK |  |
| logistic | **Koopman** | Invariant mode survival rate | 1.0000 | OK |  |
| logistic | **Neural ODE** | Relative forecasting L2 score | 0.6800 | OK |  |
| logistic | **PINN** | Parameter estimation accuracy | 1.0000 | OK |  |
| logistic | **Autonomous Loop** | Normalized Epistemic Gain | 0.5295 | OK |  |
| ECG200 | **EV3 (8D)** | Classification Accuracy/AUC | 0.9167 | OK |  |
| ECG200 | **EV3_DEEP (68D)** | Classification Accuracy/AUC | 0.9375 | OK |  |
| ECG200 | **EV3_SCIENTIFIC (84D)** | Classification Accuracy/AUC | 1.0000 | OK |  |
| ECG200 | **SINDy** | Jaccard Term Match | N/A | BYPASS | Not applicable to UCR |
| ECG200 | **PySR** | Symbolic Jaccard > 0.5 Match | N/A | BYPASS | Not applicable to UCR |
| ECG200 | **Topología** | Wasserstein Stability | 0.0000 | OK |  |
| ECG200 | **Koopman** | Invariant mode survival rate | 1.0000 | OK |  |
| ECG200 | **Neural ODE** | Relative forecasting L2 score | 0.4842 | OK |  |
| ECG200 | **PINN** | Parameter estimation accuracy | 1.0000 | OK |  |
| ECG200 | **Autonomous Loop** | Normalized Epistemic Gain | 0.5295 | OK |  |
| ECG5000 | **EV3 (8D)** | Classification Accuracy/AUC | 0.8000 | OK |  |
| ECG5000 | **EV3_DEEP (68D)** | Classification Accuracy/AUC | 0.8000 | OK |  |
| ECG5000 | **EV3_SCIENTIFIC (84D)** | Classification Accuracy/AUC | 0.9000 | OK |  |
| ECG5000 | **SINDy** | Jaccard Term Match | N/A | BYPASS | Not applicable to UCR |
| ECG5000 | **PySR** | Symbolic Jaccard > 0.5 Match | N/A | BYPASS | Not applicable to UCR |
| ECG5000 | **Topología** | Wasserstein Stability | 0.0000 | OK |  |
| ECG5000 | **Koopman** | Invariant mode survival rate | 1.0000 | OK |  |
| ECG5000 | **Neural ODE** | Relative forecasting L2 score | 0.4842 | OK |  |
| ECG5000 | **PINN** | Parameter estimation accuracy | 1.0000 | OK |  |
| ECG5000 | **Autonomous Loop** | Normalized Epistemic Gain | 0.5295 | OK |  |

## Runtime Summary
- **Total Benchmark Suite Time**: 2331.12 seconds
- **Total Evaluations Executed**: 70
- **Successful runs (OK)**: 66
- **Bypassed runs (BYPASS)**: 4
- **Failed runs (FAIL)**: 0
