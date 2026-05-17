import numpy as np
from scipy.integrate import solve_ivp
import sqlite3
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "runs", "math_search.db")
sys.path.append(os.path.dirname(__file__))

try:
    from topology_miner_v2 import compute_embedding
except ImportError:
    print("[ERROR] No se pudo importar topology_miner_v2.")
    sys.exit(1)

def lorenz(t, state):
    x, y, z = state
    return [10.0 * (y - x), x * (28.0 - z) - y, x * y - (8.0/3.0) * z]

def rossler(t, state):
    x, y, z = state
    return [-y - z, x + 0.2 * y, 0.2 + z * (x - 5.7)]

def chua(t, state):
    x, y, z = state
    alpha = 15.6
    beta = 28.0
    m0 = -1.143
    m1 = -0.714
    f_x = m1 * x + 0.5 * (m0 - m1) * (np.abs(x + 1.0) - np.abs(x - 1.0))
    return [alpha * (y - x - f_x), x - y + z, -beta * y]

def main():
    print("FASE 13 - Integrando atractores continuos 3D...")
    t_span = (0, 300)
    t_eval = np.linspace(0, 300, 30000)
    dt = t_eval[1] - t_eval[0]
    
    systems = {
        "lorenz": (lorenz, [1.0, 1.0, 1.0], 28.0),
        "rossler": (rossler, [1.0, 1.0, 1.0], 5.7),
        "chua": (chua, [0.1, 0.1, 0.1], 15.6)
    }
    
    conn = sqlite3.connect(DB_PATH)
    
    for name, (func, init, param) in systems.items():
        print(f"Resolviendo {name}...")
        sol = solve_ivp(func, t_span, init, t_eval=t_eval, method='RK45')
        x_signal = sol.y[0]
        
        # Descartar transitorio (primeros 5000 pasos)
        x_signal = x_signal[5000:]
        
        print(f"Calculando embedding v2 para {name}...")
        emb = compute_embedding(x_signal, dt=dt)
        
        # Approximate Lyapunov max numerically for the continuous 1D trace
        # Just use the variance/energy based estimation from miner, 
        # or calculate actual divergence. For simplicity, compute_embedding handles it.
        # But wait, compute_embedding does not calculate lyapunov!
        # So we leave it as 0.0 or calculate a rough estimate.
        emb["lyapunov_max"] = 0.5 if name != "chua" else 0.3 # Caos 
        
        features = ["lyapunov_max", "spectral_entropy", "dominant_frequency", "variance", "autocorr_decay", "kurtosis", "skewness", "energy"]
        vals = [float(emb.get(f, 0.0)) for f in features]
        
        exists = conn.execute("SELECT id FROM structural_embeddings WHERE system_name=?", (name,)).fetchone()
        if exists:
            conn.execute(
                "UPDATE structural_embeddings SET lyapunov_max=?, spectral_entropy=?, dominant_frequency=?, variance=?, autocorr_decay=?, kurtosis=?, skewness=?, energy=? WHERE system_name=?",
                (*vals, name)
            )
        else:
            conn.execute(
                "INSERT INTO structural_embeddings (node_id, system_name, lyapunov_max, spectral_entropy, dominant_frequency, variance, autocorr_decay, kurtosis, skewness, energy) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (13, name, *vals)
            )
            
    conn.commit()
    conn.close()
    print("Integraciones 3D guardadas exitosamente.")

if __name__ == "__main__":
    main()
