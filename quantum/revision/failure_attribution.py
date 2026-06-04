import os
import json
from typing import Dict, Any, List
from quantum.theory.theory_memory import TheoryMemory

class FailureAttributionEngine:
    """
    Component A: Failure Attribution Engine.
    Classifies failed prediction rules into physical error categories based on
    replication, calibration, adversarial, and OOD validation logs.
    """

    def __init__(self, db_path: str = "theory_memory.db"):
        self.memory = TheoryMemory(db_path=db_path)

    def attribute_failures(
        self,
        rep_report: List[Dict[str, Any]],
        cal_report: List[Dict[str, Any]],
        adv_report: List[Dict[str, Any]],
        ood_report: List[Dict[str, Any]],
        mech_report: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        
        rep_map = {r["id"]: r for r in rep_report}
        cal_map = {r["id"]: r for r in cal_report}
        adv_map = {r["id"]: r for r in adv_report}
        ood_map = {r["id"]: r for r in ood_report}
        mech_map = {r["theory_id"]: r for r in mech_report}
        
        predictions = self.memory.get_all_predictions()
        theories = {t["id"]: t for t in self.memory.get_all_theories()}
        attributions = []

        for pred in predictions:
            p_id = pred["id"]
            t_id = pred["originating_theory"]
            theory = theories.get(t_id, {})
            
            rep = rep_map.get(p_id, {})
            cal = cal_map.get(p_id, {})
            adv = adv_map.get(p_id, {})
            ood = ood_map.get(p_id, {})
            mech = mech_map.get(t_id, {})
            
            # Check if prediction was confirmed on hardware
            # (FDR adjustment is confirmed if replication rate >= 80%)
            is_confirmed = (rep.get("replication_rate", 0.0) >= 0.80)
            
            if is_confirmed:
                attributions.append({
                    "id": p_id,
                    "status": "CONFIRMED",
                    "failure_cause": None,
                    "rationale": "Prediction replicated successfully on physical backends."
                })
                continue

            # Attribute failure cause
            cause = "Unknown cause"
            rationale = "No dominant failure signature discovered."

            # 1. Mechanism failure: Causal edge is not verified on hardware
            if mech and mech.get("status") == "FAILED":
                cause = "Mechanism failure"
                rationale = "Proposed causal path variables are statistically decoupled (|r| < 0.15) under physical noise."
            
            # 2. OOD transfer failure: High IBM replication, low trapped-ion/neutral atom
            elif ood and ood.get("ood_transfer_score", 0.0) < 0.40:
                cause = "OOD transfer failure"
                rationale = "Prediction generalizes to superconducting backends but fails on trapped-ion/neutral-atom structures."
                
            # 3. Calibration-induced failure: Fails nominal/degraded, passes high_fidelity
            elif cal and cal.get("effects_by_state", {}).get("high_fidelity", 0.0) >= 0.25 and cal.get("effects_by_state", {}).get("degraded", 0.0) < 0.10:
                cause = "Calibration-induced failure"
                rationale = "Rule holds under clean calibration states but collapses under average or degraded recalibration thresholds."
                
            # 4. Noise-induced failure: High baseline, very low adversarial survival
            elif adv and adv.get("replication_rates", {}).get("baseline", 0.0) >= 0.70 and adv.get("adversarial_survival_rate", 0.0) < 0.50:
                cause = "Noise-induced failure"
                rationale = "Prediction is destroyed by circuit depth expansions and transpiler noise injections."
                
            # 5. Overfitting failure: Effect size dropped significantly across all devices
            elif rep and rep.get("replication_rate", 0.0) < 0.40:
                cause = "Overfitting failure"
                rationale = "Signal is non-existent on hardware, suggesting simulated correlations were overfitting artifacts."
                
            # 6. Statistical instability: High variance in repetition outcomes
            elif rep and any(det.get("effect_stability", 0.0) > 0.15 for det in rep.get("device_details", {}).values()):
                cause = "Statistical instability"
                rationale = "Standard deviation of repetition effect sizes is extremely high, causing prediction fluctuations."

            attributions.append({
                "id": p_id,
                "status": "FAILED",
                "failure_cause": cause,
                "rationale": rationale
            })

        # Save to JSON
        with open("failure_cause_report.json", "w", encoding="utf-8") as f:
            json.dump(attributions, f, indent=2, ensure_ascii=False)
            
        # Compile FAILURE_CAUSE_REPORT.md
        self._write_markdown_report(attributions)

        return attributions

    def _write_markdown_report(self, attributions: List[Dict[str, Any]]) -> None:
        lines = [
            "# Failure Cause Attribution Report — Phase 2D",
            "",
            "Categorizes experimental prediction failures on physical hardware to understand where theories broke down.",
            "",
            "## Failure Attribution Standing",
            "",
            "| Prediction ID | Status | Primary Failure Cause | Rationale |",
            "| :---: | :---: | :--- | :--- |"
        ]
        
        for attr in attributions:
            cause_str = f"**`{attr['failure_cause']}`**" if attr["failure_cause"] else "*N/A (Replicated)*"
            lines.append(f"| `{attr['id']}` | `{attr['status']}` | {cause_str} | {attr['rationale']} |")
            
        lines.append("")
        
        with open("docs/FAILURE_CAUSE_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
        print("Generated docs/FAILURE_CAUSE_REPORT.md")

if __name__ == "__main__":
    eng = FailureAttributionEngine()
    print(eng.attribute_failures([], [], [], [], []))
