import sqlite3
import json
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from scipy.stats import pearsonr
import os
import sys
import subprocess

# Force stdout to UTF-8 on Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "runs", "math_search.db")
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")
EVALUATOR_PATH = os.path.join(ROOT_DIR, "core", "evaluator_db.py")


def main():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # Read structural embeddings
    rows = conn.execute(
        "SELECT system_name, lyapunov_max, spectral_entropy, dominant_frequency, variance, autocorr_decay, kurtosis, skewness, energy FROM structural_embeddings"
    ).fetchall()

    if not rows:
        print("[ERROR] No embeddings found in SQLite.")
        return

    system_names = [r[0] for r in rows]
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
    matrix = np.array([r[1:] for r in rows], dtype=float)
    matrix = np.nan_to_num(matrix, nan=0.0, posinf=0.0, neginf=0.0)

    scaler = StandardScaler()
    matrix_scaled = scaler.fit_transform(matrix)

    conjectures = []

    # 1. Detección de Correlaciones
    for i in range(len(features)):
        for j in range(i + 1, len(features)):
            r_val, p_val = pearsonr(matrix_scaled[:, i], matrix_scaled[:, j])
            if abs(r_val) > 0.85:
                # Confidence: inverted p-value scaled, e.g. 1 - p_val
                conf = 1.0 - p_val
                if len(matrix_scaled) < 3:
                    conf *= 0.1

                # Cap confidence to [0, 1]
                conf = float(np.clip(conf, 0.0, 1.0))

                hyp = f"Existe una correlación estructural fuerte (r = {r_val:.3f}) entre la métrica '{features[i]}' y '{features[j]}' en el hiperespacio."

                conjectures.append(
                    {
                        "hypothesis_text": hyp,
                        "confidence_score": conf,
                        "supporting_systems": list(set(system_names)),
                        "contradictory_systems": [],
                        "evidence_json": {
                            "pearson_r": r_val,
                            "p_value": p_val,
                            "n_samples": len(matrix_scaled),
                        },
                    }
                )

    # 2. Detección de Clústeres (DBSCAN)
    best_labels = None
    best_sil = -1

    for eps in [0.5, 1.0, 1.5, 2.0, 3.0]:
        db = DBSCAN(eps=eps, min_samples=2)
        labels = db.fit_predict(matrix_scaled)
        unique_labels = set(labels) - {-1}
        if len(unique_labels) > 0 and len(set(labels)) > 1:
            try:
                sil = silhouette_score(matrix_scaled, labels)
                if sil > best_sil:
                    best_sil = sil
                    best_labels = labels
            except ValueError:
                pass

    if best_labels is not None:
        clusters = {}
        for idx, label in enumerate(best_labels):
            if label != -1:
                clusters.setdefault(label, []).append(system_names[idx])

        for label, names in clusters.items():
            unique_names = list(set(names))
            if len(unique_names) > 1:
                conf = float(max(0.0, best_sil))
                if len(names) < 3:
                    conf *= 0.2
                # Check variance degeneracy
                cluster_pts = matrix_scaled[best_labels == label]
                cluster_var = np.var(cluster_pts, axis=0).mean()
                if cluster_var < 1e-5:
                    conf *= 0.5  # penalize degenerate variance

                conf = float(np.clip(conf, 0.0, 1.0))

                hyp = f"Los sistemas {', '.join(unique_names)} pertenecen a la misma clase de universalidad topológica debido a su proximidad geométrica densa."
                conjectures.append(
                    {
                        "hypothesis_text": hyp,
                        "confidence_score": conf,
                        "supporting_systems": unique_names,
                        "contradictory_systems": [],
                        "evidence_json": {
                            "silhouette_score": best_sil,
                            "cluster_size": len(names),
                            "cluster_variance": float(cluster_var),
                        },
                    }
                )

    # Si no se encontró colisión topológica de DBSCAN, forzamos una búsqueda por coseno para asegurar
    # la generación de al menos una conjetura geométrica si es muy alta
    if not any("universalidad topológica" in c["hypothesis_text"] for c in conjectures):
        from sklearn.metrics.pairwise import cosine_similarity

        cos_sim = cosine_similarity(matrix_scaled)
        n = len(matrix_scaled)
        found = False
        for i in range(n):
            for j in range(i + 1, n):
                if system_names[i] != system_names[j] and cos_sim[i, j] > 0.90:
                    conf = float(cos_sim[i, j])
                    hyp = f"Los sistemas {system_names[i]} y {system_names[j]} pertenecen a la misma clase de universalidad topológica debido a su extrema proximidad coseno ({conf:.3f})."
                    conjectures.append(
                        {
                            "hypothesis_text": hyp,
                            "confidence_score": conf,
                            "supporting_systems": [system_names[i], system_names[j]],
                            "contradictory_systems": [],
                            "evidence_json": {"cosine_similarity": conf},
                        }
                    )
                    found = True
                    break
            if found:
                break

    # Guardar y diseñar experimentos
    conn.execute("""
        CREATE TABLE IF NOT EXISTS generated_conjectures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hypothesis_text TEXT,
            confidence_score REAL,
            supporting_systems TEXT,
            contradictory_systems TEXT,
            evidence_json TEXT,
            status TEXT DEFAULT 'provisional',
            generated_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    experiment_count = 0
    for conj in conjectures:
        # Insert into SQLite
        conn.execute(
            """
            INSERT INTO generated_conjectures 
            (hypothesis_text, confidence_score, supporting_systems, contradictory_systems, evidence_json, status)
            VALUES (?, ?, ?, ?, ?, 'provisional')
        """,
            (
                conj["hypothesis_text"],
                conj["confidence_score"],
                json.dumps(conj["supporting_systems"], ensure_ascii=False),
                json.dumps(conj["contradictory_systems"], ensure_ascii=False),
                json.dumps(conj["evidence_json"], ensure_ascii=False),
            ),
        )

        # Falsación si conf > 0.6
        if conj["confidence_score"] > 0.6:
            experiment_count += 1
            exp_path = os.path.join(
                ARTIFACTS_DIR, f"generated_experiment_{experiment_count:03d}.md"
            )
            with open(exp_path, "w", encoding="utf-8") as f:
                f.write(
                    f"# Diseño de Experimento: Falsación de Conjetura {experiment_count}\n\n"
                )
                f.write(f"## Hipótesis Original\n**{conj['hypothesis_text']}**\n\n")
                f.write(f"**Confianza Inicial:** {conj['confidence_score']:.4f}\n\n")
                f.write("## Instrucciones de Falsación (Prompt Sugerido)\n")
                f.write(
                    "> **Ejecuta lo siguiente para intentar romper esta conjetura:**\n"
                )
                f.write(
                    r"> 1. Introduce ruido estocástico (e.g., ruido Gaussiano $\sigma=0.1$) en las ecuaciones de estos sistemas y recalcula el embedding estructural."
                    + "\n"
                )
                f.write(
                    r"> 2. Realiza un barrido paramétrico extremo fuera del régimen actual para forzar transiciones de fase desconocidas."
                    + "\n"
                )
                f.write(
                    r"> 3. Verifica si la correlación o el clúster se disuelven (si la distancia coseno cae drásticamente o la correlación baja de 0.8)."
                    + "\n\n"
                )
                f.write("## Evidencia Actual\n")
                f.write(
                    "```json\n"
                    + json.dumps(conj["evidence_json"], indent=2, ensure_ascii=False)
                    + "\n```\n"
                )

    conn.commit()
    conn.close()

    print("==================================================")
    print("  MOTOR DE CONJETURAS Y EPISTEMOLOGÍA AUTÓNOMA")
    print("==================================================")
    print(f"Conjeturas generadas: {len(conjectures)}")
    print(f"Experimentos de falsación diseñados: {experiment_count}")
    for i, c in enumerate(conjectures):
        print(f"\n[Conjetura {i+1}] conf={c['confidence_score']:.3f}")
        print(f"  {c['hypothesis_text']}")
    print("\n==================================================\n")


if __name__ == "__main__":
    main()
