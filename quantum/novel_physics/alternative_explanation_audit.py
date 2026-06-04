import os
from typing import Dict, Any, List

class AlternativeExplanationAudit:
    """
    Phase 4H: Alternative Explanation Elimination.
    Tries to explain the observed residuals through conventional artifacts:
    noise, drift, leakage, calibration decay, thermal coherence limits, detector bias, or simulation mismatch.
    The theory only survives if all conventional explanations fail.
    """

    def __init__(self, validation_results: Dict[str, Any]):
        self.val_results = validation_results

    def audit_explanations(self) -> Dict[str, Any]:
        audit_records = {}
        theories_survived = 0

        # Maximum threshold bounds that conventional effects can explain:
        bounds = {
            "noise_variance_limit": 0.0005,
            "calibration_drift_limit": 0.0010,
            "thermal_relaxation_limit": 0.0008,
            "leakage_rate_limit": 0.0004,
            "measurement_bias_limit": 0.0012,
            "simulator_mismatch_limit": 0.0006
        }

        # Total combined limit conventional physics can explain:
        max_conventional_limit = sum(bounds.values())  # 0.0045

        for case_id, val in self.val_results["validation_results"].items():
            observed_gap = val["observed_gap"]
            theory_id = val["theory_id"]
            domain = val["domain"]

            # We audit each alternative explanation
            noise_ok = abs(observed_gap) > bounds["noise_variance_limit"]
            drift_ok = abs(observed_gap) > bounds["calibration_drift_limit"]
            thermal_ok = abs(observed_gap) > bounds["thermal_relaxation_limit"]
            leakage_ok = abs(observed_gap) > bounds["leakage_rate_limit"]
            bias_ok = abs(observed_gap) > bounds["measurement_bias_limit"]
            sim_ok = abs(observed_gap) > bounds["simulator_mismatch_limit"]

            # Combined conventional audit: does the observed gap exceed the sum of standard limits?
            combined_conventional_failed = abs(observed_gap) > max_conventional_limit

            survived = (
                noise_ok and drift_ok and thermal_ok and leakage_ok and bias_ok and sim_ok and combined_conventional_failed
            )

            if survived:
                theories_survived += 1

            audit_records[case_id] = {
                "theory_id": theory_id,
                "domain": domain,
                "observed_gap": observed_gap,
                "conventional_explanations": {
                    "noise_variance": "EXCLUDED" if noise_ok else "FEASIBLE",
                    "calibration_drift": "EXCLUDED" if drift_ok else "FEASIBLE",
                    "thermal_relaxation": "EXCLUDED" if thermal_ok else "FEASIBLE",
                    "leakage_rate": "EXCLUDED" if leakage_ok else "FEASIBLE",
                    "measurement_bias": "EXCLUDED" if bias_ok else "FEASIBLE",
                    "simulator_mismatch": "EXCLUDED" if sim_ok else "FEASIBLE",
                    "combined_conventional_limit": "EXCLUDED" if combined_conventional_failed else "FEASIBLE"
                },
                "status": "ELIMINATED_ALL_CONVENTIONAL" if survived else "EXPLAINED_BY_CONVENTIONAL"
            }

        total_cases = len(self.val_results["validation_results"])
        elimination_rate = theories_survived / total_cases if total_cases > 0 else 0.0

        results = {
            "audit_records": audit_records,
            "elimination_rate": round(elimination_rate, 4),
            "status": "PASSED" if elimination_rate >= 0.70 else "FAILED"
        }

        self._write_markdown_report(results)
        return results

    def _write_markdown_report(self, results: Dict[str, Any]) -> None:
        lines = [
            "# Alternative Explanation Elimination Report — Phase 4H",
            "",
            "Audits physical observations against conventional explanations to eliminate noise, calibration drift, thermal decay, and bias.",
            "",
            "| Case ID | Theory ID | Domain | Observed Gap | Noise | Drift | Thermal | Leakage | Bias | Sim Mismatch | Verdict Status |",
            "| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]

        for case_id, rec in results["audit_records"].items():
            ex = rec["conventional_explanations"]
            lines.append(
                f"| `{case_id}` | `{rec['theory_id']}` | `{rec['domain']}` | `{rec['observed_gap']:.6f}` | `{ex['noise_variance']}` | `{ex['calibration_drift']}` | `{ex['thermal_relaxation']}` | `{ex['leakage_rate']}` | `{ex['measurement_bias']}` | `{ex['simulator_mismatch']}` | **`{rec['status']}`** |"
            )

        lines.append("")
        lines.append(f"- **Conventional Explanation Elimination Rate**: **`{results['elimination_rate']*100:.2f}%`** (Target >= 70.0%)")
        lines.append(f"- **Elimination Audit Verdict**: **`{results['status']}`**")
        lines.append("")

        os.makedirs("docs", exist_ok=True)
        with open("docs/ALTERNATIVE_EXPLANATION_AUDIT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
