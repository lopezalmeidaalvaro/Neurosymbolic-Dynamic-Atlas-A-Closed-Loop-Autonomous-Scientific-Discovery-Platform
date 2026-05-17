import numpy as np
import matplotlib.pyplot as plt
import json
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")

def main():
    data_path = os.path.join(ARTIFACTS_DIR, "latent_dynamics_data.json")
    if not os.path.exists(data_path):
        print("[ERROR] No se encontró latent_dynamics_data.json")
        return
        
    with open(data_path, "r") as f:
        data = json.load(f)
        
    n_r = data["n_r"]
    n_p = data["n_p"]
    grid_r = np.array(data["grid_r"])
    grid_p = np.array(data["grid_p"])
    
    det_J = np.array(data["det_J"]).reshape((n_r, n_p))
    instability_mask = np.array(data["instability_mask"]).reshape((n_r, n_p))
    caustic_mask = np.array(data["caustic_mask"]).reshape((n_r, n_p))
    
    s = np.array(data["original_coords"]).reshape((n_r * n_p, 2))
    s_pred = np.array(data["gp_pred"]).reshape((n_r * n_p, 2))
    
    print("Generando visualizaciones del campo dinámico...")
    
    # 1. Determinante Jacobiano (Folds / Caustics)
    plt.figure(figsize=(10, 6))
    
    # Limit extreme values for better visualization
    vmax = np.percentile(np.abs(det_J), 95)
    plt.imshow(det_J, aspect='auto', origin='lower', cmap='seismic', vmin=-vmax, vmax=vmax,
               extent=[grid_p[0], grid_p[-1], grid_r[0], grid_r[-1]])
    
    plt.colorbar(label='$\det(J)$ (Determinante Jacobiano)')
    plt.title('Dinámica del Espacio Latente: Pliegues y Caústicas')
    plt.xlabel('Deformación Estructural (p)')
    plt.ylabel('Parámetro Logístico (r)')
    
    plt.savefig(os.path.join(ARTIFACTS_DIR, "jacobian_determinant.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Inestabilidad Cinemática
    plt.figure(figsize=(10, 6))
    # Combine instability and caustics masks
    combined_mask = np.zeros((n_r, n_p))
    combined_mask[instability_mask] = 1 # Kinematic instability (red)
    combined_mask[caustic_mask] = 2 # Caustics (blue)
    combined_mask[instability_mask & caustic_mask] = 3 # Both (purple)
    
    plt.imshow(combined_mask, aspect='auto', origin='lower', cmap='viridis',
               extent=[grid_p[0], grid_p[-1], grid_r[0], grid_r[-1]])
    
    plt.title('Mapa de Inestabilidades: Explosión Cinemática y Caústicas')
    plt.xlabel('Deformación Estructural (p)')
    plt.ylabel('Parámetro Logístico (r)')
    
    plt.savefig(os.path.join(ARTIFACTS_DIR, "latent_instability.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Predicción del Gaussian Process
    plt.figure(figsize=(10, 8))
    
    # Random subset of points to plot arrows
    idx = np.random.choice(n_r * n_p, 500, replace=False)
    
    plt.scatter(s[:, 0], s[:, 1], c='gray', alpha=0.3, s=10, label='Campo Real')
    plt.scatter(s_pred[idx, 0], s_pred[idx, 1], c='blue', alpha=0.6, s=10, label='Predicción GPR')
    
    # Plot errors as lines
    for i in idx:
        plt.plot([s[i, 0], s_pred[i, 0]], [s[i, 1], s_pred[i, 1]], 'r-', alpha=0.2)
        
    plt.title(f"Predictibilidad del Espacio Latente (R^2 = {data['r2_score']:.4f})")
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.legend()
    
    plt.savefig(os.path.join(ARTIFACTS_DIR, "gp_prediction.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Visualizaciones generadas en la carpeta artifacts/")

if __name__ == "__main__":
    main()
