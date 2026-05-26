import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import os
import sys
import random
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
from core.autonomous.latent_snapshot_exporter import extract_ev3_deep
from null_models import generate_erdos_renyi_null, generate_colored_noise_null

def extract_features_from_causal_layered(df) -> np.ndarray:
    """
    Extracts custom representation features for CausalLayeredGraphModel configs:
    - 68D EV3_DEEP from volume profile (interpolated to 200).
    - 15D graph topology features.
    - 5D Ricci curvature profile.
    Total: 88D features.
    """
    print("Extracting features from Causal Layered Graphs...")
    features_list = []
    
    # We rebuild G for each config to get full network metrics
    for _, row in df.iterrows():
        c_id = int(row["config_id"])
        p_intra = float(row["p_intra"])
        p_inter = float(row["p_inter"])
        
        # 1. EV3 features from V(t)
        v_cols = [c for c in df.columns if c.startswith("vol_slice_")]
        v_profile = row[v_cols].values.astype(float)
        
        # Interpolate V(t) to length 200
        x_old = np.linspace(0, 1, len(v_profile))
        x_new = np.linspace(0, 1, 200)
        v_interp = np.interp(x_new, x_old, v_profile)
        
        # Prevent phase space collapse for flat/low-variance signals
        if np.std(v_interp) < 1e-4:
            v_interp = v_interp + np.random.normal(0, 1e-6, len(v_interp))
        
        # Run EV3 deep
        try:
            ev3 = extract_ev3_deep(v_interp)
            ev3 = np.array([float(val) if np.isfinite(val) else 0.0 for val in ev3])
        except Exception:
            ev3 = np.zeros(68)
            
        # 2. Reconstruct graph
        model = CausalLayeredGraphModel(N_slices=5, N_vertices_per_slice=50, p_intra=p_intra, p_inter=p_inter, seed=42 + c_id)
        G = model.generate()
        
        # Compute 15D network topology features
        N = len(G.nodes)
        E = len(G.edges)
        density = nx.density(G)
        
        try:
            transitivity = nx.transitivity(G)
        except Exception:
            transitivity = 0.0
            
        clust = list(nx.clustering(G).values())
        mean_clust = np.mean(clust) if clust else 0.0
        std_clust = np.std(clust) if clust else 0.0
        
        components = list(nx.connected_components(G))
        n_comp = len(components)
        giant_size = len(max(components, key=len)) / N if components else 0.0
        
        degrees = [d for n, d in G.degree()]
        mean_deg = np.mean(degrees) if degrees else 0.0
        std_deg = np.std(degrees) if degrees else 0.0
        skew_deg = float(np.mean(((degrees - mean_deg) / (std_deg + 1e-15))**3)) if std_deg > 1e-15 else 0.0
        kurt_deg = float(np.mean(((degrees - mean_deg) / (std_deg + 1e-15))**4)) if std_deg > 1e-15 else 0.0
        
        try:
            assort = nx.degree_assortativity_coefficient(G)
            if not np.isfinite(assort):
                assort = 0.0
        except Exception:
            assort = 0.0
            
        n_triang = sum(nx.triangles(G).values()) / 3.0
        
        # Graph efficiency
        try:
            efficiency = nx.global_efficiency(G)
        except Exception:
            efficiency = 0.0
            
        # Fiedler algebraic connectivity
        try:
            L = nx.laplacian_matrix(G).toarray()
            eigvals = np.linalg.eigvalsh(L)
            fiedler = eigvals[1] if len(eigvals) > 1 else 0.0
        except Exception:
            fiedler = 0.0
            
        net_feats = np.array([
            float(E), density, transitivity, mean_clust, std_clust,
            float(n_comp), giant_size, mean_deg, std_deg, skew_deg,
            kurt_deg, assort, float(n_triang), efficiency, fiedler
        ])
        net_feats = np.nan_to_num(net_feats)
        
        # 3. 5D curvature profile
        curv_dict = model.compute_ricci_curvature_profile(G)
        curv_profile = np.array(curv_dict["curvature_by_slice"])
        if len(curv_profile) != 5:
            # Pad or truncate
            curv_profile = np.resize(curv_profile, 5)
            
        # Concatenate 68D + 15D + 5D = 88D
        feat_vector = np.concatenate([ev3, net_feats, curv_profile])
        features_list.append(feat_vector)
        
    return np.array(features_list)

