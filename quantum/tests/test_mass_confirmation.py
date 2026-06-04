import os
import shutil
import pytest
from quantum.reality_native.domain_expansion_engine import DomainExpansionEngine
from quantum.reality_native.parallel_theory_discovery import ParallelTheoryDiscovery
from quantum.reality_native.mass_confirmation_engine import MassConfirmationEngine

def test_mass_confirmation():
    test_db_dir = "databases_test_confirmation"
    if os.path.exists(test_db_dir):
        shutil.rmtree(test_db_dir)
    os.makedirs(test_db_dir, exist_ok=True)

    try:
        # Generate data and discover theories
        engine = DomainExpansionEngine(seed=42)
        all_data = engine.generate_all_domains()

        discovery = ParallelTheoryDiscovery(output_dir=test_db_dir)
        theories = discovery.discover_theories_for_all_domains(all_data)

        # Run confirmation
        confirmation = MassConfirmationEngine(theories, all_data)
        results = confirmation.run_mass_confirmation()

        # Assertions
        assert "overall_confirmation_rate" in results
        assert results["overall_confirmation_rate"] >= 0.70, "Confirmation success rate should be >= 70%"
        assert len(results["theories_confirmation"]) == 10

        for t_id, confirm_data in results["theories_confirmation"].items():
            assert confirm_data["status"] == "CONFIRMED"
            assert "MAE" in confirm_data
            assert "RMSE" in confirm_data

        assert os.path.exists("docs/MASS_CONFIRMATION_REPORT.md"), "Mass confirmation report should exist"

    finally:
        if os.path.exists(test_db_dir):
            shutil.rmtree(test_db_dir)
