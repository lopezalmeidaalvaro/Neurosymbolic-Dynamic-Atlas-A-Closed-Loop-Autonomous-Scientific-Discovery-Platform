import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.analysis.transferability_features import TransferabilityFeatureEngine

def run_counterfactual_scaffold_audit(num_seeds: int = 100, output_path: str = "counterfactual_scaffold_report.json") -> Dict[str, Any]:
    print(f"Running Counterfactual Scaffold Audit across {num_seeds} seeds...")
    
    # 1. Load dataset to train predictors
    dataset_path = "transferability_dataset.json"
    if not os.path.exists(dataset_path):
        # Create a small dummy dataset if file doesn't exist
        print("Dataset not found. Generating dummy dataset for training...")
        dummy_records = []
        for s in range(1, 21):
            for target_dom in ["ghz_state", "w_state", "variational_ansatz", "error_correction"]:
                dummy_records.append({
                    "seed": s,
                    "target_domain": target_dom,
                    "source_domain": "bell_state",
                    "transfer_success": 1.0 if (s + hash(target_dom)) % 2 == 0 else 0.0,
                    "transfer_utility": 0.4 if (s + hash(target_dom)) % 2 == 0 else -0.1,
                    "synergy_score": 0.3 if (s + hash(target_dom)) % 2 == 0 else 0.0,
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
            
    df = pd.DataFrame(records)
    if "transfer_success" not in df.columns:
        df["transfer_success"] = df["transfer_utility"].apply(lambda u: 1.0 if u > 0.0 else 0.0)
    if "synergy_score" not in df.columns:
        df["synergy_score"] = 0.0
        
    feature_cols = [
        "topology_similarity", "qubit_count_difference", "entanglement_overlap",
        "state_preparation_overlap", "circuit_depth_difference", "gate_distribution_distance",
        "context_distance", "scaffold_complexity", "interaction_frequency"
    ]
    
    # 2. Train baseline models
    X_train = df[feature_cols].values
    y_success = df["transfer_success"].values
    y_utility = df["transfer_utility"].values
    y_synergy = df["synergy_score"].values
    
    # Load synergy transfer registry
    registry_path = "synergy_transfer_registry.json"
    if os.path.exists(registry_path):
        with open(registry_path, "r", encoding="utf-8") as f:
            scaffolds = json.load(f)
    else:
        # Default fallback scaffolds
        scaffolds = [
            {
                "representation": "H->CNOT->H(q0)->CNOT(q0,q1)",
                "sequence": ["H", "CNOT", "H", "CNOT"],
                "interaction_type": "STATE_PREPARATION_EXTENSION",
                "contexts": {"task_name": "bell_state", "qubit_count": 2},
                "utility": 0.3,
                "synergy_score": 0.478
            }
        ]
        
    feature_engine = TransferabilityFeatureEngine()
    
    perturbations = ["swap", "remove", "insert", "perturb_param"]
    audit_results = {p: {"utility_deltas": [], "transfer_deltas": [], "synergy_deltas": []} for p in perturbations}
    
    for seed in range(1, num_seeds + 1):
        # We retrain the classifiers/regressors with seed to introduce statistical variance
        clf_success = RandomForestClassifier(n_estimators=15, random_state=seed)
        reg_utility = RandomForestRegressor(n_estimators=15, random_state=seed)
        reg_synergy = RandomForestRegressor(n_estimators=15, random_state=seed)
        
        clf_success.fit(X_train, y_success)
        reg_utility.fit(X_train, y_utility)
        reg_synergy.fit(X_train, y_synergy)
        
        for scaffold in scaffolds:
            seq = scaffold.get("sequence", ["H", "CNOT"])
            rep = scaffold.get("representation", "H->CNOT")
            source_ctx = scaffold.get("contexts", {"task_name": "bell_state", "qubit_count": 2})
            # Target context is usually different, let's assume a target domain of ghz_state
            target_ctx = {"task_name": "ghz_state", "qubit_count": 3}
            
            # Base features and predictions
            base_feats = feature_engine.compute_features(rep, seq, source_ctx, target_ctx)
            base_row = np.array([[base_feats[col] for col in feature_cols]])
            
            base_succ_prob = float(clf_success.predict_proba(base_row)[0, 1])
            base_util_pred = float(reg_utility.predict(base_row)[0])
            base_syn_pred = float(reg_synergy.predict(base_row)[0])
            
            # Evaluate each perturbation
            for pert in perturbations:
                pert_seq = seq.copy()
                if pert == "swap":
                    if len(pert_seq) >= 2:
                        pert_seq[0], pert_seq[1] = pert_seq[1], pert_seq[0]
                elif pert == "remove":
                    if len(pert_seq) >= 1:
                        pert_seq.pop(0)
                elif pert == "insert":
                    pert_seq.insert(0, "H")
                elif pert == "perturb_param":
                    # Parameter perturbation: add RX(0.05) or simulate a change in rotation
                    pert_seq.append("RX(0.05)")
                    
                pert_rep = "->".join(pert_seq)
                pert_feats = feature_engine.compute_features(pert_rep, pert_seq, source_ctx, target_ctx)
                pert_row = np.array([[pert_feats[col] for col in feature_cols]])
                
                pert_succ_prob = float(clf_success.predict_proba(pert_row)[0, 1])
                pert_util_pred = float(reg_utility.predict(pert_row)[0])
                pert_syn_pred = float(reg_synergy.predict(pert_row)[0])
                
                audit_results[pert]["utility_deltas"].append(pert_util_pred - base_util_pred)
                audit_results[pert]["transfer_deltas"].append(pert_succ_prob - base_succ_prob)
                audit_results[pert]["synergy_deltas"].append(pert_syn_pred - base_syn_pred)
                
    # Calculate stats
    report = {}
    for p in perturbations:
        u_d = np.array(audit_results[p]["utility_deltas"])
        t_d = np.array(audit_results[p]["transfer_deltas"])
        s_d = np.array(audit_results[p]["synergy_deltas"])
        
        report[p] = {
            "mean_utility_delta": round(float(np.mean(u_d)), 4),
            "std_utility_delta": round(float(np.std(u_d)), 4),
            "mean_transfer_delta": round(float(np.mean(t_d)), 4),
            "std_transfer_delta": round(float(np.std(t_d)), 4),
            "mean_synergy_delta": round(float(np.mean(s_d)), 4),
            "std_synergy_delta": round(float(np.std(s_d)), 4)
        }
        
    final_output = {
        "num_seeds": num_seeds,
        "perturbation_impact": report,
        "verdict": "COUNTERFACTUAL_AUDIT_COMPLETE"
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
        
    print("Counterfactual Scaffold Audit complete.")
    return final_output

if __name__ == "__main__":
    run_counterfactual_scaffold_audit()
