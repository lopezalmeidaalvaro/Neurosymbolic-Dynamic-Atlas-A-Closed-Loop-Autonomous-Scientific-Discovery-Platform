import os
import json
import numpy as np
from typing import Dict, Any, List
from quantum.theory.theory_memory import TheoryMemory

class RealityGapQuantificationEngine:
    """
    Component H: Reality Gap Quantification.
    Computes RealityGap = SimulationScore - HardwareScore across Laws, Mechanisms, Theories, and Predictions.
    Generates REALITY_GAP_REPORT.md and reality_gap_report.json.
    """

    def __init__(self, db_path: str = "theory_memory.db"):
        self.memory = TheoryMemory(db_path=db_path)

    def quantify_reality_gap(
        self,
        rep_report_path: str = "hardware_replication_report.json",
        survival_report_path: str = "surviving_mechanisms.json"
    ) -> Dict[str, Any]:
        
        # Load reports
        with open(rep_report_path, "r", encoding="utf-8") as f:
            rep_data = json.load(f)
        with open(survival_report_path, "r", encoding="utf-8") as f:
            survival_data = json.load(f)

        rep_map = {r["id"]: r for r in rep_data}
        survival_map = {item["theory_id"]: item for item in survival_data}

        theories = self.memory.get_all_theories()
        predictions = self.memory.get_all_predictions()

        # 1. Predictions Reality Gap
        pred_gaps = []
        for pred in predictions:
            p_id = pred["id"]
            if p_id not in rep_map:
                continue
            rep = rep_map[p_id]
            sim_score = pred["effect_size"]
            # HardwareScore is the average mean effect on physical hardware
            mean_effects = [dev["mean_effect"] for dev in rep.get("device_details", {}).values()]
            hw_score = float(np.mean(mean_effects)) if mean_effects else 0.0
            
            pred_gaps.append({
                "id": p_id,
                "sim_score": round(sim_score, 4),
                "hw_score": round(hw_score, 4),
                "reality_gap": round(sim_score - hw_score, 4)
            })

        # 2. Mechanisms Reality Gap
        mech_gaps = []
        for item in survival_data:
            t_id = item["theory_id"]
            for edge in item["edges"]:
                sim_score = abs(edge["sim_weight"])
                hw_score = abs(edge["physical_correlation"])
                mech_gaps.append({
                    "theory_id": t_id,
                    "edge": f"{edge['source']} -> {edge['target']}",
                    "sim_score": round(sim_score, 4),
                    "hw_score": round(hw_score, 4),
                    "reality_gap": round(sim_score - hw_score, 4)
                })

        # 3. Theories Reality Gap
        theory_gaps = []
        for theory in theories:
            t_id = theory["id"]
            # Use original theories before revision for baseline theory gap
            if "_REV" in t_id or "_HYB" in t_id:
                continue
                
            sim_score = theory["confidence"]
            
            # Hardware score as average prediction replication rate
            reps = []
            for p_id in theory["predictions"]:
                if p_id in rep_map:
                    reps.append(rep_map[p_id].get("replication_rate", 0.0))
            hw_score = float(np.mean(reps)) if reps else 0.0
            
            theory_gaps.append({
                "id": t_id,
                "sim_score": round(sim_score, 4),
                "hw_score": round(hw_score, 4),
                "reality_gap": round(sim_score - hw_score, 4)
            })

        # 4. Laws Reality Gap
        # Map laws explained to the predictions that test them
        law_gaps = []
        law_to_preds = {}
        for theory in theories:
            if "_REV" in theory["id"] or "_HYB" in theory["id"]:
                continue
            for law in theory["laws_explained"]:
                law_to_preds.setdefault(law, []).extend(theory["predictions"])

        for law, p_ids in law_to_preds.items():
            sim_score = 1.0 # Laws accepted in simulation have 1.0 validation status
            reps = []
            for p_id in set(p_ids):
                if p_id in rep_map:
                    reps.append(rep_map[p_id].get("replication_rate", 0.0))
            hw_score = float(np.mean(reps)) if reps else 0.0
            
            law_gaps.append({
                "id": law,
                "sim_score": round(sim_score, 4),
                "hw_score": round(hw_score, 4),
                "reality_gap": round(sim_score - hw_score, 4)
            })

        results = {
            "predictions": pred_gaps,
            "mechanisms": mech_gaps,
            "theories": theory_gaps,
            "laws": law_gaps,
            "summary": {
                "mean_prediction_gap": round(float(np.mean([x["reality_gap"] for x in pred_gaps])), 4) if pred_gaps else 0.0,
                "mean_mechanism_gap": round(float(np.mean([x["reality_gap"] for x in mech_gaps])), 4) if mech_gaps else 0.0,
                "mean_theory_gap": round(float(np.mean([x["reality_gap"] for x in theory_gaps])), 4) if theory_gaps else 0.0,
                "mean_law_gap": round(float(np.mean([x["reality_gap"] for x in law_gaps])), 4) if law_gaps else 0.0
            }
        }

        # Save to JSON
        with open("reality_gap_report.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        # Write markdown docs/REALITY_GAP_REPORT.md
        self._write_markdown_report(results)

        return results

    def _write_markdown_report(self, results: Dict[str, Any]) -> None:
        lines = [
            "# Reality Gap Quantification Report — Phase 2D / 3A.1",
            "",
            "Measures the divergence between simulated expectations and hardware realities ($RealityGap = Score_{sim} - Score_{hardware}$) across all scientific layers.",
            "",
            "## Executive Summary",
            "",
            f"- **Mean Law Reality Gap**: `{results['summary']['mean_law_gap']:.4f}`",
            f"- **Mean Theory Reality Gap**: `{results['summary']['mean_theory_gap']:.4f}`",
            f"- **Mean Mechanism Reality Gap**: `{results['summary']['mean_mechanism_gap']:.4f}`",
            f"- **Mean Prediction Reality Gap**: `{results['summary']['mean_prediction_gap']:.4f}`",
            "",
            "## 1. Laws Reality Gap",
            "",
            "| Law ID | Simulation Score | Hardware Score | Reality Gap |",
            "| :---: | :---: | :---: | :---: |"
        ]
        for item in results["laws"]:
            lines.append(f"| `{item['id']}` | {item['sim_score']:.4f} | {item['hw_score']:.4f} | **{item['reality_gap']:.4f}** |")
            
        lines.append("")
        lines.append("## 2. Theories Reality Gap")
        lines.append("")
        lines.append("| Theory ID | Simulation Score | Hardware Score | Reality Gap |")
        lines.append("| :--- | :---: | :---: | :---: |")
        for item in results["theories"]:
            lines.append(f"| `{item['id']}` | {item['sim_score']:.4f} | {item['hw_score']:.4f} | **{item['reality_gap']:.4f}** |")
            
        lines.append("")
        lines.append("## 3. Mechanisms Reality Gap")
        lines.append("")
        lines.append("| Theory ID | Causal Pathway Edge | Simulation Weight | Hardware Correlation | Reality Gap |")
        lines.append("| :--- | :--- | :---: | :---: | :---: |")
        for item in results["mechanisms"]:
            lines.append(f"| `{item['theory_id']}` | `{item['edge']}` | {item['sim_score']:.4f} | {item['hw_score']:.4f} | **{item['reality_gap']:.4f}** |")
            
        lines.append("")
        lines.append("## 4. Predictions Reality Gap")
        lines.append("")
        lines.append("| Prediction ID | Simulation Expected Effect | Hardware Mean Observed | Reality Gap |")
        lines.append("| :---: | :---: | :---: | :---: |")
        for item in results["predictions"]:
            lines.append(f"| `{item['id']}` | {item['sim_score']:.4f} | {item['hw_score']:.4f} | **{item['reality_gap']:.4f}** |")
            
        lines.append("")
        
        with open("docs/REALITY_GAP_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
        print("Generated docs/REALITY_GAP_REPORT.md")

if __name__ == "__main__":
    eng = RealityGapQuantificationEngine()
    print("Reality gap summary:", eng.quantify_reality_gap()["summary"])
