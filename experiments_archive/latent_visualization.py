import sqlite3
import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os
import subprocess
import sys

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
    rows = conn.execute(
        "SELECT embedding_json FROM structural_embeddings WHERE system_name='logistic_sweep'"
    ).fetchall()

    data = []
    for row in rows:
        emb = json.loads(row[0])
        data.append(emb)

    # Sort by r
    data.sort(key=lambda x: x["r"])

    r_vals = np.array([d["r"] for d in data])

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

    matrix = np.array([[d[f] for f in features] for d in data], dtype=float)

    # Clean NaNs and Infs
    matrix = np.nan_to_num(matrix, nan=0.0, posinf=0.0, neginf=0.0)

    # Standard scale
    scaler = StandardScaler()
    matrix_scaled = scaler.fit_transform(matrix)

    # PCA
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(matrix_scaled)

    # Calculate delta d in normalized space (not PCA space)
    delta_d = np.zeros(len(r_vals))
    for i in range(1, len(r_vals)):
        delta_d[i] = np.linalg.norm(matrix_scaled[i] - matrix_scaled[i - 1])

    # Generate PCA Plot
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(
        pca_result[:, 0], pca_result[:, 1], c=r_vals, cmap="viridis", s=20
    )
    plt.colorbar(scatter, label="Parámetro r")
    plt.plot(pca_result[:, 0], pca_result[:, 1], color="gray", alpha=0.3, linewidth=1)
    plt.title("Trayectoria Cinemática Latente (PCA) - Mapa Logístico")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    pca_path = os.path.join(ARTIFACTS_DIR, "logistic_pca_trajectory.png")
    plt.savefig(pca_path, dpi=300, bbox_inches="tight")
    plt.close()

    # Detect peaks in delta d
    peaks = []
    mean_d = np.mean(delta_d)
    std_d = np.std(delta_d)
    for i in range(1, len(delta_d) - 1):
        if (
            delta_d[i] > delta_d[i - 1]
            and delta_d[i] > delta_d[i + 1]
            and delta_d[i] > mean_d + 0.5 * std_d
        ):
            peaks.append(i)

    # Onset of chaos (lyapunov > 0)
    onset_idx = None
    for i in range(len(r_vals)):
        if data[i]["lyapunov_max"] > 0:
            onset_idx = i
            break

    # Generate Delta D Plot
    plt.figure(figsize=(10, 6))
    plt.plot(r_vals, delta_d, label=r"$\Delta d$ (Cinemática Geométrica)")

    peak_r = r_vals[peaks]
    peak_d = delta_d[peaks]
    plt.scatter(
        peak_r, peak_d, color="red", zorder=5, label="Bifurcaciones detectadas (Picos)"
    )
    for r, d in zip(peak_r, peak_d):
        plt.axvline(x=r, color="red", linestyle="--", alpha=0.3)

    if onset_idx is not None:
        r_chaos = r_vals[onset_idx]
        plt.axvline(
            x=r_chaos,
            color="black",
            linestyle=":",
            label=f"Onset of Chaos ($r \\approx {r_chaos:.4f}$)",
        )

    plt.title(r"Derivada Geométrica ($\Delta d$) vs $r$ en el Hiperespacio")
    plt.xlabel("Parámetro r")
    plt.ylabel(r"$\Delta d$ (Distancia Euclidiana Normalizada)")
    plt.legend()
    delta_path = os.path.join(ARTIFACTS_DIR, "logistic_delta_d.png")
    plt.savefig(delta_path, dpi=300, bbox_inches="tight")
    plt.close()

    # CRITICAL: close the DB connection before calling the evaluator process
    conn.close()

    # Print Console output
    print("==================================================")
    print("  ANÁLISIS DE REGÍMENES (MAPA LOGÍSTICO)")
    print("==================================================")
    print(f"Picos locales detectados (Bifurcaciones): {len(peaks)}")
    for r in peak_r:
        print(f"  - Bifurcación geométrica en r ≈ {r:.4f}")

    if onset_idx is not None:
        print(f"\n[!] Onset of Chaos detectado en r ≈ {r_vals[onset_idx]:.4f}")
        print("  Justificación: Explosión de la varianza en el espacio y lyapunov > 0.")

    # Zonas de alta estabilidad (delta d muy pequeña)
    stable_mask = delta_d < np.percentile(delta_d, 25)
    stable_r = r_vals[stable_mask]
    if len(stable_r) > 0:
        print("\nZonas de alta estabilidad geométrica:")
        print(f"  - Ej: r ≈ {stable_r[-1]:.4f}")

    print("==================================================\n")


if __name__ == "__main__":
    main()
