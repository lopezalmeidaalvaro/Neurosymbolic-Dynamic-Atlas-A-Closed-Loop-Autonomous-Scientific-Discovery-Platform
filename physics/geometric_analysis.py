import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import scipy.spatial.distance as dist
import scipy.linalg as la
import scipy.optimize as opt
import networkx as nx
from sklearn.neighbors import kneighbors_graph
from topological_analysis import reconstruct_phase_space

# Ensure UTF-8 output encoding for Windows terminal
import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Try importing GraphRicciCurvature, otherwise use resilient pure-Python LP fallback
try:
    from GraphRicciCurvature.OllivierRicci import OllivierRicci
    RICCI_AVAILABLE = True
except ImportError:
    RICCI_AVAILABLE = False
    print(
        "  [GEOM WARNING] 'GraphRicciCurvature' not found. Using resilient pure-Python LP solver fallback."
    )

# Try importing Python Optimal Transport (POT) for fast Earth Mover's Distance
try:
    import ot
    HAS_POT = True
except ImportError:
    HAS_POT = False

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN A: CONSTRUCCIÓN DE GRAFOS DE VECINDAD
# ─────────────────────────────────────────────────────────────────────────────


def build_neighborhood_graph(point_cloud, k=10, method="knn"):
    """
    Builds a neighborhood graph from a point cloud.
    Edges are weighted by the Euclidean distance.
    """
    n_points, n_dims = point_cloud.shape
    G = nx.Graph()

    if n_points < 2:
        return G

    k = min(k, n_points - 1)

    if method == "knn":
        # Compute adjacency matrix using scikit-learn
        A = kneighbors_graph(
            point_cloud, n_neighbors=k, mode="distance", include_self=False
        )
        # Convert to NetworkX Graph
        G = nx.from_scipy_sparse_array(A)

        # Ensure graph is weighted with the exact Euclidean distance
        for u, v in G.edges():
            pos_u = point_cloud[u]
            pos_v = point_cloud[v]
            distance = float(np.linalg.norm(pos_u - pos_v))
            G[u][v]["weight"] = distance

    else:  # Radius-based neighborhood
        dists = dist.squareform(dist.pdist(point_cloud))
        # Median of 5-NN distances as adaptive radius
        sorted_dists = np.sort(dists, axis=1)
        r = float(np.median(sorted_dists[:, min(5, n_points - 1)]))

        for i in range(n_points):
            for j in range(i + 1, n_points):
                if dists[i, j] <= r:
                    G.add_edge(i, j, weight=float(dists[i, j]))

    # Ensure graph is fully connected (add minimum spanning tree edges if disconnected)
    if not nx.is_connected(G) and n_points > 1:
        # Build complete distance graph for MST
        complete_G = nx.Graph()
        dists = dist.squareform(dist.pdist(point_cloud))
        for i in range(n_points):
            for j in range(i + 1, n_points):
                complete_G.add_edge(i, j, weight=float(dists[i, j]))
        mst = nx.minimum_spanning_tree(complete_G)
        G.add_edges_from(mst.edges(data=True))

    return G


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN B: CURVATURA DE OLLIVIER-RICCI
# ─────────────────────────────────────────────────────────────────────────────


