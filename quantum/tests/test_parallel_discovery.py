import os
import shutil
import pytest
from quantum.reality_native.domain_expansion_engine import DomainExpansionEngine
from quantum.reality_native.parallel_theory_discovery import ParallelTheoryDiscovery

def test_parallel_theory_discovery():
    # Setup test directory for databases to avoid overwriting production ones
    test_db_dir = "databases_test_parallel"
    if os.path.exists(test_db_dir):
        shutil.rmtree(test_db_dir)
    os.makedirs(test_db_dir, exist_ok=True)

    try:
        # Generate data
        engine = DomainExpansionEngine(seed=42)
        all_data = engine.generate_all_domains()

        # Run discovery
        discovery = ParallelTheoryDiscovery(output_dir=test_db_dir)
        theories = discovery.discover_theories_for_all_domains(all_data)

        # Assertions
        assert len(theories) == 10, "Should discover exactly 10 theories across 10 domains"
        for t in theories:
            assert t["theory_id"].startswith("RTHEORY_"), "Theory ID should start with RTHEORY_"
            assert os.path.exists(t["db_path"]), f"Database file {t['db_path']} should exist"
            assert "equation" in t, "Theory should contain equation"
            assert "confidence" in t, "Theory should contain confidence metric"
            assert t["confidence"] >= 0.0, "Confidence should be non-negative"

        # Check that MULTI_DOMAIN_DISCOVERY_REPORT.md was created
        assert os.path.exists("docs/MULTI_DOMAIN_DISCOVERY_REPORT.md"), "Discovery report should exist"

    finally:
        # Cleanup
        if os.path.exists(test_db_dir):
            shutil.rmtree(test_db_dir)
