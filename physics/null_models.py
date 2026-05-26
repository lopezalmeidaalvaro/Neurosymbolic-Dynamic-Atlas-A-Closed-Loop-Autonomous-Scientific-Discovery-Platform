import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import os
import random
import numpy as np
import pandas as pd
import networkx as nx

# Ensure UTF-8 output encoding for Windows terminal
import sys
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Import the 68D EV3 feature extractor
from core.autonomous.latent_snapshot_exporter import extract_ev3_deep

class NullModels:
    """
    Modelos nulos para control científico: si una propiedad aparece también en estos modelos, 
    no puede atribuirse a estructura física emergente.
    """
    pass

def generate_erdos_renyi_null(n_configs=100, n_nodes=100, p=0.1, seed=42) -> pd.DataFrame:
    """
    Generates Erdős-Rényi random graphs (no causal or layered structure).
    Computes spectral dimension, curvature, and volume profile metrics for control.
    """
    np.random.seed(seed)
    random.seed(seed)
    
    N_slices = 5
    results = []
    
    for c in range(n_configs):
        G = nx.fast_gnp_random_graph(n_nodes, p, seed=seed + c)
        
        # Assign random slice attribute (artificial slices)
        for u in G.nodes:
            G.nodes[u]['slice'] = int(random.randint(0, N_slices - 1))
            
        # 1. Compute volume profile
        vol_profile = np.zeros(N_slices)
        for u in G.nodes:
            s = G.nodes[u]['slice']
            if G.degree(u) > 0:
                vol_profile[s] += 1
                
        # 2. Compute spectral dimension (using lazy self-loop random walks)
        N = len(G.nodes)
        d_s = 0.0
        if N > 0:
            A = nx.to_numpy_array(G)
            A_loops = A + np.eye(N)
            degrees = np.sum(A_loops, axis=1)
            inv_degrees = np.zeros_like(degrees)
            inv_degrees[degrees > 0] = 1.0 / degrees[degrees > 0]
            P = np.diag(inv_degrees) @ A_loops
            
            P_power = np.eye(N)
            ret_prob = []
            t_max = 10
            for t in range(1, t_max + 1):
                P_power = P_power @ P
                avg_ret = np.trace(P_power) / N
                ret_prob.append(max(avg_ret, 1e-15))
                
            t_vals = np.arange(1, t_max + 1)
            slope, _ = np.polyfit(np.log(t_vals), np.log(ret_prob), 1)
            d_s = -2.0 * slope

        # 3. Compute curvature profile
        triangles = nx.triangles(G)
        curvature = {}
        for u in G.nodes:
            deg = G.degree(u)
            if deg <= 1:
                curvature[u] = -1.0
            else:
                clustering = 2.0 * triangles[u] / (deg * (deg - 1))
                curvature[u] = float(2.0 * clustering - 0.2 * deg / N)
                
        mean_curv = float(np.mean(list(curvature.values()))) if N > 0 else 0.0
        
        res_dict = {
            "config_id": c,
            "spectral_dimension": float(d_s),
            "mean_curvature": mean_curv,
            "mean_volume": float(np.mean(vol_profile)),
            "std_volume": float(np.std(vol_profile))
        }
        for s in range(N_slices):
            res_dict[f"vol_slice_{s}"] = float(vol_profile[s])
            
        results.append(res_dict)
        
    return pd.DataFrame(results)

def generate_colored_noise_null(n_configs=100, length=1000, beta=1.0, seed=42) -> np.ndarray:
    """
    Generates 1/f^beta colored noise using frequency filtering, and extracts
    the 68D EV3_DEEP features for each config.
    """
    np.random.seed(seed)
    random.seed(seed)
    
    features_ensemble = []
    
    for c in range(n_configs):
        # 1. White noise baseline
        white = np.random.normal(0, 1, length)
        fft_vals = np.fft.fft(white)
        frequencies = np.fft.fftfreq(length)
        
        # 2. Apply frequency power-law filter S(f) ~ f^-beta
        # Avoid division by zero at DC component
        frequencies[0] = 1e-15
        filter_scale = np.abs(frequencies) ** (-beta / 2.0)
        
        filtered_fft = fft_vals * filter_scale
        # Invert to real-valued time-series
        colored = np.real(np.fft.ifft(filtered_fft))
        
        # 3. Standardize and extract 68D EV3 features
        colored = (colored - np.mean(colored)) / (np.std(colored) + 1e-15)
        
        try:
            feats = extract_ev3_deep(colored)
            # Ensure the feature vector is finite
            feats = np.array([float(f) if np.isfinite(f) else 0.0 for f in feats])
        except Exception as e:
            # Fallback if feature extraction fails
            feats = np.zeros(68)
            
        features_ensemble.append(feats)
        
    return np.array(features_ensemble)

