import os
import sys
import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, auc, 
    balanced_accuracy_score, matthews_corrcoef, 
    f1_score, recall_score, precision_score
)
from sklearn.ensemble import RandomForestClassifier

def compute_ece_mce(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> Tuple[float, float]:
    """
    Computes Expected Calibration Error (ECE) and Maximum Calibration Error (MCE).
    """
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    mce = 0.0
    n_samples = len(y_true)
    
    for m in range(n_bins):
        bin_lower = bin_boundaries[m]
        bin_upper = bin_boundaries[m + 1]
        
        # Select samples in current bin
        in_bin = (y_prob > bin_lower) & (y_prob <= bin_upper)
        prop_in_bin = np.mean(in_bin)
        
        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(y_true[in_bin])
            avg_confidence_in_bin = np.mean(y_prob[in_bin])
            
            bin_error = abs(accuracy_in_bin - avg_confidence_in_bin)
            ece += prop_in_bin * bin_error
            mce = max(mce, bin_error)
            
    return float(ece), float(mce)

def run_imbalance_calibration_audit() -> Dict[str, Any]:
    print("Running Class Imbalance and Calibration Audit...")
    
    # Load dataset
    dataset_path = "transferability_dataset.json"
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
    with open(dataset_path, "r", encoding="utf-8") as f:
        records = json.load(f)
        
    feature_cols = [
        "topology_similarity", "qubit_count_difference", "entanglement_overlap",
        "state_preparation_overlap", "circuit_depth_difference", "gate_distribution_distance",
        "context_distance", "scaffold_complexity", "interaction_frequency"
    ]
    
    X = []
    y = []
    for r in records:
        row = [r.get(col, 0.5) for col in feature_cols]
        X.append(row)
        y.append(r.get("transfer_success", 0.0))
        
    X = np.array(X)
    y = np.array(y)
    
    # Split: Train 300 seeds * 4 domains = 1200 records. Test 100 seeds * 4 domains = 400 records
    N_total = len(y)
    split_idx = int(0.75 * N_total)
    
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Check balance
    non_trans_ratio = np.mean(y_test == 0.0)
    print(f"  Class balance in test set: NON_TRANSFERABLE = {non_trans_ratio:.2%}")
    
    # Train Random Forest Classifier
    clf = RandomForestClassifier(n_estimators=30, random_state=42)
    clf.fit(X_train, y_train)
    
    y_prob = clf.predict_proba(X_test)[:, 1]
    y_pred = clf.predict(X_test)
    
    # Calculate advanced imbalance metrics
    roc_auc = roc_auc_score(y_test, y_prob)
    
    # PR-AUC
    precision, recall, thresholds = precision_recall_curve(y_test, y_prob)
    pr_auc = auc(recall, precision)
    
    balanced_acc = balanced_accuracy_score(y_test, y_pred)
    mcc = matthews_corrcoef(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    prec = precision_score(y_test, y_pred, zero_division=0)
    
    # Calculate Calibration Metrics
    ece, mce = compute_ece_mce(y_test, y_prob)
    
    audit_results = {
        "imbalance_metrics": {
            "ROC_AUC": round(float(roc_auc), 6),
            "PR_AUC": round(float(pr_auc), 6),
            "Balanced_Accuracy": round(float(balanced_acc), 6),
            "Matthews_Correlation_Coefficient": round(float(mcc), 6),
            "F1_Score": round(float(f1), 6),
            "Recall": round(float(rec), 6),
            "Precision": round(float(prec), 6)
        },
        "calibration_metrics": {
            "Expected_Calibration_Error": round(ece, 6),
            "Maximum_Calibration_Error": round(mce, 6)
        }
    }
    
    print(f"  ROC-AUC: {roc_auc:.4f} | PR-AUC: {pr_auc:.4f} | Balanced Acc: {balanced_acc:.4f} | MCC: {mcc:.4f}")
    print(f"  Expected Calibration Error (ECE): {ece:.6f}")
    
    # Write calibration_audit.json
    with open("calibration_audit.json", "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2, ensure_ascii=False)
        
    return audit_results

if __name__ == "__main__":
    run_imbalance_calibration_audit()
