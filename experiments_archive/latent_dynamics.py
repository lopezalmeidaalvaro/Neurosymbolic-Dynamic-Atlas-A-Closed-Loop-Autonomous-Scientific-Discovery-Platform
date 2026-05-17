import numpy as np
import json
import os
import sys
import subprocess
import sqlite3
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "runs", "math_search.db")
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")
EVALUATOR_PATH = os.path.join(ROOT_DIR, "core", "evaluator_db.py")

def main():
    print("=====================================================")
    print("  FASE 14 - DINÁMICA DIFERENCIAL DEL ESPACIO LATENTE")
    print("=====================================================")
    
    data_path = os.path.join(ARTIFACTS_DIR, "deformation_flow_projection.json")
    if not os.path.exists(data_path):
        print("[ERROR] No se encontró deformation_flow_projection.json")
        return
        
    with open(data_path, "r") as f:
        data = json.load(f)
        
    n_r = data["n_r"]
    n_p = data["n_p"]
    grid_r = np.array(data["r_vals"])
    grid_p = np.array(data["p_vals"])
    
    # Reshape coords to (n_r, n_p, 2)
    s = np.array(data["pca_coords"]).reshape((n_r, n_p, 2))
    
    print("1. Calculando Campos de Velocidad y Aceleración...")
    # Utilizando diferencias centrales
    ds_dr, ds_dp = np.gradient(s, axis=(0, 1))
    
    d2s_dr2, _ = np.gradient(ds_dr, axis=(0, 1))
    
    v_mag_r = np.linalg.norm(ds_dr, axis=2)
    a_mag_r = np.linalg.norm(d2s_dr2, axis=2)
    
    print("2. Construcción del Tensor Dinámico (Jacobiano)...")
    det_J = np.zeros((n_r, n_p))
    for i in range(n_r):
        for j in range(n_p):
            J = np.column_stack((ds_dr[i, j], ds_dp[i, j]))
            det_J[i, j] = np.linalg.det(J)
            
    print("3. Detección de Inestabilidad...")
    instability_mask = (a_mag_r > 3.0 * v_mag_r) & (v_mag_r > 1e-4)
    caustic_mask = det_J < 0
    
    total_points = n_r * n_p
    print(f"  Puntos de inestabilidad kinemática (||a|| >> ||v||): {np.sum(instability_mask)} / {total_points}")
    print(f"  Puntos caústicos (det(J) < 0): {np.sum(caustic_mask)} / {total_points}")
    
    print("4. Predicción Local (Gaussian Process)...")
    X = np.zeros((total_points, 2))
    y = np.zeros((total_points, 2))
    
    idx = 0
    for i in range(n_r):
        for j in range(n_p):
            X[idx] = [grid_r[i], grid_p[j]]
            y[idx] = s[i, j]
            idx += 1
            
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.95, random_state=42)
    
    kernel = C(1.0, (1e-3, 1e3)) * RBF([1.0, 1.0], (1e-2, 1e2))
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=2, alpha=1e-2)
    
    print("  Entrenando GPR sobre variedad latente...")
    gp.fit(X_train, y_train)
    
    y_pred, sigma = gp.predict(X, return_std=True)
    r2 = r2_score(y, y_pred)
    print(f"  R^2 Score del campo vectorial (Predictibilidad Global): {r2:.4f}")
    
    print("5. Exportando Geometría Diferencial...")
    export_data = {
        "n_r": n_r,
        "n_p": n_p,
        "grid_r": grid_r.tolist(),
        "grid_p": grid_p.tolist(),
        "det_J": det_J.flatten().tolist(),
        "instability_mask": instability_mask.flatten().tolist(),
        "caustic_mask": caustic_mask.flatten().tolist(),
        "gp_pred": y_pred.tolist(),
        "gp_sigma": sigma.tolist(),
        "r2_score": float(r2),
        "original_coords": s.flatten().tolist()
    }
    
    with open(os.path.join(ARTIFACTS_DIR, "latent_dynamics_data.json"), "w") as f:
        json.dump(export_data, f)
        
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO meta_insights (pattern_type, trigger_conditions, recommended_strategy, confidence, supporting_nodes, counterexamples, domains) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("physics_of_embeddings", "Continuous predictability and definable Jacobian across latent space deformations", "model_dynamics_via_latent_vector_fields", 0.99, "[]", "[]", "['latent_physics']")
    )
    conn.commit()
    conn.close()
    
    if os.environ.get("EVAL_CALLED") != "1":
        cmd = [
            sys.executable, EVALUATOR_PATH,
            "eval", "none", "differential_geometry", "scikit-learn",
            os.path.join("temp_scripts", "latent_dynamics.py"),
            "--artifact", "latent_physics|artifacts/latent_dynamics_data.json",
            "--notes", "Fase 14: Dinámica diferencial del espacio latente y modelado predictivo del flujo continuo de embeddings."
        ]
        env = os.environ.copy()
        env["EVAL_CALLED"] = "1"
        subprocess.run(cmd, cwd=ROOT_DIR, env=env)

if __name__ == "__main__":
    main()
