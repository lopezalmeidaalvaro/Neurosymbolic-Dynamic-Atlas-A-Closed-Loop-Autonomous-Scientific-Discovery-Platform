#!/usr/bin/env python3
"""
test_uncertainty_pbox.py
========================
V&V Test Suite — Uncertainty Quantification & Reliability Engine
Authority  : Verification & Validation Lead (ESA/NASA Standard)
Document ID: AST-TEST-UQ-001
Target     : satellite/thermal/uncertainty_engine.py  (Lines 30-267)
CDR Gate   : AI-CDR-02  (Coverage >= 80%)

Coverage targets:
  - UncertaintyEngine.__init__
  - UncertaintyEngine.predict_with_uncertainty  (ensemble + bootstrap_physics)
  - UncertaintyEngine.calibrate_uncertainty
  - UncertaintyEngine.reliability_score
  - UncertaintyEngine.run_reliability_analysis
  - UncertaintyEngine.generate_report
  - UncertaintyEngine.plot_distribution
"""

import os
import sys
import math
import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Module under test
# ---------------------------------------------------------------------------
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "satellite", "thermal"
    ),
)
from uncertainty_engine import UncertaintyEngine

# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture(scope="module")
def engine():
    """Shared UncertaintyEngine instance (deterministic numpy seed)."""
    np.random.seed(42)
    return UncertaintyEngine()


# ===========================================================================
# 1. Initialisation
# ===========================================================================


class TestUncertaintyEngineInit:
    def test_engine_instantiates(self, engine):
        assert engine is not None

    def test_critical_threshold_set(self, engine):
        assert engine.critical_threshold == pytest.approx(85.0)

    def test_optimizer_attached(self, engine):
        """UncertaintyEngine must carry a GeometryOptimizer instance."""
        from geometry_topology_optimizer import GeometryOptimizer

        assert isinstance(engine.optimizer, GeometryOptimizer)


# ===========================================================================
# 2. predict_with_uncertainty — ensemble branch
# ===========================================================================


class TestPredictEnsemble:
    """Tests the 10-model surrogate ensemble method."""

    @pytest.fixture(scope="class")
    def ensemble_result(self, engine):
        np.random.seed(0)
        return engine.predict_with_uncertainty(
            None, [0.15, 0.85, 15.0], method="ensemble"
        )

    def test_result_has_required_keys(self, ensemble_result):
        for key in ("mean", "std", "ci95", "predictions"):
            assert key in ensemble_result

    def test_predictions_has_ten_models(self, ensemble_result):
        assert len(ensemble_result["predictions"]) == 10

    def test_mean_finite(self, ensemble_result):
        assert math.isfinite(ensemble_result["mean"])

    def test_std_non_negative(self, ensemble_result):
        assert ensemble_result["std"] >= 0.0

    def test_ci95_lower_less_than_upper(self, ensemble_result):
        lo, hi = ensemble_result["ci95"]
        assert lo < hi

    def test_mean_within_ci95(self, ensemble_result):
        lo, hi = ensemble_result["ci95"]
        assert lo <= ensemble_result["mean"] <= hi

    def test_ensemble_baseline_physics(self):
        """base_temp = 55 + 3*power - 45*area - 10*eps; verify plausible range."""
        engine = UncertaintyEngine()
        np.random.seed(42)
        result = engine.predict_with_uncertainty(
            None, [0.10, 0.50, 20.0], method="ensemble"
        )
        # base_temp = 55 + 3*20 - 45*0.10 - 10*0.50 = 55 + 60 - 4.5 - 5 = 105.5 ±noise
        assert 80.0 < result["mean"] < 130.0


# ===========================================================================
# 3. predict_with_uncertainty — bootstrap_physics branch
# ===========================================================================


