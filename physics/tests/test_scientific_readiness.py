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
    print("🧪 RUNNING SCIENTIFIC READINESS ASSESSMENT INTEGRATION TEST")
    print("=" * 70)

    # 1. Imports
    print("[TEST 1/4] Importing ScientificReadinessAssessment...")
    try:
        from physics.scientific_readiness_assessment import ScientificReadinessAssessment
        print("  Import successful!")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        sys.exit(1)

    # 2. Initialization
    print("\n[TEST 2/4] Initializing Readiness Assessment module...")
    try:
        assessment = ScientificReadinessAssessment()
        print("  Initialization successful!")
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        sys.exit(1)

    # 3. Execution
    print("\n[TEST 3/4] Running readiness assessment execution...")
    try:
        results = assessment.run()
        print("  Execution successful!")
    except Exception as e:
        print(f"[ERROR] Engine execution failed: {e}")
        sys.exit(1)

    # 4. Validating outputs and artifacts
    print("\n[TEST 4/4] Validating readiness outputs and file presence...")
    try:
        assert "metrics" in results, "Missing 'metrics' key."
        assert "report_path" in results, "Missing 'report_path' key."
        assert "ScientificReadinessScore" in results, "Missing 'ScientificReadinessScore' key."
        assert "readiness_classification" in results, "Missing 'readiness_classification' key."
        assert "supervision_verdict" in results, "Missing 'supervision_verdict' key."

        metrics = results["metrics"]
        assert "capability_areas" in metrics, "Missing capability_areas"
        assert "verdict" in metrics, "Missing verdict map"

        readiness_score = results["ScientificReadinessScore"]
        classification = results["readiness_classification"]
        verdict = results["supervision_verdict"]
        
        print(f"  Scientific Readiness Score:  {readiness_score:.2f}/100")
        print(f"  Readiness Classification:    {classification}")
        print(f"  Supervision Verdict:         {verdict}")

        assert 0.0 <= readiness_score <= 100.0, f"Invalid Readiness Score: {readiness_score}"
        assert verdict in ["SI", "NO", "SI, CON SUPERVISIÓN", "NO TODAVÍA"], f"Invalid verdict: {verdict}"

        # Verify output files
        artifacts_dir = Path(__file__).resolve().parent.parent / "artifacts"
        expected_files = [
            "scientific_readiness_report.md",
            "scientific_readiness_metrics.json"
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
    print("✨ SUCCESS: Scientific Readiness verified successfully")
    print("=" * 70)

if __name__ == "__main__":
    main()
