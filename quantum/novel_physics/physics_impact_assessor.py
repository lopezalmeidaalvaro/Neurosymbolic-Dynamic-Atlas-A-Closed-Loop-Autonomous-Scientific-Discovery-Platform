import os
from typing import Dict, Any, List

class PhysicsImpactAssessor:
    """
    Phase 4K: Physics Impact Assessment.
    Evaluates new physics candidate theories and assigns impact classification.
    """

    def classify_impact(
        self,
        novel_effects_count: int,
        verification_rate: float,
        elimination_rate: float,
        replication_equivalence: float
    ) -> str:
        
        # Criteria checks
        has_novel = novel_effects_count >= 1
        verified = verification_rate >= 0.70
        eliminated = elimination_rate >= 0.70
        replicated = replication_equivalence >= 0.90

        if has_novel and verified and eliminated and replicated:
            classification = "STRONG_NEW_PHYSICS_CANDIDATE"
        elif has_novel and verified and eliminated:
            classification = "POTENTIAL_NEW_PHYSICS"
        elif has_novel and verified:
            classification = "UNEXPLAINED_EFFECT"
        elif has_novel:
            classification = "PHENOMENOLOGICAL_EFFECT"
        else:
            classification = "KNOWN_PHYSICS"

        self._write_markdown_report(classification, novel_effects_count, verification_rate, elimination_rate, replication_equivalence)
        return classification

    def _write_markdown_report(
        self,
        classification: str,
        novel_count: int,
        val_rate: float,
        elim_rate: float,
        repl_equiv: float
    ) -> None:
        lines = [
            "# Physics Impact Assessment Report — Phase 4K",
            "",
            "Classifies the impact score and validity level of the candidate new physics theories.",
            "",
            "## Impact Category Classification",
            "",
            f"> [!IMPORTANT]",
            f"> **Assessed Impact Classification**: **`{classification}`**",
            "",
            "## Score Breakdown Metric Checklist",
            "",
            f"- [x] **Detected Novel Physical Effects (>= 1)**: `{'PASSED' if novel_count >= 1 else 'FAILED'}` (Count: `{novel_count}`)",
            f"- [x] **Independent Hardware Verification Rate (>= 70.0%)**: `{'PASSED' if val_rate >= 0.70 else 'FAILED'}` (Rate: `{val_rate*100:.2f}%`)",
            f"- [x] **Conventional Explanations Eliminated (>= 70.0%)**: `{'PASSED' if elim_rate >= 0.70 else 'FAILED'}` (Rate: `{elim_rate*100:.2f}%`)",
            f"- [x] **Cross-Lab Replication Equivalence (>= 90.0%)**: `{'PASSED' if repl_equiv >= 0.90 else 'FAILED'}` (Rate: `{repl_equiv*100:.2f}%`)",
            ""
        ]

        os.makedirs("docs", exist_ok=True)
        with open("docs/NOVEL_PHYSICS_IMPACT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
