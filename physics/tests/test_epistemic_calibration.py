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
    print("🧪 RUNNING EPISTEMIC CALIBRATION AUDIT INTEGRATION TEST")
    print("=" * 70)

    # 1. Imports
    print("[TEST 1/4] Importing EpistemicCalibrationAudit...")
    try:
        from physics.epistemic_calibration_audit import EpistemicCalibrationAudit
        print("  Import successful!")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        sys.exit(1)

    # 2. Initialization
    print("\n[TEST 2/4] Initializing calibration audit module...")
    try:
        audit = EpistemicCalibrationAudit()
        print("  Initialization successful!")
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        sys.exit(1)

    # 3. Execution
    print("\n[TEST 3/4] Running epistemic calibration audit execution...")
    try:
        results = audit.run()
        print("  Execution successful!")
    except Exception as e:
        print(f"[ERROR] Audit execution failed: {e}")
        sys.exit(1)

    # 4. Validating output fields
    print("\n[TEST 4/4] Validating audit outputs and file structure...")
    try:
        # Check dictionary keys
        assert "metrics" in results, "Missing 'metrics' key in audit results."
        assert "recommendations" in results, "Missing 'recommendations' key."
        assert "report_path" in results, "Missing 'report_path' key."

        metrics = results["metrics"]
        assert "health" in metrics, "Missing 'health' metrics."
        assert "EpistemicHealthScore" in metrics["health"], "Missing 'EpistemicHealthScore' in health."
        score = metrics["health"]["EpistemicHealthScore"]
        print(f"  Epistemic Health Score: {score:.2f}/100")
        assert 0.0 <= score <= 100.0, f"Invalid health score: {score}"

        # Verify expected files exist on disk
        artifacts_dir = Path(__file__).resolve().parent.parent / "artifacts"
        expected_files = [
            "epistemic_calibration_report.md",
            "epistemic_calibration_metrics.json",
            "epistemic_recommendations.json"
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
    print("✨ SUCCESS: Epistemic Calibration Audit verified successfully")
    print("=" * 70)

if __name__ == "__main__":
    main()
