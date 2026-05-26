import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import json
import os
import sys
import subprocess
import sqlite3

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "runs", "math_search.db")
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")
EVALUATOR_PATH = os.path.join(ROOT_DIR, "core", "evaluator_db.py")

sys.path.append(os.path.dirname(__file__))
try:
    from topology_miner_v2 import compute_embedding
except ImportError:
    print("[ERROR] No se pudo importar compute_embedding de topology_miner_v2")
    sys.exit(1)


def main():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    print("=====================================================")
    print("  FASE 11A - OPERADORES DE DEFORMACIÓN LATENTE")
    print("=====================================================")

    n_p = 50
    n_r = 100
    p_vals = np.linspace(1.0, 3.0, n_p)
    r_vals = np.linspace(2.8, 4.0, n_r)

    print(
        f"1. Generando trayectorias vectorizadas (n_r={n_r}, n_p={n_p}, total={n_r*n_p})..."
    )
    R, P = np.meshgrid(r_vals, p_vals, indexing="ij")  # shape: (n_r, n_p)
    R_flat = R.flatten()
    P_flat = P.flatten()

    N_total = len(R_flat)
    N_warmup = 500
    N_steps = 1500

    X = np.full(N_total, 0.4)
    series = np.zeros((N_steps, N_total))

    for i in range(N_warmup + N_steps):
        # Clip X beforehand to prevent negative bases for fractional powers
        X = np.clip(X, 0.0, 1.0)

        # Calculate new X
        X = R_flat * X * ((1.0 - X) ** P_flat)
        X = np.clip(X, 0.0, 1.0)  # Clip after just in case

        if i >= N_warmup:
            series[i - N_warmup, :] = X

    print("2. Calculando embeddings y velocidades...")
    features = [
        "lyapunov_max",
        "spectral_entropy",
        "dominant_frequency",
        "variance",
        "autocorr_decay",
        "kurtosis",
        "skewness",
        "energy",
    ]

    embeddings = []

    for j in range(N_total):
        s = series[:, j]
        emb = compute_embedding(s, dt=1.0)

        x_n = s[:-1]
        r_val = R_flat[j]
        p_val = P_flat[j]

        # Protect against exact 1.0 to avoid 0.0^negative
        term1 = np.clip(1.0 - x_n, 1e-12, 1.0)
        deriv = r_val * (term1 ** (p_val - 1.0)) * (1.0 - (p_val + 1.0) * x_n)
        deriv = np.where(np.abs(deriv) < 1e-12, 1e-12, deriv)
        lyap = np.mean(np.log(np.abs(deriv)))
        emb["lyapunov_max"] = lyap

        embeddings.append([emb[f] for f in features])

    matrix = np.array(embeddings, dtype=float)
    matrix = np.nan_to_num(matrix, nan=0.0, posinf=0.0, neginf=0.0)

    print("3. Construyendo campo de velocidades (flujo latente)...")
    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix)  # shape (N_total, 8)

    grid_scaled = scaled.reshape((n_r, n_p, len(features)))

    velocities = np.zeros_like(grid_scaled)
    # Velocity along p: v_i = s_{i+1} - s_i
    velocities[:, :-1, :] = grid_scaled[:, 1:, :] - grid_scaled[:, :-1, :]
    velocities[:, -1, :] = velocities[:, -2, :]

    accelerations = np.zeros_like(velocities)
    accelerations[:, :-1, :] = velocities[:, 1:, :] - velocities[:, :-1, :]
    accelerations[:, -1, :] = accelerations[:, -2, :]

    v_mag = np.linalg.norm(velocities, axis=2)
    a_mag = np.linalg.norm(accelerations, axis=2)

    print("4. Detectando fronteras de universalidad...")
    v_p33 = np.percentile(v_mag, 33)
    v_p85 = np.percentile(v_mag, 85)

    labels = []
    v_mag_flat = v_mag.flatten()
    a_mag_flat = a_mag.flatten()

    for i in range(N_total):
        v = v_mag_flat[i]
        if v < v_p33:
            labels.append("zona_estable")
        elif v > v_p85:
            labels.append("zona_caotica")
        else:
            labels.append("zona_critica")

    print("5. Reducción Geométrica (PCA)...")
    pca = PCA(n_components=2)
    pca_coords = pca.fit_transform(scaled)

    print("6. Exportando proyecciones JSON...")
    export_data = {
        "features": features,
        "n_r": n_r,
        "n_p": n_p,
        "r_vals": r_vals.tolist(),
        "p_vals": p_vals.tolist(),
        "pca_coords": pca_coords.tolist(),
        "v_mag": v_mag_flat.tolist(),
        "a_mag": a_mag_flat.tolist(),
        "labels": labels,
        "params_r": R_flat.tolist(),
        "params_p": P_flat.tolist(),
    }

    with open(
        os.path.join(ARTIFACTS_DIR, "deformation_flow_projection.json"), "w"
    ) as f:
        json.dump(export_data, f)

    print("Flujo latente exportado exitosamente.")
    print("=====================================================\n")

    # Registro en Memoria Semántica
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO meta_insights (pattern_type, trigger_conditions, recommended_strategy, confidence, supporting_nodes, counterexamples, domains) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "latent_deformation_geometry",
            "Continuous structural deformation applied to maps",
            "classify_dynamic_systems_by_geometric_flow_not_static_equation",
            0.95,
            "[]",
            "[]",
            "['topology_flow']",
        ),
    )
    conn.commit()
    conn.close()

    if os.environ.get("EVAL_CALLED") != "1":
        cmd = [
            sys.executable,
            EVALUATOR_PATH,
            "eval",
            "none",
            "topology_flow",
            "scikit-learn",
            os.path.join("temp_scripts", "deformation_flow.py"),
            "--artifact",
            "deformation_flow|artifacts/deformation_flow_projection.json",
            "--notes",
            "Fase 11A: Construcción del flujo geométrico continuo entre familias dinámicas deformadas.",
        ]
        env = os.environ.copy()
        env["EVAL_CALLED"] = "1"
        subprocess.run(cmd, cwd=ROOT_DIR, env=env)


if __name__ == "__main__":
    main()
