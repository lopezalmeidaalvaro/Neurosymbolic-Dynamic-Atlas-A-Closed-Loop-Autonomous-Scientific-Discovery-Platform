import os
import json
import sqlite3
import numpy as np
from typing import Dict, Any, List
from quantum.theory.theory_memory import TheoryMemory

class BayesianTheoryUpdatingEngine:
    """
    Component G: Bayesian Theory Updating.
    Replaces binary accept/reject logic with a continuous posterior probability calculation.
    Computes Posterior(Theory | Hardware Evidence) = Likelihood * Prior / Marginal.
    Updates the database with posterior scores.
    """

    def __init__(self, db_path: str = "theory_memory.db"):
        self.memory = TheoryMemory(db_path=db_path)

    def update_theory_probabilities(
        self,
        rep_report_path: str = "hardware_replication_report.json"
    ) -> List[Dict[str, Any]]:
        
        # Load replication data
        if not os.path.exists(rep_report_path):
            raise FileNotFoundError(f"Replication report not found at {rep_report_path}")
            
        with open(rep_report_path, "r", encoding="utf-8") as f:
            rep_data = json.load(f)
            
        rep_map = {r["id"]: r for r in rep_data}

        theories = self.memory.get_all_theories()
        
        # Calculate Likelihoods and Priors
        raw_theory_data = []
        
        for theory in theories:
            t_id = theory["id"]
            pred_ids = theory["predictions"]
            
            # Likelihood based on replication rates
            reps = []
            for p_id in pred_ids:
                if p_id in rep_map:
                    reps.append(rep_map[p_id].get("replication_rate", 0.0))
            
            mean_rep = np.mean(reps) if reps else 0.0
            
            # Prior is the simulation confidence score
            prior = theory["confidence"]
            
            # Apply adjustment factors for revised/noise-adapted/hybrid classes to likelihood
            multiplier = 1.0
            if "_REV2" in t_id:
                multiplier = 1.15
            elif "_REV3" in t_id:
                multiplier = 1.30
            elif "_HYB" in t_id:
                multiplier = 1.45
                
            likelihood = max(0.01, mean_rep * multiplier)
            
            raw_theory_data.append({
                "id": t_id,
                "name": theory["name"],
                "parent_id": t_id.split("_")[0],
                "prior": prior,
                "likelihood": likelihood
            })

        # Calculate Within-Family Posteriors (sum to 1 within family)
        families = {}
        for rtd in raw_theory_data:
            fam = rtd["parent_id"]
            families.setdefault(fam, []).append(rtd)
            
        updated_theories = []
        for fam_id, members in families.items():
            # Marginal likelihood for this family
            marginal = sum(m["prior"] * m["likelihood"] for m in members)
            if marginal == 0:
                marginal = 1.0
                
            for m in members:
                posterior = (m["prior"] * m["likelihood"]) / marginal
                m["posterior"] = round(float(posterior), 4)
                
                # Fetch original theory and save new confidence
                orig_t = self.memory.get_theory(m["id"])
                if orig_t:
                    orig_t["confidence"] = m["posterior"]
                    self.memory.save_theory(orig_t)
                    
                updated_theories.append(m)

        # Sort by family and posterior descending
        updated_theories.sort(key=lambda x: (x["parent_id"], -x["posterior"]))

        # Save report JSON
        with open("bayesian_theory_report.json", "w", encoding="utf-8") as f:
            json.dump(updated_theories, f, indent=2, ensure_ascii=False)

        # Write markdown report docs/BAYESIAN_THEORY_REPORT.md
        self._write_markdown_report(updated_theories)

        return updated_theories

    def _write_markdown_report(self, updated_theories: List[Dict[str, Any]]) -> None:
        lines = [
            "# Bayesian Theory Updating Report — Phase 2D / 3A.1",
            "",
            "Applies continuous Bayesian updating to evaluate candidate theories given hardware execution observations.",
            "",
            "## Bayesian Standing by Theory Family",
            ""
        ]
        
        current_family = None
        for item in updated_theories:
            fam = item["parent_id"]
            if fam != current_family:
                current_family = fam
                lines.append(f"### Theory Family `{fam}`")
                lines.append("")
                lines.append("| Theory ID | Description | Prior ($P(T)$) | Likelihood ($P(E \\mid T)$) | Posterior ($P(T \\mid E)$) | Status |")
                lines.append("| :--- | :--- | :---: | :---: | :---: | :--- |")
                
            status = "**`ACCEPTED`**" if item["posterior"] >= 0.40 else "`UNSUPPORTED`"
            lines.append(
                f"| `{item['id']}` | {item['name']} | "
                f"{item['prior']:.4f} | {item['likelihood']:.4f} | "
                f"**{item['posterior']:.4f}** | {status} |"
            )
            
        lines.append("")
        
        with open("docs/BAYESIAN_THEORY_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
        print("Generated docs/BAYESIAN_THEORY_REPORT.md")

if __name__ == "__main__":
    eng = BayesianTheoryUpdatingEngine()
    print("Theories updated:", len(eng.update_theory_probabilities()))
