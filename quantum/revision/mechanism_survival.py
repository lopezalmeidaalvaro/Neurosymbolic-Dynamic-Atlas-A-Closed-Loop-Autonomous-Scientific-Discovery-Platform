import os
import json
from typing import Dict, Any, List

class MechanismSurvivalAnalysis:
    """
    Component B: Mechanism Survival Analysis.
    Evaluates every causal graph transition edge from simulator theories,
    quantifying their survival ratio and effect preservation on physical quantum backends.
    """

    def __init__(self):
        pass

    def evaluate_mechanism_survival(self, physical_mechanism_report: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Computes survival ratios and effect preservation across all causal edges.
        """
        results = []

        for theory_report in physical_mechanism_report:
            t_id = theory_report["theory_id"]
            edges = theory_report["edge_details"]
            
            evaluated_edges = []
            survived_count = 0
            
            for edge in edges:
                src = edge["source"]
                tgt = edge["target"]
                sim_w = edge["sim_weight"]
                phy_c = edge["physical_correlation"]
                
                # Compute Survival Ratio
                if abs(sim_w) > 0:
                    survival_ratio = abs(phy_c) / abs(sim_w)
                else:
                    survival_ratio = 0.0
                    
                # Determine Effect Preservation Status
                if abs(phy_c) < 0.10:
                    preservation = "ELIMINATED"
                elif np.sign(sim_w) == np.sign(phy_c):
                    preservation = "PRESERVED"
                    survived_count += 1
                else:
                    preservation = "REVERSED"

                evaluated_edges.append({
                    "source": src,
                    "target": tgt,
                    "sim_weight": round(sim_w, 4),
                    "physical_correlation": round(phy_c, 4),
                    "survival_ratio": round(survival_ratio, 4),
                    "preservation": preservation
                })

            survival_rate = survived_count / len(edges) if edges else 0.0
            
            results.append({
                "theory_id": t_id,
                "overall_survival_rate": round(survival_rate, 4),
                "edges": evaluated_edges
            })

        # Save to JSON
        with open("surviving_mechanisms.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        # Write markdown report docs/SURVIVING_MECHANISMS.md
        self._write_markdown_report(results)

        return results

    def _write_markdown_report(self, results: List[Dict[str, Any]]) -> None:
        lines = [
            "# Surviving Causal Mechanisms Report — Phase 2D",
            "",
            "Compares simulated causal pathways against physical correlations to identify surviving and decoupled transitions.",
            ""
        ]
        
        for res in results:
            lines.append(f"### Theory `{res['theory_id']}`: Overall Survival Rate = **`{res['overall_survival_rate']*100:.1f}%`**")
            lines.append("")
            lines.append("| Causal Transition | Sim Weight | Hardware Correlation | Survival Ratio | Effect Preservation |")
            lines.append("| :--- | :---: | :---: | :---: | :---: |")
            for edge in res["edges"]:
                transition = f"`{edge['source']}` $\\rightarrow$ `{edge['target']}`"
                lines.append(f"| {transition} | {edge['sim_weight']:.4f} | {edge['physical_correlation']:.4f} | {edge['survival_ratio']:.4f} | **`{edge['preservation']}`** |")
            lines.append("")
            
        with open("docs/SURVIVING_MECHANISMS.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
        print("Generated docs/SURVIVING_MECHANISMS.md")

import numpy as np
