import os
import json
from typing import Dict, Any

class IndependentEpistemicVerdictEvaluator:
    """
    Phase 3B.2H: Epistemic Classification.
    Consolidates tournament results, cross-lab agreement, leakage audits,
    and external challenge metrics to output a final scientific reproducibility category.
    """

    def run_epistemic_evaluation(
        self,
        replication_rate: float,
        cross_lab_agreement: float,
        leakage_score: float,
        improvement_percent: float,
        prediction_equivalence: float,
        checksum_passed: bool,
        external_reimplementation_passed: bool
    ) -> str:
        
        # Check all conditions simultaneously for SCIENTIFICALLY_REPRODUCIBLE_THEORY
        replication_ok = replication_rate >= 0.90
        cross_lab_ok = cross_lab_agreement >= 0.90
        leakage_ok = leakage_score < 0.01
        improvement_ok = improvement_percent >= 15.0
        equivalence_ok = prediction_equivalence >= 0.99
        checksum_ok = checksum_passed
        external_ok = external_reimplementation_passed

        all_passed = (
            replication_ok and 
            cross_lab_ok and 
            leakage_ok and 
            improvement_ok and 
            equivalence_ok and 
            checksum_ok and 
            external_ok
        )

        if all_passed:
            verdict = "SCIENTIFICALLY_REPRODUCIBLE_THEORY"
        elif replication_ok and improvement_ok and leakage_ok:
            verdict = "INDEPENDENTLY_REPRODUCIBLE_THEORY"
        elif replication_ok or improvement_ok:
            verdict = "REPRODUCIBLE_THEORY"
        else:
            verdict = "FAILED_REPRODUCTION"

        # Write docs/FINAL_REPRODUCTION_VERDICT.md
        self._write_markdown_report(
            verdict,
            replication_rate,
            cross_lab_agreement,
            leakage_score,
            improvement_percent,
            prediction_equivalence,
            checksum_passed,
            external_reimplementation_passed
        )

        return verdict

    def _write_markdown_report(
        self,
        verdict: str,
        rep_rate: float,
        lab_agree: float,
        leak_score: float,
        imp_percent: float,
        eq_percent: float,
        checksum: bool,
        external: bool
    ) -> None:
        
        lines = [
            "# Final Reproduction Verdict — Phase 3B.2",
            "",
            "Presents the official epistemic status assignment for RTHEORY_001 under independent validation tests.",
            "",
            "## Epistemic Decision Verdict",
            "",
            f"> [!IMPORTANT]",
            f"> **Scientific Classification Verdict**: **`{verdict}`**",
            "",
            "## Mandatory Reproducibility Checklist",
            "",
            f"- [x] **Replication Success Rate (>= 90.0%)**: `{'PASSED' if rep_rate >= 0.90 else 'FAILED'}` (`{rep_rate*100:.2f}%`)",
            f"- [x] **Cross-Lab Implementation Agreement (>= 90.0%)**: `{'PASSED' if lab_agree >= 0.90 else 'FAILED'}` (`{lab_agree*100:.2f}%`)",
            f"- [x] **Leakage Forensics Score (< 1.0%)**: `{'PASSED' if leak_score < 0.01 else 'FAILED'}` (`{leak_score*100:.2f}%`)",
            f"- [x] **Prediction Error Improvement (>= 15.0%)**: `{'PASSED' if imp_percent >= 15.0 else 'FAILED'}` (`{imp_percent:.2f}%` MAE reduction)",
            f"- [x] **Clean-Room Prediction Equivalence (>= 99.0%)**: `{'PASSED' if eq_percent >= 0.99 else 'FAILED'}` (`{eq_percent*100:.2f}%`)",
            f"- [x] **Checksum Integrity (100.0%)**: `{'PASSED' if checksum else 'FAILED'}`",
            f"- [x] **External Reimplementation Challenge**: `{'PASSED' if external else 'FAILED'}`",
            ""
        ]

        os.makedirs("docs", exist_ok=True)
        with open("docs/FINAL_REPRODUCTION_VERDICT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
