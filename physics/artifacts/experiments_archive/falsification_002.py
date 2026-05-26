import numpy as np
from scipy.spatial.distance import cosine
import sqlite3
import json
import os
import sys
import subprocess
from sklearn.preprocessing import StandardScaler

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "runs", "math_search.db")
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")
EVALUATOR_PATH = os.path.join(ROOT_DIR, "core", "evaluator_db.py")

# Ensure topology_miner_v2 is importable
sys.path.append(os.path.dirname(__file__))
try:
    from topology_miner_v2 import compute_embedding
except ImportError:
    print("[ERROR] No se pudo importar compute_embedding de topology_miner_v2")
    sys.exit(1)


def main():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    print("=====================================================")
    print("  EXPERIMENTO DE FALSACIÓN 002 - DEFORMACIÓN TOPOLÓGICA")
    print("=====================================================")

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

    # 1. Extraer embeddings originales (clase de referencia)
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        f"SELECT {', '.join(features)} FROM structural_embeddings WHERE system_name='logistic_sweep'"
    ).fetchall()

    if not rows:
        print("[ERROR] No se encontraron embeddings de logistic_sweep en la BD.")
        conn.close()
        return

    original_matrix = np.array(rows, dtype=float)
    original_matrix = np.nan_to_num(original_matrix, nan=0.0, posinf=0.0, neginf=0.0)

    scaler = StandardScaler()
    original_scaled = scaler.fit_transform(original_matrix)

    # Calcular centroide del clúster original
    original_centroid = np.mean(original_scaled, axis=0)

    # 2. Deformación Topológica Extrema
    r_vals = np.linspace(2.8, 4.0, 150)
    deformed_embeddings = []

    print(
        f"Ejecutando barrido paramétrico con deformación estructural (N={len(r_vals)})..."
    )

    for r in r_vals:
        N_warmup = 500
        N_steps = 1500
        N_total = N_warmup + N_steps

        x = 0.4  # initial condition
        series = np.zeros(N_steps)

        for i in range(N_total):
            x = r * x * ((1 - x) ** 2)
            x = np.clip(x, 0.0, 1.0)
            if i >= N_warmup:
                series[i - N_warmup] = x

        # Compute embedding v2
        emb = compute_embedding(series, dt=1.0)

        # Calculate lyapunov max for the deformed map
        # f'(x) = r * (1 - x) * (1 - 3*x)
        derivatives = r * (1 - series) * (1 - 3 * series)
        # Avoid log(0)
        derivatives = np.where(np.abs(derivatives) < 1e-12, 1e-12, derivatives)
        lyap = np.mean(np.log(np.abs(derivatives)))
        emb["lyapunov_max"] = lyap

        vec = [emb[f] for f in features]
        deformed_embeddings.append(vec)

    deformed_matrix = np.array(deformed_embeddings, dtype=float)
    deformed_matrix = np.nan_to_num(deformed_matrix, nan=0.0, posinf=0.0, neginf=0.0)

    # Normalizar usando scaler del grupo original
    deformed_scaled = scaler.transform(deformed_matrix)

    # 3. Cálculo de Refutación Geométrica
    similarities = []
    for vec in deformed_scaled:
        # cosine distance requires non-zero vectors
        if np.linalg.norm(vec) > 0 and np.linalg.norm(original_centroid) > 0:
            sim = 1.0 - cosine(vec, original_centroid)
            similarities.append(sim)
        else:
            similarities.append(0.0)

    mean_similarity = np.mean(similarities)
    print(
        f"\n  Similitud Coseno promedio con el centroide original: {mean_similarity:.4f}"
    )

    if mean_similarity >= 0.85:
        verdict = "survived"
        print(
            "  [VEREDICTO] La conjetura SOBREVIVE. El clúster absorbe la deformación estructural."
        )
        new_status = "validated_under_deformation"
        new_confidence = 0.99
    else:
        verdict = "falsified"
        print(
            "  [VEREDICTO] La conjetura es FALSADA. El clúster se fractura ante asimetrías no lineales."
        )
        new_status = "falsified"
        new_confidence = 0.10

    print("=====================================================\n")

    # 4. Actualización Epistemológica (SQLite)
    query = """
        UPDATE generated_conjectures 
        SET status = ?, confidence_score = ? 
        WHERE hypothesis_text LIKE '%universalidad%'
    """
    conn.execute(query, (new_status, new_confidence))
    conn.commit()
    conn.close()

    # 5. Persistencia y Evaluación
    results = {
        "mean_cosine_similarity": float(mean_similarity),
        "cluster_status": new_status,
        "verdict": verdict,
    }

    results_path = os.path.join(ARTIFACTS_DIR, "falsification_002_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    # Invocar a evaluator_db.py (con protección para evitar bucle infinito)
    if os.environ.get("EVAL_CALLED") != "1":
        cmd = [
            sys.executable,
            EVALUATOR_PATH,
            "eval",
            "none",
            "epistemological_engine",
            "scipy",
            os.path.join("temp_scripts", "falsification_002.py"),
            "--artifact",
            "falsification_report|artifacts/falsification_002_results.json",
            "--notes",
            "Fase 10B: Falsación de universalidad topológica. Inyección de asimetría estructural en mapa logístico para testear la resistencia de clústeres en el espacio latente.",
        ]
        env = os.environ.copy()
        env["EVAL_CALLED"] = "1"
        subprocess.run(cmd, cwd=ROOT_DIR, env=env)


if __name__ == "__main__":
    main()