def extract_features_from_spin_network(df) -> np.ndarray:
    """
    Extracts custom representation features for SpinNetworkModel configs:
    - 68D EV3_DEEP from interpolated nodal area sequence.
    - 15D network topological features (degree, clustering, betweenness Centrality).
    Total: 83D features.
    """
    print("Extracting features from Spin Networks...")
    features_list = []
    
    for _, row in df.iterrows():
        c_id = int(row["config_id"])
        n_nodes = int(row["n_nodes"])
        
        # 1. Reconstruct graph
        model = SpinNetworkModel(n_nodes=n_nodes, max_spin=5, seed=42 + c_id)
        G = model.generate()
        
        # 2. Get Nodal Areas
        nodal_areas = model.compute_nodal_areas(G)
        # Interpolate sequence to length 200
        x_old = np.linspace(0, 1, len(nodal_areas))
        x_new = np.linspace(0, 1, 200)
        area_interp = np.interp(x_new, x_old, nodal_areas)
        
        # Prevent phase space collapse for flat/low-variance signals
        if np.std(area_interp) < 1e-4:
            area_interp = area_interp + np.random.normal(0, 1e-6, len(area_interp))
        
        # Run EV3 deep
        try:
            ev3 = extract_ev3_deep(area_interp)
            ev3 = np.array([float(val) if np.isfinite(val) else 0.0 for val in ev3])
        except Exception:
            ev3 = np.zeros(68)
            
        # 3. 15D network features: 5 stats (mean, std, skew, kurt, median) for each distribution:
        # degree, clustering coefficient, and betweenness centrality.
        degrees = np.array([d for n, d in G.degree()], dtype=float)
        clustering = np.array(list(nx.clustering(G).values()), dtype=float)
        try:
            betweenness = np.array(list(nx.betweenness_centrality(G).values()), dtype=float)
        except Exception:
            betweenness = np.zeros(n_nodes)
            
        def extract_dist_stats(arr):
            mean = np.mean(arr)
            std = np.std(arr)
            skew = float(np.mean(((arr - mean) / (std + 1e-15))**3)) if std > 1e-15 else 0.0
            kurt = float(np.mean(((arr - mean) / (std + 1e-15))**4)) if std > 1e-15 else 0.0
            median = np.median(arr)
            return [mean, std, skew, kurt, median]
            
        deg_stats = extract_dist_stats(degrees)
        clust_stats = extract_dist_stats(clustering)
        bet_stats = extract_dist_stats(betweenness)
        
        net_feats = np.array(deg_stats + clust_stats + bet_stats)
        net_feats = np.nan_to_num(net_feats)
        
        # Concatenate 68D + 15D = 83D
        feat_vector = np.concatenate([ev3, net_feats])
        features_list.append(feat_vector)
        
    return np.array(features_list)

