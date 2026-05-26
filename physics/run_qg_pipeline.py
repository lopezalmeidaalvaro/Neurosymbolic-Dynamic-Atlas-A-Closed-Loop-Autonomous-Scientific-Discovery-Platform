import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import os
import sys
import time
import json
import numpy as np
import pandas as pd

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from quantum_gravity_features import build_unified_qg_dataset, search_for_invariants
from qg_geometric_audit import run_full_qg_audit
from null_models import generate_erdos_renyi_null

def print_premium_banner():
    banner = r"""
================================================================================
  _  _                                       _  _      
 | \| |___ _  _ _ _ ___ ____  _ _ __  __ ___| |(_)__ _ 
 | .` / -_) || | '_/ _ (_-< || | '  \/ _ (_-< | | / _` |
 |_|\_\___|\_,_|_| \___/__/\_, |_|_|_|___/__/_|_|_\__, |
                           |__/                   |___/ 
      QUANTUM GRAVITY REPRESENTATION & GEOMETRIC OBSERVABILITY SUITE
================================================================================
    """
    print(banner)

def main():
    print_premium_banner()
    start_time = time.time()
    
    # 1. Configuration and Paths
    causal_ensemble_path = "data/causal_layered_ensemble.csv"
    spin_ensemble_path = "data/spin_network_ensemble.csv"
    bec_ensemble_path = "data/bec_ensemble.csv"
    
    n_configs_limit = 50
    n_bootstrap = 100
    
    print(f"[INIT] Active Observability Pipeline Config:")
    print(f"  -> Causal Ensemble Path:   {causal_ensemble_path}")
    print(f"  -> Spin Ensemble Path:     {spin_ensemble_path}")
    print(f"  -> BEC Ensemble Path:      {bec_ensemble_path}")
    print(f"  -> Selected Audit Subset:  {n_configs_limit} configurations per domain")
    print(f"  -> Bootstrap Iterations:   {n_bootstrap}")
    print("=" * 80)
    
    # 2. Unified Feature Dataset Construction
    print("\n[STEP 1] Constructing Unified Quantum Gravity Feature Dataset...")
    step1_start = time.time()
    
    X_unified, y_unified = build_unified_qg_dataset(
        causal_ensemble_path,
        spin_ensemble_path,
        bec_ensemble_path,
        n_configs_limit=n_configs_limit
    )
    
    step1_duration = time.time() - step1_start
    print(f"[STEP 1 DONE] Saved unified features dataset. Duration: {step1_duration:.2f}s")
    print("-" * 80)
    
    # 3. Bootstrap CKA Emergent Invariant Search
    print("\n[STEP 2] Launching Bootstrap Centered Kernel Alignment (CKA)...")
    step2_start = time.time()
    
    invariants, cka_matrix, significance_report = search_for_invariants(
        X_unified,
        y_unified,
        n_bootstrap=n_bootstrap
    )
    
    step2_duration = time.time() - step2_start
    print(f"[STEP 2 DONE] Isolated emergent invariants across domains. Duration: {step2_duration:.2f}s")
    print("\nPairwise CKA Representation Similarity Matrix:")
    print(cka_matrix.round(4))
    print(f"\nDiscovered Emergent Invariant Feature Candidates ({len(invariants)} features):")
    print(invariants)
    print("-" * 80)
    
    # 4. High-Fidelity Geometric Auditing
    print("\n[STEP 3] Running Geometric and Topological Audits with Null Controls...")
    step3_start = time.time()
    
    # Load ensemble DataFrames for custom domain audits
    df_causal = pd.read_csv(causal_ensemble_path).iloc[:n_configs_limit]
    df_spin = pd.read_csv(spin_ensemble_path).iloc[:n_configs_limit]
    df_bec = pd.read_csv(bec_ensemble_path).iloc[:n_configs_limit]
    
    # Generate high-fidelity Erdős-Rényi null control DataFrame
    print(f"Generating mathematically rigorous Erdős-Rényi Null controls ({n_configs_limit} configurations)...")
    df_er_null = generate_erdos_renyi_null(n_configs=n_configs_limit, n_nodes=50, p=0.2, seed=42)
    null_dfs = {"Null_ER": df_er_null}
    
    # Run full audits
    audit_report = run_full_qg_audit(df_causal, df_spin, df_bec, null_dfs)
    
    step3_duration = time.time() - step3_start
    print(f"[STEP 3 DONE] Audits complete. Diagnostic plots and JSON exported. Duration: {step3_duration:.2f}s")
    print("=" * 80)
    
    # 5. Pipeline Summary Report
    total_duration = time.time() - start_time
    print("\n=================== OBSERVABILITY SUITE RUN COMPLETE ===================")
    print(f"Total Pipeline Runtime: {total_duration:.2f}s")
    print("Exported Files & Diagnostic Assets:")
    print("  [✓] Unified Feature Dataset:  data/qg_unified_features.csv")
    print("  [✓] Geometric Audit Report:   artifacts/qg_geometric_audit.json")
    print("  [✓] Causal Phase Transition:  figures/qg_audit_phase_transition.pdf")
    print("  [✓] Spin Network RT Scaling:  figures/qg_audit_spin_network.pdf")
    print("  [✓] BEC Sonic Horizon TDA:    figures/qg_audit_bec_horizon.pdf")
    print("========================================================================\n")
    
    # Save a small runtime status log
    status_log = {
        "status": "COMPLETED",
        "runtime_seconds": total_duration,
        "n_configs_limit": n_configs_limit,
        "discovered_invariants_count": len(invariants),
        "discovered_invariants_list": invariants,
        "cka_matrix": cka_matrix.to_dict(),
        "audit_summary": {
            "causal_transition_critical_val": audit_report["causal_layered_phase_transition"]["critical_value"],
            "causal_transition_sharpness": audit_report["causal_layered_phase_transition"]["sharpness"],
            "spin_network_holographic_r_squared": audit_report["spin_network_holography"]["holographic_r_squared"],
            "bec_horizon_wasserstein_distance": audit_report["bec_horizon_topology"]["wasserstein_distance"] if "bec_horizon_topology" in audit_report else audit_report["bec_analog_horizon_topology"]["wasserstein_distance"]
        }
    }
    
    with open("artifacts/qg_pipeline_status.json", "w") as f:
        json.dump(status_log, f, indent=4)
        
if __name__ == "__main__":
    main()
