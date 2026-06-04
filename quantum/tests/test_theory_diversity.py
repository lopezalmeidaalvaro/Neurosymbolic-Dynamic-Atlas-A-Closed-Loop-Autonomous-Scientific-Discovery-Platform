import os
import shutil
import pytest
from quantum.reality_native.domain_expansion_engine import DomainExpansionEngine
from quantum.reality_native.parallel_theory_discovery import ParallelTheoryDiscovery
from quantum.reality_native.theory_diversity_analyzer import TheoryDiversityAnalyzer

def test_theory_diversity():
    test_db_dir = "databases_test_diversity"
    if os.path.exists(test_db_dir):
        shutil.rmtree(test_db_dir)
    os.makedirs(test_db_dir, exist_ok=True)

    try:
        # Generate data and discover theories
        engine = DomainExpansionEngine(seed=42)
        all_data = engine.generate_all_domains()

        discovery = ParallelTheoryDiscovery(output_dir=test_db_dir)
        theories = discovery.discover_theories_for_all_domains(all_data)

        # Run diversity analysis
        diversity_analyzer = TheoryDiversityAnalyzer(theories)
        results = diversity_analyzer.run_diversity_analysis()

        # Assertions
        assert "overall_diversity_score" in results
        assert results["overall_diversity_score"] >= 70.0, "Overall diversity score should be >= 70.0%"
        assert "equation_similarity" in results
        assert "parameter_similarity" in results
        assert "mechanism_similarity" in results
        assert "prediction_similarity" in results
        assert results["status"] == "PASSED"

        assert os.path.exists("docs/THEORY_DIVERSITY_REPORT.md"), "Theory diversity report should exist"

    finally:
        if os.path.exists(test_db_dir):
            shutil.rmtree(test_db_dir)
