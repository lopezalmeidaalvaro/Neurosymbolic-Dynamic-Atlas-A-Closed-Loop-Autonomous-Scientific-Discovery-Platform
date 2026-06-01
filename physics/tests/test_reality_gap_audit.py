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
    print("🧪 RUNNING REALITY GAP AUDIT INTEGRATION TEST")
    print("=" * 70)

    # 1. Imports
    print("[TEST 1/4] Importing RealityGapAudit...")
    try:
        from physics.reality_gap_audit import RealityGapAudit
        print("  Import successful!")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        sys.exit(1)

    # 2. Initialization
    print("\n[TEST 2/4] Initializing Reality Gap Audit module...")
    try:
        audit = RealityGapAudit()
        print("  Initialization successful!")
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        sys.exit(1)

    # 3. Execution
    print("\n[TEST 3/4] Running reality gap audit execution...")
    try:
        results = audit.run()
        print("  Execution successful!")
    except Exception as e:
        print(f"[ERROR] Audit execution failed: {e}")
        sys.exit(1)

    # 4. Validating outputs and artifacts
    print("\n[TEST 4/4] Validating reality gap outputs and file presence...")
    try:
        assert "metrics" in results, "Missing 'metrics' key."
        assert "report_path" in results, "Missing 'report_path' key."
        assert "RealityGapScore" in results, "Missing 'RealityGapScore' key."
        assert "gap_classification" in results, "Missing 'gap_classification' key."

        metrics = results["metrics"]
        assert "EvidenceCoverage" in metrics, "Missing EvidenceCoverage"
        assert "validation_depth" in metrics, "Missing validation_depth"
        assert "TraceabilityScore" in metrics, "Missing TraceabilityScore"
        assert "SpeculationRatio" in metrics, "Missing SpeculationRatio"

        gap_score = results["RealityGapScore"]
        classification = results["gap_classification"]
        print(f"  Reality Gap Score:           {gap_score:.4f}")
        print(f"  Gap Classification:          {classification}")
        print(f"  Evidence Coverage:           {metrics['EvidenceCoverage']*100.0:.2f}%")
        print(f"  Traceability:                {metrics['TraceabilityScore']*100.0:.2f}%")

        assert 0.0 <= gap_score <= 1.0, f"Invalid Reality Gap: {gap_score}"

        # Verify output files
        artifacts_dir = Path(__file__).resolve().parent.parent / "artifacts"
        expected_files = [
            "reality_gap_report.md",
            "reality_gap_metrics.json"
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
    print("✨ SUCCESS: Reality Gap Audit verified successfully")
    print("=" * 70)

if __name__ == "__main__":
    main()
