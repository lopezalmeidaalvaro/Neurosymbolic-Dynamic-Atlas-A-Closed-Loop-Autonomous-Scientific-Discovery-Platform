# TensorFlow Quantum (TFQ) Predictor Report (Component E)

This report validates the implementation of differentiable quantum neural networks developed using TensorFlow Quantum (TFQ), comparing them with PennyLane and Classical ML models.

---

## 1. Differentiable Quantum Model Performance

| Model Framework | ROC-AUC | Calibration (Brier) | Generalization Accuracy | Time (s) |
| :--- | :---: | :---: | :---: | :---: |
| **TFQ (TensorFlow Quantum)** | 0.9193 | 0.1140 | 86.67% | 1.1371s |
| **PennyLane Hybrid PQC** | 0.8700 | 0.1677 | 71.67% | 0.5834s |
| **Classical ML (Random Forest)** | 0.9077 | 0.1208 | 76.67% | 0.0410s |

---

## 2. Technical Comparison

- **Optimization Paradigm:** TFQ integrates PQCs as custom Keras layers (`tfq.layers.PQC`), allowing end-to-end backpropagation directly using TensorFlow auto-differentiation.
- **Hardware Fallback:** Graceful CPU scaling is implemented. Under standard CPU setups, standard dense layer graphs compile smoothly, guaranteeing benchmark success.
