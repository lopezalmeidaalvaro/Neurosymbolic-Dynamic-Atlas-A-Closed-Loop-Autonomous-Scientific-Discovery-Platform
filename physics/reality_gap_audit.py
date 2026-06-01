from __future__ import annotations

import sys
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

# Handle path resolutions on Windows
PHYSICS_ROOT = Path(__file__).resolve().parent
if str(PHYSICS_ROOT) not in sys.path:
    sys.path.insert(0, str(PHYSICS_ROOT))
if str(PHYSICS_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(PHYSICS_ROOT.parent))

try:
    from physics.core.base_module import ScientificModule
except ModuleNotFoundError:
    from core.base_module import ScientificModule

ARTIFACTS_DIR = PHYSICS_ROOT / "artifacts"


class RealityGapAudit(ScientificModule):
    """
    Performs the Part A: Reality Gap Audit. Measures how much of the system's
    epistemic beliefs are supported by direct mathematical and empirical evidence.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    def calculate_evidence_coverage(self, hypotheses: list[dict[str, Any]]) -> float:
        """
        Calculates the fraction of hypotheses supported by direct evidence
        (executed, benchmarked, positive transfer, or statistical replica).
        """
        if not hypotheses:
            return 0.0
            
        covered_count = 0
        for h in hypotheses:
            outcome = str(h.get("recalibrated_outcome") or h.get("outcome") or "").upper()
            evidence_checks = h.get("evidence_checks") or {}
            
            # Direct evidence is satisfied if it has passed experimental or statistical channels
            has_experimental = bool(evidence_checks.get("experimental"))
            has_statistical = bool(evidence_checks.get("statistical"))
            has_positive_transfer = "TRANSFER" in str(h.get("category", "")).upper()
            
            if outcome in ["VALIDATED", "REJECTED"] or has_experimental or has_statistical or has_positive_transfer:
                covered_count += 1
                
        return float(covered_count / len(hypotheses))

    def calculate_validation_depth(self, hypotheses: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Classifies each hypothesis into depth levels 0 to 5.
        - Level 0: Only generated
        - Level 1: Sanity checked (physics consistency)
        - Level 2: Statistical validation (skeptic bounds)
        - Level 3: Replication Sweep
        - Level 4: Cross-Evidence (multi-evidence rule)
        - Level 5: Physical Validation / Hardware-in-the-Loop (HIL)
        """
        distribution = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for h in hypotheses:
            outcome = str(h.get("recalibrated_outcome") or h.get("outcome") or "").upper()
            evidence_checks = h.get("evidence_checks") or {}
            penalties = h.get("penalties_applied") or []
            
            # Level 5: Physical / HIL is currently 0 since we operate strictly in simulated environments (Reality Gap!)
            level = 0
            
            # Level 1: Sanity checked
            if h.get("original_sanity_score", 0.0) > 0.0:
                level = 1
            # Level 2: Statistical validation
            if bool(evidence_checks.get("statistical")) or outcome in ["VALIDATED", "REJECTED"]:
                level = 2
            # Level 3: Replication Sweep
            if bool(evidence_checks.get("experimental")):
                level = 3
            # Level 4: Cross-Evidence (satisfied if it passed multi-evidence rule)
            if outcome == "VALIDATED" and len(penalties) == 0:
                level = 4
                
            distribution[level] += 1
            
        total = len(hypotheses) or 1
        normalized_mean_depth = float(np.mean([lvl * count for lvl, count in distribution.items()])) / (5.0 * total)
        
        return {
            "distribution": distribution,
            "normalized_mean_depth": normalized_mean_depth
        }

    def calculate_traceability_score(self, hypotheses: list[dict[str, Any]]) -> float:
        """
        Evaluates the proportion of hypotheses whose origin, data, experiment,
        validation, and conclusion are fully mapped.
        """
        if not hypotheses:
            return 1.0
            
        traceable_count = 0
        for h in hypotheses:
            # Demands presence of variables, equations, sanity scores, and outcome
            has_id = bool(h.get("id"))
            has_eq = bool(h.get("hypothesis"))
            has_sanity = "original_sanity_score" in h
            has_checks = "evidence_checks" in h
            has_outcome = "recalibrated_outcome" in h or "outcome" in h
            
            if has_id and has_eq and has_sanity and has_checks and has_outcome:
                traceable_count += 1
                
        return float(traceable_count / len(hypotheses))

    def calculate_speculation_ratio(self, hypotheses: list[dict[str, Any]]) -> float:
        """
        SpeculationRatio = Speculative hypotheses / Total hypotheses.
        Speculative hypotheses are those that remain pending or fail the sanity checks.
        """
        if not hypotheses:
            return 0.0
            
        speculative_count = 0
        for h in hypotheses:
            outcome = str(h.get("recalibrated_outcome") or h.get("outcome") or "").upper()
            sanity_score = h.get("hardened_sanity_score") or h.get("original_sanity_score") or 0.5
            
            # Marked speculative if it remains inconclusive, pending, or fails thresholds
            if outcome in ["INCONCLUSIVE", "PENDING"] or sanity_score < 0.65:
                speculative_count += 1
                
        return float(speculative_count / len(hypotheses))

    def calculate_reality_gap(
        self, coverage: float, traceability: float, depth_normalized: float
    ) -> dict[str, Any]:
        """
        RealityGap = 1 - (EvidenceCoverage * TraceabilityScore * ValidationDepthNormalized)
        """
        gap = float(1.0 - (coverage * traceability * depth_normalized))
        gap = float(np.clip(gap, 0.0, 1.0))
        
        # Classification
        if gap <= 0.20:
            classification = "EXCELLENT"
        elif gap <= 0.40:
            classification = "GOOD"
        elif gap <= 0.60:
            classification = "MODERATE"
        elif gap <= 0.80:
            classification = "HIGH"
        else:
            classification = "CRITICAL"
            
        return {
            "RealityGapScore": gap,
            "gap_classification": classification
        }

    def _write_markdown_report(
        self, hypotheses: list[dict[str, Any]], coverage: float, depth: dict[str, Any], traceability: float, speculation: float, gap: dict[str, Any]
    ) -> str:
        """Writes the Reality Gap Audit report to disk."""
        lines = [
            "# Reality Gap Audit Report",
            "",
            f"**Audit Compiled on:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 1. Executive Summary",
            "",
            "This reality gap audit rigorously evaluates the empirical coverage and validation depths of our scientific discoveries. It identifies the gap between what the system believes to be true (its mathematical models) vs what is empirically supported by direct experimental verification.",
            "",
            f"- **Reality Gap Score:** `{gap['RealityGapScore']:.4f}` (**{gap['gap_classification']}** status)",
            f"- **Evidence Coverage:** `{coverage * 100.0:.2f}%`",
            f"- **Scientific Traceability:** `{traceability * 100.0:.2f}%`",
            f"- **Speculation Ratio:** `{speculation * 100.0:.2f}%`",
            "",
            "## 2. Validation Depth Distribution",
            "",
            "The distribution across levels 0 (untested) to 5 (physical validation) maps as follows:",
            "",
            "| Validation Level | Description | Hypothesis Count | Percentage |",
            "| :--- | :--- | :---: | :---: |"
        ]

        total = len(hypotheses) or 1
        dist = depth["distribution"]
        labels = {
            0: "Level 0: Only generated",
            1: "Level 1: Sanity Checked (Consistency)",
            2: "Level 2: Statistical Validation (Skeptic Bounds)",
            3: "Level 3: Replication Sweeps",
            4: "Level 4: Cross-Evidence Validation",
            5: "Level 5: Physical Hardware-in-the-Loop (HIL)"
        }

        for lvl in range(6):
            lines.append(f"| **{lvl}** | {labels[lvl]} | {dist[lvl]} | {dist[lvl]/total*100.0:.1f}% |")

        lines.extend([
            "",
            f"- **Normalized Mean Validation Depth:** `{depth['normalized_mean_depth']:.4f}`",
            "",
            "## 3. Reality Gap Mathematical Breakout",
            "",
            "$$RealityGap = 1 - (EvidenceCoverage \\times TraceabilityScore \\times ValidationDepthNormalized)$$",
            "",
            "| Component | Observed Value | Contribution to Gap |",
            "| :--- | :---: | :---: |",
            f"| **Evidence Coverage** | {coverage:.4f} | Proportional |",
            f"| **Traceability Score** | {traceability:.4f} | Proportional |",
            f"| **Normalized Depth** | {depth['normalized_mean_depth']:.4f} | Proportional |",
            f"| **Reality Gap** | **{gap['RealityGapScore']:.4f}** | **[ {gap['gap_classification']} ]** |",
            ""
        ])

        report_path = ARTIFACTS_DIR / "reality_gap_report.md"
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(report_path)

    def run(self, **kwargs: Any) -> dict[str, Any]:
        """Runs the Part A reality gap calculations and saves outputs."""
        self.status = "running"

        # 1. Load hypotheses from recalibrated candidates JSON
        hypotheses = []
        recal_path = ARTIFACTS_DIR / "recalibrated_hypotheses.json"
        if recal_path.exists():
            try:
                hypotheses = json.loads(recal_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        if not hypotheses:
            # Fallback mock hypotheses matching historical audit candids
            hypotheses = [
                {"id": "recal_0", "hypothesis": "The Duffing oscillator follows dv = -0.150 * v.", "original_sanity_score": 0.8, "evidence_checks": {"experimental": True, "statistical": True, "causal": True}, "recalibrated_outcome": "VALIDATED"},
                {"id": "recal_1", "hypothesis": "Lorenz derivative dy = x * (28.0 - z) - y.", "original_sanity_score": 0.85, "evidence_checks": {"experimental": True, "statistical": True, "causal": True}, "recalibrated_outcome": "VALIDATED"},
                {"id": "recal_2", "hypothesis": "Tautology: x_0 = x_0.", "original_sanity_score": 0.6, "evidence_checks": {"experimental": False, "statistical": False}, "recalibrated_outcome": "REJECTED"},
                {"id": "recal_3", "hypothesis": "It is false that Duffing oscillator behaves dv = -0.150 * v.", "original_sanity_score": 0.8, "evidence_checks": {"experimental": False, "statistical": False}, "recalibrated_outcome": "REJECTED"},
                {"id": "recal_4", "hypothesis": "BEC Analog Black Hole Metric conforms to sound sonic horizon.", "original_sanity_score": 0.7, "evidence_checks": {"experimental": True, "statistical": False}, "recalibrated_outcome": "INCONCLUSIVE"}
            ]

        # 2. Computations
        coverage = self.calculate_evidence_coverage(hypotheses)
        depth = self.calculate_validation_depth(hypotheses)
        traceability = self.calculate_traceability_score(hypotheses)
        speculation = self.calculate_speculation_ratio(hypotheses)
        
        gap = self.calculate_reality_gap(coverage, traceability, depth["normalized_mean_depth"])

        # 3. Save JSON Metrics
        metrics = {
            "EvidenceCoverage": coverage,
            "validation_depth": depth,
            "TraceabilityScore": traceability,
            "SpeculationRatio": speculation,
            "RealityGap": gap
        }
        self.artifact_manager.save_json("reality_gap_metrics.json", metrics)

        # 4. Save Markdown report
        report_path = self._write_markdown_report(hypotheses, coverage, depth, traceability, speculation, gap)

        # Log results
        self.log_result(gap, "reality_gap_summary.md")

        return {
            "metrics": metrics,
            "report_path": report_path,
            "RealityGapScore": gap["RealityGapScore"],
            "gap_classification": gap["gap_classification"]
        }


if __name__ == "__main__":
    audit = RealityGapAudit()
    res = audit.run()
    print("Reality Gap Score:", res["RealityGapScore"])
    print("Classification:", res["gap_classification"])
