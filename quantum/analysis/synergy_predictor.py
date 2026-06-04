import json
import numpy as np
import pandas as pd
from typing import List, Dict, Any
from sklearn.feature_selection import mutual_info_regression
from sklearn.ensemble import RandomForestRegressor
from quantum.memory.context_compatibility import ContextCompatibilityEngine

class SynergyPredictor:
    """
    Analyzes which variables best explain and predict Synergy Score.
    Computes Mutual Information, Feature Importance, and Correlation.
    """

    def __init__(self):
        self.compat_engine = ContextCompatibilityEngine()

    def analyze_synergy(self, records: List[Dict[str, Any]], memory: Any) -> Dict[str, Any]:
        if not records:
            return {"status": "NO_DATA", "ranking": []}

        # Retrieve memory details for additional features
        patterns = memory.retrieve("quantum:distillation:patterns") or []
        pattern_map = {p["representation"]: p for p in patterns}

        data_rows = []
        for r in records:
            rep_a = r["pattern_a"]
            rep_b = r["pattern_b"]
            
            p_a = pattern_map.get(rep_a, {})
            p_b = pattern_map.get(rep_b, {})

            # 1. Contextual Compatibility
            ctx_a = p_a.get("context", {})
            ctx_b = p_b.get("context", {})
            compat_score = self.compat_engine.calculate_compatibility(ctx_a, ctx_b) if ctx_a and ctx_b else 0.5

            # 2. Topological similarity (qubit count difference)
            q_a = ctx_a.get("qubit_count", 0) if isinstance(ctx_a, dict) else getattr(ctx_a, "qubit_count", 0)
            q_b = ctx_b.get("qubit_count", 0) if isinstance(ctx_b, dict) else getattr(ctx_b, "qubit_count", 0)
            topo_diff = abs(q_a - q_b)

            # 3. Convergence history
            conv_a = ctx_a.get("converged", False) if isinstance(ctx_a, dict) else getattr(ctx_a, "converged", False)
            conv_b = ctx_b.get("converged", False) if isinstance(ctx_b, dict) else getattr(ctx_b, "converged", False)
            conv_score = (1.0 if conv_a else 0.0) + (1.0 if conv_b else 0.0)

            # 4. Historical frequency
            freq_a = p_a.get("frequency", 1)
            freq_b = p_b.get("frequency", 1)
            freq_sum = freq_a + freq_b

            # 5. Individual quality
            qual_a = p_a.get("mean_delta_score", 0.0)
            qual_b = p_b.get("mean_delta_score", 0.0)
            quality_sum = qual_a + qual_b

            # 6. Confidence sum
            conf_a = p_a.get("confidence_score", 0.1)
            conf_b = p_b.get("confidence_score", 0.1)
            confidence_sum = conf_a + conf_b

            # 7. Interaction Type
            interaction_type = r.get("interaction_type", "UNKNOWN")

            data_rows.append({
                "synergy_score": r["synergy_score"],
                "compat_score": compat_score,
                "topo_diff": topo_diff,
                "conv_score": conv_score,
                "freq_sum": freq_sum,
                "quality_sum": quality_sum,
                "confidence_sum": confidence_sum,
                "interaction_type": interaction_type
            })

        df = pd.DataFrame(data_rows)
        
        # Categorical encoding for interaction_type
        df_encoded = pd.get_dummies(df, columns=["interaction_type"], drop_first=False)
        
        # Target and features
        y = df_encoded["synergy_score"].values
        X_df = df_encoded.drop(columns=["synergy_score"])
        feature_names = X_df.columns.tolist()
        X = X_df.values

        # If we have zero variance in y, add a tiny bit of noise to prevent errors
        if np.std(y) < 1e-9:
            y = y + np.random.normal(0, 1e-6, len(y))

        # 1. Pearson Correlation
        correlations = {}
        for col in X_df.columns:
            corr = X_df[col].corr(df["synergy_score"])
            correlations[col] = 0.0 if pd.isna(corr) else round(corr, 4)

        # 2. Mutual Information
        if len(y) >= 5:
            mi_scores = mutual_info_regression(X, y, random_state=42)
            mi_dict = {name: round(score, 4) for name, score in zip(feature_names, mi_scores)}

            # 3. Random Forest Feature Importance
            rf = RandomForestRegressor(n_estimators=50, random_state=42)
            rf.fit(X, y)
            rf_importances = rf.feature_importances_
            rf_dict = {name: round(imp, 4) for name, imp in zip(feature_names, rf_importances)}
        else:
            mi_dict = {}
            rf_dict = {}

        # Create final ranking list
        ranking = []
        for name in feature_names:
            ranking.append({
                "feature": name,
                "mutual_information": mi_dict.get(name, 0.0),
                "random_forest_importance": rf_dict.get(name, 0.0),
                "pearson_correlation": correlations.get(name, 0.0)
            })

        # Sort by Random Forest Importance descending
        ranking.sort(key=lambda x: x["random_forest_importance"], reverse=True)

        # Calculate statistics per interaction type
        type_stats = {}
        if "interaction_type" in df.columns:
            grouped = df.groupby("interaction_type")["synergy_score"].agg(["mean", "std", "count"])
            for idx, row in grouped.iterrows():
                type_stats[idx] = {
                    "mean_synergy": 0.0 if pd.isna(row["mean"]) else round(row["mean"], 4),
                    "std_synergy": 0.0 if pd.isna(row["std"]) else round(row["std"], 4),
                    "sample_size": int(row["count"])
                }

        results = {
            "status": "SUCCESS",
            "ranking": ranking,
            "interaction_type_statistics": type_stats
        }

        # Save stats to interaction_type_statistics.json
        with open("interaction_type_statistics.json", "w", encoding="utf-8") as f:
            json.dump(type_stats, f, indent=2, ensure_ascii=False)

        return results
