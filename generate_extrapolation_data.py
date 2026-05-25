import os
import sys
import numpy as np
import torch
from scipy.integrate import solve_ivp

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

def make_eval_func(expr_str):
    if not expr_str or not expr_str.strip():
        return lambda x, y, z: 0.0
    cleaned = expr_str.strip()
    cleaned = cleaned.replace("sin(", "np.sin(").replace("cos(", "np.cos(")
    
    def f(x, y, z):
        try:
            return float(eval(cleaned, {"np": np, "x": x, "y": y, "z": z}))
        except Exception:
            return 0.0
    return f

def main():
    print("=" * 60)
    print("🔮 STARTING LORENZ EXTRAPOLATION DATA GENERATION")
    print("=" * 60)

    # 1. Ingest Lorenz dynamics from t=0 to 5 (500 timesteps, dt=0.01)
    print("Generating train Lorenz trajectory (t in [0, 5])...")
    sys_data_train = generate_lorenz(n_timesteps=500, dt=0.01, sigma=10, rho=28, beta=8/3)
    X_train = np.stack([sys_data_train["x"], sys_data_train["y"], sys_data_train["z"]], axis=1)
    initial_state = X_train[0]
    
    # Standardize data for model stability
    X_mean = X_train.mean(axis=0)
    X_std = X_train.std(axis=0)
    X_std[X_std <= 1e-12] = 1.0
    X_scaled = (X_train - X_mean) / X_std

    # 2. Train Neural ODE on t in [0, 5]
    print("Training Neural ODE Model on standardized trajectory (500 epochs)...")
    model = NeuralODEModel(input_dim=3, hidden_dim=64, num_layers=3)
    t_train = np.arange(500) * 0.01
    model.fit(t_train, X_scaled, epochs=500, lr=0.001)

    # Save Neural ODE checkpoint
    os.makedirs("checkpoints", exist_ok=True)
    model_path = "checkpoints/lorenz_node.pth"
    model.save(model_path)

    # 3. Discover equations using deterministic_symbolic_recovery
    print("Discovering symbolic equations from Neural ODE vector field...")
    pred_derivatives = model.ode_func(torch.tensor(0.0), torch.tensor(X_scaled, dtype=torch.float32)).detach().cpu().numpy()
    var_names = ["x", "y", "z"]
    eq_x = deterministic_symbolic_recovery(X_scaled, pred_derivatives[:, 0], var_names)
    eq_y = deterministic_symbolic_recovery(X_scaled, pred_derivatives[:, 1], var_names)
    eq_z = deterministic_symbolic_recovery(X_scaled, pred_derivatives[:, 2], var_names)

    print("Discovered Symbolic Equations (Standardized Space):")
    print(f"  dx/dt = {eq_x}")
    print(f"  dy/dt = {eq_y}")
    print(f"  dz/dt = {eq_z}")

    # Create evaluate functions for discovered equations
    eval_x = make_eval_func(eq_x)
    eval_y = make_eval_func(eq_y)
    eval_z = make_eval_func(eq_z)

    # 4. Integrate all flows up to t=20 (2000 timesteps, dt=0.01)
    print("Integrating and extrapolating trajectories up to t=20...")
    t_full = np.arange(2000) * 0.01

    # A. True Lorenz dynamics
    def true_lorenz_rhs(t, state):
        cx, cy, cz = state
        return [
            10.0 * (cy - cx),
            cx * (28.0 - cz) - cy,
            cx * cy - (8.0 / 3.0) * cz
        ]
    sol_true = solve_ivp(true_lorenz_rhs, [0.0, 20.0], initial_state, t_eval=t_full, method="RK45")
    X_true = sol_true.y.T # shape (2000, 3)

    # B. Neural ODE predictions (integrated starting from standardized initial state, then un-standardized)
    x0_scaled = (initial_state - X_mean) / X_std
    X_node_scaled = model.predict(x0_scaled, t_full)
    X_node = X_node_scaled * X_std + X_mean

    # C. Discovered Symbolic dynamics (integrated in standardized space, then un-standardized)
    def symbolic_rhs(t, state):
        x, y, z = state
        return [eval_x(x, y, z), eval_y(x, y, z), eval_z(x, y, z)]
    
    sol_sym = solve_ivp(symbolic_rhs, [0.0, 20.0], x0_scaled, t_eval=t_full, method="RK45")
    X_sym_scaled = sol_sym.y.T
    X_sym = X_sym_scaled * X_std + X_mean

    # 5. Save trajectories to experiments/lorenz_extrapolation.npz
    os.makedirs("experiments", exist_ok=True)
    save_path = "experiments/lorenz_extrapolation.npz"
    np.savez(save_path, t=t_full, x_true=X_true, x_node=X_node, x_sym=X_sym)

    print(f"✅ Successfully integrated, extrapolated, and saved trajectories to {save_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