class TestPredictBootstrapPhysics:
    """Tests the Monte Carlo physical bootstrap method."""

    @pytest.fixture(scope="class")
    def bootstrap_result(self, engine):
        np.random.seed(42)
        return engine.predict_with_uncertainty(
            None, [0.15, 0.85, 15.0], method="bootstrap_physics"
        )

    def test_result_has_required_keys(self, bootstrap_result):
        for key in ("mean", "std", "ci95", "predictions"):
            assert key in bootstrap_result

    def test_200_simulations_run(self, bootstrap_result):
        assert len(bootstrap_result["predictions"]) == 200

    def test_mean_temperature_in_physical_range(self, bootstrap_result):
        """CPU peak temp for nominal config should be between 15°C and 85°C."""
        assert 15.0 < bootstrap_result["mean"] < 85.0

    def test_std_positive(self, bootstrap_result):
        assert bootstrap_result["std"] > 0.0

    def test_ci95_covers_majority_of_predictions(self, bootstrap_result):
        preds = np.array(bootstrap_result["predictions"])
        lo, hi = bootstrap_result["ci95"]
        in_ci = np.sum((preds >= lo) & (preds <= hi))
        coverage = in_ci / len(preds)
        # Should be close to 95% — allow ±10% tolerance
        assert 0.85 <= coverage <= 1.0

    def test_high_power_raises_mean_temperature(self):
        """Increasing CPU power should shift the temperature distribution upward."""
        eng = UncertaintyEngine()
        np.random.seed(42)
        r_low = eng.predict_with_uncertainty(
            None, [0.15, 0.85, 5.0], method="bootstrap_physics"
        )
        np.random.seed(42)
        r_high = eng.predict_with_uncertainty(
            None, [0.15, 0.85, 30.0], method="bootstrap_physics"
        )
        assert r_high["mean"] > r_low["mean"]

    def test_larger_area_lowers_mean_temperature(self):
        """More radiator area should reduce mean peak CPU temperature."""
        eng = UncertaintyEngine()
        np.random.seed(42)
        r_small = eng.predict_with_uncertainty(
            None, [0.05, 0.85, 15.0], method="bootstrap_physics"
        )
        np.random.seed(42)
        r_large = eng.predict_with_uncertainty(
            None, [0.25, 0.85, 15.0], method="bootstrap_physics"
        )
        assert r_large["mean"] < r_small["mean"]


# ===========================================================================
# 4. calibrate_uncertainty
# ===========================================================================


class TestCalibrateUncertainty:
    """Validates the calibration of prediction intervals against experimental data."""

    def test_calibrate_returns_float(self, engine):
        experimental = [{"Temp_C": 50.0}, {"Temp_C": 55.0}, {"Temp_C": 48.0}]
        predictions = [52.0, 53.0, 49.0]
        result = engine.calibrate_uncertainty(experimental, predictions)
        assert isinstance(result, float)
        assert result >= 0.0

    def test_perfect_predictions_give_small_factor(self, engine):
        """Zero MAE → coverage_factor should be 0."""
        experimental = [{"Temp_C": 50.0}, {"Temp_C": 60.0}]
        predictions = [50.0, 60.0]
        result = engine.calibrate_uncertainty(experimental, predictions)
        assert math.isclose(result, 0.0, abs_tol=1e-9)

    def test_large_errors_give_large_factor(self, engine):
        experimental = [{"Temp_C": 50.0}, {"Temp_C": 50.0}]
        predictions = [10.0, 10.0]  # 40°C error
        result = engine.calibrate_uncertainty(experimental, predictions)
        assert result > 10.0

    def test_uses_only_matching_length(self, engine):
        """Only min(len(experimental), len(predictions)) rows are compared."""
        experimental = [{"Temp_C": 50.0}]
        predictions = [50.0, 60.0, 70.0]  # extra predictions ignored
        # Should not raise IndexError
        result = engine.calibrate_uncertainty(experimental, predictions)
        assert isinstance(result, float)


# ===========================================================================
# 5. reliability_score
# ===========================================================================


