import os
import json
import numpy as np
from typing import Dict, Any, List

class DatasetIntegrityAuditor:
    """
    Audits the transferability dataset for duplicate entries, near-duplicates 
    (Jaccard similarity), and pre-training label leakage.
    """

    def __init__(self, dataset_path: str = "transferability_dataset.json"):
        self.dataset_path = dataset_path

    def run_audit(self) -> Dict[str, Any]:
        """
        Loads the dataset and computes integrity metrics.
        """
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset file not found: {self.dataset_path}")
            
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            records = json.load(f)
            
        N = len(records)
        if N == 0:
            return {"status": "EMPTY_DATASET"}
            
        # 1. Duplicate Check
        # Convert records to JSON strings of sorted keys to identify exact duplicates
        serialized_records = [json.dumps(r, sort_keys=True) for r in records]
        unique_serialized = set(serialized_records)
        duplicate_count = N - len(unique_serialized)
        duplicate_ratio = float(duplicate_count / N)
        
        # 2. Near-Duplicates (Jaccard Similarity of features)
        # Select numeric features
        feature_cols = [
            "topology_similarity", "qubit_count_difference", "entanglement_overlap",
            "state_preparation_overlap", "circuit_depth_difference", "gate_distribution_distance",
            "context_distance", "scaffold_complexity", "interaction_frequency"
        ]
        
        # Build feature matrix
        X = []
        labels = []
        for r in records:
            row = [r.get(col, 0.5) for col in feature_cols]
            X.append(row)
            labels.append(r.get("transfer_success", 0.0))
            
        X = np.array(X)
        y = np.array(labels)
        
        # Compute pairwise Jaccard-like similarity (using MinMax Jaccard for continuous features: sum(min(x,y))/sum(max(x,y)))
        near_duplicate_count = 0
        jaccard_sums = 0.0
        comparisons = 0
        
        # Sample pairs if N is large to keep it O(N)
        step = max(1, N // 200)
        for i in range(0, N, step):
            for j in range(i + step, N, step):
                vec_i = X[i]
                vec_j = X[j]
                
                min_sum = np.sum(np.minimum(vec_i, vec_j))
                max_sum = np.sum(np.maximum(vec_i, vec_j))
                
                sim = min_sum / max_sum if max_sum > 0 else 1.0
                jaccard_sums += sim
                comparisons += 1
                
                if sim > 0.95 and not np.array_equal(vec_i, vec_j):
                    near_duplicate_count += 1
                    
        avg_jaccard = float(jaccard_sums / comparisons) if comparisons > 0 else 1.0
        
        # 3. Label Leakage (correlation with target before training)
        leakage_metrics = {}
        leakage_detected = False
        leaked_features = []
        
        for idx, col in enumerate(feature_cols):
            feat_vec = X[:, idx]
            # Avoid division by zero if feature has zero variance
            if np.std(feat_vec) < 1e-6 or np.std(y) < 1e-6:
                corr = 0.0
            else:
                corr = float(np.corrcoef(feat_vec, y)[0, 1])
                
            leakage_metrics[col] = round(corr, 6)
            
            # Check for high correlation (leaked if |corr| > 0.8)
            if abs(corr) > 0.8:
                leakage_detected = True
                leaked_features.append(col)
                
        report = {
            "dataset_size": N,
            "duplicate_count": duplicate_count,
            "duplicate_ratio": duplicate_ratio,
            "near_duplicate_count": near_duplicate_count,
            "average_jaccard_similarity": round(avg_jaccard, 6),
            "label_leakage": {
                "feature_correlations": leakage_metrics,
                "leakage_detected": leakage_detected,
                "leaked_features": leaked_features
            }
        }
        
        # Write dataset_integrity_report.json
        with open("dataset_integrity_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"Dataset integrity report generated. Duplicate ratio: {duplicate_ratio:.2%}")
        return report

if __name__ == "__main__":
    auditor = DatasetIntegrityAuditor()
    auditor.run_audit()
