import os
import json
import pytest
from quantum.law_validation.replication_engine import LawReplicationEngine
from quantum.law_validation.cross_simulator_validator import CrossSimulatorValidator

def test_law_replication():
    laws_path = "test_rep_laws.json"
    results_path = "test_rep_results.json"
    
    # Run engine
    engine = LawReplicationEngine(laws_path=laws_path, output_path=results_path)
    results = engine.run_replications(num_replications=10) # small run
    
    assert len(results) > 0
    assert "replication_rate" in results[0]
    assert os.path.exists(results_path)
    
    # Cleanup
    if os.path.exists(laws_path):
        os.remove(laws_path)
    if os.path.exists(results_path):
        os.remove(results_path)

def test_cross_simulator_validator():
    laws_path = "test_rep_laws.json"
    results_path = "test_sim_results.json"
    
    # Ensure laws exist first via replication engine helper
    engine = LawReplicationEngine(laws_path=laws_path)
    engine.get_or_create_laws()
    
    validator = CrossSimulatorValidator(laws_path=laws_path, output_path=results_path)
    results = validator.validate_simulators()
    
    assert len(results) > 0
    assert "agreement_score" in results[0]
    assert os.path.exists(results_path)
    
    # Cleanup
    if os.path.exists(laws_path):
        os.remove(laws_path)
    if os.path.exists(results_path):
        os.remove(results_path)
