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

class CausalLayeredGraphModel:
    """
    Modelo de grafo causal por capas inspirado en Causal Dynamical Triangulations. 
    No implementa simplices causales, movimientos de Pachner ni muestreo Monte Carlo; es una aproximación 
    fenomenológica para estudios exploratorios de espacio-tiempo emergente.
    """
    def __init__(self, N_slices=10, N_vertices_per_slice=100, p_intra=0.3, p_inter=0.5, seed=42):
        self.N_slices = N_slices
        self.N_vertices_per_slice = N_vertices_per_slice
        self.p_intra = p_intra
        self.p_inter = p_inter
        self.seed = seed

    def generate(self) -> nx.Graph:
        """
        Generates the layered graph. Each node has a 'slice' attribute.
        """
        np.random.seed(self.seed)
        random.seed(self.seed)
        G = nx.Graph()

        # 1. Create nodes and assign slice attributes
        total_nodes = self.N_slices * self.N_vertices_per_slice
        for u in range(total_nodes):
            s = u // self.N_vertices_per_slice
            G.add_node(u, slice=int(s))

        # 2. Add intra-slice edges (Erdos-Renyi on each slice)
        for s in range(self.N_slices):
            slice_nodes = list(range(s * self.N_vertices_per_slice, (s + 1) * self.N_vertices_per_slice))
            for i in range(len(slice_nodes)):
                for j in range(i + 1, len(slice_nodes)):
                    if random.random() < self.p_intra:
                        G.add_edge(slice_nodes[i], slice_nodes[j])

        # 3. Add inter-slice edges between s and s+1
        for s in range(self.N_slices - 1):
            slice_current = list(range(s * self.N_vertices_per_slice, (s + 1) * self.N_vertices_per_slice))
            slice_next = list(range((s + 1) * self.N_vertices_per_slice, (s + 2) * self.N_vertices_per_slice))
            for u in slice_current:
                for v in slice_next:
                    if random.random() < self.p_inter:
                        G.add_edge(u, v)

        return G

    def compute_spatial_volume_profile(self, G) -> np.ndarray:
        """
        Computes the volume of each slice (count of connected nodes in the slice).
        """
        profile = np.zeros(self.N_slices)
        for node in G.nodes:
            s = G.nodes[node]['slice']
            # Only count nodes that have at least one connection
            if G.degree(node) > 0:
                profile[s] += 1
        return profile

    def compute_spectral_dimension(self, G, t_max=10) -> float:
        """
        Computes the spectral dimension d_s of the graph using a random walk return probability decay.
        """
        nodes = list(G.nodes)
        N = len(nodes)
        if N == 0:
            return 0.0

        # Construct transition probability matrix P = D^-1 * A (with self-loops to make it lazy and non-bipartite)
        A = nx.to_numpy_array(G)
        A_loops = A + np.eye(N)
        degrees = np.sum(A_loops, axis=1)
        
        # Avoid division by zero for isolated nodes
        inv_degrees = np.zeros_like(degrees)
        inv_degrees[degrees > 0] = 1.0 / degrees[degrees > 0]
        
        P = np.diag(inv_degrees) @ A_loops

        # Trace probability decay
        P_power = np.eye(N)
        ret_prob = []
        
        for t in range(1, t_max + 1):
            P_power = P_power @ P
            avg_ret = np.trace(P_power) / N
            ret_prob.append(max(avg_ret, 1e-15))

        # Fit log(P_ret(t)) vs log(t) to get slope.
        # P_ret(t) ~ t^(-d_s/2) => log(P_ret) = -d_s/2 * log(t) + C
        t_vals = np.arange(1, t_max + 1)
        slope, _ = np.polyfit(np.log(t_vals), np.log(ret_prob), 1)
        
        d_s = -2.0 * slope
        return float(d_s)

    def compute_ricci_curvature_profile(self, G) -> dict:
        """
        Computes a stable self-contained curvature profile for the nodes.
        Curvature scales with clustering (positive) and degree density (negative).
        """
        triangles = nx.triangles(G)
        curvature = {}
        N = len(G.nodes)
        
        for u in G.nodes:
            deg = G.degree(u)
            if deg <= 1:
                curvature[u] = -1.0 # Isolated or endpoint has negative curvature
            else:
                clustering = 2.0 * triangles[u] / (deg * (deg - 1))
                # Curvature decreases with high degree (hyperbolic scaling) and increases with clustering
                curvature[u] = float(2.0 * clustering - 0.2 * deg / N)

        curvature_by_slice = []
        for s in range(self.N_slices):
            slice_nodes = [n for n in G.nodes if G.nodes[n]['slice'] == s]
            if len(slice_nodes) > 0:
                curvs = [curvature[n] for n in slice_nodes]
                curvature_by_slice.append(float(np.mean(curvs)))
            else:
                curvature_by_slice.append(0.0)

        mean_curvature = float(np.mean(list(curvature.values()))) if N > 0 else 0.0
        
        return {
            "mean_curvature": mean_curvature,
            "curvature_by_slice": curvature_by_slice
        }

    def simulate_ensemble(self, n_configs=100, p_intra_range=(0.1, 0.9), p_inter_range=(0.1, 0.9)) -> pd.DataFrame:
        """
        Simulates an ensemble of causal layered graphs with varying p_intra and p_inter.
        """
        np.random.seed(self.seed)
        random.seed(self.seed)
        
        results = []
        for c in range(n_configs):
            p_intra = random.uniform(*p_intra_range)
            p_inter = random.uniform(*p_inter_range)
            
            # Create instance and generate graph
            model = CausalLayeredGraphModel(
                N_slices=self.N_slices,
                N_vertices_per_slice=self.N_vertices_per_slice,
                p_intra=p_intra,
                p_inter=p_inter,
                seed=self.seed + c
            )
            G = model.generate()
            
            # Compute stats
            d_s = model.compute_spectral_dimension(G, t_max=10)
            curv_dict = model.compute_ricci_curvature_profile(G)
            vol_profile = model.compute_spatial_volume_profile(G)
            
            res_dict = {
                "config_id": c,
                "p_intra": p_intra,
                "p_inter": p_inter,
                "spectral_dimension": d_s,
                "mean_curvature": curv_dict["mean_curvature"],
                "mean_volume": float(np.mean(vol_profile)),
                "std_volume": float(np.std(vol_profile)),
            }
            # Add spatial volume profile values as individual columns
            for s in range(self.N_slices):
                res_dict[f"vol_slice_{s}"] = float(vol_profile[s])
                
            results.append(res_dict)
            
        return pd.DataFrame(results)

