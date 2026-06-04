import os
import shutil
import pytest
from quantum.reality_native.domain_expansion_engine import DomainExpansionEngine
from quantum.reality_native.parallel_theory_discovery import ParallelTheoryDiscovery
from quantum.reality_native.mass_reproduction_engine import MassReproductionEngine

def test_mass_reproduction():
    test_db_dir = "databases_test_reproduction"
    if os.path.exists(test_db_dir):
        shutil.rmtree(test_db_dir)
    os.makedirs(test_db_dir, exist_ok=True)

    try:
        # Generate data and discover theories
        engine = DomainExpansionEngine(seed=42)
        all_data = engine.generate_all_domains()

        discovery = ParallelTheoryDiscovery(output_dir=test_db_dir)
        theories = discovery.discover_theories_for_all_domains(all_data)

        # Run reproduction
        reproduction = MassReproductionEngine(theories, all_data)
        results = reproduction.run_mass_reproduction()
        reproduction.cleanup_external_files()

        # Assertions
        assert "overall_reproduction_rate" in results
        assert results["overall_reproduction_rate"] >= 0.70, "Reproduction success rate should be >= 70%"
        assert len(results["theories_reproduction"]) == 10

        for t_id, repro_data in results["theories_reproduction"].items():
            assert repro_data["status"] == "PASSED"
            assert "MAE_Improvement" in repro_data
            assert "PredictionEquivalence" in repro_data

        assert os.path.exists("docs/MASS_REPRODUCTION_REPORT.md"), "Mass reproduction report should exist"

    finally:
        if os.path.exists(test_db_dir):
            shutil.rmtree(test_db_dir)
