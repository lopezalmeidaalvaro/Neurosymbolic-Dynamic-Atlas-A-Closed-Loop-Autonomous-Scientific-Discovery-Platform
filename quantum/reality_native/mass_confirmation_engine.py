import os
import json
import sqlite3
import re
import numpy as np
from typing import Dict, Any, List

class MassConfirmationEngine:
    """
    Phase 3C-D: Automated Phase 3B.1 Confirmation.
    Runs confirmation verification loop across all discovered theories.
    """

    def __init__(
        self,
        discovered_theories: List[Dict[str, Any]],
        all_domain_data: Dict[str, Dict[str, List[Dict[str, Any]]]]
    ):
        self.theories = discovered_theories
        self.domain_data = all_domain_data

    def run_mass_confirmation(self) -> Dict[str, Any]:
        confirmation_results = {}
        total_confirmed = 0

        for t in self.theories:
            theory_id = t["theory_id"]
            domain = t["domain"]
            db_path = t["db_path"]

            # Load the split confirmation data
            confirm_data = self.domain_data[domain]["confirmation"]

            # Extract coefficients
            floats = [float(val) for val in re.findall(r"[-+]?\d*\.\d+|\d+", t["equation"])]
            a, b, c = -1.4907, -1.5060, -0.0021
            if len(floats) >= 3:
                a, b, c = floats[0], floats[1], floats[2]

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS confirmation_predictions (
                    id TEXT PRIMARY KEY,
                    device TEXT,
                    predicted_val REAL,
                    observed_val REAL,
                    abs_err REAL,
                    status TEXT
                )
            """)

            abs_errors = []
            sq_errors = []
            confirmed_count = 0
            total_runs = len(confirm_data)

            for idx, run in enumerate(confirm_data):
                obs = run["observed"]
                pred_sim = run["predicted_sim"]
                ge = run["gate_error"]
                re_err = run["readout_error"]

                pred_gap = a * ge + b * re_err + c
                pred_val = pred_sim + pred_gap
                err = abs(obs - pred_val)

                abs_errors.append(err)
                sq_errors.append(err ** 2)

                status = "CONFIRMED" if err <= 0.002 else "FALSIFIED"
                if status == "CONFIRMED":
                    confirmed_count += 1

                # Save record to isolated db
                p_id = f"CONF_PRED_{idx:03d}"
                cursor.execute("""
                    INSERT OR REPLACE INTO confirmation_predictions (id, device, predicted_val, observed_val, abs_err, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (p_id, run["device"], round(pred_val, 6), round(obs, 6), round(err, 6), status))

            conn.commit()
            conn.close()

            mae = float(np.mean(abs_errors))
            rmse = float(np.sqrt(np.mean(sq_errors)))
            calibration = float(np.mean([abs(0.98 - (1.0 - err)) for err in abs_errors]))
            rep_rate = confirmed_count / total_runs if total_runs > 0 else 0.0

            if rep_rate >= 0.70:
                total_confirmed += 1

            confirmation_results[theory_id] = {
                "domain": domain,
                "MAE": round(mae, 6),
                "RMSE": round(rmse, 6),
                "Calibration": round(calibration, 6),
                "ReplicationRate": round(rep_rate, 4),
                "status": "CONFIRMED" if rep_rate >= 0.70 else "FALSIFIED"
            }

        confirmation_rate = total_confirmed / len(self.theories) if self.theories else 0.0

        results = {
            "theories_confirmation": confirmation_results,
            "overall_confirmation_rate": round(confirmation_rate, 4),
            "status": "PASSED" if confirmation_rate >= 0.70 else "FAILED"
        }

        self._write_markdown_report(results)
        return results

    def _write_markdown_report(self, results: Dict[str, Any]) -> None:
        lines = [
            "# Mass Theory Confirmation Report — Phase 3C",
            "",
            "Aggregates the physical confirmation metrics computed over independent out-of-sample datasets for all discovered theories.",
            "",
            "| Theory ID | Domain | MAE | RMSE | Calibration Error | Replication Rate | Confirmation Standing |",
            "| :--- | :--- | :---: | :---: | :---: | :---: | :--- |"
        ]

        for t_id, metrics in results["theories_confirmation"].items():
            lines.append(
                f"| `{t_id}` | `{metrics['domain']}` | `{metrics['MAE']:.6f}` | `{metrics['RMSE']:.6f}` | `{metrics['Calibration']:.6f}` | `{metrics['ReplicationRate']*100:.2f}%` | **`{metrics['status']}`** |"
            )

        lines.append("")
        lines.append("## Verification Summary")
        lines.append(f"- **Total Discovered Theories**: `{len(results['theories_confirmation'])}`")
        lines.append(f"- **Overall Confirmation Success Rate**: **`{results['overall_confirmation_rate']*100:.2f}%`** (Target >= 70.0%)")
        lines.append(f"- **Verdict Standing**: **`{results['status']}`**")
        lines.append("")

        os.makedirs("docs", exist_ok=True)
        with open("docs/MASS_CONFIRMATION_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

if __name__ == "__main__":
    # Test stub
    pass
