import os
import json
import pytest
from quantum.law_validation.historical_recovery import HistoricalRecovery
from quantum.law_validation.replication_engine import LawReplicationEngine

def test_historical_recovery():
    laws_path = "test_hist_laws.json"
    report_path = "test_hist_report.json"
    
    # Initialize laws
    engine = LawReplicationEngine(laws_path=laws_path)
    engine.get_or_create_laws()
    
    benchmark = HistoricalRecovery(laws_path=laws_path, output_path=report_path)
    report = benchmark.run_benchmark()
    
    assert "rediscovery_rate" in report
    assert "details" in report
    assert os.path.exists(report_path)
    
    # Cleanup
    if os.path.exists(laws_path):
        os.remove(laws_path)
    if os.path.exists(report_path):
        os.remove(report_path)
