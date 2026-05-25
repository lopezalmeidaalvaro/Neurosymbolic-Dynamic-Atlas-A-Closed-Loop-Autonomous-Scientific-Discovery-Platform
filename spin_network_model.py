import os
import random
import numpy as np
import pandas as pd
import networkx as nx
from scipy import stats

# Ensure UTF-8 output encoding for Windows terminal
import sys
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

class SpinNetworkModel:
    """
    Modelo de red de espines simplificada inspirada en LQG/espuma de espines. 
    No implementa constraints de simplicidad ni amplitudes de transición completas.
    """
    def __init__(self, n_nodes=20, max_spin=5, seed=42):
        self.n_nodes = n_nodes
        self.max_spin = max_spin
        self.seed = seed

    def generate(self) -> nx.Graph:
        """
        Generates the spin network graph (Barabási-Albert model) with 'spin' attributes on edges.
        """
        np.random.seed(self.seed)
        random.seed(self.seed)
        
        # Use Barabási-Albert model with m=2 to ensure a connected scale-free structure
        G = nx.barabasi_albert_graph(self.n_nodes, m=2, seed=self.seed)
        
        # Assign integer spin j in [1, max_spin] to each edge
        for u, v in G.edges:
            G.edges[u, v]['spin'] = int(random.randint(1, self.max_spin))
            
        return G

    def compute_nodal_areas(self, G) -> np.ndarray:
        """
        Computes nodal area for all nodes. Area(v) = sum_{e ~ v} sqrt(j_e(j_e + 1)).
        """
        areas = np.zeros(len(G.nodes))
        for u in G.nodes:
            area_val = 0.0
            for v in G.neighbors(u):
                j = G.edges[u, v]['spin']
                area_val += np.sqrt(j * (j + 1))
            areas[u] = area_val
        return areas

    def compute_boundary_area(self, G, boundary_nodes) -> float:
        """
        Computes the boundary area enclosing the given subset of nodes.
        Area = sum_{e in Cut} sqrt(j_e(j_e + 1))
        """
        boundary_nodes = set(boundary_nodes)
        cut_edges = nx.edge_boundary(G, boundary_nodes)
        
        area_val = 0.0
        for u, v in cut_edges:
            j = G.edges[u, v]['spin']
            area_val += np.sqrt(j * (j + 1))
            
        return float(area_val)

    def compute_entanglement_entropy(self, G, boundary_nodes) -> float:
        """
        Computes the entanglement entropy of the given boundary cut.
        S_ent = sum_{e in Cut} log(2 j_e + 1)
        """
        boundary_nodes = set(boundary_nodes)
        cut_edges = nx.edge_boundary(G, boundary_nodes)
        
        entropy_val = 0.0
        for u, v in cut_edges:
            j = G.edges[u, v]['spin']
            entropy_val += np.log(2 * j + 1)
            
        return float(entropy_val)

    def generate_ensemble(self, n_configs=100, n_nodes_range=(10, 50)) -> pd.DataFrame:
        """
        Generates an ensemble of spin networks, selecting random contiguous regions to evaluate holography.
        """
        np.random.seed(self.seed)
        random.seed(self.seed)
        
        results = []
        for c in range(n_configs):
            n_nodes = random.randint(*n_nodes_range)
            
            # Create instance and generate graph
            model = SpinNetworkModel(n_nodes=n_nodes, max_spin=self.max_spin, seed=self.seed + c)
            G = model.generate()
            
            # Pick a contiguous region using BFS from a random node
            start_node = random.choice(list(G.nodes))
            depth = random.randint(1, max(1, n_nodes // 4))
            
            boundary_nodes = set([start_node])
            current_layer = [start_node]
            for _ in range(depth):
                next_layer = []
                for u in current_layer:
                    next_layer.extend([w for w in G.neighbors(u) if w not in boundary_nodes])
                boundary_nodes.update(next_layer)
                current_layer = next_layer
                if not current_layer:
                    break
                    
            # Compute holography metrics
            area = model.compute_boundary_area(G, boundary_nodes)
            entropy = model.compute_entanglement_entropy(G, boundary_nodes)
            nodal_areas = model.compute_nodal_areas(G)
            
            results.append({
                "config_id": c,
                "n_nodes": n_nodes,
                "n_edges": len(G.edges),
                "region_size": len(boundary_nodes),
                "boundary_area": area,
                "entanglement_entropy": entropy,
                "mean_nodal_area": float(np.mean(nodal_areas)),
                "std_nodal_area": float(np.std(nodal_areas))
            })
            
        return pd.DataFrame(results)

def generate_spin_network_dataset(n_configs=500, output_path="data/spin_network_ensemble.csv") -> pd.DataFrame:
    """
    Generates a spin network dataset of 500 configs and saves it to a CSV.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    model = SpinNetworkModel(n_nodes=30, max_spin=5, seed=42)
    df = model.generate_ensemble(n_configs=n_configs)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated spin network dataset and saved to: {output_path}")
    return df

def verify_area_entropy_scaling(df) -> dict:
    """
    Computes linear regression between boundary area and entanglement entropy,
    along with a 95% bootstrap confidence interval of the slope.
    """
    areas = df["boundary_area"].values
    entropies = df["entanglement_entropy"].values
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(areas, entropies)
    r_squared = r_value ** 2
    
    # 95% Bootstrap CI of the slope
    np.random.seed(42)
    n_samples = len(df)
    bootstrap_slopes = []
    
    for _ in range(1000):
        indices = np.random.choice(n_samples, size=n_samples, replace=True)
        boot_areas = areas[indices]
        boot_entropies = entropies[indices]
        
        # Fit regression if we have variance
        if np.var(boot_areas) > 1e-8:
            b_slope, _, _, _, _ = stats.linregress(boot_areas, boot_entropies)
            bootstrap_slopes.append(b_slope)
            
    ci_lower = np.percentile(bootstrap_slopes, 2.5) if len(bootstrap_slopes) > 0 else slope
    ci_upper = np.percentile(bootstrap_slopes, 97.5) if len(bootstrap_slopes) > 0 else slope
    
    return {
        "r_squared": float(r_squared),
        "slope": float(slope),
        "intercept": float(intercept),
        "bootstrap_ci_95": (float(ci_lower), float(ci_upper))
    }

if __name__ == "__main__":
    print("Testing SpinNetworkModel...")
    model = SpinNetworkModel(n_nodes=20, max_spin=5, seed=42)
    G = model.generate()
    print(f"Generated graph with {len(G.nodes)} nodes and {len(G.edges)} edges.")
    
    nodal_areas = model.compute_nodal_areas(G)
    print(f"Mean nodal area: {np.mean(nodal_areas):.4f}")
    
    # Test cut
    cut_nodes = [0, 1, 2, 3]
    area = model.compute_boundary_area(G, cut_nodes)
    entropy = model.compute_entanglement_entropy(G, cut_nodes)
    print(f"Cut boundary area: {area:.4f} | Entanglement entropy: {entropy:.4f}")
    
    # Test scaling
    df = generate_spin_network_dataset(n_configs=20, output_path="data/test_spin_network.csv")
    scaling = verify_area_entropy_scaling(df)
    print("Area-Entropy Scaling parameters:")
    print(f"  R^2: {scaling['r_squared']:.4f}")
    print(f"  Slope: {scaling['slope']:.4f}")
    print(f"  Intercept: {scaling['intercept']:.4f}")
    print(f"  95% Bootstrap CI of Slope: {scaling['bootstrap_ci_95']}")
