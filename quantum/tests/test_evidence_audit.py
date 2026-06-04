import os
import json
import sqlite3
import pytest
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
from quantum.validation.run_evidence_audit import run_evidence_pipeline

TEST_EVIDENCE_DB = "test_evidence_memory.db"

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    yield
    # Cleanup test db
    if os.path.exists(TEST_EVIDENCE_DB):
        os.remove(TEST_EVIDENCE_DB)

def test_evidence_memory():
    mem = EvidenceMemory(db_path=TEST_EVIDENCE_DB)
    mem.clear()
    
    mem.save_audit_result("test_audit", 0.95, {"some": "data"})
    mem.save_warning("test_warn", "TEST_TYPE", "Test message", "LOW")
    mem.save_weakness_risk("test_risk", "TEST_CAT", "Test risk desc", "UNRESOLVED")

    results = mem.get_all_audit_results()
    warns = mem.get_all_warnings()
    risks = mem.get_all_weaknesses_risks()

    assert len(results) == 1
    assert results[0]["id"] == "test_audit"
    assert results[0]["score"] == 0.95
    assert results[0]["details"] == {"some": "data"}

    assert len(warns) == 1
    assert warns[0]["id"] == "test_warn"
    assert warns[0]["message"] == "Test message"

    assert len(risks) == 1
    assert risks[0]["id"] == "test_risk"
    assert risks[0]["status"] == "UNRESOLVED"

def test_hardware_evidence_inventory():
    inv = HardwareEvidenceInventory()
    res = inv.compile_inventory()
    assert res["total_experiments"] > 0
    assert res["unique_hardware_platforms"] >= 3
    assert res["unique_vendors"] >= 4
    assert os.path.exists("docs/HARDWARE_EVIDENCE_INVENTORY.md")

def test_effective_sample_size():
    ess = EffectiveSampleSizeAudit()
    res = ess.audit_sample_size()
    assert res["global_ess"] > 500
    assert "predictions" in res["categories"]
    assert os.path.exists("docs/EFFECTIVE_SAMPLE_SIZE_REPORT.md")

def test_dependence_leakage_audit():
    leakage = DependenceLeakageAudit()
    res = leakage.perform_leakage_audit()
    assert res["leakage_score"] < 0.05
    assert res["evidence_independence_score"] > 0.90
    assert os.path.exists("docs/LEAKAGE_AUDIT_REPORT.md")

def test_correlation_forensics():
    cf = CorrelationForensics()
    res = cf.run_diagnostics()
    assert res["correlation_stability_percentage"] >= 80.0
    assert "leave_one_vendor_out" in res
    assert os.path.exists("docs/CORRELATION_FORENSICS_REPORT.md")

def test_technology_diversity():
    tech = TechnologyDiversityAudit()
    res = tech.audit_diversity()
    assert res["active_paradigms_count"] >= 3
    assert res["technology_diversity_score"] > 0.0
    assert os.path.exists("docs/TECHNOLOGY_DIVERSITY_REPORT.md")

def test_vendor_independence():
    vendor = VendorIndependenceAudit()
    res = vendor.audit_vendors()
    assert res["vendor_independence_score"] >= 0.70
    assert not res["exclusive_dependencies_found"]
    assert os.path.exists("docs/VENDOR_INDEPENDENCE_REPORT.md")

def test_calibration_diversity():
    cal = CalibrationDiversityAudit()
    res = cal.audit_calibrations()
    assert res["unique_calibration_states_count"] >= 20
    assert res["calibration_diversity_score"] >= 1.0
    assert os.path.exists("docs/CALIBRATION_DIVERSITY_REPORT.md")

def test_benchmark_diversity():
    bench = BenchmarkDiversityAudit()
    res = bench.audit_benchmarks()
    assert res["number_of_represented_families"] >= 10
    assert res["benchmark_coverage_score"] >= 1.0
    assert os.path.exists("docs/BENCHMARK_DIVERSITY_REPORT.md")

def test_noise_law_redundancy():
    noise = NoiseLawRedundancyAudit()
    res = noise.audit_redundancy()
    assert res["redundancy_score"] < 0.50
    assert os.path.exists("docs/NOISE_REDUNDANCY_REPORT.md")

def test_counterfactual_evidence():
    cf = CounterfactualEvidenceAudit()
    res = cf.run_counterfactual_audit()
    assert res["status"] == "PASSED"
    assert os.path.exists("docs/COUNTERFACTUAL_EVIDENCE_REPORT.md")

def test_evidence_stress_tests():
    stress = EvidenceStressTests()
    res = stress.run_stress_tests()
    assert res["evidence_robustness_score"] >= 0.85
    assert os.path.exists("docs/EVIDENCE_STRESS_TEST_REPORT.md")

def test_discovery_readiness():
    readiness = DiscoveryReadinessAudit()
    res = readiness.compute_readiness(
        {"global_ess": 550},
        {"leakage_score": 0.015},
        {"vendor_independence_score": 0.95},
        {"technology_diversity_score": 0.78},
        {"calibration_diversity_score": 1.0},
        {"benchmark_coverage_score": 1.0},
        {"correlation_stability_percentage": 100.0},
        {"evidence_robustness_score": 0.97}
    )
    assert res["discovery_readiness_score"] >= 0.80
    assert os.path.exists("docs/DISCOVERY_READINESS_REPORT.md")

def test_evidence_consensus():
    engine = EvidenceConsensusEngine()
    res = engine.evaluate_consensus(
        {"unique_vendors": 4},
        {"global_ess": 550},
        {"evidence_independence_score": 0.98, "leakage_score": 0.02},
        {"vendor_independence_score": 0.95, "exclusive_dependencies_found": False},
        {"active_paradigms_count": 4, "technology_diversity_score": 0.85},
        {"unique_calibration_states_count": 22, "calibration_diversity_score": 1.0},
        {"number_of_represented_families": 11, "benchmark_coverage_score": 1.0},
        {"correlation_stability_percentage": 90.0},
        {"evidence_robustness_score": 0.92},
        {"discovery_readiness_score": 0.94}
    )
    assert res["verdict"] == "DISCOVERY_READY"
    assert os.path.exists("docs/FINAL_PHASE_3A5_VERDICT.md")

def test_full_evidence_audit_pipeline():
    verdict = run_evidence_pipeline(evidence_db_path=TEST_EVIDENCE_DB)
    assert verdict == "DISCOVERY_READY"
    assert os.path.exists(TEST_EVIDENCE_DB)
