import os
import json
import sqlite3
import numpy as np
from typing import Dict, Any, List
from quantum.reality_native.reality_native_memory import RealityNativeMemory

class AnomalyClusteringEngine:
    """
    Phase 3B-B: Anomaly Clustering.
    Groups hardware prediction deviations into stable anomaly families using DBSCAN
    or Hierarchical Clustering models.
    """

    def __init__(self, reality_db_path: str = "reality_native.db"):
        self.reality_mem = RealityNativeMemory(db_path=reality_db_path)

    def cluster_anomalies(self) -> List[Dict[str, Any]]:
        gaps = self.reality_mem.get_all_gaps()
        if not gaps:
            return []

        # Prepare features for clustering
        # We group by prediction_id to find families of prediction failures
        # Feature vector for each prediction: [mean_gap, std_gap, max_gap]
        pred_features = {}
        for g in gaps:
            p_id = g["prediction_id"]
            pred_features.setdefault(p_id, []).append(g["gap"])

        features_matrix = []
        pred_ids = []
        for p_id, gap_vals in pred_features.items():
            features_matrix.append([
                np.mean(gap_vals),
                np.std(gap_vals),
                np.max(gap_vals)
            ])
            pred_ids.append(p_id)

        X = np.array(features_matrix)

        # Custom Agglomerative Hierarchical Clustering (distance-threshold based)
        # Pairwise distance matrix
        n = len(X)
        dists = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                dists[i, j] = np.linalg.norm(X[i] - X[j])

        # Cluster points based on distance threshold eps = 0.05
        eps = 0.05
        labels = -np.ones(n, dtype=int)
        cluster_id = 0
        
        for i in range(n):
            if labels[i] != -1:
                continue
            # Start a new cluster
            labels[i] = cluster_id
            for j in range(n):
                if dists[i, j] < eps:
                    labels[j] = cluster_id
            cluster_id += 1

        # Build Anomaly Classes
        anomaly_classes = []
        for cid in range(cluster_id):
            members = [pred_ids[i] for i in range(n) if labels[i] == cid]
            if not members:
                continue
            
            # Mean gap across members
            member_gaps = []
            for m in members:
                member_gaps.extend(pred_features[m])
            mean_gap = np.mean(member_gaps) if member_gaps else 0.0

            # Map to descriptive names based on metric behavior
            if mean_gap < -0.15:
                class_name = f"ANOMALY_CLASS_{cid+1:03d} (Severe Systematic Degradation)"
            else:
                class_name = f"ANOMALY_CLASS_{cid+1:03d} (Calibration-Linked Shift)"

            fam_record = {
                "id": f"ANOM_FAM_{cid+1:03d}",
                "name": class_name,
                "prediction_ids": members,
                "mean_gap": round(float(mean_gap), 4),
                "cluster_id": cid
            }
            
            self.reality_mem.save_anomaly_family(fam_record)
            anomaly_classes.append(fam_record)

        print(f"Clustered prediction deviations into {len(anomaly_classes)} stable anomaly families.")
        return anomaly_classes

if __name__ == "__main__":
    eng = AnomalyClusteringEngine()
    print("Anomaly families size:", len(eng.cluster_anomalies()))
