import sys
import os
import numpy as np

# Ensure root path is imported
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def run_tests():
    print("=" * 70)
    print("[TEST] RUNNING COMPREHENSIVE PHASE 4 INTEGRATION SUITE (TESTS 1 - 6)")
    print("=" * 70)

    # Imports
    try:
        import topological_analysis as tda
        import geometric_analysis as geom
        import koopman_analysis as koop
        from core.autonomous.latent_snapshot_exporter import extract_ev3_features
        import topological_robustness_audit as audit
        from synthetic_systems import generate_lorenz

        print("  Import of Phase 4 modules successful!")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        sys.exit(1)

    test_results = {}

    # Generate clean Lorenz signal for testing (X coordinate)
    try:
        lorenz_data = generate_lorenz(
            n_timesteps=1000, dt=0.01, initial_state=[10.0, 10.0, 20.0]
        )
        signal = lorenz_data["x"]
        print(f"  Generated test Lorenz signal of length {len(signal)}.")
    except Exception as e:
        print(f"[ERROR] Lorenz generator failed: {e}")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # Test 1: Phase Space, diagrams H0, H1
    # -------------------------------------------------------------------------
    print("\n[TEST 1/6] Verifying Takens embedding and persistent homology...")
    try:
        pc = tda.reconstruct_phase_space(signal, emb_dim=3, lag=2)
        assert pc.shape[0] > 0 and pc.shape[1] == 3, "Takens embedding shape incorrect."

        res = tda.compute_persistence_diagram(pc, max_dim=1)
        dgms = res["dgms"]
        print(
            f"  Computed persistence diagrams. H0 shape: {dgms[0].shape} | H1 shape: {dgms[1].shape}"
        )

        assert len(dgms) >= 2, f"Expected at least H0 and H1 diagrams, got {len(dgms)}"
        assert dgms[0].shape[0] > 0, "H0 diagram is empty."
        assert dgms[1].shape[0] > 0, "H1 diagram is empty."

        print("  Test 1 PASSED: H0 and H1 persistence diagrams successfully verified.")
        test_results["Test 1: Takens & Homology (H0, H1)"] = "PASS"
    except Exception as e:
        print(f"  Test 1 FAILED: {e}")
        test_results["Test 1: Takens & Homology (H0, H1)"] = "FAIL"

    # -------------------------------------------------------------------------
    # Test 2: Neighborhood Graph & Ollivier-Ricci Curvature
    # -------------------------------------------------------------------------
    print("\n[TEST 2/6] Verifying Ollivier-Ricci curvatures...")
    try:
        pc_sample = pc[:50]  # Sample for fast testing
        G = geom.build_neighborhood_graph(pc_sample, k=5)
        G_ricci = geom.compute_ollivier_ricci_curvature(G)
        node_curvs = geom.compute_node_curvature(G_ricci)

        print(f"  Ollivier-Ricci nodal curvatures mean: {np.mean(node_curvs):.4f}")
        assert not np.isnan(node_curvs).all(), "All node curvatures are NaN."
        assert len(node_curvs) == len(pc_sample), "Nodal curvature size mismatch."

        print("  Test 2 PASSED: Ollivier-Ricci curvatures successfully verified.")
        test_results["Test 2: Ollivier-Ricci Curvature"] = "PASS"
    except Exception as e:
        print(f"  Test 2 FAILED: {e}")
        test_results["Test 2: Ollivier-Ricci Curvature"] = "FAIL"

    # -------------------------------------------------------------------------
    # Test 3: Laplace-Beltrami normalised laplacian spectrum
    # -------------------------------------------------------------------------
    print("\n[TEST 3/6] Verifying Laplace-Beltrami Spectrum...")
    try:
        pc_sample = pc[:80]  # Sample for fast testing
        lb_eigs, _ = geom.compute_laplacian_eigenmap(pc_sample, n_components=5, k=8)
        print(f"  Laplace-Beltrami eigenvalues: {lb_eigs}")

        # In a normalised laplacian graph, the first eigenvalue represents connectivity and is 0 (or near 0)
        assert (
            abs(lb_eigs[0]) < 0.02
        ), f"First LB eigenvalue should be near 0, got {lb_eigs[0]}"
        assert len(lb_eigs) == 5, "Expected 5 eigenvalues."

        print("  Test 3 PASSED: Laplace-Beltrami graph spectrum verified successfully.")
        test_results["Test 3: Laplace-Beltrami Spectrum"] = "PASS"
    except Exception as e:
        print(f"  Test 3 FAILED: {e}")
        test_results["Test 3: Laplace-Beltrami Spectrum"] = "FAIL"

    # -------------------------------------------------------------------------
    # Test 4: Koopman Operator Decomposition
    # -------------------------------------------------------------------------
    print("\n[TEST 4/6] Verifying Koopman DMD Modes...")
    try:
        eigs, modes, freqs, growths = koop.compute_koopman_modes(
            signal, emb_dim=3, lag=1, n_modes=5
        )
        mags = np.abs(eigs)
        print(f"  Koopman eigenvalue magnitudes: {mags}")

        # Check if at least one eigenvalue has magnitude close to 1 (conservative mode)
        conservative_count = np.sum(np.abs(mags - 1.0) < 0.05)
        print(
            f"  Count of conservative modes (|lambda| approx 1): {conservative_count}"
        )

        assert (
            conservative_count >= 1
        ), "Expected at least one conservative mode near 1.0."

        print("  Test 4 PASSED: Koopman operator modes verified successfully.")
        test_results["Test 4: Koopman DMD Modes"] = "PASS"
    except Exception as e:
        print(f"  Test 4 FAILED: {e}")
        test_results["Test 4: Koopman DMD Modes"] = "FAIL"

    # -------------------------------------------------------------------------
    # Test 5: EV3_DEEP (68 dimensions) Shape and NaN Check
    # -------------------------------------------------------------------------
    print("\n[TEST 5/6] Verifying EV3_DEEP (68D) feature extraction...")
    try:
        # Extract deep features
        feats = extract_ev3_features(signal, extended=True, deep=True)
        print(f"  Extracted EV3_DEEP feature vector shape: {feats.shape}")

        # Check NaNs
        nan_count = np.isnan(feats).sum()
        nan_fraction = nan_count / len(feats)
        print(f"  NaN Count: {nan_count} | NaN Fraction: {nan_fraction * 100:.2f}%")

        assert feats.shape == (68,), f"Expected shape (68,), got {feats.shape}"
        assert (
            nan_fraction < 0.30
        ), f"Expected NaN fraction < 30%, got {nan_fraction * 100:.2f}%"

        print("  Test 5 PASSED: EV3_DEEP feature extractor verified successfully.")
        test_results["Test 5: EV3_DEEP Extractor"] = "PASS"
    except Exception as e:
        print(f"  Test 5 FAILED: {e}")
        test_results["Test 5: EV3_DEEP Extractor"] = "FAIL"

    # -------------------------------------------------------------------------
    # Test 6: Topological stability Wasserstein distance increases with noise
    # -------------------------------------------------------------------------
    print("\n[TEST 6/6] Verifying topological stability under noise...")
    try:
        # Run topological stability on a short Lorenz signal for fast execution
        short_sig = signal[:400]
        snrs = [30, 20, 10, 0]
        tda_stab = audit.compute_topological_stability(short_sig, snr_levels=snrs)

        w_h1_30 = tda_stab.loc[tda_stab["SNR"] == 30, "Wasserstein_H1"].values[0]
        w_h1_0 = tda_stab.loc[tda_stab["SNR"] == 0, "Wasserstein_H1"].values[0]

        print(f"  H1 Wasserstein distance at SNR 30dB: {w_h1_30:.4f}")
        print(f"  H1 Wasserstein distance at SNR  0dB: {w_h1_0:.4f}")

        # Assert that Wasserstein distance increases as noise increases (SNR decreases)
        assert (
            w_h1_0 > w_h1_30
        ), f"Expected Wasserstein distance at 0dB ({w_h1_0:.4f}) to be greater than at 30dB ({w_h1_30:.4f})."

        print("  Test 6 PASSED: Topological stability verified successfully.")
        test_results["Test 6: Topological Stability Audit"] = "PASS"
    except Exception as e:
        print(f"  Test 6 FAILED: {e}")
        test_results["Test 6: Topological Stability Audit"] = "FAIL"

    # Consolidated Results Table
    print("\n" + "=" * 70)
    print("CONSOLIDATED INTEGRATION TEST RESULTS:")
    print("=" * 70)
    all_passed = True
    for name, status in test_results.items():
        print(f"  {name:<48} : {status}")
        if status == "FAIL":
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("SUCCESS: All Phase 4 integration tests passed!")
    else:
        print("FAILURE: Some Phase 4 integration tests failed.")
    print("=" * 70)

    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
