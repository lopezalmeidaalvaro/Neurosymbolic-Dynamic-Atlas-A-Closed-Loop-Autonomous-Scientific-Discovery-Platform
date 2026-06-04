import os
import json
from quantum.evidence_audit.evidence_memory import EvidenceMemory
from quantum.evidence_audit.hardware_evidence_inventory import HardwareEvidenceInventory
from quantum.evidence_audit.effective_sample_size import EffectiveSampleSizeAudit
from quantum.evidence_audit.dependence_leakage_audit import DependenceLeakageAudit
from quantum.evidence_audit.correlation_forensics import CorrelationForensics
from quantum.evidence_audit.technology_diversity import TechnologyDiversityAudit
from quantum.evidence_audit.vendor_independence import VendorIndependenceAudit
from quantum.evidence_audit.calibration_diversity import CalibrationDiversityAudit
from quantum.evidence_audit.benchmark_diversity import BenchmarkDiversityAudit
from quantum.evidence_audit.noise_law_redundancy import NoiseLawRedundancyAudit
from quantum.evidence_audit.counterfactual_evidence import CounterfactualEvidenceAudit
from quantum.evidence_audit.evidence_stress_tests import EvidenceStressTests
from quantum.evidence_audit.discovery_readiness import DiscoveryReadinessAudit
from quantum.evidence_audit.evidence_consensus import EvidenceConsensusEngine

def run_evidence_pipeline(
    db_path: str = "theory_memory.db",
    evidence_db_path: str = "evidence_memory.db"
) -> str:
    
    print("====================================================")
    print("Starting Hardware Evidence Sufficiency Audit Engine")
    print("====================================================")

    # Initialize Evidence Memory database
    mem = EvidenceMemory(db_path=evidence_db_path)
    mem.clear()

    # Step A: Compile Hardware Evidence Inventory
    print("\n[Step A] Compiling Hardware Evidence Inventory...")
    inv_eng = HardwareEvidenceInventory(db_path=db_path)
    inv_results = inv_eng.compile_inventory()
    mem.save_audit_result("hardware_evidence_inventory", float(inv_results["total_experiments"]), inv_results)

    # Step B: Effective Sample Size Audit
    print("\n[Step B] Auditing Effective Sample Size...")
    ess_eng = EffectiveSampleSizeAudit(db_path=db_path)
    ess_results = ess_eng.audit_sample_size()
    mem.save_audit_result("effective_sample_size", float(ess_results["global_ess"]), ess_results)

    # Step C: Dependence & Leakage Audit
    print("\n[Step C] Running Dependence & Leakage Audit...")
    leakage_eng = DependenceLeakageAudit()
    leakage_results = leakage_eng.perform_leakage_audit()
    mem.save_audit_result("dependence_leakage_audit", float(leakage_results["evidence_independence_score"]), leakage_results)

    # Step D: Correlation Forensics
    print("\n[Step D] Investigating Correlation Forensics...")
    corr_eng = CorrelationForensics(db_path=db_path)
    corr_results = corr_eng.run_diagnostics()
    mem.save_audit_result("correlation_forensics", float(corr_results["correlation_stability_percentage"]), corr_results)

    # Step E: Technology Diversity Audit
    print("\n[Step E] Auditing Technology Diversity...")
    tech_eng = TechnologyDiversityAudit()
    tech_results = tech_eng.audit_diversity()
    mem.save_audit_result("technology_diversity", float(tech_results["technology_diversity_score"]), tech_results)

    # Step F: Vendor Independence Audit
    print("\n[Step F] Auditing Vendor Independence...")
    vendor_eng = VendorIndependenceAudit(db_path=db_path)
    vendor_results = vendor_eng.audit_vendors()
    mem.save_audit_result("vendor_independence", float(vendor_results["vendor_independence_score"]), vendor_results)

    # Step G: Calibration Diversity Audit
    print("\n[Step G] Auditing Calibration Diversity...")
    cal_eng = CalibrationDiversityAudit(db_path=db_path)
    cal_results = cal_eng.audit_calibrations()
    mem.save_audit_result("calibration_diversity", float(cal_results["calibration_diversity_score"]), cal_results)

    # Step H: Benchmark Diversity Audit
    print("\n[Step H] Auditing Benchmark Diversity...")
    bench_eng = BenchmarkDiversityAudit()
    bench_results = bench_eng.audit_benchmarks()
    mem.save_audit_result("benchmark_diversity", float(bench_results["benchmark_coverage_score"]), bench_results)

    # Step I: Noise Law Redundancy Audit
    print("\n[Step I] Auditing Noise Law Redundancy...")
    noise_eng = NoiseLawRedundancyAudit()
    noise_results = noise_eng.audit_redundancy()
    mem.save_audit_result("noise_law_redundancy", float(noise_results["redundancy_score"]), noise_results)

    # Step J: Counterfactual Evidence Audit
    print("\n[Step J] Running Counterfactual Evidence Audit...")
    cf_eng = CounterfactualEvidenceAudit(db_path=db_path)
    cf_results = cf_eng.run_counterfactual_audit()
    mem.save_audit_result("counterfactual_evidence", 1.0 if cf_results["status"] == "PASSED" else 0.0, cf_results)

    # Step K: Scientific Evidence Stress Test
    print("\n[Step K] Running Scientific Evidence Stress Tests...")
    stress_eng = EvidenceStressTests()
    stress_results = stress_eng.run_stress_tests()
    mem.save_audit_result("evidence_stress_tests", float(stress_results["evidence_robustness_score"]), stress_results)

    # Step L: Discovery Readiness Score
    print("\n[Step L] Computing Unified Discovery Readiness Score...")
    readiness_eng = DiscoveryReadinessAudit()
    readiness_results = readiness_eng.compute_readiness(
        ess_results, leakage_results, vendor_results, tech_results, cal_results, bench_results, corr_results, stress_results
    )
    mem.save_audit_result("discovery_readiness", float(readiness_results["discovery_readiness_score"]), readiness_results)

    # Step N: Consensus Verdict Engine
    print("\n[Step N] Evaluating Global Consensus Verdict...")
    consensus_eng = EvidenceConsensusEngine()
    consensus_results = consensus_eng.evaluate_consensus(
        inv_results, ess_results, leakage_results, vendor_results, tech_results, cal_results, bench_results, corr_results, stress_results, readiness_results
    )
    mem.save_audit_result("evidence_consensus", float(consensus_results["epistemic_confidence_score"]), consensus_results)

    # Save unresolved warnings or risks if any compliance failed
    for criterion, passed in consensus_results["criteria_compliance"].items():
        if not passed:
            mem.save_warning(f"WARN_{criterion.replace(' ', '_')}", "COMPLIANCE_VIOLATION", f"Threshold for {criterion} was not satisfied.", "HIGH")
            mem.save_weakness_risk(f"RISK_{criterion.replace(' ', '_')}", "DATA_QUALITY", f"Insufficient diversity or robustness in {criterion}.", "UNRESOLVED")

    verdict = consensus_results["verdict"]
    print("====================================================")
    print(f"Orchestration Completed. Final Consensus Verdict: {verdict}")
    print("====================================================")

    return verdict

if __name__ == "__main__":
    run_evidence_pipeline()
