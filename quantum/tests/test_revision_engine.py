import os
import json
import sqlite3
import pytest
import numpy as np
from quantum.revision.failure_attribution import FailureAttributionEngine
from quantum.revision.mechanism_survival import MechanismSurvivalAnalysis
from quantum.revision.theory_surgery import TheorySurgeryEngine
from quantum.revision.residual_discovery import ResidualDiscoveryEngine
from quantum.revision.noise_meta_law_discovery import NoiseMetaLawDiscoveryEngine
from quantum.revision.theory_revision_tournament import TheoryRevisionTournamentEngine
from quantum.revision.bayesian_updating import BayesianTheoryUpdatingEngine
from quantum.revision.reality_gap_quantification import RealityGapQuantificationEngine
from quantum.validation.run_revision_engine import run_revision_pipeline

TEST_DB_PATH = "test_theory_memory.db"

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    # Copy production db to test db to avoid mutating production data
    if os.path.exists("theory_memory.db"):
        conn_src = sqlite3.connect("theory_memory.db")
        conn_dst = sqlite3.connect(TEST_DB_PATH)
        conn_src.backup(conn_dst)
        conn_src.close()
        conn_dst.close()
    yield
    # Cleanup test db
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_failure_attribution():
    fa = FailureAttributionEngine(db_path=TEST_DB_PATH)
    rep = json.load(open("hardware_replication_report.json"))
    cal = json.load(open("calibration_audit_report.json"))
    adv = json.load(open("hardware_adversary_report.json"))
    ood = json.load(open("ood_hardware_validation_report.json"))
    mech = json.load(open("physical_mechanism_validation_report.json"))

    attributions = fa.attribute_failures(rep, cal, adv, ood, mech)
    assert len(attributions) > 0
    assert os.path.exists("failure_cause_report.json")
    assert os.path.exists("docs/FAILURE_CAUSE_REPORT.md")

def test_mechanism_survival():
    ms = MechanismSurvivalAnalysis()
    mech = json.load(open("physical_mechanism_validation_report.json"))
    results = ms.evaluate_mechanism_survival(mech)

    assert len(results) > 0
    for res in results:
        assert "overall_survival_rate" in res
        assert "edges" in res
        for edge in res["edges"]:
            assert "survival_ratio" in edge
            assert edge["preservation"] in ["PRESERVED", "ELIMINATED", "REVERSED"]

    assert os.path.exists("surviving_mechanisms.json")
    assert os.path.exists("docs/SURVIVING_MECHANISMS.md")

def test_theory_surgery():
    ts = TheorySurgeryEngine(db_path=TEST_DB_PATH)
    revised = ts.perform_surgery("surviving_mechanisms.json")

    assert len(revised) > 0
    for cand in revised:
        assert "_REV" in cand["id"]
        assert "confidence" in cand
        assert len(cand["mechanism_graph"]["edges"]) >= 0

    assert os.path.exists("theory_surgery_report.json")
    assert os.path.exists("docs/THEORY_EVOLUTION_REPORT.md")

def test_residual_discovery():
    rd = ResidualDiscoveryEngine(db_path=TEST_DB_PATH)
    results = rd.analyze_residuals("hardware_replication_report.json", "temporal_stability_report.json")

    assert "residuals" in results
    assert "correlations" in results
    assert "dominant_factor" in results
    assert len(results["residuals"]) > 0

    assert os.path.exists("residual_discovery_report.json")
    assert os.path.exists("docs/RESIDUAL_DISCOVERY_REPORT.md")

def test_noise_meta_law_discovery():
    nml = NoiseMetaLawDiscoveryEngine(db_path=TEST_DB_PATH)
    meta_laws = nml.discover_noise_meta_laws(
        "hardware_replication_report.json",
        "calibration_audit_report.json",
        "hardware_adversary_report.json"
    )

    assert len(meta_laws) == 3
    for law in meta_laws:
        assert "NOISE_LAW_" in law["id"]
        assert "statement" in law
        assert "r_squared" in law

    assert os.path.exists("noise_meta_laws.json")
    assert os.path.exists("docs/NOISE_META_LAWS.md")

def test_theory_revision_tournament():
    trt = TheoryRevisionTournamentEngine(db_path=TEST_DB_PATH)
    leaderboard = trt.run_tournament(
        "hardware_replication_report.json",
        "calibration_audit_report.json",
        "ood_hardware_validation_report.json",
        "residual_discovery_report.json"
    )

    assert len(leaderboard) > 0
    # The first element must have the highest score
    assert leaderboard[0]["composite_score"] >= leaderboard[-1]["composite_score"]
    
    # Check that there is at least one Hybrid theory ranked
    types = [x["type"] for x in leaderboard]
    assert "Hybrid" in types

    assert os.path.exists("revised_theory_leaderboard.json")
    assert os.path.exists("docs/REVISED_THEORY_LEADERBOARD.md")

def test_bayesian_theory_updating():
    btu = BayesianTheoryUpdatingEngine(db_path=TEST_DB_PATH)
    updated = btu.update_theory_probabilities("hardware_replication_report.json")

    assert len(updated) > 0
    # Group by family and check sum of posteriors
    family_sums = {}
    for item in updated:
        fam = item["parent_id"]
        family_sums[fam] = family_sums.get(fam, 0.0) + item["posterior"]

    for fam, s in family_sums.items():
        assert pytest.approx(s, 1e-2) == 1.0

    assert os.path.exists("bayesian_theory_report.json")
    assert os.path.exists("docs/BAYESIAN_THEORY_REPORT.md")

def test_reality_gap_quantification():
    rg = RealityGapQuantificationEngine(db_path=TEST_DB_PATH)
    results = rg.quantify_reality_gap("hardware_replication_report.json", "surviving_mechanisms.json")

    assert "summary" in results
    assert "laws" in results
    assert "theories" in results
    assert "mechanisms" in results
    assert "predictions" in results

    assert os.path.exists("reality_gap_report.json")
    assert os.path.exists("docs/REALITY_GAP_REPORT.md")

def test_full_pipeline_orchestration():
    verdict = run_revision_pipeline(db_path=TEST_DB_PATH)
    assert verdict in ["REVISED_THEORY_FRAMEWORK", "NOISE_AUGMENTED_THEORY", "PARTIALLY_RECOVERED_THEORIES", "INSUFFICIENT_EVIDENCE_FOR_REVISION"]
    assert os.path.exists("docs/FINAL_REVISED_VERDICT.md")