def extract_features_from_bec(df) -> np.ndarray:
    """
    Extracts custom representation features for BEC Analog Model configs:
    - 68D EV3_DEEP from flow velocity profile v(x).
    - 1D horizon feature (has_horizon).
    - 1D Hawking temperature.
    - 6D quasinormal frequencies (first 3 complex modes: real and imaginary parts).
    Total: 76D features.
    """
    print("Extracting features from BEC flows...")
    features_list = []
    
    for _, row in df.iterrows():
        # 1. Rebuild flow
        v0 = float(row["v0"])
        c_sound = float(row["c_sound"])
        sim = simulate_bec_flow(n_grid=200, L=10.0, v0=v0, c_sound=c_sound, width=2.0)
        v_profile = np.array(sim["v_profile"])
        
        # Prevent phase space collapse for flat/low-variance signals
        if np.std(v_profile) < 1e-4:
            v_profile = v_profile + np.random.normal(0, 1e-6, len(v_profile))
        
        # Run EV3 deep on v_profile
        try:
            ev3 = extract_ev3_deep(v_profile)
            ev3 = np.array([float(val) if np.isfinite(val) else 0.0 for val in ev3])
        except Exception:
            ev3 = np.zeros(68)
            
        # 2. Horizon, Hawking temp, and QNMs
        has_horizon = float(row["has_horizon"])
        t_hawking = float(row["hawking_temperature"])
        
        # Quasinormal frequencies: omega_n = Omega_real - i * (n + 1/2) * kappa
        # kappa = 2 * pi * T_H
        # Omega_real ~ c_sound / width
        kappa = 2.0 * np.pi * t_hawking
        omega_real = c_sound / 2.0 # width = 2.0
        
        qnm = []
        for n in range(3):
            # Complex QNM frequency
            re = omega_real
            im = -(n + 0.5) * kappa
            qnm.extend([re, im])
            
        bec_feats = np.array([has_horizon, t_hawking] + qnm)
        
        # Concatenate 68D + 8D = 76D
        feat_vector = np.concatenate([ev3, bec_feats])
        features_list.append(feat_vector)
        
    return np.array(features_list)

def build_unified_qg_dataset(causal_path, spin_path, bec_path, null_paths=None, n_configs_limit=None) -> tuple:
    """
    Loads causal layered, spin network, and BEC datasets alongside null models.
    Applies custom features and pads all domains to a unified 88D feature matrix.
    Saves the dataset to data/qg_unified_features.csv.
    Returns (X_unified, y_unified).
    """
    # 1. Load real datasets
    df_causal = pd.read_csv(causal_path)
    df_spin = pd.read_csv(spin_path)
    df_bec = pd.read_csv(bec_path)
    
    n_configs = len(df_causal)
    if n_configs_limit is not None:
        n_configs = min(n_configs, n_configs_limit)
    
    # 2. Extract features
    X_causal = extract_features_from_causal_layered(df_causal.iloc[:n_configs]) # (N, 88)
    X_spin = extract_features_from_spin_network(df_spin.iloc[:n_configs])       # (N, 83)
    X_bec = extract_features_from_bec(df_bec.iloc[:n_configs])                 # (N, 76)
    
    print("Generating Null Erdős-Rényi baseline...")
    df_er_null = generate_erdos_renyi_null(n_configs=n_configs, n_nodes=50, p=0.2, seed=42)
    df_er_null["p_intra"] = 0.2
    df_er_null["p_inter"] = 0.2
    X_null_er = extract_features_from_causal_layered(df_er_null) # (N, 88)
    
    print("Generating Null Colored Noise baseline...")
    X_null_noise_ev3 = generate_colored_noise_null(n_configs=n_configs, length=200, beta=1.0, seed=42) # (N, 68)
    
    D_max = 88
    
    def pad_matrix(X, D_target):
        n, d = X.shape
        if d < D_target:
            padding = np.zeros((n, D_target - d))
            return np.hstack([X, padding])
        return X[:, :D_target]
        
    X_causal_pad = pad_matrix(X_causal, D_max)
    X_spin_pad = pad_matrix(X_spin, D_max)
    X_bec_pad = pad_matrix(X_bec, D_max)
    X_null_er_pad = pad_matrix(X_null_er, D_max)
    X_null_noise_pad = pad_matrix(X_null_noise_ev3, D_max)
    
    # 5. Concatenate and build Labels
    X_unified = np.vstack([
        X_causal_pad,
        X_spin_pad,
        X_bec_pad,
        X_null_er_pad,
        X_null_noise_pad
    ])
    
    labels = (
        ["CausalLayered"] * n_configs +
        ["SpinNetwork"] * n_configs +
        ["BEC"] * n_configs +
        ["Null_ER"] * n_configs +
        ["Null_Noise"] * n_configs
    )
    y_unified = np.array(labels)
    
    # 6. Save to CSV
    columns = ["config_id", "domain"] + [f"feature_{i}" for i in range(D_max)]
    data_rows = []
    
    idx = 0
    for domain_name in ["CausalLayered", "SpinNetwork", "BEC", "Null_ER", "Null_Noise"]:
        for c in range(n_configs):
            row_data = [c, domain_name] + list(X_unified[idx])
            data_rows.append(row_data)
            idx += 1
            
    df_unified = pd.DataFrame(data_rows, columns=columns)
    output_path = "data/qg_unified_features.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_unified.to_csv(output_path, index=False)
    print(f"Successfully constructed and saved unified dataset: {output_path} (shape: {df_unified.shape})")
    
    return X_unified, y_unified

