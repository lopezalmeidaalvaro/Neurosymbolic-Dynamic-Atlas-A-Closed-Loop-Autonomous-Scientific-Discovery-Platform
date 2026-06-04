import os
import json
import numpy as np
from typing import Dict, Any, List

class TechnologyDiversityAudit:
    """
    Component E: Technology Diversity Audit.
    Quantifies the diversity of hardware paradigms representing the physical quantum executions.
    Calculates paradigm entropy, balance, and composite diversity score.
    """

    def __init__(self):
        pass

    def audit_diversity(
        self,
        rep_report_path: str = "hardware_replication_report.json",
        ood_report_path: str = "ood_hardware_validation_report.json"
    ) -> Dict[str, Any]:
        
        with open(rep_report_path, "r", encoding="utf-8") as f:
            rep_data = json.load(f)
        with open(ood_report_path, "r", encoding="utf-8") as f:
            ood_data = json.load(f)

        # Count executions by hardware paradigm
        counts = {
            "Superconducting": 0,
            "Ion Trap": 0,
            "Neutral Atom": 0,
            "Photonic": 0,
            "Silicon Spin": 0
        }

        # 1. Parse standard replication report
        for item in rep_data:
            for dev_name in item.get("device_details", {}).keys():
                if "ibm" in dev_name or "rigetti" in dev_name:
                    counts["Superconducting"] += 1
                elif "ionq" in dev_name or "quantinuum" in dev_name:
                    counts["Ion Trap"] += 1

        # 2. Parse OOD report
        for item in ood_data:
            for dev_name in item.get("device_replication", {}).keys():
                if "neutral" in dev_name:
                    counts["Neutral Atom"] += 1
                elif "photonic" in dev_name:
                    counts["Photonic"] += 1
                elif "silicon" in dev_name:
                    counts["Silicon Spin"] += 1

        total_runs = sum(counts.values())
        if total_runs == 0:
            total_runs = 1.0

        proportions = [c / total_runs for c in counts.values() if c > 0]
        num_active_paradigms = len(proportions)

        # Calculate Technology Coverage Entropy (H)
        entropy = -sum(p * np.log(p) for p in proportions) if proportions else 0.0

        # Calculate Hardware Family Balance (normalized entropy: H / ln(K))
        max_entropy = np.log(len(counts))
        balance = entropy / max_entropy if max_entropy > 0 else 0.0

        # Technology Diversity Score
        # Scales balance based on paradigm representation relative to standard types
        tech_diversity_score = round(float(balance * (num_active_paradigms / 5.0)), 4)
        # Ensure we clamp it between 0.0 and 1.0
        tech_diversity_score = min(1.0, max(0.0, tech_diversity_score))

        results = {
            "execution_counts_by_paradigm": counts,
            "total_audit_runs": total_runs,
            "active_paradigms_count": num_active_paradigms,
            "coverage_entropy": round(float(entropy), 4),
            "family_balance": round(float(balance), 4),
            "technology_diversity_score": tech_diversity_score,
            "status": "PASSED" if (num_active_paradigms >= 3 and tech_diversity_score >= 0.60) else "FAILED"
        }

        # Write docs/TECHNOLOGY_DIVERSITY_REPORT.md
        self._write_markdown_report(results)

        return results

    def _write_markdown_report(self, results: Dict[str, Any]) -> None:
        lines = [
            "# Technology Diversity Audit Report — Phase 3A.5",
            "",
            "Measures the variety and balance of physical quantum hardware architectures represented in the evidence base.",
            "",
            "## Paradigm Distribution Matrix",
            "",
            "| Hardware Paradigm | Execution Count | Percentage Coverage | Status |",
            "| :--- | :---: | :---: | :--- |"
        ]
        
        for paradigm, count in results["execution_counts_by_paradigm"].items():
            pct = (count / results["total_audit_runs"]) * 100
            status = "`REPRESENTED`" if count > 0 else "`ABSENT`"
            lines.append(f"| {paradigm} | {count} | {pct:.2f}% | {status} |")
            
        lines.append("")
        lines.append("## Diversity Diagnostics")
        lines.append("")
        lines.append(f"- **Active Physical Paradigms Count ($K$)**: **`{results['active_paradigms_count']}`** (Target >= 3)")
        lines.append(f"- **Technology Coverage Entropy ($H$)**: `{results['coverage_entropy']:.4f}`")
        lines.append(f"- **Hardware Family Balance (Normalized Entropy)**: `{results['family_balance']:.4f}`")
        lines.append(f"- **Aggregate Technology Diversity Score**: **`{results['technology_diversity_score']:.4f}`**")
        lines.append(f"- **Audit Verdict**: **`{results['status']}`**")
        lines.append("")
        
        os.makedirs("docs", exist_ok=True)
        with open("docs/TECHNOLOGY_DIVERSITY_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

if __name__ == "__main__":
    audit = TechnologyDiversityAudit()
    print(audit.audit_diversity())
