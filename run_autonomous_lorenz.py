import os
import sys
import csv
import numpy as np
import torch

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Set global seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

from synthetic_systems import generate_lorenz
from neural_ode_module import NeuralODEModel
from symbolic_discovery import deterministic_symbolic_recovery
from neurosymbolic.audit import compute_cka, compute_ev3

def get_hidden_activations(model, X):
    x_tensor = torch.tensor(X, dtype=torch.float32)
    curr = x_tensor
    activations = []
    for layer in model.ode_func.net:
        curr = layer(curr)
        if isinstance(layer, torch.nn.Tanh):
            activations.append(curr.detach().cpu().numpy())
    return activations[-1]

def main():
    print("=" * 60)
    print("🚀 STARTING AUTONOMOUS LORENZ SCIENTIST LOOP")
    print("=" * 60)

    # 1. Generate Lorenz trajectory
    print("Generating standard Lorenz trajectory...")
    sys_data = generate_lorenz(n_timesteps=1000, dt=0.01, sigma=10, rho=28, beta=8/3)
    X = np.stack([sys_data["x"], sys_data["y"], sys_data["z"]], axis=1)

    # Standardize the trajectory
    X_mean = X.mean(axis=0)
    X_std = X.std(axis=0)
    X_std[X_std <= 1e-12] = 1.0
    X_standardized = (X - X_mean) / X_std

    # Prepare CSV file
    os.makedirs("experiments", exist_ok=True)
    csv_path = "experiments/lorenz_autonomous_metrics.csv"
    
    cycles = [1, 2, 3, 4, 5]
    epochs_per_cycle = {1: 10, 2: 20, 3: 30, 4: 40, 5: 50}
    
    metrics = []
    prev_activations = None

    for cycle in cycles:
        epochs = epochs_per_cycle[cycle]
        print(f"\n--- Cycle {cycle} (Epochs: {epochs}) ---")
        
        # Initialize and train Neural ODE
        model = NeuralODEModel(input_dim=3, hidden_dim=64, num_layers=3)
        t_grid = np.arange(len(X_standardized)) * 0.01
        
        # Train
        model.fit(t_grid, X_standardized, epochs=epochs, lr=0.01)
        
        # Extract activations
        curr_activations = get_hidden_activations(model, X_standardized)
        
        # Compute CKA
        if cycle == 1:
            cka_val = 1.0
        else:
            cka_val = compute_cka(curr_activations, prev_activations)
            
        # Compute EV3
        ev3_val = compute_ev3(curr_activations)
        
        # Discovers symbolic equations
        pred_derivatives = model.ode_func(torch.tensor(0.0), torch.tensor(X_standardized, dtype=torch.float32)).detach().cpu().numpy()
        var_names = ["x", "y", "z"]
        eq_x = deterministic_symbolic_recovery(X_standardized, pred_derivatives[:, 0], var_names)
        eq_y = deterministic_symbolic_recovery(X_standardized, pred_derivatives[:, 1], var_names)
        eq_z = deterministic_symbolic_recovery(X_standardized, pred_derivatives[:, 2], var_names)
        
        print(f"Cycle {cycle} Discovered Equations:")
        print(f"  dx/dt = {eq_x}")
        print(f"  dy/dt = {eq_y}")
        print(f"  dz/dt = {eq_z}")
        print(f"Cycle {cycle} Metrics: CKA = {cka_val:.6f}, EV3 = {ev3_val:.6e}")
        
        metrics.append({
            "cycle": cycle,
            "cka": cka_val,
            "ev3": ev3_val
        })
        
        prev_activations = curr_activations

    # Save to CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["cycle", "cka", "ev3"])
        writer.writeheader()
        for m in metrics:
            writer.writerow(m)
            
    print(f"\n✅ Successfully generated and saved metrics to {csv_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
