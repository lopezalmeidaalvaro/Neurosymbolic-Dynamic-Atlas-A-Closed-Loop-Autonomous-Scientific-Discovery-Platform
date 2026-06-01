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
    print("🧪 RUNNING SCIENTIFIC MEMORY CONSOLIDATION INTEGRATION TEST")
    print("=" * 70)

    # 1. Imports
    print("[TEST 1/4] Importing MemoryConsolidationEngine...")
    try:
        from physics.memory_consolidation_engine import MemoryConsolidationEngine
        print("  Import successful!")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        sys.exit(1)

    # 2. Initialization
    print("\n[TEST 2/4] Initializing memory consolidation engine...")
    try:
        engine = MemoryConsolidationEngine()
        print("  Initialization successful!")
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        sys.exit(1)

    # 3. Execution
    print("\n[TEST 3/4] Running memory consolidation pipeline execution...")
    try:
        results = engine.run()
        print("  Execution successful!")
    except Exception as e:
        print(f"[ERROR] Engine execution failed: {e}")
        sys.exit(1)

    # 4. Validating output fields and artifacts
    print("\n[TEST 4/4] Validating consolidation outputs and file structure...")
    try:
        # Check dictionary keys
        assert "metrics" in results, "Missing 'metrics' key in results."
        assert "report_path" in results, "Missing 'report_path' key."
        assert "MemoryHealthScore" in results, "Missing 'MemoryHealthScore' key."
        assert "health_classification" in results, "Missing 'health_classification' key."

        metrics = results["metrics"]
        assert "compression" in metrics, "Missing 'compression' in metrics."
        assert "frontier_recycling_rate" in metrics, "Missing 'frontier_recycling_rate' in metrics."
        assert "recommended_exploration_zones" in metrics, "Missing 'recommended_exploration_zones' in metrics."
        assert "memory_health" in metrics, "Missing 'memory_health' in metrics."

        compression = metrics["compression"]
        assert "hypotheses_before" in compression, "Missing hypotheses_before"
        assert "hypotheses_after" in compression, "Missing hypotheses_after"
        assert "compression_ratio" in compression, "Missing compression_ratio"
        assert "pre_redundancy_ratio" in compression, "Missing pre_redundancy_ratio"
        assert "post_redundancy_ratio" in compression, "Missing post_redundancy_ratio"

        score = results["MemoryHealthScore"]
        classification = results["health_classification"]
        print(f"  Memory Health Score:         {score:.2f}/100")
        print(f"  Classification:              {classification}")
        print(f"  Compression Ratio achieved:  {compression['compression_ratio']*100.0:.2f}%")
        print(f"  Post-Redundancy Rate:        {compression['post_redundancy_ratio']*100.0:.2f}%")

        assert 0.0 <= score <= 100.0, f"Invalid memory health score: {score}"
        
        # Redundancy must be compressed from pre-redundancy down to a healthy post-redundancy rate (typically 0% for consolidated canon list)
        assert compression["post_redundancy_ratio"] < 0.10, f"Consolidation failed to drop redundancy under 10%. Post rate: {compression['post_redundancy_ratio']}"

        # Verify expected files exist on disk
        artifacts_dir = Path(__file__).resolve().parent.parent / "artifacts"
        expected_files = [
            "memory_consolidation_report.md",
            "memory_clusters.json",
            "memory_compression_metrics.json",
            "recommended_frontier_regions.json",
            "memory_health_score.json"
        ]

        for filename in expected_files:
            file_path = artifacts_dir / filename
            print(f"  Checking output: {filename} -> {file_path.exists()}")
            assert file_path.exists(), f"Output file missing: {filename}"

        # Additional assertions on recommended regions to ensure under-represented zones are priority
        rec_zones = metrics["recommended_exploration_zones"]
        assert len(rec_zones) > 0, "No exploration zones recommended."
        high_priority_zones = [z for z in rec_zones if z["exploration_priority"] == "HIGH"]
        print(f"  Under-explored High-Priority zones: {[z['domain_name'] for z in high_priority_zones]}")
        assert len(high_priority_zones) > 0, "Exploration mapping failed to detect high-priority zones."

        print("  All assertions passed successfully!")
    except AssertionError as e:
        print(f"[ERROR] Assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] General verification failure: {e}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✨ SUCCESS: Memory Consolidation Engine verified successfully")
    print("=" * 70)

if __name__ == "__main__":
    main()
