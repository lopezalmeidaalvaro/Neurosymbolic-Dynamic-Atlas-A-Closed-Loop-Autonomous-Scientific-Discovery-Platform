import os
import pytest
from quantum.external_audit.forensic_export_engine import ForensicExportEngine
from quantum.external_audit.chain_of_custody import ChainOfCustodyVerifier

def test_chain_of_custody():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    exporter = ForensicExportEngine(root)
    manifest = exporter.generate_manifest()
    
    verifier = ChainOfCustodyVerifier(root, manifest)
    res = verifier.verify()
    
    assert res["verdict"] == "PASS"
    assert res["checksum_integrity"] is True
    assert res["sqlite_integrity"] is True
    assert res["no_orphan_entries"] is True
    assert res["no_broken_references"] is True
    
    report_path = os.path.join(root, "docs", "CHAIN_OF_CUSTODY_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
