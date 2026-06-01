#!/usr/bin/env python3
"""
Phase 1: PINN Warp Metric Optimizer
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Ensure complete reproducibility
np.random.seed(42)
torch.manual_seed(42)

# Define the original Alcubierre shape function
def alcubierre_shape_function(r, R, sigma):
    """
    Computes the standard Alcubierre shape function f(r).
    f(r) = (tanh(sigma * (r + R)) - tanh(sigma * (r - R))) / (2 * tanh(sigma * R))
    """
    numerator = np.tanh(sigma * (r + R)) - np.tanh(sigma * (r - R))
    denominator = 2 * np.tanh(sigma * R)
    return numerator / denominator

# PyTorch compatible Alcubierre shape function
def alcubierre_shape_function_torch(r, R, sigma):
    numerator = torch.tanh(sigma * (r + R)) - torch.tanh(sigma * (r - R))
    denominator = 2 * torch.tanh(torch.tensor(sigma * R))
    return numerator / denominator

# Neural Network architecture for the PINN
class WarpPINN(nn.Module):
    def __init__(self, hidden_dim=50):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, r):
        return self.net(r)

def train_pinn(R=0.5, sigma=8.0, velocity=1.0, epochs=5000, lr=1e-3, beta_energy=0.05, beta_data=0.1):
    print(f"[*] Inicializando entrenamiento PINN para R={R}, sigma={sigma}, v={velocity}...")
    
    # 1. Instantiate the model
    model = WarpPINN()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    # 2. Setup collocation points (r in [0, 1])
    r_colloc = torch.linspace(0.0, 1.0, 250, requires_grad=True).unsqueeze(1)
    
    # Compute baseline Alcubierre values for data regularization
    f_baseline = alcubierre_shape_function_torch(r_colloc.detach(), R, sigma)
    
    # 3. Training Loop
    for epoch in range(1, epochs + 1):
        optimizer.zero_grad(set_to_none=True)
        
        # Predict shape function f(r)
        f_pred = model(r_colloc)
        
        # Boundary Conditions loss
        # f(0) = 1.0 (flat space at center), f(1) = 0.0 (flat space far away)
        bc_0 = model(torch.tensor([[0.0]], dtype=torch.float32))
        bc_1 = model(torch.tensor([[1.0]], dtype=torch.float32))
        bc_loss = (bc_0 - 1.0)**2 + (bc_1 - 0.0)**2
        
        # Compute derivatives using autograd for energy loss
        df_dr = torch.autograd.grad(
            f_pred, r_colloc,
            grad_outputs=torch.ones_like(f_pred),
            create_graph=True,
            retain_graph=True
        )[0]
        
        # Energy loss: penalizes the square gradient (df/dr)^2
        energy_loss = torch.mean(df_dr ** 2)
        
        # Data loss: preserves warp bubble structure (prevents converging to simple linear f(r) = 1 - r)
        # Allows PINN to smoothly deform Alcubierre shape while keeping the bubble characteristic
        data_loss = torch.mean((f_pred - f_baseline) ** 2)
        
        # Total Loss
        total_loss = bc_loss + beta_energy * energy_loss + beta_data * data_loss
        
        # Backpropagation
        total_loss.backward()
        optimizer.step()
        
        if epoch % 500 == 0 or epoch == 1:
            print(f"    Época {epoch:4d}/{epochs} | Loss Total: {total_loss.item():.6f} | BC Loss: {bc_loss.item():.6f} | Energy Loss: {energy_loss.item():.6f} | Data Loss: {data_loss.item():.6f}")
            
    print("[+] Entrenamiento PINN finalizado con éxito.")
    
    # 4. Generate final predictions
    model.eval()
    with torch.no_grad():
        r_eval = torch.linspace(0.0, 1.0, 500).unsqueeze(1)
        f_opt = model(r_eval).numpy().flatten()
        r_eval_np = r_eval.numpy().flatten()
        f_orig = alcubierre_shape_function(r_eval_np, R, sigma)
        
    # Save optimized coordinates to CSV
    os.makedirs("physics/warp/data", exist_ok=True)
    df_out = pd.DataFrame({"r": r_eval_np, "f_r": f_opt})
    csv_path = "physics/warp/data/optimized_bubble.csv"
    df_out.to_csv(csv_path, index=False)
    print(f"[+] Datos optimizados guardados en: {csv_path}")
    
    # Save comparison plot
    plt.figure(figsize=(10, 6))
    plt.style.use('dark_background')
    plt.plot(r_eval_np, f_orig, label=f"Alcubierre Original (R={R}, $\\sigma$={sigma})", color="#ff2a5f", linestyle="--", linewidth=2.5)
    plt.plot(r_eval_np, f_opt, label="Alcubierre Optimizado (PINN)", color="#26ffad", linewidth=2.5)
    
    # Shade exotic energy density area (proportional to (df/dr)^2)
    # Compute derivative of optimized curve numerically for visualization
    df_opt_dr = np.gradient(f_opt, r_eval_np)
    df_orig_dr = np.gradient(f_orig, r_eval_np)
    
    plt.fill_between(r_eval_np, df_orig_dr**2 * 0.05, alpha=0.15, color="#ff2a5f", label="Densidad Energía Original (Escalada)")
    plt.fill_between(r_eval_np, df_opt_dr**2 * 0.05, alpha=0.25, color="#26ffad", label="Densidad Energía Optimizada (Escalada)")
    
    plt.title("Optimización de Métrica de Alcubierre mediante PINN", color="white", fontsize=14, pad=15)
    plt.xlabel("Coordenada Radial Normalizada r", color="#94a3b8", fontsize=11)
    plt.ylabel("Función de Forma f(r)", color="#94a3b8", fontsize=11)
    plt.grid(color="white", linestyle=":", alpha=0.1)
    plt.legend(facecolor="#0f172a", edgecolor="#1e293b", labelcolor="white")
    
    plot_path = "physics/warp/pinn_optimization.png"
    plt.tight_layout()
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"[+] Gráfica comparativa guardada en: {plot_path}")
    
    return r_eval_np, f_orig, f_opt

if __name__ == "__main__":
    # Default parameters: Bubble radius = 0.5, thickness = 8.0, spacecraft velocity = 1.0
    train_pinn(R=0.5, sigma=8.0, velocity=1.0)
