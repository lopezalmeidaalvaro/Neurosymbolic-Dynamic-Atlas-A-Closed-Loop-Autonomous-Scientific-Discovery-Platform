import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from sklearn.feature_selection import mutual_info_classif

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def run_leakage_forensics(output_path: str = "leakage_forensics_report.json") -> Dict[str, Any]:
    print("Running Dataset Leakage Forensics...")
    
    # 1. Load dataset
    dataset_path = "transferability_dataset.json"
    if not os.path.exists(dataset_path):
        print("Dataset not found. Generating dummy dataset for leakage forensics...")
        dummy_records = []
        for s in range(1, 21):
            for target_dom in ["ghz_state", "w_state", "variational_ansatz", "error_correction"]:
                dummy_records.append({
                    "seed": s,
                    "split": "TRAIN" if s <= 15 else "TEST",
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
    
    # Ensure transfer_success exists
    if "transfer_success" not in df.columns:
        df["transfer_success"] = df["transfer_utility"].apply(lambda u: 1.0 if u > 0.0 else 0.0)
        
    feature_cols = [
        "topology_similarity", "qubit_count_difference", "entanglement_overlap",
        "state_preparation_overlap", "circuit_depth_difference", "gate_distribution_distance",
        "context_distance", "scaffold_complexity", "interaction_frequency"
    ]
    
    # Fill missing values with default values
    for col in feature_cols + ["transfer_success", "transfer_utility"]:
        if col not in df.columns:
            df[col] = 0.0
            
    # 2. Exact duplicate check (based on features only)
    features_df = df[feature_cols]
    num_exact_duplicates = int(features_df.duplicated().sum())
    
    # 3. Near duplicates check
    # Check if any non-identical rows are very close (Euclidean distance < 1e-4)
    # To keep it efficient, we check a subset if the dataset is large
    normed_features = (features_df - features_df.mean()) / (features_df.std().replace(0, 1))
    near_dups_count = 0
    if len(normed_features) > 1:
        # compute pairwise distances
        from scipy.spatial.distance import pdist, squareform
        dists = pdist(normed_features.values, metric='euclidean')
        # near duplicates: distance > 0 but < 0.01
        near_dups_count = int(np.sum((dists > 0) & (dists < 0.01)))
        
    # 4. Train/Test leakage & overlap
    overlap_count = 0
    if "split" in df.columns:
        train_df = df[df["split"] == "TRAIN"]
        test_df = df[df["split"] == "TEST"]
        if len(train_df) > 0 and len(test_df) > 0:
            train_feats = set(tuple(x) for x in train_df[feature_cols].values)
            test_feats = set(tuple(x) for x in test_df[feature_cols].values)
            overlap_count = len(train_feats.intersection(test_feats))
            
    # 5. Target leakage (correlation > 0.95 or mutual info > 0.95 with target)
    target_leakage_features = []
    correlation_matrix = df[feature_cols + ["transfer_success"]].corr()
    for col in feature_cols:
        corr_val = correlation_matrix.loc[col, "transfer_success"]
        if abs(corr_val) > 0.95:
            target_leakage_features.append({"feature": col, "metric": "correlation", "value": round(float(corr_val), 4)})
            
    # 6. Mutual Information
    mi_vals = {}
    if len(df["transfer_success"].unique()) >= 2:
        mi_scores = mutual_info_classif(features_df.values, df["transfer_success"].values, random_state=42)
        for idx, col in enumerate(feature_cols):
            mi_vals[col] = round(float(mi_scores[idx]), 4)
            if mi_scores[idx] > 0.95:
                # also flag as target leakage if MI is suspiciously high
                target_leakage_features.append({"feature": col, "metric": "mutual_information", "value": round(float(mi_scores[idx]), 4)})
    else:
        mi_vals = {col: 0.0 for col in feature_cols}
        
    # 7. Convert correlation matrix to clean dict format
    corr_dict = {}
    for col1 in correlation_matrix.index:
        corr_dict[col1] = {}
        for col2 in correlation_matrix.columns:
            corr_dict[col1][col2] = round(float(correlation_matrix.loc[col1, col2]), 4)
            
    # 8. Report final metrics
    leakage_detected = len(target_leakage_features) > 0 or overlap_count > 0 or near_dups_count > 0
    
    final_output = {
        "dataset_statistics": {
            "total_records": len(df),
            "num_exact_duplicates": num_exact_duplicates,
            "num_near_duplicates": near_dups_count,
            "train_test_overlap_count": overlap_count
        },
        "target_leakage": {
            "leakage_detected": leakage_detected,
            "flagged_features": target_leakage_features
        },
        "correlation_matrix": corr_dict,
        "mutual_information": mi_vals,
        "verdict": "LEAKAGE_DETECTED" if leakage_detected else "CLEAN_DATASET"
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
        
    print(f"Dataset Leakage Forensics complete. Verdict: {final_output['verdict']}")
    return final_output

if __name__ == "__main__":
    run_leakage_forensics()
