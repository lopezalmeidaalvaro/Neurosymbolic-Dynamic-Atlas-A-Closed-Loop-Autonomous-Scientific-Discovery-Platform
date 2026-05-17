import sqlite3
import json
import numpy as np
import os
import sys

# Import computation logic from topology_miner_v2
sys.path.append(os.path.dirname(__file__))
from topology_miner_v2 import compute_embedding, lyapunov_map

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runs", "math_search.db")

def integrate_logistic_map_r(r):
    fn = lambda x: r * x * (1 - x)
    N = 20000; x = 0.4
    for _ in range(5000): x = fn(x)
    series = []
    for _ in range(N): x = fn(x); series.append(x)
    x_s = np.array(series[N // 5:])
    emb = compute_embedding(x_s, 1.0)
    emb["lyapunov_max"] = lyapunov_map(fn, 0.4)
    emb["r"] = r
    return emb

def main():
    conn = sqlite3.connect(DB_PATH)
    
    # Check if already generated
    count = conn.execute("SELECT COUNT(*) FROM structural_embeddings WHERE system_name='logistic_sweep'").fetchone()[0]
    if count > 0:
        print("Already generated.")
        return
        
    print("Generating logistic sweep...")
    r_vals = np.linspace(2.5, 4.0, 150)
    for r in r_vals:
        emb = integrate_logistic_map_r(r)
        
        # Replace NaNs
        for k in emb:
            if not np.isfinite(emb[k]):
                emb[k] = 0.0
                
        vals = [
            emb["lyapunov_max"], emb["spectral_entropy"], emb["dominant_frequency"],
            emb["variance"], emb["autocorr_decay"], emb["kurtosis"], emb["skewness"], emb["energy"]
        ]
        
        conn.execute("""
            INSERT INTO structural_embeddings
                (node_id, system_name, lyapunov_max, spectral_entropy,
                 dominant_frequency, variance, autocorr_decay, kurtosis,
                 skewness, energy, embedding_json)
            VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("logistic_sweep", *vals, json.dumps(emb)))
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()
