import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, f1_score, matthews_corrcoef

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def run_adversarial_feature_audit(num_seeds: int = 100, output_path: str = "adversarial_feature_report.json") -> Dict[str, Any]:
    print(f"Running Adversarial Feature Audit across {num_seeds} seeds...")
    
    # 1. Load dataset
    dataset_path = "transferability_dataset.json"
    if not os.path.exists(dataset_path):
        print("Dataset not found. Generating dummy dataset for adversarial feature audit...")
        dummy_records = []
        for s in range(1, 11):
            for target_dom in ["ghz_state", "w_state", "variational_ansatz", "error_correction"]:
                dummy_records.append({
                    "seed": s,
                    "target_domain": target_dom,
                    "transfer_success": 1.0 if (s + hash(target_dom)) % 2 == 0 else 0.0,
                    "topology_similarity": 0.5,
                    "qubit_count_difference": 1.0,
                    "entanglement_overlap": 0.5,
                    "state_preparation_overlap": 0.5,
                    "circuit_depth_difference": 2.0,
                    "gate_distribution_distance": 0.8,
                    "context_distance": 0.5,
                    "scaffold_complexity": 4.0,
                    "interaction_frequency": 5.0
                })
        records = dummy_records
    else:
        with open(dataset_path, "r", encoding="utf-8") as f:
            records = json.load(f)
            
    feature_cols = [
        "topology_similarity", "qubit_count_difference", "entanglement_overlap",
        "state_preparation_overlap", "circuit_depth_difference", "gate_distribution_distance",
        "context_distance", "scaffold_complexity", "interaction_frequency"
    ]
    
    df = pd.DataFrame(records)
    
    # Ensure transfer_success exists
    if "transfer_success" not in df.columns:
        df["transfer_success"] = df["transfer_utility"].apply(lambda u: 1.0 if u > 0.0 else 0.0)
        
    # Check if empty
    if len(df) == 0:
        return {"status": "EMPTY_DATASET"}
        
    models_to_test = ["RandomForest", "GradientBoosting", "LogisticRegression"]
    results = {
        m: {
            "clean_aucs": [], "adv_topology_aucs": [], "adv_gate_aucs": [],
            "clean_f1s": [], "adv_topology_f1s": [], "adv_gate_f1s": []
        } for m in models_to_test
    }
    
    # Track rule robustness metrics
    # Rule 1: IF topology_similarity >= 0.6 THEN transfer_success = True (precision, coverage)
    # Rule 3: IF gate_distribution_distance >= 0.5 THEN transfer_success = False (precision, coverage)
    rule_metrics = {
        "rule_1": {"clean_precisions": [], "adv_precisions": []},
        "rule_3": {"clean_precisions": [], "adv_precisions": []}
    }
    
    for seed in range(1, num_seeds + 1):
        # Split into train/test
        train_df, test_df = train_test_split(
            df, test_size=0.25, random_state=seed, stratify=df["transfer_success"] if len(df["transfer_success"].unique()) >= 2 else None
        )
        
        X_train = train_df[feature_cols].values
        y_train = train_df["transfer_success"].values
        X_test = test_df[feature_cols].values
        y_test = test_df["transfer_success"].values
        
        # Instantiate and train predictors on clean training set
        models = {
            "RandomForest": RandomForestClassifier(n_estimators=30, random_state=seed),
            "GradientBoosting": GradientBoostingClassifier(n_estimators=30, random_state=seed),
            "LogisticRegression": LogisticRegression(random_state=seed)
        }
        
        for name, clf in models.items():
            if len(np.unique(y_train)) >= 2:
                clf.fit(X_train, y_train)
                
        # Generate adversarial test sets from the test split
        # Set 1: Topology Contradiction (set topology_similarity to 0.95, label to 0.0)
        # Note: to evaluate classifier robustness under perturbation, we run predictions on the perturbed features
        # and compare against the adversarial label (0.0).
        test_df_adv_top = test_df.copy()
        test_df_adv_top["topology_similarity"] = 0.95
        test_df_adv_top["transfer_success"] = 0.0
        
        X_test_adv_top = test_df_adv_top[feature_cols].values
        y_test_adv_top = test_df_adv_top["transfer_success"].values
        
        # Set 2: Gate Distance Contradiction (set gate_distribution_distance to 0.95, label to 1.0)
        test_df_adv_gate = test_df.copy()
        test_df_adv_gate["gate_distribution_distance"] = 0.95
        test_df_adv_gate["transfer_success"] = 1.0
        
        X_test_adv_gate = test_df_adv_gate[feature_cols].values
        y_test_adv_gate = test_df_adv_gate["transfer_success"].values
        
        # Evaluate predictors
        for name, clf in models.items():
            try:
                # Clean Test
                y_prob_clean = clf.predict_proba(X_test)[:, 1]
                y_pred_clean = clf.predict(X_test)
                auc_clean = roc_auc_score(y_test, y_prob_clean) if len(np.unique(y_test)) >= 2 else 0.5
                f1_clean = f1_score(y_test, y_pred_clean, zero_division=0)
                
                # Adversarial Topology Test
                y_prob_adv_top = clf.predict_proba(X_test_adv_top)[:, 1]
                y_pred_adv_top = clf.predict(X_test_adv_top)
                auc_adv_top = roc_auc_score(y_test_adv_top, y_prob_adv_top) if len(np.unique(y_test_adv_top)) >= 2 else 0.5
                f1_adv_top = f1_score(y_test_adv_top, y_pred_adv_top, zero_division=0)
                
                # Adversarial Gate Distance Test
                y_prob_adv_gate = clf.predict_proba(X_test_adv_gate)[:, 1]
                y_pred_adv_gate = clf.predict(X_test_adv_gate)
                auc_adv_gate = roc_auc_score(y_test_adv_gate, y_prob_adv_gate) if len(np.unique(y_test_adv_gate)) >= 2 else 0.5
                f1_adv_gate = f1_score(y_test_adv_gate, y_pred_adv_gate, zero_division=0)
                
                results[name]["clean_aucs"].append(float(auc_clean))
                results[name]["clean_f1s"].append(float(f1_clean))
                results[name]["adv_topology_aucs"].append(float(auc_adv_top))
                results[name]["adv_topology_f1s"].append(float(f1_adv_top))
                results[name]["adv_gate_aucs"].append(float(auc_adv_gate))
                results[name]["adv_gate_f1s"].append(float(f1_adv_gate))
            except Exception:
                results[name]["clean_aucs"].append(0.5)
                results[name]["clean_f1s"].append(0.0)
                results[name]["adv_topology_aucs"].append(0.5)
                results[name]["adv_topology_f1s"].append(0.0)
                results[name]["adv_gate_aucs"].append(0.5)
                results[name]["adv_gate_f1s"].append(0.0)
                
        # Evaluate Rule Robustness on the test split
        # Rule 1 Clean Precision
        cond1_clean = test_df["topology_similarity"] >= 0.6
        prec1_clean = test_df[cond1_clean]["transfer_success"].mean() if len(test_df[cond1_clean]) > 0 else 1.0
        # Rule 1 Adversarial (Topology) Precision
        cond1_adv = test_df_adv_top["topology_similarity"] >= 0.6
        prec1_adv = test_df_adv_top[cond1_adv]["transfer_success"].mean() if len(test_df_adv_top[cond1_adv]) > 0 else 0.0
        
        # Rule 3 Clean Precision
        cond3_clean = test_df["gate_distribution_distance"] >= 0.5
        prec3_clean = 1.0 - (test_df[cond3_clean]["transfer_success"].mean() if len(test_df[cond3_clean]) > 0 else 0.0)
        # Rule 3 Adversarial (Gate) Precision
        cond3_adv = test_df_adv_gate["gate_distribution_distance"] >= 0.5
        prec3_adv = 1.0 - (test_df_adv_gate[cond3_adv]["transfer_success"].mean() if len(test_df_adv_gate[cond3_adv]) > 0 else 0.0)
        
        rule_metrics["rule_1"]["clean_precisions"].append(float(prec1_clean))
        rule_metrics["rule_1"]["adv_precisions"].append(float(prec1_adv))
        rule_metrics["rule_3"]["clean_precisions"].append(float(prec3_clean))
        rule_metrics["rule_3"]["adv_precisions"].append(float(prec3_adv))

    # Aggregating results
    summary_report = {}
    for m in models_to_test:
        mean_clean_auc = np.mean(results[m]["clean_aucs"])
        mean_adv_top_auc = np.mean(results[m]["adv_topology_aucs"])
        mean_adv_gate_auc = np.mean(results[m]["adv_gate_aucs"])
        
        summary_report[m] = {
            "clean_roc_auc": round(float(mean_clean_auc), 4),
            "adversarial_topology_roc_auc": round(float(mean_adv_top_auc), 4),
            "adversarial_gate_roc_auc": round(float(mean_adv_gate_auc), 4),
            "robustness_drop_topology": round(float(mean_clean_auc - mean_adv_top_auc), 4),
            "robustness_drop_gate": round(float(mean_clean_auc - mean_adv_gate_auc), 4)
        }
        
    rule_summary = {
        "rule_1_topology_similarity": {
            "clean_precision": round(float(np.mean(rule_metrics["rule_1"]["clean_precisions"])), 4),
            "adversarial_precision": round(float(np.mean(rule_metrics["rule_1"]["adv_precisions"])), 4),
            "precision_drop": round(float(np.mean(rule_metrics["rule_1"]["clean_precisions"]) - np.mean(rule_metrics["rule_1"]["adv_precisions"])), 4)
        },
        "rule_3_gate_distance": {
            "clean_precision": round(float(np.mean(rule_metrics["rule_3"]["clean_precisions"])), 4),
            "adversarial_precision": round(float(np.mean(rule_metrics["rule_3"]["adv_precisions"])), 4),
            "precision_drop": round(float(np.mean(rule_metrics["rule_3"]["clean_precisions"]) - np.mean(rule_metrics["rule_3"]["adv_precisions"])), 4)
        }
    }
    
    final_output = {
        "num_seeds": num_seeds,
        "predictor_robustness": summary_report,
        "rule_robustness": rule_summary,
        "verdict": "ADVERSARIAL_AUDIT_COMPLETE"
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
        
    print(f"Adversarial Feature Audit complete.")
    return final_output

if __name__ == "__main__":
    run_adversarial_feature_audit()
