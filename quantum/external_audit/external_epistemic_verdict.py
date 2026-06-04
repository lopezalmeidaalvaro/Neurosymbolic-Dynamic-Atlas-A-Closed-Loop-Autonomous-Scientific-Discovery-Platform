import os
from typing import Dict, Any

class ExternalEpistemicVerdict:
    """
    Phase X-L: Final External Audit Verdict.
    Aggregates all previous audit findings, evaluates against strict criteria thresholds,
    and issues the definitive epistemic verdict of the hostile external replication program.
    """

    def __init__(self, project_root: str):
        self.project_root = project_root

    def evaluate_verdict(self, results: Dict[str, Any]) -> str:
        # Check thresholds
        leak = results.get("leakage_score", 1.0)
        chk = results.get("checksum_integrity", False)
        rt = results.get("red_team_equivalence", 0.0)
        db = results.get("double_blind_agreement", 0.0)
        hw = results.get("external_hardware_replication", 0.0)
        adv = results.get("adversarial_tournament_win_rate", 0.0)
        phys = results.get("independent_physics_survival", 0.0)
        panel = results.get("external_review_score", 0.0)
        meta = results.get("meta_reproduction_rate", 0.0)

        # Threshold validations
        leak_pass = leak < 0.01
        chk_pass = chk
        rt_pass = rt >= 0.95
        db_pass = db >= 0.90
        hw_pass = hw >= 0.90
        adv_pass = adv >= 0.75
        phys_pass = phys >= 0.80
        panel_pass = panel >= 80.0
        meta_pass = meta >= 0.90

        all_passes = [
            leak_pass, chk_pass, rt_pass, db_pass, hw_pass,
            adv_pass, phys_pass, panel_pass, meta_pass
        ]

        success_count = sum(1 for p in all_passes if p)

        if all(all_passes):
            verdict = "EXTERNALLY_AUDITED_NEW_PHYSICS_CANDIDATE"
        elif success_count >= 7:
            verdict = "EXTERNALLY_AUDITED_DISCOVERY"
        elif success_count >= 5:
            verdict = "STRONGLY_REPRODUCIBLE"
        elif success_count >= 3:
            verdict = "REPRODUCIBLE"
        elif success_count >= 1:
            verdict = "PARTIALLY_REPRODUCIBLE"
        else:
            verdict = "INVALIDATED"

        results_report = {
            "verdict": verdict,
            "leak_pass": leak_pass,
            "chk_pass": chk_pass,
            "rt_pass": rt_pass,
            "db_pass": db_pass,
            "hw_pass": hw_pass,
            "adv_pass": adv_pass,
            "phys_pass": phys_pass,
            "panel_pass": panel_pass,
            "meta_pass": meta_pass,
            "success_count": success_count,
            "total_criteria": len(all_passes)
        }

        self._write_report(results, results_report)
        return verdict

    def _write_report(self, results: Dict[str, Any], report: Dict[str, Any]) -> None:
        lines = [
            "# Final External Audit Verdict -- Phase X-L",
            "",
            "Documents the definitive scientific classification of the hostile external replication program.",
            "",
            "## Definitive Verdict",
            "",
            f"> [!IMPORTANT]",
            f"> **Epistemic Verdict**: **`{report['verdict']}`**",
            "",
            "## Success Criteria Verification Matrix",
            "",
            "| Criteria | Value | Target | Status |",
            "| :--- | :---: | :---: | :--- |",
            f"| Leakage Score | `{results['leakage_score']*100:.2f}%` | `< 1.00%` | {'PASS' if report['leak_pass'] else 'FAIL'} |",
            f"| Checksum Integrity | `{'100.00%' if results['checksum_integrity'] else 'FAILED'}` | `100.00%` | {'PASS' if report['chk_pass'] else 'FAIL'} |",
            f"| Red Team Equivalence | `{results['red_team_equivalence']*100:.2f}%` | `> 95.00%` | {'PASS' if report['rt_pass'] else 'FAIL'} |",
            f"| Double Blind Agreement | `{results['double_blind_agreement']*100:.2f}%` | `> 90.00%` | {'PASS' if report['db_pass'] else 'FAIL'} |",
            f"| External Hardware Replication | `{results['external_hardware_replication']*100:.2f}%` | `> 90.00%` | {'PASS' if report['hw_pass'] else 'FAIL'} |",
            f"| Adversarial Tournament Win Rate | `{results['adversarial_tournament_win_rate']*100:.2f}%` | `> 75.00%` | {'PASS' if report['adv_pass'] else 'FAIL'} |",
            f"| Independent Physics Survival | `{results['independent_physics_survival']*100:.2f}%` | `> 80.00%` | {'PASS' if report['phys_pass'] else 'FAIL'} |",
            f"| External Review Panel Score | `{results['external_review_score']:.2f}%` | `> 80.00%` | {'PASS' if report['panel_pass'] else 'FAIL'} |",
            f"| Meta-Reproduction Rate | `{results['meta_reproduction_rate']*100:.2f}%` | `> 90.00%` | {'PASS' if report['meta_pass'] else 'FAIL'} |",
            "",
            f"- **Criteria Passed**: `{report['success_count']}/{report['total_criteria']}`",
            ""
        ]

        docs_dir = os.path.join(self.project_root, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        with open(os.path.join(docs_dir, "FINAL_EXTERNAL_AUDIT_REPORT.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
