import os
import json
import pytest
from quantum.law_validation.fdr_audit import FDRAudit
from quantum.law_validation.replication_engine import LawReplicationEngine

def test_fdr_audit():
    laws_path = "test_fdr_laws.json"
    report_path = "test_fdr_report.json"
    
    # Initialize laws
    engine = LawReplicationEngine(laws_path=laws_path)
    engine.get_or_create_laws()
    
    audit = FDRAudit(laws_path=laws_path, output_path=report_path)
    report = audit.run_fdr_audit()
    
    assert "average_fdr" in report
    assert "laws_p_values" in report
    assert os.path.exists(report_path)
    
    # Cleanup
    if os.path.exists(laws_path):
        os.remove(laws_path)
    if os.path.exists(report_path):
        os.remove(report_path)
