import os
import pytest
from quantum.scientific_reproduction.scientific_dossier_export import ScientificDossierExport

def test_scientific_dossier():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    exporter = ScientificDossierExport(root)
    content = exporter.export_dossier()
    
    assert "Complete Scientific Dossier" in content
    assert "Discovered Candidate Theories" in content
    assert "Physical Assumptions" in content
    
    report_path = os.path.join(root, "docs", "SCIENTIFIC_DOSSIER.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
