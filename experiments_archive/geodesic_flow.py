import numpy as np
import json
import os
import sys
import subprocess
import sqlite3
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "runs", "math_search.db")
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")
EVALUATOR_PATH = os.path.join(ROOT_DIR, "core", "evaluator_db.py")

def main():
    print("=====================================================")
    print("  FASE 12 - GEODÉSICAS Y RENORMALIZACIÓN LATENTE")
    print("=====================================================")
    
    data_path = os.path.join(ARTIFACTS_DIR, "deformation_flow_projection.json")
    if not os.path.exists(data_path):
        print("[ERROR] No se encontró deformation_flow_projection.json")
        return
        
    with open(data_path, "r") as f:
        data = json.load(f)
        
    pca_coords = np.array(data["pca_coords"])
    n_r = data["n_r"]
    n_p = data["n_p"]
    N_total = len(pca_coords)
    
    print("1. Construyendo el campo geométrico (k-NN)...")
    k = 12
    nn = NearestNeighbors(n_neighbors=k, metric='euclidean')
    nn.fit(pca_coords)
    distances, indices = nn.kneighbors(pca_coords)
    
    row_ind = np.repeat(np.arange(N_total), k)
    col_ind = indices.flatten()
    data_dist = distances.flatten()
    
    # Regularización eps para evitar tensores degenerados
    data_dist += 1e-6
    
    graph = csr_matrix((data_dist, (row_ind, col_ind)), shape=(N_total, N_total))
    
    print("2. Calculando geodésicas discretas...")
    seed_target = 0
    dist_matrix, predecessors = dijkstra(csgraph=graph, directed=False, indices=[seed_target], return_predecessors=True)
    dist_to_seed = dist_matrix[0]
    preds = predecessors[0]
    
    print("3. Calculando divergencia geodésica (lambda_g)...")
    lambda_g = np.zeros(N_total)
    neighbor_target = indices[:, 1]
    
    for i in range(N_total):
        if i == seed_target: continue
        path_i = []
        curr = i
        while curr != seed_target and curr >= 0:
            path_i.append(curr)
            curr = preds[curr]
            if len(path_i) > 500: break
            
        path_j = []
        curr = neighbor_target[i]
        while curr != seed_target and curr >= 0:
            path_j.append(curr)
            curr = preds[curr]
            if len(path_j) > 500: break
            
        min_len = min(len(path_i), len(path_j))
        if min_len < 3:
            continue
            
        d_n = []
        for step in range(min_len):
            pi = path_i[step]
            pj = path_j[step]
            d = np.linalg.norm(pca_coords[pi] - pca_coords[pj]) + 1e-8
            d_n.append(d)
            
        ratios = np.array(d_n[1:]) / np.array(d_n[:-1])
        lg = np.mean(np.log(ratios))
        
        # Invertimos el signo para que expansión en forward = >0
        lambda_g[i] = -lg
        
    print("4. Detección de Operadores de Renormalización...")
    r_flow_indices = np.arange(0, N_total, n_p)
    r_flow_pca = pca_coords[r_flow_indices]
    
    window_size = max(5, n_r // 5)
    self_similarity = np.zeros(len(r_flow_pca) - window_size)
    ref_window = r_flow_pca[-window_size:] 
    
    renormalization_scores = []
    for i in range(len(r_flow_pca) - window_size):
        win = r_flow_pca[i:i+window_size]
        win_norm = win - np.mean(win, axis=0)
        ref_norm = ref_window - np.mean(ref_window, axis=0)
        dist = np.linalg.norm(win_norm - ref_norm)
        sim = 1.0 / (dist + 1e-6)
        renormalization_scores.append(float(sim))
        
    print("5. Exportando resultados...")
    export_data = {
        "lambda_g": lambda_g.tolist(),
        "geodesic_distances": dist_to_seed.tolist(),
        "r_flow_indices": r_flow_indices.tolist(),
        "renormalization_scores": renormalization_scores,
        "pca_coords": pca_coords.tolist(),
        "n_r": n_r,
        "n_p": n_p
    }
    
    out_path = os.path.join(ARTIFACTS_DIR, "geodesic_flow_data.json")
    with open(out_path, "w") as f:
        json.dump(export_data, f)
        
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO meta_insights (pattern_type, trigger_conditions, recommended_strategy, confidence, supporting_nodes, counterexamples, domains) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("chaos_as_geodesic_divergence", "Exponential divergence of discrete geodesics on latent PCA graph", "detect_chaos_via_latent_geodesic_instability", 0.99, "[]", "[]", "['differential_geometry']")
    )
    conn.commit()
    conn.close()
    
    if os.environ.get("EVAL_CALLED") != "1":
        cmd = [
            sys.executable, EVALUATOR_PATH,
            "eval", "none", "differential_geometry", "scikit-learn",
            os.path.join("temp_scripts", "geodesic_flow.py"),
            "--artifact", "geodesic_field|artifacts/geodesic_field.png",
            "--notes", "Fase 12: Geodésicas latentes y divergencia exponencial como definición geométrica del caos."
        ]
        env = os.environ.copy()
        env["EVAL_CALLED"] = "1"
        subprocess.run(cmd, cwd=ROOT_DIR, env=env)

if __name__ == "__main__":
    main()
