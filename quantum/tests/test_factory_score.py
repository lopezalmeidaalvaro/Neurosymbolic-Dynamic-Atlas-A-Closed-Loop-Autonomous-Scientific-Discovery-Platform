import os
import pytest
from quantum.reality_native.theory_factory_score import TheoryFactoryScore

def test_theory_factory_score_calculation():
    # Test passing case
    score_calc_pass = TheoryFactoryScore(
        discovery_success=1.0,
        confirmation_success=1.0,
        reproduction_success=1.0,
        novelty_score=0.98,
        diversity_score=0.85
    )
    results_pass = score_calc_pass.calculate_score()
    
    # Formula: 1.0 * 1.0 * 1.0 * 0.98 * 0.85 * 100 = 83.3
    assert results_pass["factory_score"] == pytest.approx(83.3, 0.01)
    assert results_pass["status"] == "PASSED"

    # Test failing case
    score_calc_fail = TheoryFactoryScore(
        discovery_success=1.0,
        confirmation_success=0.80,
        reproduction_success=0.80,
        novelty_score=0.90,
        diversity_score=0.60
    )
    results_fail = score_calc_fail.calculate_score()
    
    # Formula: 1.0 * 0.8 * 0.8 * 0.9 * 0.6 * 100 = 34.56
    assert results_fail["factory_score"] == pytest.approx(34.56, 0.01)
    assert results_fail["status"] == "FAILED"

    assert os.path.exists("docs/THEORY_FACTORY_SCORE.md"), "Theory factory score report should exist"