class TestReliabilityScore:
    """Tests probability-of-safety computation via Normal CDF."""

    def test_high_safety_when_mean_far_below_threshold(self, engine):
        score = engine.reliability_score(40.0, 1.0, threshold=85.0)
        assert score > 0.999

    def test_low_safety_when_mean_above_threshold(self, engine):
        score = engine.reliability_score(90.0, 1.0, threshold=85.0)
        assert score < 0.01

    def test_score_at_threshold_is_near_50_percent(self, engine):
        score = engine.reliability_score(85.0, 5.0, threshold=85.0)
        assert 0.45 < score < 0.55

    def test_score_bounded_between_0_and_1(self, engine):
        for mean in [20.0, 50.0, 85.0, 100.0, 200.0]:
            score = engine.reliability_score(mean, 5.0, threshold=85.0)
            assert 0.0 <= score <= 1.0

    def test_larger_uncertainty_reduces_reliability(self, engine):
        score_tight = engine.reliability_score(60.0, 1.0, threshold=85.0)
        score_wide = engine.reliability_score(60.0, 20.0, threshold=85.0)
        assert score_tight > score_wide

    def test_custom_threshold(self, engine):
        score_low = engine.reliability_score(50.0, 2.0, threshold=55.0)
        score_high = engine.reliability_score(50.0, 2.0, threshold=85.0)
        assert score_high > score_low


# ===========================================================================
# 6. generate_report
# ===========================================================================


class TestGenerateReport:
    """Tests the markdown report generation."""

    @pytest.fixture(scope="class")
    def report_file(self, tmp_path_factory, engine):
        tmp = tmp_path_factory.mktemp("uq_report")
        np.random.seed(42)
        uq_res = engine.predict_with_uncertainty(
            None, [0.15, 0.85, 15.0], method="bootstrap_physics"
        )
        rel_score = engine.reliability_score(uq_res["mean"], uq_res["std"])
        original = os.getcwd()
        os.chdir(str(tmp))
        try:
            engine.generate_report(uq_res, rel_score)
        finally:
            os.chdir(original)
        return tmp / "uncertainty_report.md"

    def test_report_file_exists(self, report_file):
        assert report_file.exists()

    def test_report_contains_mean_temperature(self, report_file):
        content = report_file.read_text()
        assert "°C" in content

    def test_report_contains_confidence_interval(self, report_file):
        content = report_file.read_text()
        assert "Confidence Interval" in content or "CI" in content

    def test_report_contains_reliability_score(self, report_file):
        content = report_file.read_text()
        assert "Reliability" in content or "reliability" in content

    def test_report_has_risk_statement(self, report_file):
        content = report_file.read_text()
        assert "Risk Statement" in content or "IMPORTANT" in content


# ===========================================================================
# 7. plot_distribution
# ===========================================================================


class TestPlotDistribution:
    """Tests the probability density function plot generation."""

    def test_plot_creates_file(self, engine, tmp_path):
        np.random.seed(42)
        uq_res = engine.predict_with_uncertainty(
            None, [0.15, 0.85, 15.0], method="ensemble"
        )
        out = str(tmp_path / "uncertainty_dist.png")
        engine.plot_distribution(uq_res, out)
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0


# ===========================================================================
# 8. run_reliability_analysis (integration — triggers full pipeline)
# ===========================================================================


class TestRunReliabilityAnalysis:
    """Integration test: run_reliability_analysis exercises the entire UQ pipeline."""

    def test_analysis_runs_without_error(self, tmp_path):
        eng = UncertaintyEngine()
        np.random.seed(42)
        original = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            eng.run_reliability_analysis(area=0.15, eps=0.85, power=15.0)
        finally:
            os.chdir(original)

    def test_analysis_generates_report_file(self, tmp_path):
        eng = UncertaintyEngine()
        np.random.seed(42)
        original = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            eng.run_reliability_analysis(area=0.15, eps=0.85, power=15.0)
        finally:
            os.chdir(original)
        assert (tmp_path / "uncertainty_report.md").exists()

    def test_analysis_generates_plot_file(self, tmp_path):
        eng = UncertaintyEngine()
        np.random.seed(42)
        original = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            eng.run_reliability_analysis(area=0.15, eps=0.85, power=15.0)
        finally:
            os.chdir(original)
        assert (tmp_path / "uncertainty_distribution.png").exists()

    def test_analysis_with_custom_parameters(self, tmp_path):
        eng = UncertaintyEngine()
        np.random.seed(0)
        original = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            eng.run_reliability_analysis(area=0.20, eps=0.90, power=20.0)
        finally:
            os.chdir(original)