def generate_degree_preserved_null(G, n_configs=100, seed=42) -> list:
    """
    Generates configurations of graphs with the exact same degrees as G but randomized edges
    using the configuration model or degree-preserving double edge swaps.
    """
    random.seed(seed)
    np.random.seed(seed)
    
    null_graphs = []
    num_edges = len(G.edges)
    
    # We run 2 * num_edges swaps for complete randomization
    n_swaps = 2 * num_edges
    
    for c in range(n_configs):
        G_null = G.copy()
        try:
            # Randomize edges while strictly preserving degrees
            nx.double_edge_swap(G_null, nswap=n_swaps, max_tries=n_swaps * 5, seed=seed + c)
        except Exception:
            # Fallback configuration model if swap fails
            degrees = [d for n, d in G.degree()]
            G_null = nx.configuration_model(degrees, seed=seed + c)
            G_null = nx.Graph(G_null) # Remove parallel edges/self-loops
            G_null.remove_edges_from(nx.selfloop_edges(G_null))
            
        null_graphs.append(G_null)
        
    return null_graphs

def compute_null_baseline(real_property, null_distribution, ci=95) -> dict:
    """
    Computes statistical significance metrics for a real measured property against
    the control null distribution baseline.
    """
    null_distribution = np.array(null_distribution)
    mu_null = np.mean(null_distribution)
    std_null = np.std(null_distribution)
    
    # Compute robust Z-score
    z_score = float((real_property - mu_null) / (std_null + 1e-15))
    
    # Empirical two-tailed p-value
    extreme_count = np.sum(np.abs(null_distribution - mu_null) >= np.abs(real_property - mu_null))
    p_value = float(extreme_count / len(null_distribution))
    
    # Confidence intervals
    alpha = (100.0 - ci) / 2.0
    ci_lower = float(np.percentile(null_distribution, alpha))
    ci_upper = float(np.percentile(null_distribution, 100.0 - alpha))
    
    is_significant = bool(p_value < 0.05)
    
    return {
        "is_significant": is_significant,
        "p_value": p_value,
        "z_score": z_score,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper
    }

if __name__ == "__main__":
    print("Testing NullModels...")
    
    # 1. Test ER Random null
    df_er = generate_erdos_renyi_null(n_configs=5, n_nodes=50, p=0.2, seed=42)
    print("Erdős-Rényi Nulls dataframe:")
    print(df_er.head())
    
    # 2. Test Colored noise null
    features = generate_colored_noise_null(n_configs=5, length=500, beta=1.0, seed=42)
    print(f"Colored noise feature matrix shape: {features.shape} (Expected: 5 x 68)")
    
    # 3. Test Degree preserved edge swaps
    G = nx.barabasi_albert_graph(20, 2, seed=42)
    null_graphs = generate_degree_preserved_null(G, n_configs=2, seed=42)
    print(f"Degree sequence G:      {sorted([d for n, d in G.degree()])}")
    print(f"Degree sequence null 0: {sorted([d for n, d in null_graphs[0].degree()])}")
    
    # 4. Test Significance calculation
    real_prop = 4.5
    null_dist = np.random.normal(0, 1.0, 1000)
    sig_test = compute_null_baseline(real_prop, null_dist)
    print("Significance check against null normal distribution:")
    print(f"  Real property value: {real_prop}")
    print(f"  Z-score:             {sig_test['z_score']:.4f}")
    print(f"  Empirical p-value:   {sig_test['p_value']:.4f}")
    print(f"  Significant (p<0.05): {sig_test['is_significant']}")
    print(f"  Null CI 95%:         ({sig_test['ci_lower']:.4f}, {sig_test['ci_upper']:.4f})")
