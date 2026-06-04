import os
import pytest
from quantum.external_audit.forensic_export_engine import ForensicExportEngine

def test_forensic_export():
    # Use workspace root as project root
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    exporter = ForensicExportEngine(root)
    manifest = exporter.generate_manifest()
    
    assert "timestamp" in manifest
    assert "records" in manifest
    assert len(manifest["records"]) > 0
    
    # Check that FORENSIC_EXPORT_MANIFEST.md is generated
    manifest_path = os.path.join(root, "docs", "FORENSIC_EXPORT_MANIFEST.md")
    assert os.path.exists(manifest_path)
    assert os.path.getsize(manifest_path) > 0
