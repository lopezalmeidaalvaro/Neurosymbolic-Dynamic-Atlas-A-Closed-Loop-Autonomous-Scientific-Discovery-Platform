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
    print("🧪 RUNNING SYSTEM MATURITY ASSESSMENT INTEGRATION TEST")
    print("=" * 70)

    # 1. Imports
    print("[TEST 1/4] Importing SystemMaturityAssessment...")
    try:
        from physics.system_maturity_assessment import SystemMaturityAssessment
        print("  Import successful!")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        sys.exit(1)

    # 2. Initialization
    print("\n[TEST 2/4] Initializing Maturity Assessment module...")
    try:
        assessment = SystemMaturityAssessment()
        print("  Initialization successful!")
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        sys.exit(1)

    # 3. Execution
    print("\n[TEST 3/4] Running system maturity audit execution...")
    try:
        results = assessment.run()
        print("  Execution successful!")
    except Exception as e:
        print(f"[ERROR] Engine execution failed: {e}")
        sys.exit(1)

    # 4. Validating outputs and artifacts
    print("\n[TEST 4/4] Validating maturity outputs, evidence types, and executive reports...")
    try:
        assert "metrics" in results, "Missing 'metrics' key."
        assert "report_path" in results, "Missing 'report_path' key."
        assert "final_assessment_report_path" in results, "Missing 'final_assessment_report_path' key."
        assert "SystemMaturityScore" in results, "Missing 'SystemMaturityScore' key."
        assert "level" in results, "Missing 'level' key."

        metrics = results["metrics"]
        assert "areas_breakout" in metrics, "Missing areas_breakout"
        
        # Verify evidence classifications (OBLIGATORY)
        for name, data in metrics["areas_breakout"].items():
            assert "evidence_type" in data, f"Missing evidence type in capability {name}"
            ev = data["evidence_type"]
            print(f"  Capability: {name: <22} -> Score: {data['score']:.1f} -> Tag: [ {ev} ]")
            assert ev in ["OBSERVED", "INFERRED", "SIMULATED", "UNVERIFIED"], f"Invalid evidence tag: {ev}"

        maturity_score = results["SystemMaturityScore"]
        level = results["level"]
        print(f"\n  System Maturity Score:       {maturity_score:.2f}/100")
        print(f"  Maturity Tier Level:         {level}")

        assert 0.0 <= maturity_score <= 100.0, f"Invalid System Maturity Score: {maturity_score}"

        # Verify output files
        artifacts_dir = Path(__file__).resolve().parent.parent / "artifacts"
        expected_files = [
            "system_maturity_assessment.md",
            "system_maturity_metrics.json",
            "system_capability_matrix.json",
            "system_gap_analysis.json",
            "final_scientific_assessment.md",
            "final_scientific_assessment.json"
        ]

        for filename in expected_files:
            file_path = artifacts_dir / filename
            print(f"  Checking output: {filename} -> {file_path.exists()}")
            assert file_path.exists(), f"Output file missing: {filename}"

        # Verify final critical questions presence in the maturity report
        report_text = (artifacts_dir / "system_maturity_assessment.md").read_text(encoding="utf-8")
        critical_indicators = [
            "1. ¿Qué puede hacer el sistema hoy?",
            "2. ¿Qué NO puede hacer todavía?",
            "3. ¿Qué afirmaciones están observadas?",
            "4. ¿Qué afirmaciones son inferidas?",
            "5. ¿Qué afirmaciones siguen siendo simuladas?",
            "6. ¿Cuál es el principal cuello de botella actual?",
            "7. ¿Qué mejora única produciría el mayor salto de capacidad?"
        ]

        print("\n🧪 Verifying presence of the 7 final questions...")
        for q in critical_indicators:
            print(f"  Checking question presence: '{q}' -> {q in report_text}")
            assert q in report_text, f"Mandatory final question missing in maturity report: {q}"

        print("  All assertions passed successfully!")
    except AssertionError as e:
        print(f"[ERROR] Assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] General verification failure: {e}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✨ SUCCESS: System Maturity validated successfully")
    print("=" * 70)

if __name__ == "__main__":
    main()
