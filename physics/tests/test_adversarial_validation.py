import os
import sys
from pathlib import Path

# Handle path resolutions on Windows
TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR.parent))
sys.path.insert(0, str(TEST_DIR.parent.parent))

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    print("=" * 70)
    print("🧪 RUNNING ADVERSARIAL SCIENTIFIC VALIDATION INTEGRATION TEST")
    print("=" * 70)

    # 1. Imports
    print("[TEST 1/4] Importing AdversarialScientificValidation...")
    try:
        from physics.adversarial_scientific_validation import AdversarialScientificValidation
        print("  Import successful!")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        sys.exit(1)

    # 2. Initialization
    print("\n[TEST 2/4] Initializing validation module...")
    try:
        validator = AdversarialScientificValidation()
        print("  Initialization successful!")
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        sys.exit(1)

    # 3. Execution (Dry-Run)
    print("\n[TEST 3/4] Running adversarial validation audit (lightweight dry-run)...")
    try:
        # We run with small parameters to verify execution path without high cost
        results = validator.run(n_hypotheses_per_category=3, red_team_rounds=5)
        print("  Execution successful!")
    except Exception as e:
        print(f"[ERROR] Audit execution failed: {e}")
        sys.exit(1)

    # 4. Validating output fields
    print("\n[TEST 4/4] Validating audit outputs and file structure...")
    try:
        # Check dictionary fields
        assert "metrics" in results, "Missing 'metrics' key in audit results."
        assert "red_team_failures" in results, "Missing 'red_team_failures' key."
        assert "failure_analysis" in results, "Missing 'failure_analysis' key."
        assert "report_path" in results, "Missing 'report_path' key."

        metrics = results["metrics"]
        assert "global" in metrics, "Missing 'global' metrics."
        assert "robustness_score" in metrics["global"], "Missing 'robustness_score' in metrics."
        score = metrics["global"]["robustness_score"]
        print(f"  System Robustness Score: {score:.2f}%")
        assert 0.0 <= score <= 100.0, f"Invalid robustness score: {score}"

        # Verify expected files exist on disk
        artifacts_dir = Path(validator.sanity_engine.cache_path).parent
        expected_files = [
            "adversarial_validation_report.md",
            "adversarial_validation_metrics.json",
            "adversarial_validation_dataset.json",
            "red_team_failures.json",
            "failure_mode_analysis.json"
        ]

        for filename in expected_files:
            file_path = artifacts_dir / filename
            print(f"  Checking output: {filename} -> {file_path.exists()}")
            assert file_path.exists(), f"Output file missing: {filename}"

        print("  All assertions passed successfully!")
    except AssertionError as e:
        print(f"[ERROR] Assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] General verification failure: {e}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✨ SUCCESS: Adversarial Scientific Validation verified successfully")
    print("=" * 70)

if __name__ == "__main__":
    main()
