"""
Phase 8 — Dry-Run Integration Tests
======================================
Fast validation that each Phase 8 script imports correctly and
executes a minimal mock scenario without errors.

Settings:
  - n_seeds = 2, bootstrap = 5, signal_length = 200
  - Systems: lorenz only
  - Modules: EV3 only
  - Ablation: BASELINE_FULL + NO_TDA only

Usage:
    python test_phase8_dry.py
    pytest test_phase8_dry.py -v
"""

import sys
import os
import io
import unittest
import warnings
import logging
from pathlib import Path

# Force UTF-8
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

warnings.filterwarnings("ignore")
logging.disable(logging.WARNING)  # suppress test noise

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent))

# ---------------------------------------------------------------------------
# Helper: fast kwargs for all modules
# ---------------------------------------------------------------------------
FAST_KWARGS = {
    "systems": ["lorenz"],
    "modules": ["EV3"],
    "dry_run": True,
}


class TestPhase8AImport(unittest.TestCase):
    """Tests that reproducibility_audit.py can be imported."""

    def test_import(self):
        import reproducibility_audit as ra
        self.assertTrue(hasattr(ra, "run_reproducibility_audit"))
        self.assertTrue(hasattr(ra, "generate_sobol_seeds"))
        self.assertTrue(hasattr(ra, "bca_bootstrap_ci"))
        self.assertTrue(hasattr(ra, "adaptive_evaluation"))

    def test_sobol_seeds(self):
        import reproducibility_audit as ra
        seeds = ra.generate_sobol_seeds(8)
        self.assertEqual(len(seeds), 8)
        # All seeds should be unique non-negative integers
        self.assertEqual(len(set(seeds)), len(seeds))
        self.assertTrue(all(s >= 0 for s in seeds))

    def test_bca_bootstrap(self):
        import numpy as np
        from reproducibility_audit import bca_bootstrap_ci
        samples = np.array([1.0, 1.1, 0.9, 1.05, 0.95, 1.02, 0.98, 1.03])
        mu, lo, hi = bca_bootstrap_ci(samples, n_resamples=50)
        self.assertAlmostEqual(mu, float(np.mean(samples)), places=5)
        self.assertLess(lo, mu)
        self.assertGreater(hi, mu)

    def test_relative_ci_width(self):
        from reproducibility_audit import relative_ci_width
        w = relative_ci_width(0.9, 1.1, 1.0)
        self.assertAlmostEqual(w, 0.2, places=5)
        w_nan = relative_ci_width(float("nan"), 1.1, 1.0)
        self.assertEqual(w_nan, float("inf"))

    def test_dry_run_small(self):
        """Tests adaptive_evaluation with 2 seeds on lorenz/EV3."""
        from reproducibility_audit import adaptive_evaluation
        result = adaptive_evaluation(
            module="EV3", system="lorenz",
            initial_seeds=2, increment=1, max_seeds=4,
            n_resamples=5, signal_length=200,
        )
        self.assertIn("module", result)
        self.assertIn("convergence_status", result)
        self.assertIn("stability", result)
        self.assertIn("n_seeds", result)
        self.assertIn(result["convergence_status"], ("CONVERGED", "NOT_CONVERGED"))
        self.assertIn(result["stability"], ("STABLE", "UNSTABLE"))


