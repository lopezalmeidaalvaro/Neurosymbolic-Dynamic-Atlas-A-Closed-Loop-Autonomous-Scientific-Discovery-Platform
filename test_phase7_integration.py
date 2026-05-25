import os
import sys
import unittest
import numpy as np
import pandas as pd
import networkx as nx

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from causal_layered_graph import CausalLayeredGraphModel
from spin_network_model import SpinNetworkModel
from bec_analog_model import simulate_bec_flow, compute_analog_hawking_temperature
from null_models import generate_erdos_renyi_null, generate_colored_noise_null, compute_null_baseline
from quantum_gravity_features import extract_features_from_causal_layered, extract_features_from_spin_network, extract_features_from_bec, build_unified_qg_dataset
from scientific_guard import sanitize_hypothesis, validate_hypothesis_structure, reality_check
from qg_geometric_audit import run_full_qg_audit
from qg_autonomous_discovery import run_qg_discovery_cycle

class TestPhase7Integration(unittest.TestCase):

    def setUp(self):
        # Create directories if they do not exist
        os.makedirs("data", exist_ok=True)
        os.makedirs("figures", exist_ok=True)
        os.makedirs("artifacts", exist_ok=True)

    def test_01_causal_layered_graph(self):
        """TEST 1: CausalLayeredGraph - Generates and verifies volume profile and spectral dimension."""
        print("\n--- Running TEST 1: CausalLayeredGraph ---")
        model = CausalLayeredGraphModel(N_slices=5, N_vertices_per_slice=40, p_intra=0.4, p_inter=0.3, seed=42)
        G = model.generate()
        self.assertGreater(len(G.nodes), 0)
        self.assertGreater(len(G.edges), 0)
        
        # Verify volume profile
        vol_prof = model.compute_spatial_volume_profile(G)
        self.assertEqual(len(vol_prof), 5)
        for val in vol_prof:
            self.assertGreater(val, 0)
            
        # Verify spectral dimension d_s > 0
        d_s = model.compute_spectral_dimension(G, t_max=6)
        print(f"  Generated Causal Graph d_s: {d_s:.4f}")
        self.assertGreater(d_s, 0.0)

    def test_02_spin_network(self):
        """TEST 2: SpinNetwork - Generates, computes boundary cuts and area-entropy scaling."""
        print("\n--- Running TEST 2: SpinNetwork ---")
        model = SpinNetworkModel(n_nodes=30, max_spin=5, seed=42)
        G = model.generate()
        self.assertGreater(len(G.nodes), 0)
        
        # Verify boundary cuts area > 0
        nodal_areas = model.compute_nodal_areas(G)
        self.assertGreater(float(np.mean(nodal_areas)), 0.0)
        
        nodes_list = list(G.nodes)
        subset = nodes_list[:15]
        area = model.compute_boundary_area(G, subset)
        entropy = model.compute_entanglement_entropy(G, subset)
        
        print(f"  Spin Network boundary area: {area:.4f}, RT Entropy: {entropy:.4f}")
        self.assertGreater(area, 0.0)
        self.assertGreater(entropy, 0.0)

    def test_03_bec_acoustic_flow(self):
        """TEST 3: BEC Flow - Simulates BEC acoustic horizons and analog Hawking temperature."""
        print("\n--- Running TEST 3: BEC Flow ---")
        # High-velocity scenario triggers horizon emergence
        sim = simulate_bec_flow(n_grid=100, L=10.0, v0=2.2, c_sound=1.5, width=2.0)
        self.assertEqual(len(sim["v_profile"]), 100)
        
        # Verify horizon detection
        horizons = sim["horizon_positions"]
        self.assertGreater(len(horizons), 0)
        
        # Compute Hawking temperature manually
        dx = 10.0 / 100
        bh_horizon = max(horizons)
        t_hawking = compute_analog_hawking_temperature(bh_horizon, sim["v_profile"], 1.5, dx)
        self.assertGreater(t_hawking, 0.0)
        print(f"  BEC Horizon Positions: {horizons}, Hawking Temp: {t_hawking:.4f}")

    def test_04_null_models(self):
        """TEST 4: Null Models - Generates Erdős-Rényi and Colored Noise baselines."""
        print("\n--- Running TEST 4: Null Models ---")
        # 1. ER Null Graph
        df_er = generate_erdos_renyi_null(n_configs=3, n_nodes=30, p=0.2, seed=42)
        self.assertEqual(len(df_er), 3)
        self.assertTrue("spectral_dimension" in df_er.columns)
        self.assertTrue("mean_curvature" in df_er.columns)
        
        # 2. Pink Noise (beta = 1.0) Null features extraction
        features = generate_colored_noise_null(n_configs=3, length=100, beta=1.0, seed=42)
        self.assertEqual(features.shape, (3, 68))
        print("  Null ER & Colored Noise matrices verified.")

    def test_05_unified_features(self):
        """TEST 5: Unified Features - Verifies padded feature matrix assembly and domain layout."""
        print("\n--- Running TEST 5: Unified Features ---")
        # Generate temporary test CSV files
        df_c = pd.DataFrame({
            "config_id": [0], "p_intra": [0.5], "p_inter": [0.3], "spectral_dimension": [1.4], "mean_curvature": [0.1],
            "mean_volume": [40.0], "std_volume": [0.0], "vol_slice_0": [40.0], "vol_slice_1": [40.0], "vol_slice_2": [40.0],
            "vol_slice_3": [40.0], "vol_slice_4": [40.0]
        })
        df_s = pd.DataFrame({
            "config_id": [0], "n_nodes": [30], "boundary_area": [12.5], "entanglement_entropy": [6.75], "std_nodal_area": [1.2]
        })
        df_b = pd.DataFrame({
            "config_id": [0], "v0": [2.2], "c_sound": [1.5], "has_horizon": [1], "hawking_temperature": [0.15]
        })
        
        df_c.to_csv("data/temp_test_causal.csv", index=False)
        df_s.to_csv("data/temp_test_spin.csv", index=False)
        df_b.to_csv("data/temp_test_bec.csv", index=False)
        
        # Extract features and assemble unified dataset
        X_u, y_u = build_unified_qg_dataset(
            "data/temp_test_causal.csv",
            "data/temp_test_spin.csv",
            "data/temp_test_bec.csv",
            n_configs_limit=1
        )
        # 5 domains (Causal, Spin, BEC, Null ER, Null Noise) * 1 config = 5 rows, 88 features padded
        self.assertEqual(X_u.shape, (5, 88))
        self.assertEqual(len(y_u), 5)
        print(f"  Unified Dataset shape: {X_u.shape} (Expected: 5 x 88)")
        
        # Cleanup
        for path in ["data/temp_test_causal.csv", "data/temp_test_spin.csv", "data/temp_test_bec.csv"]:
            if os.path.exists(path):
                os.remove(path)

    def test_06_scientific_guard_sanitization(self):
        """TEST 6: Scientific Guard - Verifies that forbidden terms are blocked and sanitized."""
        print("\n--- Running TEST 6: Scientific Guard Sanitization ---")
        hyp = "This provides proof of quantum gravity and verifies the theory of everything in our real spacetime."
        sanitized = sanitize_hypothesis(hyp)
        
        # Verify prefix and substitutions
        self.assertTrue(sanitized.startswith("[MODEL-SPECIFIC OBSERVATION]:"))
        self.assertFalse("proof of quantum gravity" in sanitized.lower())
        self.assertFalse("theory of everything" in sanitized.lower())
        self.assertFalse("real spacetime" in sanitized.lower())
        print(f"  Sanitized Text: '{sanitized}'")

    def test_07_hypothesis_structure_validation(self):
        """TEST 7: Hypothesis Template - Verifies that rigid JSON layout checker flags format violations."""
        print("\n--- Running TEST 7: Hypothesis Structure Validation ---")
        # 1. Valid hypothesis dict
        valid = {
            "hypothesis": "The analogue sonic horizon Hawking radiation correlates with fluid sound speed.",
            "equation": "$T_H \\approx c_s \\cdot \\kappa$",
            "variables": ["v0", "c_sound", "hawking_temperature"],
            "falsification_test": "Wasserstein distance < 0.02",
            "confidence_prior": 0.75
        }
        is_v, errs = validate_hypothesis_structure(valid)
        self.assertTrue(is_v)
        self.assertEqual(len(errs), 0)
        
        # 2. Invalid hypothesis dict (multiple equations, too long, out-of-bounds prior)
        invalid = {
            "hypothesis": "This description is way too long. " * 10, # exceeds 200 chars
            "equation": "$S = A$ and $S = k \\log(W)$", # multiple equations
            "variables": ["v1", "v2", "v3", "v4"], # exceeds 3 elements
            "falsification_test": "Looks good to me", # no numerical comparison
            "confidence_prior": 1.4 # out of [0, 1]
        }
        is_v, errs = validate_hypothesis_structure(invalid)
        self.assertFalse(is_v)
        self.assertGreater(len(errs), 0)
        print("  Invalid hypothesis structure errors successfully intercepted:")
        for err in errs:
            print(f"    - {err}")

    def test_08_geometric_audit_orchestration(self):
        """TEST 8: Geometric Audit - Verifies the auditor runs and exports JSON and PDFs."""
        print("\n--- Running TEST 8: Geometric Audit Orchestration ---")
        c_df = pd.DataFrame({
            "config_id": [0, 1, 2], "p_intra": [0.2, 0.4, 0.6], "p_inter": [0.2, 0.2, 0.2],
            "spectral_dimension": [1.2, 1.4, 1.6], "mean_curvature": [0.01, 0.02, 0.03],
            "mean_volume": [40.0, 40.0, 40.0], "std_volume": [0.0, 0.0, 0.0],
            "vol_slice_0": [40.0, 40.0, 40.0], "vol_slice_1": [40.0, 40.0, 40.0], "vol_slice_2": [40.0, 40.0, 40.0],
            "vol_slice_3": [40.0, 40.0, 40.0], "vol_slice_4": [40.0, 40.0, 40.0]
        })
        s_df = pd.DataFrame({
            "config_id": [0, 1, 2], "n_nodes": [20, 20, 20], "boundary_area": [5.0, 10.0, 15.0],
            "entanglement_entropy": [2.7, 5.4, 8.1], "std_nodal_area": [1.0, 1.1, 1.2]
        })
        b_df = pd.DataFrame({
            "config_id": [0, 1, 2], "v0": [1.0, 2.0, 2.5], "c_sound": [1.5, 1.5, 1.5],
            "has_horizon": [0, 1, 1], "hawking_temperature": [0.0, 0.12, 0.18]
        })
        null_er = pd.DataFrame({
            "spectral_dimension": [1.3, 1.3, 1.3], "mean_curvature": [0.02, 0.02, 0.02]
        })
        
        run_full_qg_audit(c_df, s_df, b_df, {"Null_ER": null_er})
        
        # Verify files are exported
        self.assertTrue(os.path.exists("artifacts/qg_geometric_audit.json"))
        self.assertTrue(os.path.exists("figures/qg_audit_phase_transition.pdf"))
        self.assertTrue(os.path.exists("figures/qg_audit_spin_network.pdf"))
        self.assertTrue(os.path.exists("figures/qg_audit_bec_horizon.pdf"))
        print("  Geometric audit diagnostic plots and JSON successfully written.")

    def test_09_qg_autonomous_discovery_cycle(self):
        """TEST 9: QG Discovery - Executes 1 mock iteration cycle and checks JSON output report."""
        print("\n--- Running TEST 9: QG Discovery Loop ---")
        # Ensure stochastically generated ensembles exist for the mock discovery loop
        df_c = pd.DataFrame({"config_id": range(5), "p_intra": np.random.uniform(0.1, 0.9, 5), "spectral_dimension": np.random.uniform(1.2, 1.8, 5)})
        df_s = pd.DataFrame({"config_id": range(5), "boundary_area": np.random.uniform(2, 20, 5), "entanglement_entropy": np.random.uniform(1, 10, 5)})
        df_b = pd.DataFrame({"config_id": range(5), "has_horizon": [0, 1, 1, 0, 1], "hawking_temperature": np.random.uniform(0, 0.2, 5)})
        
        df_c.to_csv("data/causal_layered_ensemble.csv", index=False)
        df_s.to_csv("data/spin_network_ensemble.csv", index=False)
        df_b.to_csv("data/bec_ensemble.csv", index=False)
        
        # Run 1 specialized iteration cycle
        run_log = run_qg_discovery_cycle("find_stable_correlations", max_iterations=1)
        self.assertEqual(len(run_log), 1)
        
        item = run_log[0]
        hyp = item["hypothesis"]
        
        # Check structure keys are QG compliant
        self.assertTrue("hypothesis" in hyp)
        self.assertTrue("equation" in hyp)
        self.assertTrue("variables" in hyp)
        self.assertTrue("falsification_test" in hyp)
        self.assertTrue(item["verdict"] in ["VALIDATED", "FALSIFIED", "INCONCLUSIVE"])
        print(f"  QG Specialized loop run completed. Verdict: {item['verdict']}")

    def test_10_null_baseline_significance(self):
        """TEST 10: Null Baseline - Computes Z-scores and empirical p-values."""
        print("\n--- Running TEST 10: Null Baseline ---")
        real_value = 5.2
        null_distribution = np.random.normal(loc=0.0, scale=1.0, size=500)
        
        stats_dict = compute_null_baseline(real_value, null_distribution)
        self.assertTrue(stats_dict["is_significant"])
        self.assertGreater(stats_dict["z_score"], 4.0)
        self.assertLess(stats_dict["p_value"], 0.01)
        print(f"  Real val: {real_value:.2f}, Z-score: {stats_dict['z_score']:.4f}, p-value: {stats_dict['p_value']:.4f}")

if __name__ == "__main__":
    unittest.main()
