import os
import json
import pytest
from quantum.law_validation.law_blind_validation import LawBlindValidation
from quantum.law_validation.replication_engine import LawReplicationEngine

def test_blind_validation():
    laws_path = "test_blind_laws.json"
    data_path = "test_blind_data.json"
    report_path = "test_blind_report.json"
    
    # Pre-create test data and laws
    engine = LawReplicationEngine(laws_path=laws_path)
    engine.get_or_create_laws()
    
    from quantum.law_discovery.scientific_observer import ScientificObserver
    observer = ScientificObserver(output_path=data_path)
    observer.generate_large_scale_dataset(target_count=20)
    
    validator = LawBlindValidation(laws_path=laws_path, data_path=data_path, output_path=report_path)
    report = validator.run_blind_validation()
    
    assert "blind_success_rate" in report
    assert "blind_results" in report
    assert len(report["blind_results"]) > 0
    assert os.path.exists(report_path)
    
    # Cleanup
    for f in [laws_path, data_path, report_path]:
        if os.path.exists(f):
            os.remove(f)