def linear_cka(X1, X2) -> float:
    """
    Computes Centered Kernel Alignment (CKA) between two feature matrices.
    Uses efficient linear Frobenius formulation.
    """
    # Center columns
    X1_centered = X1 - np.mean(X1, axis=0)
    X2_centered = X2 - np.mean(X2, axis=0)
    
    # HSIC = || X2_T * X1 ||_F^2 / (N-1)^2
    hsic = np.linalg.norm(X2_centered.T @ X1_centered, ord="fro")**2
    var1 = np.linalg.norm(X1_centered.T @ X1_centered, ord="fro")**2
    var2 = np.linalg.norm(X2_centered.T @ X2_centered, ord="fro")**2
    
    denom = np.sqrt(var1 * var2) + 1e-15
    return float(hsic / denom)

def search_for_invariants(X_unified, y_unified, n_bootstrap=100, ci=95) -> tuple:
    """
    Evaluates Centered Kernel Alignment (CKA) across real and null domains.
    Runs bootstrap analysis to identify representation invariants (CKA > CKA_null + 2*std_null).
    Returns (invariants_candidates, cka_matrix, significance_report).
    """
    print("Searching for emergent representation invariants using Bootstrap CKA...")
    domains = ["CausalLayered", "SpinNetwork", "BEC", "Null_ER", "Null_Noise"]
    
    # Slice X_unified by domain
    domain_matrices = {}
    for d in domains:
        domain_matrices[d] = X_unified[y_unified == d]
        
    n_samples = len(domain_matrices["CausalLayered"])
    
    # 1. Pairwise CKA matrix (mean across bootstrap iterations)
    cka_matrix = pd.DataFrame(np.eye(5), index=domains, columns=domains)
    
    # Bootstrap evaluations of CKA between domains
    pairwise_bootstrap_vals = {}
    for i in range(len(domains)):
        for j in range(i + 1, len(domains)):
            d1, d2 = domains[i], domains[j]
            X1, X2 = domain_matrices[d1], domain_matrices[d2]
            
            boot_vals = []
            np.random.seed(42)
            for _ in range(n_bootstrap):
                indices = np.random.choice(n_samples, size=n_samples, replace=True)
                boot_vals.append(linear_cka(X1[indices], X2[indices]))
                
            pairwise_bootstrap_vals[(d1, d2)] = boot_vals
            mean_cka = np.mean(boot_vals)
            cka_matrix.loc[d1, d2] = mean_cka
            cka_matrix.loc[d2, d1] = mean_cka
            
    # 2. Evaluate individual feature invariants
    # We analyze each of the 88 features across the domains.
    # CKA for a 1D feature between two domains is the squared correlation coefficient.
    invariants_candidates = []
    significance_report = {}
    
    # Establish a baseline null standard from pairings with null models
    null_pairs = [
        ("CausalLayered", "Null_ER"),
        ("SpinNetwork", "Null_ER"),
        ("BEC", "Null_Noise")
    ]
    
    for f in range(88):
        # Extract feature f values
        f_causal = domain_matrices["CausalLayered"][:, f]
        f_spin = domain_matrices["SpinNetwork"][:, f]
        f_bec = domain_matrices["BEC"][:, f]
        f_null_er = domain_matrices["Null_ER"][:, f]
        f_null_noise = domain_matrices["Null_Noise"][:, f]
        
        # Skip if zero variance (padding features)
        if np.var(f_causal) < 1e-9 and np.var(f_spin) < 1e-9 and np.var(f_bec) < 1e-9:
            continue
            
        def single_feature_cka(arr1, arr2):
            if np.std(arr1) < 1e-9 or np.std(arr2) < 1e-9:
                return 0.0
            # Centered values
            a1 = arr1 - np.mean(arr1)
            a2 = arr2 - np.mean(arr2)
            denom = np.std(arr1) * np.std(arr2) * len(arr1)
            corr = np.dot(a1, a2) / (denom + 1e-15)
            return float(corr ** 2)
            
        # Compute real domain pair CKAs
        real_ckas = [
            single_feature_cka(f_causal, f_spin),
            single_feature_cka(f_causal, f_bec),
            single_feature_cka(f_spin, f_bec)
        ]
        mean_real_cka = np.mean(real_ckas)
        
        # Compute null CKA baselines
        null_ckas = [
            single_feature_cka(f_causal, f_null_er),
            single_feature_cka(f_spin, f_null_er),
            single_feature_cka(f_bec, f_null_noise)
        ]
        mean_null_cka = np.mean(null_ckas)
        std_null_cka = np.std(null_ckas) if len(null_ckas) > 1 else 0.0
        
        # Bootstrap feature CKA significance
        np.random.seed(42 + f)
        boot_real_ckas = []
        for _ in range(n_bootstrap):
            indices = np.random.choice(n_samples, size=n_samples, replace=True)
            b_causal, b_spin, b_bec = f_causal[indices], f_spin[indices], f_bec[indices]
            boot_real_ckas.append(np.mean([
                single_feature_cka(b_causal, b_spin),
                single_feature_cka(b_causal, b_bec),
                single_feature_cka(b_spin, b_bec)
            ]))
            
        alpha = (100.0 - ci) / 2.0
        ci_lower = np.percentile(boot_real_ckas, alpha)
        ci_upper = np.percentile(boot_real_ckas, 100.0 - alpha)
        
        # Threshold: CKA_real > CKA_null + 2 * std_null
        threshold = mean_null_cka + 2.0 * max(std_null_cka, 0.01)
        is_invariant = bool(mean_real_cka > threshold)
        
        sig_entry = {
            "mean_real_cka": mean_real_cka,
            "mean_null_cka": mean_null_cka,
            "null_std": std_null_cka,
            "threshold": threshold,
            "ci_95": (ci_lower, ci_upper),
            "is_invariant": is_invariant
        }
        significance_report[f"feature_{f}"] = sig_entry
        
        if is_invariant:
            invariants_candidates.append(f)
            
    print(f"Identified {len(invariants_candidates)} invariant candidates across domains: {invariants_candidates}")
    return invariants_candidates, cka_matrix, significance_report

