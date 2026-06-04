import os
import json
from typing import Dict, Any

class EvidenceConsensusEngine:
    """
    Component N: Final Consensus Engine.
    Evaluates evidence scores against scientific acceptance criteria and issues the finalallowed verdict
    (DISCOVERY_READY, PARTIALLY_SUFFICIENT_EVIDENCE, or INSUFFICIENT_HARDWARE_EVIDENCE).
    """

    def __init__(self):
        pass

    def evaluate_consensus(
        self,
        inventory_results: Dict[str, Any],
        ess_results: Dict[str, Any],
        leakage_results: Dict[str, Any],
        vendor_results: Dict[str, Any],
        tech_results: Dict[str, Any],
        cal_results: Dict[str, Any],
        bench_results: Dict[str, Any],
        corr_results: Dict[str, Any],
        stress_results: Dict[str, Any],
        readiness_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        # Check all criteria thresholds
        criteria = {
            "ESS > 500": ess_results["global_ess"] >= 500,
            "Evidence Independence > 90%": leakage_results["evidence_independence_score"] >= 0.90,
            "Leakage Score < 5%": leakage_results["leakage_score"] < 0.05,
            "Technology Diversity >= 3": tech_results["active_paradigms_count"] >= 3,
            "Vendor Diversity >= 4": inventory_results["unique_vendors"] >= 4,
            "Calibration Diversity >= 20": cal_results["unique_calibration_states_count"] >= 20,
            "Benchmark Diversity >= 10": bench_results["number_of_represented_families"] >= 10,
            "Correlation Stability >= 80%": corr_results["correlation_stability_percentage"] >= 80.0,
            "Evidence Robustness >= 85%": stress_results["evidence_robustness_score"] >= 0.85
        }

        # Calculate consolidation scores
        evidence_sufficiency = round(float(ess_results["global_ess"] / 500.0), 4)
        evidence_independence = leakage_results["evidence_independence_score"]
        hardware_diversity = round(float(tech_results["active_paradigms_count"] / 5.0), 4)
        leakage_score = leakage_results["leakage_score"]
        readiness_score = readiness_results["discovery_readiness_score"]

        # Calculate Epistemic Confidence Score (average of compliance ratios)
        compliance_ratio = sum(1 for v in criteria.values() if v) / len(criteria)
        epistemic_confidence = round(float(compliance_ratio), 4)

        # Determine allowed final verdict
        all_passed = all(criteria.values())
        if all_passed and readiness_score >= 0.80 and epistemic_confidence >= 0.80:
            verdict = "DISCOVERY_READY"
            reason = "The accumulated hardware evidence is scientifically sufficient and epistemically valid. All criteria pass, allowing transition to Phase 3B."
        elif compliance_ratio >= 0.70:
            verdict = "PARTIALLY_SUFFICIENT_EVIDENCE"
            reason = "Most criteria pass, but minor deficiencies remain in calibration or technology representation, blocking Phase 3B."
        else:
            verdict = "INSUFFICIENT_HARDWARE_EVIDENCE"
            reason = "Critical thresholds are violated. The evidence base is insufficient to support reality-native theory discovery, blocking Phase 3B."

        consensus = {
            "evidence_sufficiency_score": evidence_sufficiency,
            "evidence_independence_score": evidence_independence,
            "hardware_diversity_score": hardware_diversity,
            "leakage_score": leakage_score,
            "discovery_readiness_score": readiness_score,
            "epistemic_confidence_score": epistemic_confidence,
            "criteria_compliance": criteria,
            "verdict": verdict,
            "reason": reason
        }

        # Write docs/FINAL_PHASE_3A5_VERDICT.md
        self._write_markdown_report(consensus)

        return consensus

    def _write_markdown_report(self, results: Dict[str, Any]) -> None:
        lines = [
            "# Final Phase 3A.5 Scientific Verdict Report",
            "",
            "## Consensus Verdict",
            "",
            f"**`{results['verdict']}`**",
            "",
            "### Rationale",
            "",
            results["reason"],
            "",
            "## Consolidation Scores Ledger",
            "",
            f"- **Evidence Sufficiency Score**: `{results['evidence_sufficiency_score']:.4f}` (Kish ESS relative to discovery baseline)",
            f"- **Evidence Independence Score**: `{results['evidence_independence_score']*100:.2f}%` (Unleaked independent variance)",
            f"- **Hardware Diversity Score**: `{results['hardware_diversity_score']:.4f}` (Technology balance index)",
            f"- **Leakage Score**: `{results['leakage_score']*100:.2f}%`",
            f"- **Discovery Readiness Score**: **`{results['discovery_readiness_score']:.4f}`** (Target >= 0.80)",
            f"- **Epistemic Confidence Score**: **`{results['epistemic_confidence_score']*100:.2f}%`** (Target >= 80.0%)",
            "",
            "## Scientific Acceptance Criteria Compliance",
            "",
            "| Scientific Acceptance Criterion | Evaluation Result | Compliance Status |",
            "| :--- | :---: | :--- |"
        ]
        
        for criterion, passed in results["criteria_compliance"].items():
            status = "**`PASSED`**" if passed else "`FAILED`"
            lines.append(f"| {criterion} | {str(passed)} | {status} |")
            
        lines.append("")
        
        os.makedirs("docs", exist_ok=True)
        with open("docs/FINAL_PHASE_3A5_VERDICT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

if __name__ == "__main__":
    engine = EvidenceConsensusEngine()
    print(engine.evaluate_consensus(
        {"unique_vendors": 4},
        {"global_ess": 550},
        {"evidence_independence_score": 0.98, "leakage_score": 0.02},
        {"vendor_independence_score": 0.95, "exclusive_dependencies_found": False},
        {"active_paradigms_count": 4, "technology_diversity_score": 0.85},
        {"unique_calibration_states_count": 22, "calibration_diversity_score": 1.0},
        {"number_of_represented_families": 11, "benchmark_coverage_score": 1.0},
        {"correlation_stability_percentage": 90.0},
        {"evidence_robustness_score": 0.92},
        {"discovery_readiness_score": 0.94}
    ))
