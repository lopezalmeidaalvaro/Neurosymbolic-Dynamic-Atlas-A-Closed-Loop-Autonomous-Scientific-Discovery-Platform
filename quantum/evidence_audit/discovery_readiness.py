import os
import json
from typing import Dict, Any

class DiscoveryReadinessAudit:
    """
    Component L: Discovery Readiness Score.
    Aggregates metrics from Components B to K to compute a unified Discovery Readiness Score between 0.0 and 1.0.
    """

    def __init__(self):
        pass

    def compute_readiness(
        self,
        ess_results: Dict[str, Any],
        leakage_results: Dict[str, Any],
        vendor_results: Dict[str, Any],
        tech_results: Dict[str, Any],
        cal_results: Dict[str, Any],
        bench_results: Dict[str, Any],
        corr_results: Dict[str, Any],
        stress_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        # Normalize and extract raw scores
        ess_score = 1.0 if ess_results["global_ess"] >= 500 else 0.0
        leakage_score = 1.0 - leakage_results["leakage_score"]
        vendor_score = vendor_results["vendor_independence_score"]
        tech_score = tech_results["technology_diversity_score"]
        cal_score = cal_results["calibration_diversity_score"]
        bench_score = bench_results["benchmark_coverage_score"]
        corr_score = corr_results["correlation_stability_percentage"] / 100.0
        robustness_score = stress_results["evidence_robustness_score"]

        # Weighted calculation of Discovery Readiness Score
        # Total weights sum to 1.0
        weights = {
            "ess": 0.15,
            "leakage": 0.15,
            "vendor": 0.15,
            "technology": 0.15,
            "calibration": 0.10,
            "benchmark": 0.10,
            "correlation": 0.10,
            "robustness": 0.10
        }

        readiness_score = (
            ess_score * weights["ess"] +
            leakage_score * weights["leakage"] +
            vendor_score * weights["vendor"] +
            tech_score * weights["technology"] +
            cal_score * weights["calibration"] +
            bench_score * weights["benchmark"] +
            corr_score * weights["correlation"] +
            robustness_score * weights["robustness"]
        )

        readiness_score = round(float(readiness_score), 4)

        results = {
            "component_readiness_metrics": {
                "effective_sample_size": ess_score,
                "leakage_avoidance": round(leakage_score, 4),
                "vendor_independence": round(vendor_score, 4),
                "technology_diversity": round(tech_score, 4),
                "calibration_diversity": round(cal_score, 4),
                "benchmark_diversity": round(bench_score, 4),
                "correlation_stability": round(corr_score, 4),
                "evidence_robustness": round(robustness_score, 4)
            },
            "weights": weights,
            "discovery_readiness_score": readiness_score,
            "status": "PASSED" if readiness_score >= 0.80 else "FAILED"
        }

        # Write docs/DISCOVERY_READINESS_REPORT.md
        self._write_markdown_report(results)

        return results

    def _write_markdown_report(self, results: Dict[str, Any]) -> None:
        lines = [
            "# Discovery Readiness Report — Phase 3A.5",
            "",
            "Aggregates the individual scores of the physical quantum hardware evidence base to compute the unified Discovery Readiness index.",
            "",
            "## Readiness Metrics Ledger",
            "",
            "| Readiness Metric Dimension | Raw Score Value | Metric Weight | Weighted Contribution | Status |",
            "| :--- | :---: | :---: | :---: | :--- |"
        ]
        
        dims = results["component_readiness_metrics"]
        weights = results["weights"]
        key_map = {
            "effective_sample_size": "ess",
            "leakage_avoidance": "leakage",
            "vendor_independence": "vendor",
            "technology_diversity": "technology",
            "calibration_diversity": "calibration",
            "benchmark_diversity": "benchmark",
            "correlation_stability": "correlation",
            "evidence_robustness": "robustness"
        }
        for k, val in dims.items():
            wt = weights[key_map[k]]
            weighted_val = val * wt
            status = "**`READY`**" if val >= 0.70 else "`DEFICIENT`"
            lines.append(f"| {k.replace('_', ' ').capitalize()} | {val:.4f} | {wt:.2f} | {weighted_val:.4f} | {status} |")
            
        lines.append("")
        lines.append("## Executive Score Summary")
        lines.append("")
        lines.append(f"- **Unified Discovery Readiness Score**: **`{results['discovery_readiness_score']:.4f}`** (Target >= 0.80)")
        lines.append(f"- **Readiness Standing Status**: **`{results['status']}`**")
        lines.append("")
        
        os.makedirs("docs", exist_ok=True)
        with open("docs/DISCOVERY_READINESS_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

if __name__ == "__main__":
    audit = DiscoveryReadinessAudit()
    print(audit.compute_readiness(
        {"global_ess": 550},
        {"leakage_score": 0.015},
        {"vendor_independence_score": 0.95},
        {"technology_diversity_score": 0.78},
        {"calibration_diversity_score": 1.0},
        {"benchmark_coverage_score": 1.0},
        {"correlation_stability_percentage": 100.0},
        {"evidence_robustness_score": 0.97}
    ))
