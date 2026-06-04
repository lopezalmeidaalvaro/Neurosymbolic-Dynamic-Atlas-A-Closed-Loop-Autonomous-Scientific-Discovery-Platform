import os
import json
import math
from typing import Dict, Any, List

class HoldoutValidation:
    """
    Component C: Domain Holdout Challenge.
    Trains laws on training domains and validates them on holdout target domains.
    """

    def __init__(self, laws_path: str = "accepted_laws.json", data_path: str = "observation_dataset.json", output_path: str = "holdout_report.json"):
        self.laws_path = laws_path
        self.data_path = data_path
        self.output_path = output_path
        self.report: List[Dict[str, Any]] = []

    def load_data(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.data_path):
            from quantum.law_discovery.scientific_observer import ScientificObserver
            observer = ScientificObserver(output_path=self.data_path)
            observer.generate_large_scale_dataset(target_count=1000)
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_laws(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.laws_path):
            from quantum.law_validation.replication_engine import LawReplicationEngine
            engine = LawReplicationEngine(laws_path=self.laws_path)
            return engine.get_or_create_laws()
        with open(self.laws_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def check_antecedents(self, obs: Dict[str, Any], rule_str: str) -> bool:
        satisfied = True
        if "gate_entropy < 0.25" in rule_str and obs["gate_entropy"] >= 0.25:
            satisfied = False
        if "stabilizer_overlap > 0.6" in rule_str and obs["stabilizer_overlap"] <= 0.6:
            satisfied = False
        if "tensor_rank < 3" in rule_str and obs["tensor_rank"] >= 3:
            satisfied = False
        if "clifford_ratio > 0.7" in rule_str and obs["clifford_ratio"] <= 0.7:
            satisfied = False
        if "betweenness_centrality > 0.25" in rule_str and obs["betweenness_centrality"] <= 0.25:
            satisfied = False
        return satisfied

    def run_holdouts(self) -> List[Dict[str, Any]]:
        print("Running Domain Holdout Validation...")
        observations = self.load_data()
        laws = self.load_laws()
        self.report = []
        
        train_domains = {"Bell", "GHZ", "QAOA"}
        # Holdouts matches standard non-train domains
        
        train_obs = [obs for obs in observations if obs["domain"] in train_domains]
        holdout_obs = [obs for obs in observations if obs["domain"] not in train_domains]
        
        for law in laws:
            rule_str = law["rule"]
            law_id = law["id"]
            consequent = law["consequent"]
            
            # Binary target threshold
            threshold = 0.6 if consequent in ["synergy", "novelty"] else 0.7
            
            def evaluate_split(split_data):
                tp = fp = fn = tn = 0
                for obs in split_data:
                    ant_sat = self.check_antecedents(obs, rule_str)
                    cons_val = obs[consequent]
                    cons_sat = (cons_val >= threshold)
                    
                    if ant_sat and cons_sat:
                        tp += 1
                    elif ant_sat and not cons_sat:
                        fp += 1
                    elif not ant_sat and cons_sat:
                        fn += 1
                    elif not ant_sat and not cons_sat:
                        tn += 1
                        
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
                
                denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
                mcc = (tp * tn - fp * fn) / denom if denom > 0 else 0.0
                
                tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                tnr = tn / (tn + fp) if (tn + fp) > 0 else 0.0
                auc = 0.5 * (tpr + tnr)
                return f1, mcc, auc, precision
                
            train_f1, train_mcc, train_auc, train_prec = evaluate_split(train_obs)
            holdout_f1, holdout_mcc, holdout_auc, holdout_prec = evaluate_split(holdout_obs)
            
            # Generalization gap is training accuracy minus holdout accuracy
            generalization_gap = abs(train_prec - holdout_prec)
            
            record = {
                "id": law_id,
                "rule": rule_str,
                "consequent": consequent,
                "metrics": {
                    "train_f1": round(train_f1, 4),
                    "train_auc": round(train_auc, 4),
                    "train_precision": round(train_prec, 4),
                    "holdout_f1": round(holdout_f1, 4),
                    "holdout_auc": round(holdout_auc, 4),
                    "holdout_mcc": round(holdout_mcc, 4),
                    "generalization_gap": round(generalization_gap, 4)
                }
            }
            self.report.append(record)
            
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
            
        print(f"Domain holdout challenge completed. Saved results to: {self.output_path}")
        return self.report

if __name__ == "__main__":
    validation = HoldoutValidation()
    validation.run_holdouts()
