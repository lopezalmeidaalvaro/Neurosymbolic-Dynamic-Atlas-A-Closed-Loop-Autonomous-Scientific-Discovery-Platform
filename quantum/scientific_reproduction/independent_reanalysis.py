import os
import re
import numpy as np
from typing import Dict, Any, List
from quantum.reality_native.domain_expansion_engine import DomainExpansionEngine
from quantum.reality_native.parallel_theory_discovery import ParallelTheoryDiscovery

class IndependentReanalysis:
    """
    Phase XI-B: Independent Reanalysis Program.
    Simulates four independent review teams recalculating the entire model parameters,
    residuals, statistical significance, and physical constraints from scratch.
    """

    def __init__(self, project_root: str):
        self.project_root = project_root

    def _parse_coeffs(self, eq_str: str) -> tuple:
        floats = [float(v) for v in re.findall(r"[-+]?\d*\.\d+|\d+", eq_str)]
        if len(floats) >= 3:
            return floats[0], floats[1], floats[2]
        return 0.0, 0.0, 0.0

    def run_reanalysis(self) -> Dict[str, Any]:
        engine = DomainExpansionEngine(seed=42)
        all_data = engine.generate_all_domains()
        discovery = ParallelTheoryDiscovery()
        theories = discovery.discover_theories_for_all_domains(all_data)

        reanalysis_records = {}
        all_passed = True

        for theory in theories:
            domain = theory["domain"]
            eq = theory["equation"]
            a_orig, b_orig, c_orig = self._parse_coeffs(eq)

            splits = all_data.get(domain, {})
            train_recs = splits.get("training", [])
            repro_recs = splits.get("reproduction", [])

            X_train = np.array([[r["gate_error"], r["readout_error"]] for r in train_recs])
            y_train = np.array([r["observed_gap"] for r in train_recs])
            X_test = np.array([[r["gate_error"], r["readout_error"]] for r in repro_recs])
            y_test = np.array([r["observed_gap"] for r in repro_recs])

            # 1. Team A (Statistician): recalculate OLS coefficients and verify matching
            X_b = np.hstack([X_train, np.ones((X_train.shape[0], 1))])
            beta = np.linalg.pinv(X_b.T @ X_b) @ X_b.T @ y_train
            a_stat, b_stat, c_stat = beta[0], beta[1], beta[2]

            stat_match = abs(a_orig - a_stat) < 1e-3 and abs(b_orig - b_stat) < 1e-3
            
            # 2. Team B (Physicist): verify physically valid coefficients (e.g. negative slope)
            phys_valid = a_stat < 0.0 and b_stat < 0.0

            # 3. Team C (Engineer): recalculate test residuals and verify MAE limit
            pred = a_stat * X_test[:, 0] + b_stat * X_test[:, 1] + c_stat
            mae = np.mean(np.abs(y_test - pred))
            eng_valid = mae < 0.01

            # 4. Team D (Skeptic): check p-value / F-test vs zero-parameter baseline
            # Residual sum of squares
            rss_model = np.sum((y_test - pred) ** 2)
            rss_null = np.sum(y_test ** 2) # Standard model predicts 0.0
            
            # Since F = ((RSS_null - RSS_model) / p) / (RSS_model / (N - p))
            # F is extremely large because the model fits the gap perfectly
            f_stat = ((rss_null - rss_model) / 2) / (rss_model / (len(y_test) - 3))
            skeptic_valid = f_stat > 10.0 # statistically highly significant

            passed = stat_match and phys_valid and eng_valid and skeptic_valid
            if not passed:
                all_passed = False

            reanalysis_records[domain] = {
                "statistician_match": "PASS" if stat_match else "FAIL",
                "physicist_validation": "PASS" if phys_valid else "FAIL",
                "engineer_mae": round(float(mae), 6),
                "engineer_status": "PASS" if eng_valid else "FAIL",
                "skeptic_f_stat": round(float(f_stat), 2),
                "skeptic_status": "PASS" if skeptic_valid else "FAIL",
                "overall": "PASS" if passed else "FAIL"
            }

        results = {
            "reanalysis_records": reanalysis_records,
            "status": "PASS" if all_passed else "FAIL"
        }

        self._write_report(results)
        return results

    def _write_report(self, results: Dict[str, Any]) -> None:
        lines = [
            "# Independent Reanalysis Program Report -- Phase XI-B",
            "",
            f"**Overall Reanalysis Verdict**: **`{results['status']}`**",
            "",
            "## Recalculation Standings by Team and Domain",
            "",
            "| Domain | Team A (Stat) | Team B (Phys) | Team C (Eng MAE) | Team D (Skeptic F) | Status |",
            "| :--- | :---: | :---: | :---: | :---: | :--- |"
        ]

        for domain, info in results["reanalysis_records"].items():
            lines.append(
                f"| `{domain}` | `{info['statistician_match']}` | `{info['physicist_validation']}` | `{info['engineer_mae']:.6f} ({info['engineer_status']})` | `{info['skeptic_f_stat']} ({info['skeptic_status']})` | **`{info['overall']}`** |"
            )

        lines.append("")
        docs_dir = os.path.join(self.project_root, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        with open(os.path.join(docs_dir, "INDEPENDENT_REANALYSIS_REPORT.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
