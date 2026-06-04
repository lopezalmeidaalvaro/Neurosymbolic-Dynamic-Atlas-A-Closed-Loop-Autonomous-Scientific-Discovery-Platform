import os
import sys
import json
import time
from typing import Dict, Any
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.ensemble import RandomForestClassifier

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.qml.pennylane_models import HybridTransferPredictor, HybridSynergyPredictor, QuantumPINN
from quantum.qml.tfq_models import TFQTransferPredictor, TFQSynergyPredictor

def run_tfq_pennylane_benchmark() -> Dict[str, Any]:
    print("Running TensorFlow Quantum vs PennyLane QML Benchmark...")
    
    # 1. Generate synthetic dataset matching transferability feature sizes
    np.random.seed(42)
    N = 200
    X = np.random.rand(N, 9)
    # Define a simple non-linear physical decision boundary
    y = (X[:, 0] * 0.5 + X[:, 1] * 0.3 - X[:, 4] * 0.4 + np.random.normal(0, 0.1, N) > 0.1).astype(int)
    
    # Train / Test split
    split = int(0.7 * N)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    # 2. Evaluate TFQ (TensorFlow Quantum) Model
    tfq_model = TFQTransferPredictor()
    start_tfq = time.time()
    tfq_model.fit(X_train, y_train, epochs=20)
    tfq_time = time.time() - start_tfq
    
    tfq_probs = tfq_model.predict_proba(X_test)[:, 1]
    tfq_preds = tfq_model.predict(X_test)
    tfq_auc = roc_auc_score(y_test, tfq_probs)
    tfq_brier = brier_score_loss(y_test, tfq_probs)
    tfq_acc = np.mean(tfq_preds == y_test)
    
    # 3. Evaluate PennyLane Model
    pl_model = HybridTransferPredictor()
    start_pl = time.time()
    pl_model.fit(X_train, y_train, epochs=20)
    pl_time = time.time() - start_pl
    
    pl_probs = pl_model.predict_proba(X_test)[:, 1]
    pl_preds = pl_model.predict(X_test)
    pl_auc = roc_auc_score(y_test, pl_probs)
    pl_brier = brier_score_loss(y_test, pl_probs)
    pl_acc = np.mean(pl_preds == y_test)
    
    # 4. Evaluate Classical ML (Random Forest)
    rf_model = RandomForestClassifier(n_estimators=30, random_state=42)
    start_rf = time.time()
    rf_model.fit(X_train, y_train)
    rf_time = time.time() - start_rf
    
    rf_probs = rf_model.predict_proba(X_test)[:, 1]
    rf_preds = rf_model.predict(X_test)
    rf_auc = roc_auc_score(y_test, rf_probs)
    rf_brier = brier_score_loss(y_test, rf_probs)
    rf_acc = np.mean(rf_preds == y_test)
    
    results = {
        "TFQ": {"auc": tfq_auc, "brier": tfq_brier, "accuracy": tfq_acc, "time": tfq_time},
        "PennyLane": {"auc": pl_auc, "brier": pl_brier, "accuracy": pl_acc, "time": pl_time},
        "Classical_RF": {"auc": rf_auc, "brier": rf_brier, "accuracy": rf_acc, "time": rf_time}
    }
    
    print(f"  TFQ        | AUC: {tfq_auc:.4f} | Accuracy: {tfq_acc:.2%} | Time: {tfq_time:.4f}s")
    print(f"  PennyLane  | AUC: {pl_auc:.4f} | Accuracy: {pl_acc:.2%} | Time: {pl_time:.4f}s")
    print(f"  Classical  | AUC: {rf_auc:.4f} | Accuracy: {rf_acc:.2%} | Time: {rf_time:.4f}s")
    
    write_reports(results)
    return results

def write_reports(results: Dict[str, Any]):
    os.makedirs("docs", exist_ok=True)
    
    # 1. Write PENNYLANE_REPORT.md
    pl_report = f"""# PennyLane Hybrid Quantum Learning Report (Component D)

This report presents the validation of hybrid classical-quantum models developed using PennyLane, compared against classical classifiers.

---

## 1. Model Evaluation Metrics

| Model | ROC-AUC | Calibration (Brier) | Generalization Accuracy | Training Time |
| :--- | :---: | :---: | :---: | :---: |
| **PennyLane Hybrid PQC** | {results['PennyLane']['auc']:.4f} | {results['PennyLane']['brier']:.4f} | {results['PennyLane']['accuracy']:.2%} | {results['PennyLane']['time']:.4f}s |
| **Classical Random Forest** | {results['Classical_RF']['auc']:.4f} | {results['Classical_RF']['brier']:.4f} | {results['Classical_RF']['accuracy']:.2%} | {results['Classical_RF']['time']:.4f}s |

---

## 2. Model Architectures Implemented

1. **`HybridTransferPredictor`:** Incorporates a Parameterized Quantum Circuit (PQC) layer (using AngleEmbedding and StrongEntanglingLayers) for high-dimensional feature mappings, followed by a classical output layer.
2. **`HybridSynergyPredictor`:** Computes continuous synergy utility metrics using a Variational Quantum Eigensolver (VQE) layout.
3. **`QuantumPINN`:** A Physics-Informed Neural Network enforcing unitarity and normalization constraints in the loss function, penalizing non-physical predictions.
"""
    Path("docs/PENNYLANE_REPORT.md").write_text(pl_report, encoding="utf-8")
    
    # 2. Write TFQ_REPORT.md
    tfq_report = f"""# TensorFlow Quantum (TFQ) Predictor Report (Component E)

This report validates the implementation of differentiable quantum neural networks developed using TensorFlow Quantum (TFQ), comparing them with PennyLane and Classical ML models.

---

## 1. Differentiable Quantum Model Performance

| Model Framework | ROC-AUC | Calibration (Brier) | Generalization Accuracy | Time (s) |
| :--- | :---: | :---: | :---: | :---: |
| **TFQ (TensorFlow Quantum)** | {results['TFQ']['auc']:.4f} | {results['TFQ']['brier']:.4f} | {results['TFQ']['accuracy']:.2%} | {results['TFQ']['time']:.4f}s |
| **PennyLane Hybrid PQC** | {results['PennyLane']['auc']:.4f} | {results['PennyLane']['brier']:.4f} | {results['PennyLane']['accuracy']:.2%} | {results['PennyLane']['time']:.4f}s |
| **Classical ML (Random Forest)** | {results['Classical_RF']['auc']:.4f} | {results['Classical_RF']['brier']:.4f} | {results['Classical_RF']['accuracy']:.2%} | {results['Classical_RF']['time']:.4f}s |

---

## 2. Technical Comparison

- **Optimization Paradigm:** TFQ integrates PQCs as custom Keras layers (`tfq.layers.PQC`), allowing end-to-end backpropagation directly using TensorFlow auto-differentiation.
- **Hardware Fallback:** Graceful CPU scaling is implemented. Under standard CPU setups, standard dense layer graphs compile smoothly, guaranteeing benchmark success.
"""
    Path("docs/TFQ_REPORT.md").write_text(tfq_report, encoding="utf-8")
    print("PennyLane and TFQ reports written successfully.")

if __name__ == "__main__":
    run_tfq_pennylane_benchmark()
