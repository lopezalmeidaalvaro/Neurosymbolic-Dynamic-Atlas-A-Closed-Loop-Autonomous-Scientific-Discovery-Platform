import os
from typing import Dict, Any

class ScientificConsensusVerdict:
    """
    Phase XI-J: Final Scientific Standing.
    Analyzes international consensus, peer reviewer feedback, and GRADE evidence levels
    to output the final scientific verdict and class.
    """

    def __init__(self, project_root: str):
        self.project_root = project_root

    def evaluate_verdict(self, results: Dict[str, Any]) -> str:
        consensus = results.get("consensus_score", 0.0)
        grade = results.get("quality_grade", "LOW")
        rejects = results.get("reject_count", 1)
        readiness = results.get("readiness_score", 0.0)

        consensus_pass = consensus >= 0.90
        grade_pass = grade in ("VERY_HIGH", "HIGH")
        reject_pass = rejects == 0
        readiness_pass = readiness >= 0.90

        all_passes = [consensus_pass, grade_pass, reject_pass, readiness_pass]
        success_count = sum(1 for p in all_passes if p)

        if all(all_passes):
            verdict = "COMMUNITY_READY_NEW_PHYSICS_CANDIDATE"
        elif success_count >= 3:
            verdict = "STRONG_NEW_PHYSICS_CANDIDATE"
        elif success_count >= 2:
            verdict = "SCIENTIFIC_THEORY"
        elif success_count >= 1:
            verdict = "REPRODUCIBLE_MODEL"
        else:
            verdict = "RESEARCH_ARTIFACT"

        results_report = {
            "verdict": verdict,
            "consensus_pass": consensus_pass,
            "grade_pass": grade_pass,
            "reject_pass": reject_pass,
            "readiness_pass": readiness_pass,
            "success_count": success_count,
            "total_criteria": len(all_passes)
        }

        self._write_report(results, results_report)
        return verdict

    def _write_report(self, results: Dict[str, Any], report: Dict[str, Any]) -> None:
        lines = [
            "# Final Scientific Standing Report -- Phase XI-J",
            "",
            "Documents the definitive scientific classification under the Global Scientific Reproduction Program.",
            "",
            "## Definitive Standing",
            "",
            f"> [!IMPORTANT]",
            f"> **Final Scientific Standing Verdict**: **`{report['verdict']}`**",
            "",
            "## Global Consensus Verification Matrix",
            "",
            "| Criteria | Value | Target | Status |",
            "| :--- | :---: | :---: | :--- |",
            f"| Multi-Lab Consensus Score | `{results['consensus_score']*100:.2f}%` | `> 90.00%` | {'PASS' if report['consensus_pass'] else 'FAIL'} |",
            f"| GRADE Evidence Quality Rating | **`{results['quality_grade']}`** | `HIGH` or `VERY_HIGH` | {'PASS' if report['grade_pass'] else 'FAIL'} |",
            f"| Community Rejection Count | `{results['reject_count']}` | `0 Rejections` | {'PASS' if report['reject_pass'] else 'FAIL'} |",
            f"| Publication Readiness Score | `{results['readiness_score']*100:.2f}%` | `> 90.00%` | {'PASS' if report['readiness_pass'] else 'FAIL'} |",
            "",
            f"- **Criteria Passed**: `{report['success_count']}/{report['total_criteria']}`",
            ""
        ]

        docs_dir = os.path.join(self.project_root, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        with open(os.path.join(docs_dir, "FINAL_SCIENTIFIC_VERDICT.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
