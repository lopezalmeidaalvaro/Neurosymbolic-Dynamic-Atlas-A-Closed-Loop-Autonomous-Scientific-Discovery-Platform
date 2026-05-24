import numpy as np
import matplotlib.pyplot as plt
import json
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")


def main():
    data_path = os.path.join(ARTIFACTS_DIR, "geodesic_flow_data.json")
    if not os.path.exists(data_path):
        print(
            "[ERROR] No se encontró geodesic_flow_data.json. Ejecuta geodesic_flow.py primero."
        )
        return

    with open(data_path, "r") as f:
        data = json.load(f)

    pca_coords = np.array(data["pca_coords"])
    lambda_g = np.array(data["lambda_g"])
    distances = np.array(data["geodesic_distances"])
    r_flow_indices = data["r_flow_indices"]
    renorm_scores = data["renormalization_scores"]

    print("Generando visualizaciones geodésicas...")

    # 1. Campo Geodésico (Distancias desde la semilla)
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(
        pca_coords[:, 0], pca_coords[:, 1], c=distances, cmap="GnBu", s=5, alpha=0.8
    )
    plt.colorbar(scatter, label="Distancia Geodésica Discreta al Origen Estable")
    plt.title("Topología Riemanniana: Campo Geodésico en el Espacio Latente")
    plt.xlabel("PC1")
    plt.ylabel("PC2")

    # Seed
    plt.scatter(
        pca_coords[0, 0],
        pca_coords[0, 1],
        color="red",
        s=50,
        marker="*",
        label="Semilla Estable",
    )
    plt.legend()
    plt.savefig(
        os.path.join(ARTIFACTS_DIR, "geodesic_field.png"), dpi=300, bbox_inches="tight"
    )
    plt.close()

    # 2. Divergencia Exponencial Geodésica
    plt.figure(figsize=(10, 8))
    scatter2 = plt.scatter(
        pca_coords[:, 0], pca_coords[:, 1], c=lambda_g, cmap="coolwarm", s=5, alpha=0.8
    )
    plt.colorbar(scatter2, label="Exponente Geodésico ($\lambda_g$)")
    plt.title("Divergencia Exponencial: Caos Geométrico Local")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.savefig(
        os.path.join(ARTIFACTS_DIR, "geodesic_divergence.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    # 3. Operadores de Renormalización (Ciclos de Auto-Similitud)
    plt.figure(figsize=(10, 5))
    x_axis = np.arange(len(renorm_scores))
    plt.plot(
        x_axis, renorm_scores, color="purple", label="Similitud Fractal (DTW / Norm)"
    )
    plt.title("Flujo de Renormalización de Feigenbaum en Espacio Latente")
    plt.xlabel("Paso Paramétrico ($r$)")
    plt.ylabel("Puntuación de Auto-Similitud Multiescala")
    plt.legend()
    plt.savefig(
        os.path.join(ARTIFACTS_DIR, "renormalization_cycles.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    print("Visualizaciones generadas en la carpeta artifacts/")


if __name__ == "__main__":
    main()