if __name__ == "__main__":
    print("Testing Quantum Gravity Features script...")
    
    # 1. Quick feature extraction test from small tests
    df_causal = pd.read_csv("data/test_causal_layered.csv")
    df_spin = pd.read_csv("data/test_spin_network.csv")
    df_bec = pd.read_csv("data/test_bec_ensemble.csv")
    
    X_c = extract_features_from_causal_layered(df_causal)
    print(f"Causal Layered Graph feature matrix shape: {X_c.shape} (Expected: 5 x 88)")
    
    X_s = extract_features_from_spin_network(df_spin)
    print(f"Spin Network feature matrix shape: {X_s.shape} (Expected: 5 x 83)")
    
    X_b = extract_features_from_bec(df_bec)
    print(f"BEC Analog Flow feature matrix shape: {X_b.shape} (Expected: 5 x 76)")
    
    # 2. Unified dataset construction test
    X_u, y_u = build_unified_qg_dataset(
        "data/test_causal_layered.csv",
        "data/test_spin_network.csv",
        "data/test_bec_ensemble.csv"
    )
    print(f"Unified feature matrix shape: {X_u.shape} (Expected: 25 x 88)")
    print(f"Unified labels shape: {y_u.shape}")
    
    # 3. Test Invariants search
    invars, cka, report = search_for_invariants(X_u, y_u, n_bootstrap=10)
    print("CKA pairwise matrix:")
    print(cka)
    print("Invariant Features discovered:")
    print(invars)
