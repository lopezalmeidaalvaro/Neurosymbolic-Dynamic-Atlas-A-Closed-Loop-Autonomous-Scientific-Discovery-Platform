import numpy as np
import matplotlib.pyplot as plt
import json
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")


def main():
    data_path = os.path.join(ARTIFACTS_DIR, "latent_curvature_data.json")
    if not os.path.exists(data_path):
        print(
            "[ERROR] No se encontró latent_curvature_data.json. Ejecuta latent_curvature.py primero."
        )
        return

    with open(data_path, "r") as f:
        data = json.load(f)

    n_r = data["n_r"]
    n_p = data["n_p"]
    grid_r = np.array(data["r_vals"])
    grid_p = np.array(data["p_vals"])

    pca_coords = np.array(data["pca_coords"])
    kappa_r = np.array(data["kappa_r"])
    area_expansion = np.array(data["area_expansion"])

    print("Generando visualizaciones diferenciales...")

    # 1. Mapa PCA coloreado por curvatura discreta (kappa)
    # Log scale for curvature because it can be highly peaked
    log_kappa = np.log10(kappa_r + 1e-8)

    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(
        pca_coords[:, 0], pca_coords[:, 1], c=log_kappa, cmap="inferno", s=8, alpha=0.8
    )
    plt.colorbar(scatter, label="Log10(Curvatura $\kappa$)")
    plt.title("Geometría Diferencial: Curvatura Discreta en PCA")
    plt.xlabel("PC1")
    plt.ylabel("PC2")

    plt.savefig(
        os.path.join(ARTIFACTS_DIR, "latent_curvature.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    # 2. Mapa de calor métrico (Densidad de Singularidades / Expansión del Área)
    area_grid = area_expansion.reshape((n_r, n_p))
    log_area = np.log10(area_grid + 1e-12)

    plt.figure(figsize=(10, 6))
    plt.imshow(
        log_area,
        aspect="auto",
        origin="lower",
        cmap="viridis",
        extent=[grid_p[0], grid_p[-1], grid_r[0], grid_r[-1]],
    )
    plt.colorbar(label="Log10(Expansión Métrica Local $\sqrt{\det g}$)")
    plt.title("Mapa de Densidad Métrica y Geodésicas Latentes")
    plt.xlabel("Deformación Estructural (p)")
    plt.ylabel("Parámetro Logístico (r)")

    plt.savefig(
        os.path.join(ARTIFACTS_DIR, "latent_metric_density.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    print("Visualizaciones generadas en la carpeta artifacts/")


if __name__ == "__main__":
    main()
