import os
import shutil
import pytest
from quantum.reality_native.domain_expansion_engine import DomainExpansionEngine
from quantum.reality_native.parallel_theory_discovery import ParallelTheoryDiscovery
from quantum.novel_physics.impossible_prediction_generator import ImpossiblePredictionGenerator
from quantum.novel_physics.independent_novel_physics_validation import IndependentNovelPhysicsValidation

def test_novel_physics_validation():
    test_db_dir = "databases_test_novel_val"
    if os.path.exists(test_db_dir):
        shutil.rmtree(test_db_dir)

    try:
        engine = DomainExpansionEngine(seed=42)
        all_data = engine.generate_all_domains()
        discovery = ParallelTheoryDiscovery(output_dir=test_db_dir)
        theories = discovery.discover_theories_for_all_domains(all_data)

        ipg = ImpossiblePredictionGenerator(theories)
        impossible_cases = ipg.generate_impossible_predictions()

        validator = IndependentNovelPhysicsValidation(all_data, theories=theories)
        results = validator.run_validation(impossible_cases)

        assert "overall_verification_rate" in results
        assert results["overall_verification_rate"] >= 0.70
        assert results["status"] == "PASSED"
        assert os.path.exists("docs/NOVEL_PHYSICS_VALIDATION.md")

    finally:
        if os.path.exists(test_db_dir):
            shutil.rmtree(test_db_dir)
