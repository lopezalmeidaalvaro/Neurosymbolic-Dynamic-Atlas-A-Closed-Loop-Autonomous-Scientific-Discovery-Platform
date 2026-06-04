import json
from typing import Dict, Any, List

class HardwareConsensus:
    """
    Component O: Scientific Consensus Engine.
    Aggregates statistical results across replication, cross-vendor agreement,
    temporal stability, OOD generalization, and external reproduction
    to compute a unified Global Hardware Confidence Score.
    """

    def __init__(self, db_path: str = "theory_memory.db"):
        self.db_path = db_path

    def calculate_consensus(
        self,
        replication_reports: List[Dict[str, Any]],
        temporal_reports: List[Dict[str, Any]],
        ood_reports: List[Dict[str, Any]],
        external_report: Dict[str, Any],
        fdr_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Computes Global Hardware Confidence Score (0.0 to 1.0) and determines final verdict.
        """
        # Load values
        mean_rep = float(np.mean([r["replication_rate"] for r in replication_reports])) if replication_reports else 0.0
        mean_vendor = float(np.mean([r["cross_vendor_agreement"] for r in replication_reports])) if replication_reports else 0.0
        mean_temp = float(np.mean([r["temporal_stability_score"] for r in temporal_reports])) if temporal_reports else 0.0
        mean_ood = float(np.mean([r["ood_transfer_score"] for r in ood_reports])) if ood_reports else 0.0
        
        ext_score = external_report.get("external_replication_score", 0.0)
        fdr_rate = fdr_report.get("fdr_rate", 1.0)
        fdr_pass = 1.0 if fdr_report.get("status") == "PASSED" else 0.0
        
        # Weighted Consensus Formula
        # Weights: replication=0.20, cross_vendor=0.20, temporal=0.15, OOD=0.15, external=0.15, FDR=0.15
        global_score = (
            0.20 * mean_rep +
            0.20 * mean_vendor +
            0.15 * mean_temp +
            0.15 * mean_ood +
            0.15 * ext_score +
            0.15 * fdr_pass
        )

        # Decide final verdict
        # Accepted Outcomes:
        # - HARDWARE_SUPPORTED_THEORY: If global_score >= 0.80 and FDR < 5% and replication >= 80%
        # - PARTIALLY_TRANSFERRED_THEORY: If global_score is between 0.60 and 0.80
        # - SIMULATION_ONLY_THEORY: If replication < 50% but simulation was good
        # - THEORY_RETRACTED: If it failed everything completely
        # - INSUFFICIENT_HARDWARE_EVIDENCE: If datasets or runs were empty
        
        if not replication_reports:
            verdict = "INSUFFICIENT_HARDWARE_EVIDENCE"
            rationale = "No hardware replication trials were executed."
        elif global_score >= 0.80 and fdr_rate < 0.05 and mean_rep >= 0.80:
            verdict = "HARDWARE_SUPPORTED_THEORY"
            rationale = "Candidate theories successfully passed replication, OOD generalizability, temporal stability, and strict FDR controls on real physical quantum hardware."
        elif global_score >= 0.60:
            verdict = "PARTIALLY_TRANSFERRED_THEORY"
            rationale = "Theories transfer partially, but suffer from significant calibration shifts, temporal degradation, or OOD noise limitations."
        elif mean_rep >= 0.30:
            verdict = "SIMULATION_ONLY_THEORY"
            rationale = "Theories hold in clean simulators but collapse under physical gate/readout noise regimes."
        else:
            verdict = "THEORY_RETRACTED"
            rationale = "Experimental predictions were falsified across all hardware vendors. Theories retracted from scientific memory."

        report = {
            "global_hardware_confidence_score": round(global_score, 4),
            "mean_replication_rate": round(mean_rep, 4),
            "cross_vendor_agreement": round(mean_vendor, 4),
            "temporal_stability": round(mean_temp, 4),
            "ood_generalization": round(mean_ood, 4),
            "external_reproduction": round(ext_score, 4),
            "fdr_rate": round(fdr_rate, 4),
            "final_allowed_verdict": verdict,
            "rationale": rationale
        }

        with open("hardware_consensus_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report

import numpy as np
