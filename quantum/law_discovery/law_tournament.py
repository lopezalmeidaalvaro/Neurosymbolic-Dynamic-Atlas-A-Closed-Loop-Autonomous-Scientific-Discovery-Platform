import os
import json
from typing import Dict, Any, List

class LawTournament:
    """
    Component I: Law Tournament.
    Compares discovered candidate/causal laws against existing baseline laws, ranking them in a leaderboard.
    """

    def __init__(self, validation_path: str = "causal_law_validation.json", falsification_path: str = "law_falsification_report.json", baseline_path: str = "transferability_rules.json", output_path: str = "law_leaderboard.json"):
        self.validation_path = validation_path
        self.falsification_path = falsification_path
        self.baseline_path = baseline_path
        self.output_path = output_path
        self.leaderboard: List[Dict[str, Any]] = []

    def load_json(self, path: str) -> List[Any]:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def run_tournament(self) -> List[Dict[str, Any]]:
        print("Running Law Tournament...")
        val_data = self.load_json(self.validation_path)
        fal_data = self.load_json(self.falsification_path)
        baselines = self.load_json(self.baseline_path)
        
        # Build map of validation and falsification records by ID/Rule
        val_map = {item["rule"]: item for item in val_data}
        fal_map = {item["rule"]: item for item in fal_data}
        
        all_competitors = []
        
        # 1. Process Discovered Laws
        for item in val_data:
            rule_str = item["rule"]
            law_id = item["id"]
            
            val_metrics = item.get("metrics", {})
            fal_metrics = fal_map.get(rule_str, {}).get("metrics", {})
            survival_score = fal_map.get(rule_str, {}).get("survival_score", 0.5)
            
            precision = val_metrics.get("base_f1", 0.5) # using F1 as a proxy
            mcc = val_metrics.get("base_mcc", 0.0)
            coverage = val_metrics.get("base_auc", 0.5) # using AUC as proxy for performance coverage
            generalization = fal_metrics.get("holdout_precision", 0.5)
            causality = val_metrics.get("counterfactual_effect", 0.0)
            robustness = survival_score
            
            # Weighted Composite Tournament Score
            score = (0.2 * precision) + (0.2 * max(0.0, mcc)) + (0.2 * generalization) + (0.2 * max(0.0, causality)) + (0.2 * robustness)
            
            competitor = {
                "id": law_id,
                "rule": rule_str,
                "type": "DISCOVERED",
                "precision": round(precision, 4),
                "mcc": round(mcc, 4),
                "coverage": round(coverage, 4),
                "generalization": round(generalization, 4),
                "causality_score": round(causality, 4),
                "robustness": round(robustness, 4),
                "tournament_score": round(score, 4)
            }
            all_competitors.append(competitor)
            
        # 2. Process Baseline Laws
        for idx, base in enumerate(baselines):
            rule_str = base.get("rule", "IF unknown THEN success = True")
            
            # Baseline performance stats (we can approximate using baseline metrics, or assign standard values)
            precision = base.get("precision", 0.6)
            coverage = base.get("coverage", 0.5)
            mcc = 0.35 # Standard baseline MCC
            generalization = 0.55
            causality = 0.20
            robustness = 0.58
            
            score = (0.2 * precision) + (0.2 * mcc) + (0.2 * generalization) + (0.2 * causality) + (0.2 * robustness)
            
            competitor = {
                "id": f"BASE_{idx+1:03d}",
                "rule": rule_str,
                "type": "BASELINE",
                "precision": round(precision, 4),
                "mcc": round(mcc, 4),
                "coverage": round(coverage, 4),
                "generalization": round(generalization, 4),
                "causality_score": round(causality, 4),
                "robustness": round(robustness, 4),
                "tournament_score": round(score, 4)
            }
            all_competitors.append(competitor)
            
        # Sort leaderboard by tournament score
        all_competitors.sort(key=lambda x: x["tournament_score"], reverse=True)
        self.leaderboard = all_competitors
        
        # Save Leaderboard
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.leaderboard, f, indent=2, ensure_ascii=False)
            
        print(f"Law Tournament complete. Created leaderboard with {len(self.leaderboard)} entries. Output: {self.output_path}")
        return self.leaderboard

if __name__ == "__main__":
    tournament = LawTournament()
    tournament.run_tournament()
