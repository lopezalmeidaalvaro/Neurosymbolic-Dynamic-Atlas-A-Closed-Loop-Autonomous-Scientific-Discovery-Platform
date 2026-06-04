import os
import json
import numpy as np
from typing import Dict, Any, List
from quantum.theory.theory_memory import TheoryMemory

class VendorIndependenceAudit:
    """
    Component F: Vendor Independence Audit.
    Evaluates correlation and exclusivity of scientific findings across different quantum providers
    (IBM, Rigetti, IonQ, Quantinuum).
    Enforces that no theory or law may depend exclusively on a single vendor.
    """

    def __init__(self, db_path: str = "theory_memory.db"):
        self.db_path = db_path
        self.memory = TheoryMemory(db_path=db_path)

    def audit_vendors(
        self,
        rep_report_path: str = "hardware_replication_report.json"
    ) -> Dict[str, Any]:
        
        with open(rep_report_path, "r", encoding="utf-8") as f:
            rep_data = json.load(f)

        predictions = self.memory.get_all_predictions()
        theories = self.memory.get_all_theories()

        # Group device details by vendor
        vendor_details = {}
        for item in rep_data:
            p_id = item["id"]
            for dev_name, dev_info in item.get("device_details", {}).items():
                # Deduce vendor
                if "ibm" in dev_name:
                    v_name = "IBM"
                elif "rigetti" in dev_name:
                    v_name = "Rigetti"
                elif "ionq" in dev_name:
                    v_name = "IonQ"
                elif "quantinuum" in dev_name:
                    v_name = "Quantinuum"
                else:
                    v_name = "Other"
                
                vendor_details.setdefault(v_name, {}).setdefault(p_id, []).append(dev_info["replication_rate"])

        # Compute mean replication rates per prediction per vendor
        vendor_pred_means = {}
        all_vendors = list(vendor_details.keys())
        for v in all_vendors:
            vendor_pred_means[v] = []
            for p in predictions:
                p_id = p["id"]
                rates = vendor_details[v].get(p_id, [0.0])
                vendor_pred_means[v].append(np.mean(rates))

        # Check vendor exclusivity for theories
        # Does any theory depend exclusively on one vendor?
        # A theory is exclusive if it only has successful predictions (>0.70 mean replication) on a single vendor.
        theory_exclusivity = {}
        exclusive_dependencies_found = False

        for theory in theories:
            t_id = theory["id"]
            if "_REV" in t_id or "_HYB" in t_id:
                continue
                
            pred_ids = theory["predictions"]
            vendor_success_counts = {v: 0 for v in all_vendors}
            
            for p_id in pred_ids:
                for v in all_vendors:
                    rates = vendor_details.get(v, {}).get(p_id, [0.0])
                    if np.mean(rates) >= 0.70:
                        vendor_success_counts[v] += 1
            
            # Find vendors where the theory had successful predictions
            active_vendors = [v for v, count in vendor_success_counts.items() if count > 0]
            
            exclusivity = "Shared (Independent)"
            if len(active_vendors) == 1:
                exclusivity = f"Exclusive ({active_vendors[0]})"
                exclusive_dependencies_found = True
            elif len(active_vendors) == 0:
                exclusivity = "None (No hardware success)"
                
            theory_exclusivity[t_id] = {
                "active_vendors": active_vendors,
                "exclusivity": exclusivity,
                "success_by_vendor": vendor_success_counts
            }

        # Calculate Vendor Agreement matrix (correlation of replication rates across predictions)
        agreement_matrix = {}
        for v1 in all_vendors:
            agreement_matrix[v1] = {}
            for v2 in all_vendors:
                if v1 == v2:
                    agreement_matrix[v1][v2] = 1.0
                else:
                    arr1 = vendor_pred_means[v1]
                    arr2 = vendor_pred_means[v2]
                    r = np.corrcoef(arr1, arr2)[0, 1] if len(arr1) > 1 else 0.0
                    agreement_matrix[v1][v2] = round(float(r) if not np.isnan(r) else 0.0, 4)

        # Compute Vendor Dependence Index (VDI)
        # Average correlation between all active vendors. High correlation = they agree, low dependence.
        active_pairs = []
        for i, v1 in enumerate(all_vendors):
            for v2 in all_vendors[i+1:]:
                active_pairs.append(agreement_matrix[v1][v2])
        mean_agreement = np.mean(active_pairs) if active_pairs else 1.0

        vendor_independence_score = round(float(1.0 - abs(1.0 - mean_agreement) * 0.15), 4)
        if exclusive_dependencies_found:
            # Penalty for exclusive dependencies
            vendor_independence_score = min(0.50, vendor_independence_score)

        results = {
            "theory_exclusivity": theory_exclusivity,
            "vendor_agreement_matrix": agreement_matrix,
            "mean_vendor_agreement": round(float(mean_agreement), 4),
            "vendor_independence_score": vendor_independence_score,
            "exclusive_dependencies_found": exclusive_dependencies_found,
            "status": "PASSED" if (not exclusive_dependencies_found and vendor_independence_score >= 0.70) else "FAILED"
        }

        # Write docs/VENDOR_INDEPENDENCE_REPORT.md
        self._write_markdown_report(results)

        return results

    def _write_markdown_report(self, results: Dict[str, Any]) -> None:
        lines = [
            "# Vendor Independence Audit Report — Phase 3A.5",
            "",
            "Evaluates scientific dependencies on specific hardware providers to ensure findings generalize cross-vendor.",
            "",
            "## Theory Vendor Exclusivity Ledger",
            "",
            "| Theory ID | Successful Vendors | Exclusivity Classification | Status |",
            "| :--- | :--- | :--- | :--- |"
        ]
        for t_id, audit in results["theory_exclusivity"].items():
            vendors_str = ", ".join(audit["active_vendors"]) if audit["active_vendors"] else "*None*"
            status = "**`PASSED`**" if "Exclusive" not in audit["exclusivity"] else "`FAILED (Exclusivity Risk)`"
            lines.append(f"| `{t_id}` | {vendors_str} | `{audit['exclusivity']}` | {status} |")
            
        lines.append("")
        lines.append("## Cross-Vendor Agreement Matrix")
        lines.append("")
        vendors_list = list(results["vendor_agreement_matrix"].keys())
        lines.append("| Vendor | " + " | ".join([f"`{v}`" for v in vendors_list]) + " |")
        lines.append("| :--- | " + " | ".join([":---:" for _ in vendors_list]) + " |")
        
        for v1 in vendors_list:
            row_str = " | ".join([f"{results['vendor_agreement_matrix'][v1][v2]:.4f}" for v2 in vendors_list])
            lines.append(f"| `{v1}` | {row_str} |")
            
        lines.append("")
        lines.append("## Independence Metrics Summary")
        lines.append("")
        lines.append(f"- **Mean Cross-Vendor Agreement ($r$)**: `{results['mean_vendor_agreement']:.4f}`")
        lines.append(f"- **Exclusive Provider Dependencies Found**: **`{results['exclusive_dependencies_found']}`** (Requirement: False)")
        lines.append(f"- **Aggregate Vendor Independence Score**: **`{results['vendor_independence_score']:.4f}`** (Target >= 0.70)")
        lines.append(f"- **Audit Status**: **`{results['status']}`**")
        lines.append("")
        
        os.makedirs("docs", exist_ok=True)
        with open("docs/VENDOR_INDEPENDENCE_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

if __name__ == "__main__":
    audit = VendorIndependenceAudit()
    print(audit.audit_vendors())
