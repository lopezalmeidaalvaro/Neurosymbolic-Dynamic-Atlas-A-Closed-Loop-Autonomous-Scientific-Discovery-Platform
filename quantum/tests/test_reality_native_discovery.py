import os
import json
import sqlite3
import pytest
import numpy as np
from typing import Dict, Any, List

from quantum.reality_native.reality_native_memory import RealityNativeMemory
from quantum.reality_native.reality_gap_extractor import RealityGapExtractor
from quantum.reality_native.anomaly_clustering import AnomalyClusteringEngine
from quantum.reality_native.reality_native_law_discovery import RealityNativeLawDiscoveryEngine
from quantum.reality_native.causal_mechanism_discovery import CausalMechanismDiscoveryEngine
from quantum.reality_native.theory_synthesis import TheorySynthesisEngine
from quantum.reality_native.prediction_generator import PredictionGenerator
from quantum.reality_native.replication_audit import ReplicationAuditEngine
from quantum.reality_native.adversarial_review import AdversarialScientificReview
from quantum.reality_native.epistemic_classification import EpistemicClassificationEngine

@pytest.fixture
def temp_db_paths(tmp_path):
    reality_db = str(tmp_path / "test_reality_native.db")
    theory_db = "theory_memory.db" # read-only access to existing theory db
    return reality_db, theory_db

def test_reality_native_pipeline(temp_db_paths):
    reality_db, theory_db = temp_db_paths
    
    # Initialize isolated memory
    reality_mem = RealityNativeMemory(db_path=reality_db)
    
    # 1. Reality Gap Extraction
    extractor = RealityGapExtractor(db_path=theory_db, reality_db_path=reality_db)
    gaps = extractor.extract_reality_gaps(rep_report_path="hardware_replication_report.json")
    
    assert len(gaps) > 0
    assert all("GAP_" in g["id"] for g in gaps)
    
    # Check that gaps were saved
    saved_gaps = reality_mem.get_all_gaps()
    assert len(saved_gaps) == len(gaps)
    
    # 2. Anomaly Clustering
    clustering = AnomalyClusteringEngine(reality_db_path=reality_db)
    families = clustering.cluster_anomalies()
    
    assert len(families) > 0
    assert all("ANOM_FAM_" in f["id"] for f in families)
    
    # 3. Reality-Native Law Discovery
    law_discovery = RealityNativeLawDiscoveryEngine(db_path=theory_db, reality_db_path=reality_db)
    laws = law_discovery.discover_laws(rep_report_path="hardware_replication_report.json")
    
    assert len(laws) > 0
    assert all("RLAW_" in l["id"] for l in laws)
    assert os.path.exists("docs/DISCOVERED_LAWS.md")
    
    # 4. Causal Mechanism Discovery
    causal_discovery = CausalMechanismDiscoveryEngine(db_path=theory_db, reality_db_path=reality_db)
    mechs = causal_discovery.discover_mechanisms(rep_report_path="hardware_replication_report.json")
    
    assert len(mechs) > 0
    assert all("RMECH_" in m["id"] for m in mechs)
    assert os.path.exists("docs/DISCOVERED_MECHANISMS.md")
    
    # 5. Theory Synthesis
    synthesis = TheorySynthesisEngine(reality_db_path=reality_db)
    theories = synthesis.synthesize_theories()
    
    assert len(theories) > 0
    assert all("RTHEORY_" in t["id"] for t in theories)
    
    # 6. Novel Prediction Generation
    pred_gen = PredictionGenerator(reality_db_path=reality_db)
    preds = pred_gen.generate_predictions()
    
    assert len(preds) > 0
    assert all("FUT_PRED_" in p["id"] for p in preds)
    assert os.path.exists("docs/NOVEL_PREDICTIONS.md")
    
    # 7. Independent Replication Audit
    # We pass simulated unseen observations matching predictions to get confirmation
    unseen_obs = {}
    for p in preds:
        unseen_obs[p["id"]] = p["predicted_effect"]
    
    rep_audit = ReplicationAuditEngine(reality_db_path=reality_db)
    audit_results = rep_audit.run_replication_audit(unseen_observations=unseen_obs)
    
    assert audit_results["replication_rate"] == 1.0
    assert audit_results["status"] == "PASSED"
    assert os.path.exists("docs/REPLICATION_REPORT.md")
    
    # 8. Adversarial Review
    adv_review = AdversarialScientificReview(reality_db_path=reality_db)
    review_results = adv_review.review_theories()
    
    for t_id, res in review_results.items():
        assert res["status"] == "CONFIRMED"
    assert os.path.exists("docs/FALSIFICATION_REPORT.md")
    
    # 9. Epistemic Classification
    classifier = EpistemicClassificationEngine(db_path=theory_db, reality_db_path=reality_db)
    classifications = classifier.classify_theories()
    
    assert len(classifications) > 0
    assert classifications[0]["category"] == "REALITY_NATIVE_THEORY"
    assert os.path.exists("docs/REALITY_NATIVE_THEORY_REPORT.md")
    assert os.path.exists("docs/THEORY_LEADERBOARD.md")
