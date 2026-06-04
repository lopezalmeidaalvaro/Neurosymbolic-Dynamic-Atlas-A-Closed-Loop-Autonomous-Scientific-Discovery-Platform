import os
import sys
import json
from typing import Dict, Any, List

from quantum.reality_native.reality_gap_extractor import RealityGapExtractor
from quantum.reality_native.anomaly_clustering import AnomalyClusteringEngine
from quantum.reality_native.reality_native_law_discovery import RealityNativeLawDiscoveryEngine
from quantum.reality_native.causal_mechanism_discovery import CausalMechanismDiscoveryEngine
from quantum.reality_native.theory_synthesis import TheorySynthesisEngine
from quantum.reality_native.prediction_generator import PredictionGenerator
from quantum.reality_native.replication_audit import ReplicationAuditEngine
from quantum.reality_native.adversarial_review import AdversarialScientificReview
from quantum.reality_native.epistemic_classification import EpistemicClassificationEngine

def run_pipeline() -> str:
    print("====================================================")
    print("STARTING PHASE 3B: REALITY-NATIVE THEORY DISCOVERY")
    print("====================================================")
    
    # Paths to files
    rep_report = "hardware_replication_report.json"
    
    # 1. Reality Gap Extraction
    print("\n[Phase 3B-A] Extracting Reality Gaps...")
    extractor = RealityGapExtractor()
    gaps = extractor.extract_reality_gaps(rep_report_path=rep_report)
    print(f"Computed {len(gaps)} reality gap records.")
    
    # 2. Anomaly Clustering
    print("\n[Phase 3B-B] Clustering Anomalies...")
    clustering = AnomalyClusteringEngine()
    families = clustering.cluster_anomalies()
    print(f"Identified {len(families)} stable anomaly families.")
    
    # 3. Reality-Native Law Discovery
    print("\n[Phase 3B-C] Discovering Symbolic Laws...")
    law_discovery = RealityNativeLawDiscoveryEngine()
    laws = law_discovery.discover_laws(rep_report_path=rep_report)
    print(f"Mined {len(laws)} physical laws satisfying multi-platform filters.")
    
    # 4. Causal Mechanism Discovery
    print("\n[Phase 3B-D] Discovering Causal Mechanisms...")
    causal_discovery = CausalMechanismDiscoveryEngine()
    mechs = causal_discovery.discover_mechanisms(rep_report_path=rep_report)
    print(f"Verified causal structures for {len(mechs)} laws.")
    
    # 5. Theory Synthesis
    print("\n[Phase 3B-E] Synthesizing Candidate Theories...")
    synthesis = TheorySynthesisEngine()
    theories = synthesis.synthesize_theories()
    print(f"Formulated {len(theories)} candidate theories.")
    
    # 6. Novel Prediction Generation
    print("\n[Phase 3B-F] Generating Out-Of-Sample Predictions...")
    pred_gen = PredictionGenerator()
    preds = pred_gen.generate_predictions()
    print(f"Preregistered {len(preds)} predictions targeting future runs.")
    
    # 7. Independent Replication Audit
    print("\n[Phase 3B-G] Executing Blind Replication Audit...")
    rep_audit = ReplicationAuditEngine()
    audit_results = rep_audit.run_replication_audit()
    print(f"Replication success rate: {audit_results.get('replication_rate', 0.0)*100:.2f}%")
    
    # 8. Adversarial Scientific Review
    print("\n[Phase 3B-H] Running Adversarial Falsification Review...")
    adv_review = AdversarialScientificReview()
    review_results = adv_review.review_theories()
    
    # 9. Epistemic Classification
    print("\n[Phase 3B-I] Executing Epistemic Classification...")
    classifier = EpistemicClassificationEngine()
    classifications = classifier.classify_theories()
    
    # Check if we have any proven Reality-Native Theories
    reality_native_theories = [c for c in classifications if c["category"] == "REALITY_NATIVE_THEORY"]
    
    print("\n====================================================")
    print("PHASE 3B EVALUATION RESULTS SUMMARY")
    print("====================================================")
    for c in classifications:
        print(f"- Theory: {c['id']}")
        print(f"  Classification Category: {c['category']}")
        print(f"  Accuracy Improvement: {c['metrics']['improvement_percent']}%")
        print(f"  Replication Rate: {c['metrics']['replication_rate']*100:.2f}%")
        print(f"  Survived Adversarial: {c['metrics']['survived_adversarial']}")
    print("====================================================")
    
    if reality_native_theories:
        verdict = "REALITY_NATIVE_THEORY"
        print(f"VERDICT: {verdict}")
        print(f"Successfully validated {len(reality_native_theories)} reality-native theories.")
    else:
        verdict = "NO_REALITY_NATIVE_THEORY_DISCOVERED"
        print(f"VERDICT: {verdict}")
        print("No candidate theories survived all validation constraints.")
        
    return verdict

if __name__ == "__main__":
    verdict = run_pipeline()
    if verdict == "REALITY_NATIVE_THEORY":
        sys.exit(0)
    else:
        sys.exit(1)