def _pure_python_ollivier_ricci_fallback(G):
    """
    Resilient, pure-Python Ollivier-Ricci curvature solver using shortest paths
    and linear programming transportation (Earth Mover's Distance) via scipy.optimize.linprog.
    Eliminates all native Optimal Transport compiler issues.
    """
    # Clone graph
    G_ricci = G.copy()

    # Calculate all-pairs shortest paths for transportation cost
    # (Using weights or hops; geodetic distance in graph space)
    lengths = dict(nx.all_pairs_dijkstra_path_length(G, weight="weight"))

    for u, v in G_ricci.edges():
        # 1. Define local distributions m_u and m_v over nodes
        # Uniform distributions on neighbors + self
        neighbors_u = list(G.neighbors(u)) + [u]
        neighbors_v = list(G.neighbors(v)) + [v]

        du = len(neighbors_u)
        dv = len(neighbors_v)

        # Probability vectors
        mu = np.ones(du) / du
        mv = np.ones(dv) / dv

        # 2. Build cost matrix (geodetic distances between u's neighbors and v's neighbors)
        cost_matrix = np.zeros((du, dv))
        for i, node_u in enumerate(neighbors_u):
            for j, node_v in enumerate(neighbors_v):
                # Retrieve precomputed shortest path length
                cost_matrix[i, j] = float(lengths.get(node_u, {}).get(node_v, 1.0))

        # 3. Solve exact Optimal Transport using POT if available (extremely fast!), else scipy.optimize.linprog
        _used_pot = False
        if HAS_POT:
            try:
                emd = float(ot.emd2(mu, mv, cost_matrix))
                _used_pot = True
            except Exception:
                pass

        if not _used_pot:
            # Equality constraints
            A_eq = []
            b_eq = []

            # Row constraints (sum over columns = mu_i)
            for i in range(du):
                row = np.zeros((du, dv))
                row[i, :] = 1.0
                A_eq.append(row.flatten())
                b_eq.append(mu[i])

            # Col constraints (sum over rows = mv_j)
            for j in range(dv):
                col = np.zeros((du, dv))
                col[:, j] = 1.0
                A_eq.append(col.flatten())
                b_eq.append(mv[j])

            c = cost_matrix.flatten()
            res = opt.linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, 1), method="highs")
            emd = float(res.fun) if res.success else float(np.mean(cost_matrix))

        # 4. Ollivier-Ricci Curvature: k = 1 - EMD(m_u, m_v) / d(u, v)
        edge_dist = G_ricci[u][v].get("weight", 1.0)
        if edge_dist > 0.0:
            k = 1.0 - (emd / edge_dist)
        else:
            k = 0.0

        G_ricci[u][v]["ricciCurvature"] = k

    return G_ricci


def compute_ollivier_ricci_curvature(G):
    """
    Computes Ollivier-Ricci curvature for each edge of G.
    Falls back gracefully to our pure-Python LP transportation solver if GraphRicciCurvature is offline.
    """
    if len(G) < 2:
        return G

    if RICCI_AVAILABLE:
        try:
            # We clone the graph to avoid side effects
            G_ricci = G.copy()
            # Initialize Ollivier-Ricci calculator
            orc = OllivierRicci(G_ricci, alpha=0.5, method="Sinkhorn", verbose="ERROR")
            orc.compute_ricci_curvature()
            return orc.G
        except Exception as e:
            print(
                f"  [GEOM ERROR] GraphRicciCurvature failed ({e}). Bypassing to fallback..."
            )

    # Resilient pure-Python LP fallback
    return _pure_python_ollivier_ricci_fallback(G)


def compute_node_curvature(G_with_curvature):
    """
    Aggregates edge curvatures to compute nodal curvatures (average of incident edges).
    """
    n_nodes = len(G_with_curvature)
    node_curvatures = np.zeros(n_nodes)

    for node in G_with_curvature.nodes():
        incident_edges = G_with_curvature.edges(node)
        if incident_edges:
            curvs = [
                G_with_curvature[u][v].get("ricciCurvature", 0.0)
                for u, v in incident_edges
            ]
            node_curvatures[node] = float(np.mean(curvs))
        else:
            node_curvatures[node] = 0.0

    return node_curvatures


