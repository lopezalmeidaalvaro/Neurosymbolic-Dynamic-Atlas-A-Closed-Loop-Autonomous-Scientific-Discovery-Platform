# PennyLane Hybrid Quantum Learning Report (Component D)

This report presents the validation of hybrid classical-quantum models developed using PennyLane, compared against classical classifiers.

---

## 1. Model Evaluation Metrics

| Model | ROC-AUC | Calibration (Brier) | Generalization Accuracy | Training Time |
| :--- | :---: | :---: | :---: | :---: |
| **PennyLane Hybrid PQC** | 0.8700 | 0.1677 | 71.67% | 0.5834s |
| **Classical Random Forest** | 0.9077 | 0.1208 | 76.67% | 0.0410s |

---

## 2. Model Architectures Implemented

1. **`HybridTransferPredictor`:** Incorporates a Parameterized Quantum Circuit (PQC) layer (using AngleEmbedding and StrongEntanglingLayers) for high-dimensional feature mappings, followed by a classical output layer.
2. **`HybridSynergyPredictor`:** Computes continuous synergy utility metrics using a Variational Quantum Eigensolver (VQE) layout.
3. **`QuantumPINN`:** A Physics-Informed Neural Network enforcing unitarity and normalization constraints in the loss function, penalizing non-physical predictions.
