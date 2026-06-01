import os
import sys
import json
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
    print("🧪 RUNNING EPISTEMIC HARDENING ENGINE INTEGRATION TEST")
    print("=" * 70)

    # 1. Imports
    print("[TEST 1/4] Importing EpistemicHardeningEngine...")
    try:
        from physics.epistemic_hardening_engine import EpistemicHardeningEngine
        print("  Import successful!")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        sys.exit(1)

    # 2. Initialization
    print("\n[TEST 2/4] Initializing epistemic hardening engine...")
    try:
        engine = EpistemicHardeningEngine()
        print("  Initialization successful!")
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        sys.exit(1)

    # 3. Execution
    print("\n[TEST 3/4] Running epistemic hardening engine execution...")
    try:
        results = engine.run()
        print("  Execution successful!")
    except Exception as e:
        print(f"[ERROR] Engine execution failed: {e}")
        sys.exit(1)

    # 4. Validating output fields
    print("\n[TEST 4/4] Validating hardening engine outputs and file structure...")
    try:
        # Check dictionary keys
        assert "metrics" in results, "Missing 'metrics' key in results."
        assert "report_path" in results, "Missing 'report_path' key in results."
        assert "delta_health_score" in results, "Missing 'delta_health_score' key in results."

        metrics = results["metrics"]
        assert "pre_audit_metrics" in metrics, "Missing 'pre_audit_metrics' in metrics."
        assert "hardened_parameters" in metrics, "Missing 'hardened_parameters' in metrics."
        assert "recalibration_rates" in metrics, "Missing 'recalibration_rates' in metrics."
        assert "epistemic_health_delta" in metrics, "Missing 'epistemic_health_delta' in metrics."

        health_delta = metrics["epistemic_health_delta"]
        assert "PreCalibrationHealthScore" in health_delta, "Missing PreCalibrationHealthScore"
        assert "PostCalibrationHealthScore" in health_delta, "Missing PostCalibrationHealthScore"
        assert "delta_health_score" in health_delta, "Missing delta_health_score"

        pre_score = health_delta["PreCalibrationHealthScore"]
        post_score = health_delta["PostCalibrationHealthScore"]
        delta_score = health_delta["delta_health_score"]

        print(f"  Pre-Calibration Health Score:  {pre_score:.2f}/100")
        print(f"  Post-Calibration Health Score: {post_score:.2f}/100")
        print(f"  Delta Health Score:            {delta_score:+.2f} points")

        assert 0.0 <= pre_score <= 100.0, f"Invalid pre-health score: {pre_score}"
        assert 0.0 <= post_score <= 100.0, f"Invalid post-health score: {post_score}"

        # Verify expected files exist on disk
        artifacts_dir = Path(__file__).resolve().parent.parent / "artifacts"
        expected_files = [
            "epistemic_hardening_report.md",
            "epistemic_hardening_metrics.json",
            "recalibrated_hypotheses.json"
        ]

        for filename in expected_files:
            file_path = artifacts_dir / filename
            print(f"  Checking output file: {filename} -> {file_path.exists()}")
            assert file_path.exists(), f"Output file missing: {filename}"

        # Additional assertions on the recalibrated output to verify acceptance control
        recal_data_path = artifacts_dir / "recalibrated_hypotheses.json"
        with open(recal_data_path, "r", encoding="utf-8") as f:
            recal_list = json.load(f)
        
        print(f"  Recalibrated hypotheses count: {len(recal_list)}")
        assert len(recal_list) > 0, "No hypotheses recalibrated in benchmark."

        print("  All assertions passed successfully!")
    except AssertionError as e:
        print(f"[ERROR] Assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] General verification failure: {e}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✨ SUCCESS: Epistemic Hardening Engine verified successfully")
    print("=" * 70)

if __name__ == "__main__":
    main()
