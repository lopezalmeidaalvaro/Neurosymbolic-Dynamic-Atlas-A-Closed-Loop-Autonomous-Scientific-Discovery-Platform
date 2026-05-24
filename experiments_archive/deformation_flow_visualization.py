import numpy as np
import matplotlib.pyplot as plt
import json
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")


def main():
    data_path = os.path.join(ARTIFACTS_DIR, "deformation_flow_projection.json")
    if not os.path.exists(data_path):
        print(
            "[ERROR] El archivo de proyección JSON no existe. Corre deformation_flow.py primero."
        )
        return

    with open(data_path, "r") as f:
        data = json.load(f)

    pca_coords = np.array(data["pca_coords"])
    p_vals = np.array(data["params_p"])
    r_vals = np.array(data["params_r"])
    v_mag = np.array(data["v_mag"])

    n_r = data["n_r"]
    n_p = data["n_p"]
    grid_r = np.array(data["r_vals"])
    grid_p = np.array(data["p_vals"])

    print("Generando visualizaciones...")

    # 1. Mapa PCA coloreado por p
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(
        pca_coords[:, 0], pca_coords[:, 1], c=p_vals, cmap="plasma", s=5, alpha=0.7
    )
    plt.colorbar(scatter, label="Parámetro de Deformación (p)")
    plt.title("Flujo Geométrico en el Espacio Latente (PCA)")
    plt.xlabel("PC1")
    plt.ylabel("PC2")

    # Draw some flow lines (for fixed r)
    for i in range(0, n_r, max(1, n_r // 15)):
        start_idx = i * n_p
        end_idx = start_idx + n_p
        plt.plot(
            pca_coords[start_idx:end_idx, 0],
            pca_coords[start_idx:end_idx, 1],
            color="gray",
            alpha=0.3,
            linewidth=0.8,
        )

    plt.savefig(
        os.path.join(ARTIFACTS_DIR, "deformation_flow_pca.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    # 2. Mapa de calor de velocidades latentes
    v_grid = v_mag.reshape((n_r, n_p))

    plt.figure(figsize=(10, 6))
    plt.imshow(
        v_grid,
        aspect="auto",
        origin="lower",
        cmap="magma",
        extent=[grid_p[0], grid_p[-1], grid_r[0], grid_r[-1]],
    )
    plt.colorbar(label="Magnitud de Velocidad Latente ($||v||$)")
    plt.title("Velocidades Geométricas vs Parámetros (Singularidades)")
    plt.xlabel("Deformación Estructural (p)")
    plt.ylabel("Parámetro Logístico (r)")

    plt.savefig(
        os.path.join(ARTIFACTS_DIR, "deformation_flow_velocity.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    print("Visualizaciones generadas en la carpeta artifacts/")


if __name__ == "__main__":
    main()
