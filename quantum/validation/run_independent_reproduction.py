import os
import sys
import json
import sqlite3
from typing import Dict, Any, List

from quantum.reality_native.independent_theory_export import IndependentTheoryExporter
from quantum.reality_native.theory_reconstruction import TheoryReconstructor
from quantum.reality_native.prediction_locking_engine import PredictionLockingEngine
from quantum.reality_native.independent_validation_dataset import IndependentValidationDataset
from quantum.reality_native.independent_reproduction_tournament import IndependentReproductionTournament
from quantum.reality_native.cross_lab_simulation import CrossLabSimulationEngine
from quantum.reality_native.reproduction_leakage_audit import ReproductionLeakageAuditor
from quantum.reality_native.independent_epistemic_verdict import IndependentEpistemicVerdictEvaluator
from quantum.reality_native.external_reimplementation_challenge import ExternalReimplementationChallenge

def write_reproduction_report(
    verdict: str,
    tour: Dict[str, Any],
    labs: Dict[str, Any],
    leak: Dict[str, Any],
    challenge: Dict[str, Any]
) -> None:
    
    # Read locked predictions counts and metadata
    conn = sqlite3.connect("reality_native.db")
    c = conn.cursor()
    c.execute("SELECT count(*) FROM locked_predictions")
    locked_count = c.fetchone()[0]
    
    c.execute("SELECT checksum FROM locked_predictions LIMIT 1")
    sample_hash = c.fetchone()
    sample_hash_str = sample_hash[0] if sample_hash else "None"
    
    conn.close()

    lines = [
        "# Independent Reproduction Report — Phase 3B.2",
        "",
        "Provides the consolidated verification evidence and standings for the independent reproduction of RTHEORY_001.",
        "",
        "## Final Epistemic Classification Verdict",
        "",
        f"> [!IMPORTANT]",
        f"> **Epistemic Standing Verdict**: **`{verdict}`**",
        "",
        "## Summary Verification Metrics Dashboard",
        "",
        f"- **Reproduction Tournament MAE**: `{tour['RECONSTRUCTED_THEORY']['MAE']:.6f}` vs Sim Baseline MAE `{tour['SIM_THEORY']['MAE']:.6f}`",
        f"- **Relative Error Reduction (Improvement)**: **`{tour['RECONSTRUCTED_THEORY']['ImprovementPercent']:.2f}%`** (Target >= 15.0%)",
        f"- **Replication Success Rate**: **`{tour['RECONSTRUCTED_THEORY']['ReplicationRate']*100:.2f}%`** (Target >= 90.0%)",
        f"- **Mean Cross-Lab Implementation Agreement**: **`{labs['mean_agreement']*100:.2f}%`** (Target >= 90.0%)",
        f"- **Cryptographic Checksum Locked Predictions**: `{locked_count}` records registered (Sample Hash: `{sample_hash_str}`)",
        f"- **Leakage Forensics Score**: **`{leak['total_leakage_score']*100:.2f}%`** (Target < 1.0%)",
        f"- **Clean-Room Prediction Equivalence**: **`{challenge['prediction_equivalence']*100:.2f}%`** (Target >= 99.0%)",
        f"- **Clean-Room Decision Agreement**: **`{challenge['decision_agreement']*100:.2f}%`** (Target >= 99.0%)",
        "",
        "## Section Breakdown Detail Recaps",
        f"- **Export Specification**: Verified and written to [RTHEORY_001_EXPORT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/RTHEORY_001_EXPORT.md).",
        f"- **Reconstructed Predict Engine**: Independently implemented and verified in [theory_reconstruction.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/reality_native/theory_reconstruction.py).",
        f"- **Clean-Room Challenge Code**: Successfully executed inside [external_reimplementation_challenge.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/reality_native/external_reimplementation_challenge.py).",
        ""
    ]

    with open("docs/INDEPENDENT_REPRODUCTION_REPORT.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def run_independent_reproduction_pipeline() -> str:
    print("====================================================")
    print("STARTING PHASE 3B.2: INDEPENDENT THEORY REPRODUCTION")
    print("====================================================")

    # 1. Export Complete Theory Specification
    print("\n[Phase 3B.2A] Exporting RTHEORY_001 specification...")
    exporter = IndependentTheoryExporter()
    spec = exporter.export_theory()
    print("Specification exported to docs/RTHEORY_001_EXPORT.md.")

    # 2. Reconstruct Predict Engine
    print("\n[Phase 3B.2B] Reconstructing predictor engine...")
    reconstructor = TheoryReconstructor()
    print("Standalone predict() constructed.")

    # 3. Generate OOD Validation Dataset
    print("\n[Phase 3B.2D] Generating OOD validation dataset...")
    dataset_gen = IndependentValidationDataset()
    validation_data = dataset_gen.generate_dataset()
    print(f"Dataset generated with {len(validation_data)} OOD backend records.")

    # 4. Preregistered Prediction Locking
    print("\n[Phase 3B.2C] Preregistering and locking predictions...")
    locker = PredictionLockingEngine()
    
    # Compile prediction trials for locking
    predictions_to_lock = []
    for idx, run in enumerate(validation_data):
        pred_val = reconstructor.predict(run["predicted_sim"], run["gate_error"], run["readout_error"])
        predictions_to_lock.append({
            "id": f"LOCK_REPRO_{idx:03d}",
            "theory_id": "RTHEORY_001",
            "predicted_val": pred_val,
            "condition": {
                "device": run["device"],
                "gate_error": run["gate_error"],
                "readout_error": run["readout_error"]
            }
        })
    locked_records = locker.lock_predictions(predictions_to_lock)
    checksum_passed = all(r["status"] in ("NEW_LOCKED", "LOCKED_PREVENTED_MUTATION") for r in locked_records)
    print(f"Locked {len(locked_records)} predictions with SHA-256 hashes.")

    # 5. Reproduction Tournament
    print("\n[Phase 3B.2E] Running reproduction tournament...")
    tour_engine = IndependentReproductionTournament()
    tour_results = tour_engine.run_tournament(validation_data)
    print(f"MAE Improvement: {tour_results['RECONSTRUCTED_THEORY']['ImprovementPercent']}%")

    # 6. Cross-Lab Simulation
    print("\n[Phase 3B.2F] Running cross-lab simulation validation...")
    cross_lab = CrossLabSimulationEngine()
    cross_results = cross_lab.run_cross_lab_validation(validation_data)
    print(f"Mean Cross-Lab Agreement: {cross_results['mean_agreement']*100:.2f}%")

    # 7. Leakage Forensics
    print("\n[Phase 3B.2G] Running leakage forensics check...")
    auditor = ReproductionLeakageAuditor()
    leakage_results = auditor.run_leakage_audit(validation_data)
    print(f"Leakage check: {leakage_results['status']} (score: {leakage_results['total_leakage_score']})")

    # 8. Clean-Room Reimplementation Challenge
    print("\n[Phase 3B.2J] Executing clean-room challenge...")
    challenge = ExternalReimplementationChallenge()
    challenge_results = challenge.run_challenge(validation_data)
    print(f"Equivalence Rate: {challenge_results['prediction_equivalence']*100:.2f}%")

    # 9. Epistemic Verdict Evaluation
    print("\n[Phase 3B.2H] Evaluating epistemic verdict standings...")
    evaluator = IndependentEpistemicVerdictEvaluator()
    verdict = evaluator.run_epistemic_evaluation(
        replication_rate=tour_results["RECONSTRUCTED_THEORY"]["ReplicationRate"],
        cross_lab_agreement=cross_results["mean_agreement"],
        leakage_score=leakage_results["total_leakage_score"],
        improvement_percent=tour_results["RECONSTRUCTED_THEORY"]["ImprovementPercent"],
        prediction_equivalence=challenge_results["prediction_equivalence"],
        checksum_passed=checksum_passed,
        external_reimplementation_passed=(challenge_results["status"] == "PASSED")
    )
    
    print("\n====================================================")
    print("PHASE 3B.2 REPRODUCTION RESULTS SUMMARY")
    print("====================================================")
    print(f"- Final Epistemic Verdict: {verdict}")
    print(f"- Replication Success Rate: {tour_results['RECONSTRUCTED_THEORY']['ReplicationRate']*100:.2f}%")
    print(f"- Mean Lab Agreement Rate: {cross_results['mean_agreement']*100:.2f}%")
    print(f"- Clean-Room Equivalence: {challenge_results['prediction_equivalence']*100:.2f}%")
    print(f"- Leakage Audit: {leakage_results['status']}")
    print("====================================================")

    # 10. Write aggregated reproduction report
    write_reproduction_report(verdict, tour_results, cross_results, leakage_results, challenge_results)

    return verdict

if __name__ == "__main__":
    verdict = run_independent_reproduction_pipeline()
    if verdict == "SCIENTIFICALLY_REPRODUCIBLE_THEORY":
        sys.exit(0)
    else:
        sys.exit(1)
