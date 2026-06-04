import os
import json
import math
import random
from typing import Dict, Any, List

class FDRAudit:
    """
    Component H: FDR Audit.
    Applies Benjamini-Hochberg (BH) and Benjamini-Yekutieli (BY) corrections to control false discovery rates.
    """

    def __init__(self, laws_path: str = "accepted_laws.json", output_path: str = "fdr_report.json"):
        self.laws_path = laws_path
        self.output_path = output_path
        self.report: Dict[str, Any] = {}

    def load_laws(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.laws_path):
            from quantum.law_validation.replication_engine import LawReplicationEngine
            engine = LawReplicationEngine(laws_path=self.laws_path)
            return engine.get_or_create_laws()
        with open(self.laws_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def run_fdr_audit(self) -> Dict[str, Any]:
        print("Running FDR Audit (BH and BY adjustments)...")
        laws = self.load_laws()
        m = len(laws)
        
        # 1. Model raw p-values for each law
        # Validated laws have very small p-values
        rng = random.Random(432)
        raw_p_values = []
        for law in laws:
            precision = law["precision"]
            # z-score approximation of precision vs random guessing
            z = (precision - 0.5) / 0.05
            p_val = 0.5 * (1.0 - math.erf(abs(z) / math.sqrt(2.0)))
            p_val = max(1e-15, p_val)
            raw_p_values.append((law["id"], law["rule"], p_val))
            
        # Sort by p-value
        raw_p_values.sort(key=lambda x: x[2])
        
        # 2. Benjamini-Hochberg (BH)
        bh_adjusted = []
        for idx, (law_id, rule_str, p_val) in enumerate(raw_p_values):
            rank = idx + 1
            p_adj_bh = p_val * m / rank
            p_adj_bh = min(1.0, p_adj_bh)
            bh_adjusted.append((law_id, rule_str, p_val, p_adj_bh))
            
        # 3. Benjamini-Yekutieli (BY)
        # BY factor = sum(1/i for i in 1..m)
        by_factor = sum(1.0 / i for i in range(1, m + 1))
        by_adjusted = []
        for idx, (law_id, rule_str, p_val, p_adj_bh) in enumerate(bh_adjusted):
            p_adj_by = p_adj_bh * by_factor
            p_adj_by = min(1.0, p_adj_by)
            by_adjusted.append({
                "id": law_id,
                "rule": rule_str,
                "raw_p_value": round(p_val, 6),
                "q_value_bh": round(p_adj_bh, 6),
                "q_value_by": round(p_adj_by, 6)
            })
            
        # 4. Estimate Expected False Laws and FDR
        # FDR is the average q_value of the significant rejected hypotheses
        fdr_val = sum(item["q_value_bh"] for item in by_adjusted) / m
        expected_false_laws = fdr_val * m
        
        self.report = {
            "expected_false_laws": round(expected_false_laws, 4),
            "average_fdr": round(fdr_val, 4),
            "by_factor": round(by_factor, 4),
            "laws_p_values": by_adjusted
        }
        
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
            
        print(f"FDR Audit complete. Expected False Laws: {expected_false_laws:.4f}. Report: {self.output_path}")
        return self.report

if __name__ == "__main__":
    audit = FDRAudit()
    audit.run_fdr_audit()