class TestPhase8BImport(unittest.TestCase):
    """Tests that ablation_study.py can be imported and DAG logic works."""

    def test_import(self):
        import ablation_study as ab
        self.assertTrue(hasattr(ab, "run_ablation_study"))
        self.assertTrue(hasattr(ab, "cohens_d"))
        self.assertTrue(hasattr(ab, "resolve_disabled_modules"))

    def test_resolve_disabled_modules(self):
        from ablation_study import resolve_disabled_modules
        # Disabling EV3 should cascade to EV3_EXT, EV3_DEEP, EV3_SCI, etc.
        result = resolve_disabled_modules({"EV3"})
        self.assertIn("EV3", result)
        self.assertIn("EV3_EXT", result)
        self.assertIn("EV3_DEEP", result)
        self.assertIn("EV3_SCI", result)

    def test_cohens_d_identical(self):
        import numpy as np
        from ablation_study import cohens_d
        a = np.array([1.0, 1.0, 1.0, 1.0])
        b = np.array([1.0, 1.0, 1.0, 1.0])
        d = cohens_d(a, b)
        self.assertEqual(d, 0.0)

    def test_cohens_d_large(self):
        import numpy as np
        from ablation_study import cohens_d
        a = np.array([10.0, 10.0, 10.0, 10.0])
        b = np.array([0.0, 0.0, 0.0, 0.1])
        d = cohens_d(a, b)
        self.assertGreater(abs(d), 0.8)

    def test_classify_impact(self):
        from ablation_study import classify_impact
        self.assertEqual(classify_impact(0.1), "Negligible")
        self.assertEqual(classify_impact(0.3), "Small")
        self.assertEqual(classify_impact(0.6), "Medium")
        self.assertEqual(classify_impact(1.2), "Large")

    def test_delta_percent(self):
        from ablation_study import delta_percent
        dp = delta_percent(10.0, 8.0)
        self.assertAlmostEqual(dp, 20.0, places=4)


class TestPhase8CImport(unittest.TestCase):
    """Tests that sota_benchmark.py can be imported."""

    def test_import(self):
        import sota_benchmark as sb
        self.assertTrue(hasattr(sb, "run_sota_benchmark"))
        self.assertTrue(hasattr(sb, "probe_packages"))
        self.assertTrue(hasattr(sb, "accuracy_per_second"))

    def test_probe_packages(self):
        from sota_benchmark import probe_packages
        result = probe_packages()
        # Must return a dict with at least sklearn
        self.assertIsInstance(result, dict)
        self.assertIn("sklearn", result)

    def test_accuracy_per_second(self):
        from sota_benchmark import accuracy_per_second
        self.assertEqual(accuracy_per_second(1.0, 2.0), 0.5)
        import math
        self.assertTrue(math.isnan(accuracy_per_second(float("nan"), 2.0)))
        self.assertTrue(math.isnan(accuracy_per_second(1.0, 0.0)))

    def test_dry_run(self):
        from sota_benchmark import run_sota_benchmark
        df = run_sota_benchmark(systems=["lorenz"], dry_run=True, skip_plots=True)
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        self.assertIn("baseline", df.columns)
        self.assertIn("status", df.columns)


class TestPhase8EImport(unittest.TestCase):
    """Tests that robustness_stress_test.py can be imported."""

    def test_import(self):
        import robustness_stress_test as rs
        self.assertTrue(hasattr(rs, "run_robustness_stress_test"))
        self.assertTrue(hasattr(rs, "inject_noise"))
        self.assertTrue(hasattr(rs, "drop_and_interpolate"))

    def test_inject_noise_clean(self):
        import numpy as np
        from robustness_stress_test import inject_noise
        sig = np.ones(100)
        noisy = inject_noise(sig, None)
        np.testing.assert_array_equal(sig, noisy)

    def test_inject_noise_snr0(self):
        import numpy as np
        from robustness_stress_test import inject_noise
        np.random.seed(42)
        sig = np.sin(np.linspace(0, 10, 200))
        noisy = inject_noise(sig, 0)  # 0 dB SNR
        # Power of noise should approximate power of signal
        p_sig = np.mean(sig ** 2)
        p_noise = np.mean((noisy - sig) ** 2)
        self.assertAlmostEqual(p_noise / p_sig, 1.0, delta=0.5)

    def test_drop_and_interpolate(self):
        import numpy as np
        from robustness_stress_test import drop_and_interpolate
        sig = np.linspace(0, 10, 200)
        recovered = drop_and_interpolate(sig, 0.3, seed=42)
        self.assertEqual(len(recovered), len(sig))
        # No NaN after interpolation
        self.assertFalse(np.any(np.isnan(recovered)))

    def test_dry_run(self):
        from robustness_stress_test import run_robustness_stress_test
        dfs = run_robustness_stress_test(
            systems=["lorenz"], modules=["EV3"],
            dry_run=True, skip_plots=True,
        )
        self.assertIsInstance(dfs, dict)
        self.assertIn("noise", dfs)
        self.assertIn("missing_data", dfs)
        self.assertIn("ood", dfs)


