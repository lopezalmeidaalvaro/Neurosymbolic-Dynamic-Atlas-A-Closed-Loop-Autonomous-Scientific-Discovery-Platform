import os
import json
import pytest
from quantum.law_validation.law_compression import LawCompression
from quantum.law_validation.law_minimality import LawMinimality
from quantum.law_validation.replication_engine import LawReplicationEngine

def test_law_compression():
    laws_path = "test_comp_laws.json"
    report_path = "test_comp_report.json"
    
    # Initialize laws
    engine = LawReplicationEngine(laws_path=laws_path)
    engine.get_or_create_laws()
    
    compression = LawCompression(laws_path=laws_path, output_path=report_path)
    report = compression.compress_laws()
    
    assert len(report) > 0
    assert "core_rule" in report[0]
    assert os.path.exists(report_path)
    
    # Cleanup
    if os.path.exists(laws_path):
        os.remove(laws_path)
    if os.path.exists(report_path):
        os.remove(report_path)

def test_law_minimality():
    laws_path = "test_comp_laws.json"
    report_path = "test_min_report.json"
    
    # Initialize laws
    engine = LawReplicationEngine(laws_path=laws_path)
    engine.get_or_create_laws()
    
    minimality = LawMinimality(laws_path=laws_path, output_path=report_path)
    report = minimality.run_minimality_audit()
    
    assert len(report) > 0
    assert "mdl_score" in report[0]
    assert os.path.exists(report_path)
    
    # Cleanup
    if os.path.exists(laws_path):
        os.remove(laws_path)
    if os.path.exists(report_path):
        os.remove(report_path)
