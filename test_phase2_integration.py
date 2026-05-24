import sys
import os
import numpy as np
import pandas as pd

# Ensure root path is imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def run_tests():
    print("=" * 70)
    print("[TEST] RUNNING COMPREHENSIVE PHASE 2 INTEGRATION TEST SUITE")
    print("=" * 70)

    # Imports
    try:
        import synthetic_systems
        import symbolic_discovery

        print("  Import successful!")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        sys.exit(1)

    test_results = {}

    # Test 1: Lorenz Generation
    print("\n[TEST 1/5] Verifying Lorenz data generation...")
    try:
        data = synthetic_systems.generate_lorenz(n_timesteps=1000)
        assert "x" in data, "Missing 'x' coordinate."
        assert "y" in data, "Missing 'y' coordinate."
        assert "z" in data, "Missing 'z' coordinate."
        assert "t" in data, "Missing 't' time vector."
        assert "derivatives" in data, "Missing 'derivatives' dictionary."
        assert "dx" in data["derivatives"], "Missing 'dx' derivative."
        assert "dy" in data["derivatives"], "Missing 'dy' derivative."
        assert "dz" in data["derivatives"], "Missing 'dz' derivative."
        assert data["x"].shape == (1000,), f"Incorrect shape: {data['x'].shape}"
        print("  Test 1 PASSED: Lorenz generator functions successfully.")
        test_results["Test 1: Lorenz Generation"] = "PASS"
    except Exception as e:
        print(f"  Test 1 FAILED: {e}")
        test_results["Test 1: Lorenz Generation"] = "FAIL"

    # Test 2: Lorenz SINDy Discovery
    print("\n[TEST 2/5] Running SINDy equation discovery on Lorenz...")
    try:
        res = symbolic_discovery.discover_system_dynamics("lorenz", method="sindy")
        jaccard = res["evaluation"]["jaccard_terms"]
        match = res["evaluation"]["match"]
        print(f"  Lorenz SINDy Jaccard term overlap: {jaccard * 100:.2f}%")
        print(f"  Lorenz SINDy algebraic match: {match}")
        assert jaccard > 0.5 or match, f"Jaccard term overlap too low: {jaccard:.4f}"
        print("  Test 2 PASSED: SINDy recovered Lorenz equations successfully.")
        test_results["Test 2: Lorenz SINDy Discovery"] = "PASS"
    except Exception as e:
        print(f"  Test 2 FAILED: {e}")
        test_results["Test 2: Lorenz SINDy Discovery"] = "FAIL"

    # Test 3: Logistic PySR (Deterministic Failsafe) Discovery
    print("\n[TEST 3/5] Running PySR equation discovery on Logistic Map...")
    try:
        res = symbolic_discovery.discover_system_dynamics("logistic", method="pysr")
        discovered_eqs = res["discovered_equations"]
        print(f"  Logistic discovered equations: {discovered_eqs}")
        eq_str = discovered_eqs["x_next"]
        assert (
            "x" in eq_str
        ), f"Discovered formula does not contain variable 'x': {eq_str}"
        print("  Test 3 PASSED: PySR/Lasso recovered Logistic map terms successfully.")
        test_results["Test 3: Logistic PySR Discovery"] = "PASS"
    except Exception as e:
        print(f"  Test 3 FAILED: {e}")
        test_results["Test 3: Logistic PySR Discovery"] = "FAIL"

    # Test 4: Complete Multi-System Benchmark
    print("\n[TEST 4/5] Executing full multi-system benchmark...")
    try:
        df_bench = symbolic_discovery.run_full_discovery_benchmark(
            systems=["lorenz", "rossler", "duffing", "van_der_pol", "logistic"],
            methods=["sindy"],
        )
        print("  Benchmark report output:")
        print(df_bench.to_string(index=False))

        successful_recoveries = 0
        for _, row in df_bench.iterrows():
            if row["match"] or row["jaccard_terms"] > 0.5:
                successful_recoveries += 1

        print(f"  Successful structural recoveries: {successful_recoveries}/5")
        assert (
            successful_recoveries >= 3
        ), f"Fewer than 3 successful recoveries: {successful_recoveries}"
        print(
            "  Test 4 PASSED: Benchmark benchmark executed successfully with high recovery rate."
        )
        test_results["Test 4: Full Multi-System Benchmark"] = "PASS"
    except Exception as e:
        print(f"  Test 4 FAILED: {e}")
        test_results["Test 4: Full Multi-System Benchmark"] = "FAIL"

    # Test 5: Physics Penalty
    print("\n[TEST 5/5] Verifying PINN-style physics penalties...")
    try:
        eq_wrong = "10.0 * y - 10.0 * x"
        penalty = symbolic_discovery.add_physics_penalty(
            eq_wrong, expected_terms=["x * z"]
        )
        print(
            f"  Wrong equation: '{eq_wrong}' | Expected: ['x * z'] | Penalty score: {penalty}"
        )
        assert penalty > 0.0, f"Expected penalty to be positive, got {penalty}"

        eq_right = "-0.2*v - 1.0*x - -1.0*x**3 + 0.3*cos(1.2*t)"
        penalty_right = symbolic_discovery.add_physics_penalty(
            eq_right, expected_terms=["v"]
        )
        print(
            f"  Right equation: '{eq_right}' | Expected: ['v'] | Penalty score: {penalty_right}"
        )
        assert penalty_right == 0.0, f"Expected penalty to be zero, got {penalty_right}"

        print(
            "  Test 5 PASSED: Physics penalty correctly penalizes symmetry/term violations."
        )
        test_results["Test 5: PINN-style Physics Penalty"] = "PASS"
    except Exception as e:
        print(f"  Test 5 FAILED: {e}")
        test_results["Test 5: PINN-style Physics Penalty"] = "FAIL"

    # Consolidated Results Table
    print("\n" + "=" * 70)
    print("CONSOLIDATED INTEGRATION TEST RESULTS:")
    print("=" * 70)
    all_passed = True
    for name, status in test_results.items():
        print(f"  {name:<45} : {status}")
        if status == "FAIL":
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("SUCCESS: Phase 2 integrated successfully")
    else:
        print("FAILURE: Some Phase 2 tests failed")
    print("=" * 70)

    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