def compute_curvature_statistics(node_curvatures):
    """
    Extracts statistical descriptors of the manifold's curvature.
    """
    from scipy.stats import skew, kurtosis

    if len(node_curvatures) == 0:
        return {
            "mean": 0.0,
            "variance": 0.0,
            "skewness": 0.0,
            "kurtosis": 0.0,
            "min": 0.0,
            "max": 0.0,
        }

    return {
        "mean": float(np.mean(node_curvatures)),
        "variance": float(np.var(node_curvatures)),
        "skewness": float(skew(node_curvatures)) if len(node_curvatures) > 2 else 0.0,
        "kurtosis": (
            float(kurtosis(node_curvatures)) if len(node_curvatures) > 2 else 0.0
        ),
        "min": float(np.min(node_curvatures)),
        "max": float(np.max(node_curvatures)),
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN C: LAPLACE-BELTRAMI OPERATOR
# ─────────────────────────────────────────────────────────────────────────────


def compute_laplacian_eigenmap(point_cloud, n_components=10, k=10):
    """
    Computes normalised Laplace-Beltrami Graph Laplacian eigenvalues and eigenvectors.
    L = D^{-1/2} (D - W) D^{-1/2}
    """
    n_points, n_dims = point_cloud.shape
    n_components = min(n_components, n_points - 1)

    if n_points < 3:
        return np.zeros(n_components), np.zeros((n_points, n_components))

    # 1. Build Similarity Weight Matrix (Gaussian similarity weights based on Euclidean distance)
    # W_ij = exp(-d_ij^2 / 2*sigma^2)
    dists = dist.squareform(dist.pdist(point_cloud))
    sigma = np.median(dists)
    if sigma == 0.0:
        sigma = 1.0

    W = np.exp(-(dists**2) / (2 * (sigma**2)))

    # Sparsify W using k-NN neighborhood mask
    G = build_neighborhood_graph(point_cloud, k=k)
    mask = np.zeros_like(W)
    for u, v in G.edges():
        mask[u, v] = 1.0
        mask[v, u] = 1.0
    np.fill_diagonal(mask, 1.0)
    W = W * mask

    # 2. Build Degree Matrix D
    D_vec = np.sum(W, axis=1)
    # Avoid division by zero
    D_vec[D_vec == 0.0] = 1.0

    # 3. Compute Normalized Laplacian L
    # L_ij = - W_ij / sqrt(D_i * D_j)
    D_inv_sqrt = 1.0 / np.sqrt(D_vec)
    L = np.eye(n_points) - (D_inv_sqrt[:, None] * W * D_inv_sqrt[None, :])

    # 4. Solve eigenvalues/eigenvectors
    try:
        # Use Hermite solver since L is symmetric
        eigenvalues, eigenvectors = la.eigh(L)
        # Sort ascending
        idx = np.argsort(eigenvalues)
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        # Take the top n_components eigenvalues/eigenvectors (skipping first trivial eigenvalue which is 0)
        return eigenvalues[1 : 1 + n_components], eigenvectors[:, 1 : 1 + n_components]
    except Exception as e:
        print(f"  [GEOM ERROR] Laplace-Beltrami solver failed ({e}). Returning zeros.")
        return np.zeros(n_components), np.zeros((n_points, n_components))


def compute_spectral_statistics(eigenvalues):
    """
    Computes spectral statistics: mean, variance, gap_ratio, and estimated spectral dimension.
    """
    if len(eigenvalues) < 2:
        return {
            "mean": 0.0,
            "variance": 0.0,
            "gap_ratio": 0.0,
            "spectral_dimension": 0.0,
        }

    # Gap ratio: median of differences of consecutive eigenvalues
    gaps = np.diff(eigenvalues)
    gap_ratio = float(np.median(gaps))

    # Spectral dimension d: estimated from power law scaling lambda_k ~ k^{2/d}
    # log(lambda_k) = const + (2/d) * log(k)
    # Slope of log(lambda_k) vs log(k) is 2/d => d = 2 / slope
    try:
        # Filter negative or zero values
        val_mask = eigenvalues > 1e-5
        if np.sum(val_mask) > 3:
            y = np.log(eigenvalues[val_mask])
            x = np.log(np.arange(1, len(y) + 1))
            slope, _ = np.polyfit(x, y, 1)
            spectral_dim = float(2.0 / slope) if slope > 0.05 else 0.0
        else:
            spectral_dim = 0.0
    except Exception:
        spectral_dim = 0.0

    return {
        "mean": float(np.mean(eigenvalues)),
        "variance": float(np.var(eigenvalues)),
        "gap_ratio": gap_ratio,
        "spectral_dimension": spectral_dim,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN D: GEOMETRIC DIFFUSION (DIFFUSION MAPS)
# ─────────────────────────────────────────────────────────────────────────────


def compute_diffusion_map(point_cloud, n_components=5, t=1, k=10):
    """
    Computes Diffusion Maps coordinates and transition eigenvalues.
    """
    n_points, n_dims = point_cloud.shape
    n_components = min(n_components, n_points - 2)

    if n_points < 5:
        return np.zeros((n_points, n_components)), np.zeros(n_components)

    # 1. Pairwise distance kernel K
    dists = dist.squareform(dist.pdist(point_cloud))

    # Adaptive epsilon: median of distance to the k-th neighbor
    sorted_dists = np.sort(dists, axis=1)
    k_val = min(k, n_points - 1)
    epsilon = float(np.median(sorted_dists[:, k_val]))
    if epsilon == 0.0:
        epsilon = 1.0

    K = np.exp(-(dists**2) / (epsilon**2))

    # 2. Re-normalization to normalize density effects
    # q_i = sum_j K_ij
    q = np.sum(K, axis=1)
    q[q == 0.0] = 1.0
    K_alpha = K / (q[:, None] * q[None, :])

    # 3. Transition Matrix P = D^{-1} K_alpha
    d = np.sum(K_alpha, axis=1)
    d[d == 0.0] = 1.0
    P = K_alpha / d[:, None]

    # 4. Compute right eigenvalues/eigenvectors of P
    try:
        # P is similar to a symmetric matrix, so eigenvalues are real
        eigenvalues, eigenvectors = la.eig(P)
        # Sort descending (real parts)
        idx = np.argsort(np.real(eigenvalues))[::-1]
        eigenvalues = np.real(eigenvalues[idx])
        eigenvectors = np.real(eigenvectors[:, idx])

        # First eigenvalue is always 1 (trivial constant eigenvector), skip it
        lambdas = eigenvalues[1 : 1 + n_components]
        psis = eigenvectors[:, 1 : 1 + n_components]

        # Calculate diffusion coordinates: psi_i * lambda_i^t
        diffusion_coords = psis * (lambdas**t)[None, :]
        return diffusion_coords, lambdas
    except Exception as e:
        print(f"  [GEOM ERROR] Diffusion Maps solver failed ({e}). Returning zeros.")
        return np.zeros((n_points, n_components)), np.zeros(n_components)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN E: PIPELINE GEOMÉTRICO CONSOLIDADO
# ─────────────────────────────────────────────────────────────────────────────


def extract_geometric_features(signal, emb_dim=3, lag=1, k=10):
    """
    Orchestrates the entire Geometrical and Intrinsic Curvature pipeline,
    returning a fixed 20D vector of manifold geometrical descriptors.
    Vector mapping:
      0-5  : Ollivier-Ricci [mean, var, skew, kurt, min, max]
      6-9  : Laplace-Beltrami Stats [mean, var, gap_ratio, spectral_dim]
      10-14: Laplace-Beltrami Eigenvalues [first 5 eigenvalues]
      15-19: Diffusion Maps Stats & Eigenvalues [mean_diff_coord, var_diff_coord, total_diffusion_energy, first 2 diff_lambdas]
    """
    feat_vector = np.full(20, np.nan)

    # 1. Reconstruct space
    point_cloud = reconstruct_phase_space(signal, emb_dim=emb_dim, lag=lag)
    if len(point_cloud) < 10:
        print(
            "  [GEOM WARNING] Signal too short to extract geometrical features. Returning NaNs."
        )
        return feat_vector

    # Downsample point cloud uniformly if too large to make pure-Python LP solver extremely fast
    if len(point_cloud) > 200:
        indices = np.linspace(0, len(point_cloud) - 1, 200, dtype=int)
        point_cloud = point_cloud[indices]

    try:
        # 2. Neighborhood Graph
        G = build_neighborhood_graph(point_cloud, k=k)

        # 3. Ollivier-Ricci Curvature
        G_ricci = compute_ollivier_ricci_curvature(G)
        node_curvs = compute_node_curvature(G_ricci)
        ricci_stats = compute_curvature_statistics(node_curvs)

        feat_vector[0] = ricci_stats["mean"]
        feat_vector[1] = ricci_stats["variance"]
        feat_vector[2] = ricci_stats["skewness"]
        feat_vector[3] = ricci_stats["kurtosis"]
        feat_vector[4] = ricci_stats["min"]
        feat_vector[5] = ricci_stats["max"]

        # 4. Laplace-Beltrami spectrum
        lb_eigs, _ = compute_laplacian_eigenmap(point_cloud, n_components=10, k=k)
        lb_stats = compute_spectral_statistics(lb_eigs)

        feat_vector[6] = lb_stats["mean"]
        feat_vector[7] = lb_stats["variance"]
        feat_vector[8] = lb_stats["gap_ratio"]
        feat_vector[9] = lb_stats["spectral_dimension"]

        # Fill first 5 eigenvalues (pad with 0 if fewer than 5)
        for i in range(5):
            feat_vector[10 + i] = float(lb_eigs[i]) if i < len(lb_eigs) else 0.0

        # 5. Diffusion Maps
        diff_coords, diff_lambdas = compute_diffusion_map(
            point_cloud, n_components=5, t=1, k=k
        )

        feat_vector[15] = float(np.mean(diff_coords)) if len(diff_coords) > 0 else 0.0
        feat_vector[16] = float(np.var(diff_coords)) if len(diff_coords) > 0 else 0.0
        feat_vector[17] = (
            float(np.sum(diff_lambdas**2)) if len(diff_lambdas) > 0 else 0.0
        )
        feat_vector[18] = float(diff_lambdas[0]) if len(diff_lambdas) > 0 else 0.0
        feat_vector[19] = float(diff_lambdas[1]) if len(diff_lambdas) > 1 else 0.0

    except Exception as e:
        print(f"  [GEOM ERROR] Failed to run geometrical feature pipeline: {e}")

    return feat_vector
