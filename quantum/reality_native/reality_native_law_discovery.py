import os
import json
import sqlite3
import numpy as np
from typing import Dict, Any, List
from quantum.theory.theory_memory import TheoryMemory
from quantum.reality_native.reality_native_memory import RealityNativeMemory

class RealityNativeLawDiscoveryEngine:
    """
    Phase 3B-C: Reality-Native Law Discovery.
    Fits symbolic candidate equations to anomaly families, evaluates MDL,
    applies acceptance filters (>=2 vendors, >=2 technologies, >=5% improvement over null models),
    saves accepted laws, and generates docs/DISCOVERED_LAWS.md.
    """

    def __init__(
        self,
        db_path: str = "theory_memory.db",
        reality_db_path: str = "reality_native.db"
    ):
        self.memory = TheoryMemory(db_path=db_path)
        self.reality_mem = RealityNativeMemory(db_path=reality_db_path)

    def discover_laws(
        self,
        rep_report_path: str = "hardware_replication_report.json"
    ) -> List[Dict[str, Any]]:
        
        # Load data
        gaps = self.reality_mem.get_all_gaps()
        families = self.reality_mem.get_all_anomaly_families()
        if not gaps or not families:
            return []

        # Load device statistics for fitting variables
        with open(rep_report_path, "r", encoding="utf-8") as f:
            rep_data = json.load(f)
            
        dev_stats = {}
        for item in rep_data:
            p_id = item["id"]
            for dev_name, dev_info in item.get("device_details", {}).items():
                dev_stats[(p_id, dev_name)] = {
                    "gate_error": dev_info.get("gate_error", 0.0),
                    "readout_error": dev_info.get("readout_error", 0.0)
                }

        discovered_laws = []

        for fam in families:
            p_ids = fam["prediction_ids"]
            
            # Gather training vectors for this family
            X_gate = []
            X_read = []
            y_gap = []
            vendors = set()
            paradigms = set()

            for g in gaps:
                if g["prediction_id"] in p_ids:
                    dev_name = g["device"]
                    stats = dev_stats.get((g["prediction_id"], dev_name), {"gate_error": 0.01, "readout_error": 0.02})
                    
                    X_gate.append(stats["gate_error"])
                    X_read.append(stats["readout_error"])
                    y_gap.append(g["gap"])

                    # Extract platform and vendor
                    if "ibm" in dev_name:
                        vendors.add("IBM")
                        paradigms.add("Superconducting")
                    elif "rigetti" in dev_name:
                        vendors.add("Rigetti")
                        paradigms.add("Superconducting")
                    elif "ionq" in dev_name:
                        vendors.add("IonQ")
                        paradigms.add("Ion Trap")
                    elif "quantinuum" in dev_name:
                        vendors.add("Quantinuum")
                        paradigms.add("Ion Trap")

            if len(y_gap) < 5:
                continue

            y = np.array(y_gap)
            n_samples = len(y)

            # Define Null Model (Model 0: constant mean gap)
            null_val = np.mean(y)
            rss_null = np.sum((y - null_val) ** 2)

            # Fit candidate equations
            # Candidate Law 1: Gap = a * GateError + b * ReadoutError + c
            # Design matrix for Law 1
            A1 = np.column_stack((X_gate, X_read, np.ones_like(X_gate)))
            coeffs1, _, _, _ = np.linalg.lstsq(A1, y, rcond=None)
            pred1 = A1 @ coeffs1
            rss1 = np.sum((y - pred1) ** 2)
            r_sq1 = 1.0 - (rss1 / rss_null) if rss_null > 0 else 0.0

            # Candidate Law 2: Gap = a * (GateError * ReadoutError) + b
            A2 = np.column_stack((np.array(X_gate) * np.array(X_read), np.ones_like(X_gate)))
            coeffs2, _, _, _ = np.linalg.lstsq(A2, y, rcond=None)
            pred2 = A2 @ coeffs2
            rss2 = np.sum((y - pred2) ** 2)
            r_sq2 = 1.0 - (rss2 / rss_null) if rss_null > 0 else 0.0

            # Select best model based on R-squared & MDL
            # MDL = k * ln(n) + n * ln(RSS)
            mdl1 = 3 * np.log(n_samples) + n_samples * np.log(max(1e-6, rss1 / n_samples))
            mdl2 = 2 * np.log(n_samples) + n_samples * np.log(max(1e-6, rss2 / n_samples))

            best_model_idx = 1 if mdl1 <= mdl2 else 2
            
            if best_model_idx == 1:
                eq_str = f"Gap = {coeffs1[0]:.4f} * E_gate + {coeffs1[1]:.4f} * E_readout + {coeffs1[2]:.4f}"
                confidence = max(0.01, r_sq1)
                complexity = round(float(mdl1), 4)
                improvement = (rss_null - rss1) / rss_null if rss_null > 0 else 0.0
            else:
                eq_str = f"Gap = {coeffs2[0]:.4f} * (E_gate * E_readout) + {coeffs2[1]:.4f}"
                confidence = max(0.01, r_sq2)
                complexity = round(float(mdl2), 4)
                improvement = (rss_null - rss2) / rss_null if rss_null > 0 else 0.0

            # LAW ACCEPTANCE FILTER
            v_count = len(vendors)
            p_count = len(paradigms)
            
            # Must support >= 2 vendors, >= 2 technologies, and show >= 5% improvement over null
            passes_filters = (v_count >= 2) and (p_count >= 2) and (improvement >= 0.05) and (complexity < 100.0)

            if passes_filters:
                law_record = {
                    "id": f"RLAW_{fam['id'].split('_')[-1]}",
                    "equation": eq_str,
                    "confidence": round(float(confidence), 4),
                    "complexity": complexity,
                    "supporting_observations": [g["id"] for g in gaps if g["prediction_id"] in p_ids],
                    "cross_platform_support": {
                        "vendors": list(vendors),
                        "paradigms": list(paradigms)
                    }
                }
                self.reality_mem.save_discovered_law(law_record)
                discovered_laws.append(law_record)

        # Write report
        self._write_markdown_report(discovered_laws)
        return discovered_laws

    def _write_markdown_report(self, laws: List[Dict[str, Any]]) -> None:
        lines = [
            "# Reality-Native Discovered Laws Report — Phase 3B",
            "",
            "Documents the mathematical laws discovered directly from physical hardware observations bypassing simulation biases.",
            "",
            "## Accepted Reality-Native Laws",
            ""
        ]
        
        if not laws:
            lines.append("*No reality-native laws discovered that satisfied all multi-vendor/platform filters and MDL criteria.*")
        else:
            for law in laws:
                lines.append(f"### Law `{law['id']}`")
                lines.append(f"- **Formulation**: `{law['equation']}`")
                lines.append(f"- **Empirical Confidence ($R^2$)**: `{law['confidence']:.4f}`")
                lines.append(f"- **Model Complexity (MDL Score)**: `{law['complexity']:.4f}`")
                lines.append(f"- **Number of Supporting Observations**: `{len(law['supporting_observations'])}` runs")
                lines.append("- **Cross-Platform Verification Matrix**:")
                lines.append(f"  - **Vendors**: {', '.join(law['cross_platform_support']['vendors'])}")
                lines.append(f"  - **Paradigms**: {', '.join(law['cross_platform_support']['paradigms'])}")
                lines.append("")
                
        os.makedirs("docs", exist_ok=True)
        with open("docs/DISCOVERED_LAWS.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

if __name__ == "__main__":
    eng = RealityNativeLawDiscoveryEngine()
    print("Laws mined size:", len(eng.discover_laws()))
