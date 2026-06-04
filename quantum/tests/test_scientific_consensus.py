import os
import json
import pytest
from quantum.law_validation.scientific_consensus import ScientificConsensusEngine
from quantum.law_validation.law_retraction import LawRetractionEngine

def test_scientific_consensus():
    report_path = "test_consensus_report.json"
    consensus = ScientificConsensusEngine(output_path=report_path)
    
    # Run compute
    report = consensus.compute_consensus([], [], [], [], {}, {})
    
    assert "scientific_confidence" in report
    assert "consensus_verdict" in report
    assert os.path.exists(report_path)
    os.remove(report_path)

def test_law_retraction():
    report_path = "test_retraction_report.json"
    retraction = LawRetractionEngine(output_path=report_path)
    
    replications = [
        {"id": "LAW_001", "rule": "rule1", "replication_rate": 0.95}
    ]
    simulators = [
        {"id": "LAW_001", "agreement_score": 0.90}
    ]
    counterexamples = [
        {"id": "LAW_001", "law_break_rate": 0.05}
    ]
    meta_vals = [
        {"id": "META_001", "statement": "statement1", "status": "ESTABLISHED_META_LAW", "bootstrap_survival_rate": 0.95}
    ]
    
    registry = retraction.retract_and_update(replications, simulators, counterexamples, meta_vals)
    
    assert "laws" in registry
    assert "meta_laws" in registry
    assert registry["laws"]["LAW_001"]["status"] == "SCIENTIFICALLY_ESTABLISHED"
    assert registry["meta_laws"]["META_001"]["status"] == "ESTABLISHED_META_LAW"
    assert os.path.exists(report_path)
    os.remove(report_path)
