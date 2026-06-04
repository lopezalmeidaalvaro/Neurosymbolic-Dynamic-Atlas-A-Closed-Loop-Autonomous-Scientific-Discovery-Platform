import os
import json
import numpy as np
from typing import Dict, Any, List, Tuple
from quantum.theory.theory_memory import TheoryMemory

class CorrelationForensics:
    """
    Component D: Correlation Forensics.
    Investigates Residual vs Readout Error and Residual vs Gate Error.
    Performs partial correlations, permutation tests, bootstrap stability, and leave-one-out audits.
    """

    def __init__(self, db_path: str = "theory_memory.db"):
        self.db_path = db_path
        self.memory = TheoryMemory(db_path=db_path)

    def run_diagnostics(
        self,
        rep_report_path: str = "hardware_replication_report.json"
    ) -> Dict[str, Any]:
        
        with open(rep_report_path, "r", encoding="utf-8") as f:
            rep_data = json.load(f)

        predictions = self.memory.get_all_predictions()
        pred_map = {p["id"]: p for p in predictions}

        residuals = []
        gate_errors = []
        readout_errors = []
        vendors = []
        devices = []

        for item in rep_data:
            p_id = item["id"]
            if p_id not in pred_map:
                continue
            expected = pred_map[p_id]["effect_size"]
            
            for dev_name, dev_info in item.get("device_details", {}).items():
                obs = dev_info["mean_effect"]
                residuals.append(expected - obs)
                gate_errors.append(dev_info.get("gate_error", 0.0))
                readout_errors.append(dev_info.get("readout_error", 0.0))
                
                # Deduce vendor
                if "ibm" in dev_name:
                    vendors.append("IBM")
                elif "rigetti" in dev_name:
                    vendors.append("Rigetti")
                elif "ionq" in dev_name:
                    vendors.append("IonQ")
                elif "quantinuum" in dev_name:
                    vendors.append("Quantinuum")
                else:
                    vendors.append("Other")
                    
                devices.append(dev_name)

        res_arr = np.array(residuals)
        gate_arr = np.array(gate_errors)
        read_arr = np.array(readout_errors)

        # Compute basic Pearson correlations
        r_gate = np.corrcoef(res_arr, gate_arr)[0, 1] if len(res_arr) > 1 else 0.0
        r_read = np.corrcoef(res_arr, read_arr)[0, 1] if len(res_arr) > 1 else 0.0
        r_gate_read = np.corrcoef(gate_arr, read_arr)[0, 1] if len(res_arr) > 1 else 0.0

        if np.isnan(r_gate): r_gate = 0.0
        if np.isnan(r_read): r_read = 0.0
        if np.isnan(r_gate_read): r_gate_read = 0.0

        # Perform partial correlation: r(Residual, Readout | Gate)
        # r12.3 = (r12 - r13*r23) / sqrt((1 - r13^2)*(1 - r23^2))
        num = r_read - r_gate * r_gate_read
        den = np.sqrt((1.0 - r_gate**2) * (1.0 - r_gate_read**2))
        partial_r_read = num / den if den > 0 else 0.0

        # Permutation tests (1000 shuffles)
        p_val_gate = self._permutation_test(res_arr, gate_arr)
        p_val_read = self._permutation_test(res_arr, read_arr)

        # Bootstrap stability (95% CI)
        ci_gate = self._bootstrap_ci(res_arr, gate_arr)
        ci_read = self._bootstrap_ci(res_arr, read_arr)

        # Leave-one-vendor-out analysis
        lovo_results = {}
        for unique_v in set(vendors):
            mask = np.array([v != unique_v for v in vendors])
            if np.sum(mask) > 1:
                r_gate_sub = np.corrcoef(res_arr[mask], gate_arr[mask])[0, 1]
                r_read_sub = np.corrcoef(res_arr[mask], read_arr[mask])[0, 1]
                lovo_results[unique_v] = {
                    "gate_correlation": round(float(r_gate_sub), 4) if not np.isnan(r_gate_sub) else 0.0,
                    "readout_correlation": round(float(r_read_sub), 4) if not np.isnan(r_read_sub) else 0.0
                }

        # Classify the relationship type
        # If correlation is high and partial correlation remains high, it's a real relationship.
        # If it drops, it's a proxy or collinearity artifact.
        relationship_readout = "Real Relationship" if abs(partial_r_read) > 0.40 else "Proxy Relationship (mediated by Gate Errors)"
        
        # We also compute an index of correlation stability (percentage of LOVO correlations within 0.15 of baseline)
        baseline_r = r_read
        stable_count = 0
        for lovo in lovo_results.values():
            if abs(lovo["readout_correlation"] - baseline_r) <= 0.15:
                stable_count += 1
        stability_pct = (stable_count / len(lovo_results)) * 100 if lovo_results else 100.0

        results = {
            "baseline_correlations": {
                "residual_vs_gate_error": round(float(r_gate), 4),
                "residual_vs_readout_error": round(float(r_read), 4),
                "gate_error_vs_readout_error": round(float(r_gate_read), 4)
            },
            "partial_correlations": {
                "residual_vs_readout_error_given_gate": round(float(partial_r_read), 4)
            },
            "permutation_p_values": {
                "gate_error": p_val_gate,
                "readout_error": p_val_read
            },
            "bootstrap_95_ci": {
                "gate_error": [round(ci_gate[0], 4), round(ci_gate[1], 4)],
                "readout_error": [round(ci_read[0], 4), round(ci_read[1], 4)]
            },
            "leave_one_vendor_out": lovo_results,
            "correlation_stability_percentage": round(stability_pct, 2),
            "findings": {
                "readout_error_relationship": relationship_readout
            }
        }

        # Write docs/CORRELATION_FORENSICS_REPORT.md
        self._write_markdown_report(results)

        return results

    def _permutation_test(self, x: np.ndarray, y: np.ndarray, num_permutations: int = 1000) -> float:
        if len(x) <= 2:
            return 1.0
        obs_r = abs(np.corrcoef(x, y)[0, 1])
        if np.isnan(obs_r):
            return 1.0
            
        count = 0
        y_shuffled = y.copy()
        for _ in range(num_permutations):
            np.random.shuffle(y_shuffled)
            r_shuf = abs(np.corrcoef(x, y_shuffled)[0, 1])
            if not np.isnan(r_shuf) and r_shuf >= obs_r:
                count += 1
        return float(count / num_permutations)

    def _bootstrap_ci(self, x: np.ndarray, y: np.ndarray, num_resamples: int = 1000) -> Tuple[float, float]:
        if len(x) <= 2:
            return 0.0, 0.0
        r_list = []
        indices = np.arange(len(x))
        for _ in range(num_resamples):
            idx = np.random.choice(indices, size=len(x), replace=True)
            r = np.corrcoef(x[idx], y[idx])[0, 1]
            if not np.isnan(r):
                r_list.append(r)
        if not r_list:
            return 0.0, 0.0
        return float(np.percentile(r_list, 2.5)), float(np.percentile(r_list, 97.5))

    def _write_markdown_report(self, results: Dict[str, Any]) -> None:
        lines = [
            "# Correlation Forensics Report — Phase 3A.5",
            "",
            "Conducts multi-variable diagnostics on prediction residuals and device errors to separate physical causal relationships from collinear artifacts.",
            "",
            "## Baseline Correlations",
            "",
            f"- **r(Residual, Gate Error)**: `{results['baseline_correlations']['residual_vs_gate_error']:.4f}`",
            f"- **r(Residual, Readout Error)**: `{results['baseline_correlations']['residual_vs_readout_error']:.4f}`",
            f"- **r(Gate Error, Readout Error)**: `{results['baseline_correlations']['gate_error_vs_readout_error']:.4f}`",
            "",
            "## Partial Correlations & Independence Audits",
            "",
            f"- **r(Residual, Readout Error | Gate Error)**: `{results['partial_correlations']['residual_vs_readout_error_given_gate']:.4f}`",
            f"- **Permutation Test p-value (Gate Error)**: `{results['permutation_p_values']['gate_error']:.4f}`",
            f"- **Permutation Test p-value (Readout Error)**: `{results['permutation_p_values']['readout_error']:.4f}`",
            f"- **95% Bootstrap CI (Gate Error)**: `[{results['bootstrap_95_ci']['gate_error'][0]:.4f}, {results['bootstrap_95_ci']['gate_error'][1]:.4f}]`",
            f"- **95% Bootstrap CI (Readout Error)**: `[{results['bootstrap_95_ci']['readout_error'][0]:.4f}, {results['bootstrap_95_ci']['readout_error'][1]:.4f}]`",
            "",
            "## Robustness Under Leave-One-Vendor-Out (LOVO)",
            "",
            "| Vendor Excluded | Gate Correlation ($r$) | Readout Correlation ($r$) |",
            "| :--- | :---: | :---: |"
        ]
        for vendor, corrs in results["leave_one_vendor_out"].items():
            lines.append(f"| `{vendor}` | {corrs['gate_correlation']:.4f} | {corrs['readout_correlation']:.4f} |")
            
        lines.append("")
        lines.append(f"- **Correlation Stability Score**: **`{results['correlation_stability_percentage']:.1f}%`** (Target >= 80.0%)")
        lines.append(f"- **Epistemic Classification**: **`{results['findings']['readout_error_relationship']}`**")
        lines.append("")
        
        os.makedirs("docs", exist_ok=True)
        with open("docs/CORRELATION_FORENSICS_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

if __name__ == "__main__":
    cf = CorrelationForensics()
    print(cf.run_diagnostics())
