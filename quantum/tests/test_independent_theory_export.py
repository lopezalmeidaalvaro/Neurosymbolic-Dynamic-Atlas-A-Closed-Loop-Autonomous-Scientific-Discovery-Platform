import os
import sqlite3
import pytest
from quantum.reality_native.independent_theory_export import IndependentTheoryExporter

@pytest.fixture
def temp_reality_db(tmp_path):
    reality_db = str(tmp_path / "test_reality_native_export.db")
    conn = sqlite3.connect(reality_db)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidate_theories (
            id TEXT PRIMARY KEY,
            name TEXT,
            assumptions TEXT,
            equations TEXT,
            mechanisms TEXT,
            failure_modes TEXT,
            validity_domain TEXT,
            status TEXT
        )
    """)
    cursor.execute("""
        INSERT INTO candidate_theories (id, name, assumptions, equations, mechanisms, failure_modes, validity_domain, status)
        VALUES (
            'RTHEORY_001',
            'Test Theory Name',
            '["Assumption 1", "Assumption 2"]',
            '[]',
            '[]',
            '["Failure Mode 1"]',
            '{"max_gate_error": 0.10, "max_readout_error": 0.15, "min_shots": 500, "supported_paradigms": ["Superconducting"]}',
            'CANDIDATE'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discovered_laws (
            equation TEXT,
            confidence REAL,
            complexity REAL
        )
    """)
    cursor.execute("""
        INSERT INTO discovered_laws (equation, confidence, complexity)
        VALUES ('Gap = -1.4500 * E_gate + -1.5000 * E_readout + -0.0100', 0.95, 2.0)
    """)
    conn.commit()
    conn.close()
    return reality_db

def test_independent_theory_export_flow(temp_reality_db):
    exporter = IndependentTheoryExporter(reality_db_path=temp_reality_db)
    spec = exporter.export_theory()
    
    assert spec["id"] == "RTHEORY_001"
    assert spec["name"] == "Test Theory Name"
    assert abs(spec["coefficients"]["a"] - (-1.45)) < 1e-5
    assert abs(spec["coefficients"]["b"] - (-1.50)) < 1e-5
    assert abs(spec["coefficients"]["c"] - (-0.01)) < 1e-5
    assert os.path.exists("docs/RTHEORY_001_EXPORT.md")
