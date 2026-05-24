import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
import os
import matplotlib.patches as mpatches

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")


def main():
    data_path = os.path.join(ARTIFACTS_DIR, "universal_atlas_data.json")
    if not os.path.exists(data_path):
        print("[ERROR] No se encontró universal_atlas_data.json")
        return

    with open(data_path, "r") as f:
        data = json.load(f)

    names = data["names"]
    pca_coords = np.array(data["pca_coords"])
    curvatures = np.array(data["curvatures"])
    lambda_g = np.array(data["lambda_g"])
    labels = np.array(data["labels"])

    # 1. Atlas Universal PCA Coloreado por Clústeres Topológicos
    plt.figure(figsize=(12, 10))
    scatter = plt.scatter(
        pca_coords[:, 0],
        pca_coords[:, 1],
        c=labels,
        cmap="tab20",
        s=40,
        alpha=0.8,
        edgecolors="w",
    )

    # Anotar los nombres para los sistemas más relevantes o agruparlos
    # Simplificación: anotar solo una vez cada sistema cerca de su centroide
    unique_names = list(set(names))
    for un in unique_names:
        idx = [i for i, n in enumerate(names) if n == un]
        centroid = np.mean(pca_coords[idx], axis=0)
        plt.annotate(
            un,
            (centroid[0], centroid[1]),
            fontsize=9,
            fontweight="bold",
            ha="center",
            bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
        )

    plt.title("Atlas Universal: Atractores 3D y Mapas 1D en Espacio Latente")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.savefig(
        os.path.join(ARTIFACTS_DIR, "universal_atlas_pca.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    # 2. Geodésicas Universales (Divergencia lambda_g)
    plt.figure(figsize=(10, 8))
    sc = plt.scatter(
        pca_coords[:, 0],
        pca_coords[:, 1],
        c=lambda_g,
        cmap="coolwarm",
        s=50,
        alpha=0.8,
        edgecolors="k",
    )
    plt.colorbar(sc, label=r"Divergencia Geodésica Universal ($\lambda_g$)")
    plt.title("Geometría del Caos: Expansión Exponencial Compartida")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.savefig(
        os.path.join(ARTIFACTS_DIR, "universal_geodesics.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    # 3. Curvatura y Regiones Hiperbólicas
    # Log scale curvature
    log_curv = np.log10(curvatures + 1e-6)
    plt.figure(figsize=(10, 8))
    sc2 = plt.scatter(
        pca_coords[:, 0],
        pca_coords[:, 1],
        c=log_curv,
        cmap="magma",
        s=50,
        alpha=0.8,
        edgecolors="k",
    )
    plt.colorbar(sc2, label=r"Log10(Curvatura Local $\kappa$)")
    plt.title("Singularidades Topológicas y Regiones Hiperbólicas")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.savefig(
        os.path.join(ARTIFACTS_DIR, "curvature_clusters.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    print("Visualizaciones del Atlas Universal generadas.")


if __name__ == "__main__":
    main()
