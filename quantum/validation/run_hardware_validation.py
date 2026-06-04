import os
import sys
import json
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.hardware.hardware_runner import HardwareRunner
from quantum.hardware.theory_experiment_generator import TheoryExperimentGenerator
from quantum.hardware.preregistered_predictions import PreregisteredPredictions
from quantum.hardware.hardware_replication import HardwareReplication
from quantum.hardware.temporal_stability import TemporalStability
from quantum.hardware.calibration_audit import CalibrationAudit
from quantum.hardware.hardware_adversary import HardwareAdversary
from quantum.hardware.ood_hardware_validation import OodHardwareValidation
from quantum.hardware.physical_mechanism_validation import PhysicalMechanismValidation
from quantum.hardware.hardware_fdr_audit import HardwareFdrAudit
from quantum.hardware.hardware_theory_tournament import HardwareTheoryTournament
from quantum.hardware.reality_evolution import RealityEvolution
from quantum.hardware.external_reproduction import ExternalReproduction
from quantum.hardware.negative_results_repository import NegativeResultsRepository
from quantum.hardware.hardware_consensus import HardwareConsensus

def main():
    print("======================================================================")
    print("Executing Phase 3A — Reality Transfer & Hardware Scientific Engine")
    print("======================================================================")

    # 1. Initialize Components
    generator = TheoryExperimentGenerator()
    preregister = PreregisteredPredictions()
    replication = HardwareReplication()
    temporal = TemporalStability()
    calibration = CalibrationAudit()
    adversary = HardwareAdversary()
    ood_validation = OodHardwareValidation()
    mechanism_validation = PhysicalMechanismValidation()
    fdr_auditor = HardwareFdrAudit()
    tournament = HardwareTheoryTournament()
    evolution = RealityEvolution()
    reproduction = ExternalReproduction()
    consensus = HardwareConsensus()

    # 2. Run reality transfer loop
    print("\n[Step 1] Translating qualitative rules to quantitative predictions...")
    translated_preds = generator.translate_predictions()
    
    print("\n[Step 2] Freezing and cryptographically pre-registering predictions...")
    preregister.register_predictions(translated_preds)
    
    print("\n[Step 3] Executing multi-hardware replication programs (100 repetitions)...")
    rep_results = replication.run_replication(translated_preds)
    
    print("\n[Step 4] Auditing temporal stability and calibration drift (Days 1-90)...")
    temp_results = temporal.run_temporal_audit(translated_preds)
    
    print("\n[Step 5] Auditing hardware calibration robustness (High/Degraded)...")
    cal_results = calibration.run_calibration_audit(translated_preds)
    
    print("\n[Step 6] Running hardware adversarial tests (Circuit inflation, transpilation noise)...")
    adv_results = adversary.run_adversarial_tests(translated_preds)
    
    print("\n[Step 7] Evaluating Out-of-Distribution (OOD) hardware generalization...")
    ood_results = ood_validation.run_ood_validation(translated_preds)
    
    print("\n[Step 8] Running mechanistic reality check (physical correlations)...")
    mech_results = mechanism_validation.run_mechanism_audit()
    
    print("\n[Step 9] Applying statistical corrections (FDR controls BH/BY)...")
    fdr_results = fdr_auditor.run_fdr_audit(rep_results)
    
    print("\n[Step 10] Running hardware competing theory tournament standings...")
    tournament_standings = tournament.run_tournament(
        replication_reports=rep_results,
        temporal_reports=temp_results,
        calibration_reports=cal_results,
        adversarial_reports=adv_results,
        ood_reports=ood_results,
        mechanism_reports=mech_results,
        fdr_report=fdr_results
    )
    
    print("\n[Step 11] Evolving theories under reality (Retirement & Revision)...")
    evolution_records = evolution.evolve_theories(
        tournament_results=tournament_standings,
        temporal_results=temp_results
    )
    
    print("\n[Step 12] Packaging standalone reproduction package...")
    reproduction_report = reproduction.package_reproduction_suite(translated_preds)
    
    print("\n[Step 13] Running consensus aggregator...")
    consensus_report = consensus.calculate_consensus(
        replication_reports=rep_results,
        temporal_reports=temp_results,
        ood_reports=ood_results,
        external_report=reproduction_report,
        fdr_report=fdr_results
    )

    # 3. Write reports to docs/
    print("\n[Step 14] Compiling and writing Phase 3A reports to docs/...")
    os.makedirs("docs", exist_ok=True)

    # A. HARDWARE_REPLICATION_REPORT.md
    with open("docs/HARDWARE_REPLICATION_REPORT.md", "w", encoding="utf-8") as f:
        f.write("# Hardware Replication Report — Phase 3A\n\n")
        f.write("Logs multi-hardware replication rates across 5 devices and 3 independent vendors.\n\n")
        f.write("## Device Replication Summary\n\n")
        f.write("| Prediction ID | Mean Replication Rate | Cross-Vendor Agreement | Device Variance | Status |\n")
        f.write("| :---: | :---: | :---: | :---: | :---: |\n")
        for r in rep_results:
            p_status = "CONFIRMED" if r["replication_rate"] >= 0.80 else "FAILED"
            f.write(f"| `{r['id']}` | {r['replication_rate']*100:.2f}% | {r['cross_vendor_agreement']*100:.2f}% | {r['device_variance']:.6f} | `{p_status}` |\n")

    # B. HARDWARE_TEMPORAL_REPORT.md
    with open("docs/HARDWARE_TEMPORAL_REPORT.md", "w", encoding="utf-8") as f:
        f.write("# Hardware Temporal Stability Report — Phase 3A\n\n")
        f.write("Evaluates prediction persistence over temporal calibration shifts.\n\n")
        f.write("## Temporal Degradation Standings\n\n")
        f.write("| Prediction ID | Day 1 | Day 7 | Day 30 | Day 90 | Degradation Score | Status |\n")
        f.write("| :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for r in temp_results:
            f.write(f"| `{r['id']}` | {r['replication_rates']['day_1']*100:.1f}% | {r['replication_rates']['day_7']*100:.1f}% | {r['replication_rates']['day_30']*100:.1f}% | {r['replication_rates']['day_90']*100:.1f}% | {r['temporal_degradation']:.4f} | `{r['status']}` |\n")

    # C. HARDWARE_CALIBRATION_REPORT.md
    with open("docs/HARDWARE_CALIBRATION_REPORT.md", "w", encoding="utf-8") as f:
        f.write("# Hardware Calibration Robustness Report — Phase 3A\n\n")
        f.write("Audits prediction accuracy under varying calibration states.\n\n")
        f.write("## Robustness Coefficients\n\n")
        f.write("| Prediction ID | High Fidelity | Nominal | Degraded | Robustness Coef | Status |\n")
        f.write("| :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for r in cal_results:
            f.write(f"| `{r['id']}` | {r['replication_rates_by_state']['high_fidelity']*100:.1f}% | {r['replication_rates_by_state']['nominal']*100:.1f}% | {r['replication_rates_by_state']['degraded']*100:.1f}% | {r['robustness_coefficient']:.4f} | `{r['status']}` |\n")

    # D. HARDWARE_ADVERSARY_REPORT.md
    with open("docs/HARDWARE_ADVERSARY_REPORT.md", "w", encoding="utf-8") as f:
        f.write("# Hardware Adversarial Stress Report — Phase 3A\n\n")
        f.write("Stress-tests predictions under randomized transpilation and circuit depth expansions.\n\n")
        f.write("## Adversarial Survival Summary\n\n")
        f.write("| Prediction ID | Baseline | Transpilation | Depth Inflation | Noise Injection | Survival Rate | Status |\n")
        f.write("| :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for r in adv_results:
            f.write(f"| `{r['id']}` | {r['replication_rates']['baseline']*100:.1f}% | {r['replication_rates']['transpilation_jitter']*100:.1f}% | {r['replication_rates']['depth_expansion']*100:.1f}% | {r['replication_rates']['noise_injection']*100:.1f}% | {r['adversarial_survival_rate']*100:.1f}% | `{r['status']}` |\n")

    # E. HARDWARE_OOD_REPORT.md
    with open("docs/HARDWARE_OOD_REPORT.md", "w", encoding="utf-8") as f:
        f.write("# Hardware OOD Generalization Report — Phase 3A\n\n")
        f.write("Audits generalization on unseen technologies (Neutral Atom, Photonic, Silicon Spin).\n\n")
        f.write("## OOD Generalization Scores\n\n")
        f.write("| Prediction ID | Neutral Atom | Photonic | Silicon Spin | OOD Transfer Score | Status |\n")
        f.write("| :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for r in ood_results:
            f.write(f"| `{r['id']}` | {r['device_replication']['neutral_phoenix']['replication_rate']*100:.1f}% | {r['device_replication']['photonic_helios']['replication_rate']*100:.1f}% | {r['device_replication']['silicon_spin_s1']['replication_rate']*100:.1f}% | {r['ood_transfer_score']*100:.1f}% | `{r['status']}` |\n")

    # F. HARDWARE_MECHANISM_REPORT.md
    with open("docs/HARDWARE_MECHANISM_REPORT.md", "w", encoding="utf-8") as f:
        f.write("# Physical Causal Mechanism Verification Report — Phase 3A\n\n")
        f.write("Checks if simulated mechanism edges remain statistically visible under physical hardware noise.\n\n")
        f.write("## Mechanistic Reality Standings\n\n")
        for r in mech_results:
            f.write(f"### Theory `{r['theory_id']}`: Status = `{r['status']}`\n\n")
            f.write("| Source Node | Target Node | Simulated Weight | Physical Correlation | Status |\n")
            f.write("| :--- | :--- | :---: | :---: | :---: |\n")
            for edge in r["edge_details"]:
                f.write(f"| `{edge['source']}` | `{edge['target']}` | {edge['sim_weight']:.4f} | {edge['physical_correlation']:.4f} | `{edge['status']}` |\n")
            f.write("\n")

    # G. HARDWARE_FDR_REPORT.md
    with open("docs/HARDWARE_FDR_REPORT.md", "w", encoding="utf-8") as f:
        f.write("# Hardware False Discovery Control Report — Phase 3A\n\n")
        f.write("Applies multiple-testing corrections and bootstrap confidence intervals to control false positive confirmations.\n\n")
        f.write(f"- **Total tested:** {fdr_results['total_tested']}\n")
        f.write(f"- **Confirmed discoveries:** {fdr_results['confirmed_discoveries']}\n")
        f.write(f"- **False Discovery Rate:** {fdr_results['fdr_rate']*100:.2f}%\n")
        f.write(f"- **Status:** {fdr_results['status']}\n\n")
        f.write("## Prediction Statistical Significance Details\n\n")
        f.write("| ID | Raw p-value | BH-adjusted p-value | BY-adjusted p-value | 95% Bootstrap CI | Status |\n")
        f.write("| :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for p in fdr_results["predictions"]:
            f.write(f"| `{p['id']}` | {p['raw_p_value']:.4e} | {p['bh_adjusted_p_value']:.4e} | {p['by_adjusted_p_value']:.4e} | {p['bootstrap_ci_95']} | `{p['status']}` |\n")

    # H. HARDWARE_EVOLUTION_REPORT.md
    with open("docs/HARDWARE_EVOLUTION_REPORT.md", "w", encoding="utf-8") as f:
        f.write("# Hardware Reality Theory Evolution Report — Phase 3A\n\n")
        f.write("Tracks status transitions throughout the hardware falsification and evolution loop.\n\n")
        f.write("## Hardware Evolution History Log\n\n")
        f.write("| ID | Theory Name | Evolved Operation | Old Status | New Status | Rationale |\n")
        f.write("| :---: | :--- | :---: | :---: | :---: | :--- |\n")
        for e in evolution_records:
            f.write(f"| `{e['theory_id']}` | {e['name']} | `{e['evolution_operation']}` | `{e['old_status']}` | `{e['new_status']}` | {e['rationale']} |\n")

    # I. FINAL_PHASE_3A_VERDICT.md
    with open("docs/FINAL_PHASE_3A_VERDICT.md", "w", encoding="utf-8") as f:
        f.write("# Final Phase 3A Verdict\n\n")
        f.write(f"Final Allowed Verdict: **`{consensus_report['final_allowed_verdict']}`**\n\n")
        f.write(f"> [!IMPORTANT]\n")
        f.write(f"> **Verdict Rationale:** {consensus_report['rationale']}\n\n")
        f.write("## Global Scientific Verification Summary\n\n")
        f.write("| Target Verification Metric | Target Threshold | Actual Score | Status |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        f.write(f"| **Global Confidence Score** | Score >= 0.80 | {consensus_report['global_hardware_confidence_score']:.4f} | {'PASSED' if consensus_report['global_hardware_confidence_score'] >= 0.80 else 'FAILED'} |\n")
        f.write(f"| **Mean Replication Rate** | Rate >= 80.0% | {consensus_report['mean_replication_rate']*100:.2f}% | {'PASSED' if consensus_report['mean_replication_rate'] >= 0.80 else 'FAILED'} |\n")
        f.write(f"| **Cross-Vendor Agreement** | Agreement >= 80.0% | {consensus_report['cross_vendor_agreement']*100:.2f}% | {'PASSED' if consensus_report['cross_vendor_agreement'] >= 0.80 else 'FAILED'} |\n")
        f.write(f"| **OOD Hardware Generalization** | Generalization >= 75.0% | {consensus_report['ood_generalization']*100:.2f}% | {'PASSED' if consensus_report['ood_generalization'] >= 0.75 else 'FAILED'} |\n")
        f.write(f"| **Temporal Calibration Stability**| Stability >= 75.0% | {consensus_report['temporal_stability']*100:.2f}% | {'PASSED' if consensus_report['temporal_stability'] >= 0.75 else 'FAILED'} |\n")
        f.write(f"| **External Replication Score** | Replication >= 70.0% | {consensus_report['external_reproduction']*100:.2f}% | {'PASSED' if consensus_report['external_reproduction'] >= 0.70 else 'FAILED'} |\n")
        f.write(f"| **False Discovery Rate** | FDR < 5.0% | {consensus_report['fdr_rate']*100:.2f}% | {'PASSED' if consensus_report['fdr_rate'] < 0.05 else 'FAILED'} |\n")

    print("\nPhase 3A Hardware Validation Pipeline Completed Successfully.")
    print("======================================================================")

if __name__ == "__main__":
    main()
