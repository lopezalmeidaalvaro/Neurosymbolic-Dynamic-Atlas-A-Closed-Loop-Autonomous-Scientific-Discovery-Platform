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
    print("🧪 RUNNING SCIENTIFIC IMPACT ASSESSMENT INTEGRATION TEST")
    print("=" * 70)

    # 1. Imports
    print("[TEST 1/4] Importing ScientificImpactAssessment...")
    try:
        from physics.scientific_impact_assessment import ScientificImpactAssessment
        print("  Import successful!")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        sys.exit(1)

    # 2. Initialization
    print("\n[TEST 2/4] Initializing impact assessment module...")
    try:
        assessment = ScientificImpactAssessment()
        print("  Initialization successful!")
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        sys.exit(1)

    # 3. Execution
    print("\n[TEST 3/4] Running scientific impact assessment execution...")
    try:
        results = assessment.run()
        print("  Execution successful!")
    except Exception as e:
        print(f"[ERROR] Engine execution failed: {e}")
        sys.exit(1)

    # 4. Validating output fields and file presence
    print("\n[TEST 4/4] Validating audit outputs and file structure...")
    try:
        # Check dictionary keys
        assert "metrics" in results, "Missing 'metrics' key in results."
        assert "report_path" in results, "Missing 'report_path' key."
        assert "ScientificImpactScore" in results, "Missing 'ScientificImpactScore' key."
        assert "impact_classification" in results, "Missing 'impact_classification' key."

        metrics = results["metrics"]
        assert "sub_components" in metrics, "Missing 'sub_components' in metrics."
        
        sub = metrics["sub_components"]
        expected_components = [
            "NoveltyImpactScore",
            "ValidationStrengthScore",
            "GeneralizationScore",
            "TheoryContributionScore",
            "EfficiencyScore",
            "MemoryContributionScore"
        ]

        for comp in expected_components:
            assert comp in sub, f"Missing sub-component: {comp}"
            score_val = sub[comp]
            print(f"  Pillar Score: {comp: <25} -> {score_val:.2f}/100")
            assert 0.0 <= score_val <= 100.0, f"Invalid sub-score: {score_val}"

        global_score = results["ScientificImpactScore"]
        classification = results["impact_classification"]
        print(f"\n  Global Impact Score:         {global_score:.2f}/100")
        print(f"  Impact Classification:       {classification}")

        assert 0.0 <= global_score <= 100.0, f"Invalid global score: {global_score}"

        # Verify expected files exist on disk
        artifacts_dir = Path(__file__).resolve().parent.parent / "artifacts"
        expected_files = [
            "scientific_impact_report.md",
            "scientific_impact_metrics.json",
            "scientific_impact_summary.json"
        ]

        for filename in expected_files:
            file_path = artifacts_dir / filename
            print(f"  Checking output: {filename} -> {file_path.exists()}")
            assert file_path.exists(), f"Output file missing: {filename}"

        # Verify that all 5 critical questions are explicitly answered in the markdown report
        print("\n🧪 Verifying presence of the 5 obligatory critical questions...")
        report_text = (artifacts_dir / "scientific_impact_report.md").read_text(encoding="utf-8")
        
        critical_keywords = [
            "¿El sistema genera descubrimientos útiles?",
            "¿Existe evidencia de aprendizaje acumulativo?",
            "¿Existe evidencia de falsación real?",
            "¿Existe evidencia de generalización entre dominios?",
            "¿El sistema está optimizando ciencia o métricas?"
        ]

        for q in critical_keywords:
            print(f"  Checking question presence: '{q}' -> {q in report_text}")
            assert q in report_text, f"Mandatory question missing in report: {q}"

        print("  All assertions passed successfully!")
    except AssertionError as e:
        print(f"[ERROR] Assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] General verification failure: {e}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✨ SUCCESS: Scientific Impact Assessment verified successfully")
    print("=" * 70)

if __name__ == "__main__":
    main()