class TestPhase8DImport(unittest.TestCase):
    """Tests that auto_paper_generator.py can be imported."""

    def test_import(self):
        import auto_paper_generator as apg
        self.assertTrue(hasattr(apg, "run_auto_paper_generator"))
        self.assertTrue(hasattr(apg, "generate_markdown_paper"))
        self.assertTrue(hasattr(apg, "generate_latex_paper"))
        self.assertTrue(hasattr(apg, "save_bibliography"))

    def test_fmt_helper(self):
        from auto_paper_generator import _fmt
        import math
        self.assertEqual(_fmt(float("nan")), "N/A")
        self.assertEqual(_fmt(None), "N/A")
        self.assertEqual(_fmt(3.14159, 2), "3.14")
        self.assertEqual(_fmt(3.14159, 2, "%"), "3.14%")

    def test_safe_read_csv_missing(self):
        from auto_paper_generator import _safe_read_csv
        from pathlib import Path
        result = _safe_read_csv(Path("nonexistent_file_xyz.csv"))
        self.assertIsNone(result)

    def test_paper_generation_dry(self):
        """Generates paper with empty results (all N/A) — should not crash."""
        from auto_paper_generator import (
            generate_markdown_paper, generate_latex_paper, _extract_key_stats
        )
        # Empty results
        empty_results = {
            "reproducibility": None, "ablation": None, "sota": None,
            "robustness_noise": None, "robustness_missing": None, "robustness_ood": None,
        }
        stats = _extract_key_stats(empty_results)
        # All stats should be N/A
        self.assertTrue(all(v == "N/A" for v in stats.values()))

        md = generate_markdown_paper(stats, empty_results)
        self.assertIn("N/A", md)
        self.assertIn("Threats to Validity", md)
        self.assertGreater(len(md), 100)

        tex = generate_latex_paper(stats, empty_results)
        self.assertIn(r"\begin{document}", tex)
        self.assertIn(r"\end{document}", tex)
        self.assertGreater(len(tex), 100)

    def test_bibliography(self):
        """Tests that bibliography generation creates a valid .bib string."""
        from auto_paper_generator import BIB_CONTENT
        self.assertIn("@article", BIB_CONTENT)
        self.assertIn("brunton2016discovering", BIB_CONTENT)
        self.assertIn("raissi2019physics", BIB_CONTENT)


class TestPhase8OrchestratorImport(unittest.TestCase):
    """Tests that run_phase8.py can be imported."""

    def test_import(self):
        import run_phase8 as rp
        self.assertTrue(hasattr(rp, "main"))
        self.assertTrue(hasattr(rp, "run_subphase"))
        self.assertTrue(hasattr(rp, "is_complete"))
        self.assertTrue(hasattr(rp, "mark_complete"))
        self.assertTrue(hasattr(rp, "SUBPHASES"))
        self.assertTrue(hasattr(rp, "SUBPHASE_INFO"))

    def test_subphase_registry(self):
        from run_phase8 import SUBPHASES, SUBPHASE_INFO
        for sp in SUBPHASES:
            self.assertIn(sp, SUBPHASE_INFO)
            info = SUBPHASE_INFO[sp]
            self.assertIn("name", info)
            self.assertIn("module", info)
            self.assertIn("function", info)
            self.assertIn("flag", info)

    def test_flag_lifecycle(self):
        """Tests write/read/clear of completion flags."""
        from run_phase8 import is_complete, mark_complete, clear_flag
        # Use a real subphase key
        sp = "8A"
        clear_flag(sp)  # ensure clean state
        self.assertFalse(is_complete(sp))
        mark_complete(sp, {"elapsed_s": 0.1, "dry_run": True})
        self.assertTrue(is_complete(sp))
        clear_flag(sp)
        self.assertFalse(is_complete(sp))


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  PHASE 8 — DRY-RUN INTEGRATION TESTS")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestPhase8AImport,
        TestPhase8BImport,
        TestPhase8CImport,
        TestPhase8EImport,
        TestPhase8DImport,
        TestPhase8OrchestratorImport,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