def generate_causal_layered_dataset(n_configs=500, output_path="data/causal_layered_ensemble.csv") -> pd.DataFrame:
    """
    Generates a causal layered dataset of 500 configs and saves it to a CSV.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Using 5 slices and 50 nodes per slice to ensure extremely fast simulation under standard budgets
    model = CausalLayeredGraphModel(N_slices=5, N_vertices_per_slice=50, seed=42)
    df = model.simulate_ensemble(n_configs=n_configs)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated causal layered dataset and saved to: {output_path}")
    return df

if __name__ == "__main__":
    print("Testing CausalLayeredGraphModel...")
    model = CausalLayeredGraphModel(N_slices=5, N_vertices_per_slice=30, p_intra=0.3, p_inter=0.5, seed=42)
    G = model.generate()
    
    print(f"Generated graph with {len(G.nodes)} nodes and {len(G.edges)} edges.")
    vol = model.compute_spatial_volume_profile(G)
    print(f"Volume profile: {vol}")
    
    d_s = model.compute_spectral_dimension(G)
    print(f"Spectral dimension: {d_s:.4f}")
    
    curv = model.compute_ricci_curvature_profile(G)
    print(f"Mean curvature: {curv['mean_curvature']:.4f}")
    print(f"Curvature by slice: {curv['curvature_by_slice']}")
    
    # Generate a small dataset
    df = generate_causal_layered_dataset(n_configs=5, output_path="data/test_causal_layered.csv")
    print(df.head())
