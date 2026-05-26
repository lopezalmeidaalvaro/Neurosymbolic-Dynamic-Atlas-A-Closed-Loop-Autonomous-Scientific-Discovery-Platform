import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import os
import sys
import numpy as np
import torch

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure reproducibility
torch.manual_seed(42)
np.random.seed(42)


class DeepONet(torch.nn.Module):
    """
    Deep Operator Network (DeepONet) mapping input function u (evaluated at m points)
    to output solution function G(u) evaluated at coordinates y.
    G(u)(y) = sum_{k=1}^p branch_k(u) * trunk_k(y)
    """

    def __init__(
        self, branch_input_dim, trunk_input_dim=1, hidden_dim=64, output_dim=10
    ):
        super().__init__()
        torch.manual_seed(42)

        # Branch Network: processes sensor evaluations of input functions
        self.branch = torch.nn.Sequential(
            torch.nn.Linear(branch_input_dim, hidden_dim),
            torch.nn.Tanh(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.Tanh(),
            torch.nn.Linear(hidden_dim, output_dim),
        )

        # Trunk Network: processes output evaluation coordinates
        self.trunk = torch.nn.Sequential(
            torch.nn.Linear(trunk_input_dim, hidden_dim),
            torch.nn.Tanh(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.Tanh(),
            torch.nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, u, y):
        """
        u: shape (batch, branch_input_dim)
        y: shape (batch, n_points, trunk_input_dim)
        Returns: shape (batch, n_points, 1)
        """
        # Branch features B: (batch, output_dim)
        B = self.branch(u)

        # Trunk features T: (batch, n_points, output_dim)
        batch_size, n_points, y_dim = y.shape
        y_flat = y.view(-1, y_dim)
        T_flat = self.trunk(y_flat)
        T = T_flat.view(batch_size, n_points, -1)

        # Compute dot-product: sum_k B_k * T_k
        # Expand B to (batch, 1, output_dim) to multiply with T
        out = torch.sum(B.unsqueeze(1) * T, dim=2, keepdim=True)
        return out


def train_deeponet(model, u_train, y_train, G_train, epochs=1000, lr=0.001):
    """
    Trains DeepONet to minimize the relative L2 error on solution function datasets.
    """
    torch.manual_seed(42)

    # Standardize tensors
    if not isinstance(u_train, torch.Tensor):
        u_train = torch.tensor(u_train, dtype=torch.get_default_dtype())
    if not isinstance(y_train, torch.Tensor):
        y_train = torch.tensor(y_train, dtype=torch.get_default_dtype())
    if not isinstance(G_train, torch.Tensor):
        G_train = torch.tensor(G_train, dtype=torch.get_default_dtype())

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        pred = model(u_train, y_train)  # (batch, n_points, 1)

        # Relative L2 Loss: ||pred - G||_2 / ||G||_2
        diff_norm = torch.norm(pred - G_train, p=2, dim=1)
        target_norm = torch.norm(G_train, p=2, dim=1)
        loss = torch.mean(diff_norm / (target_norm + 1e-8))

        loss.backward()
        optimizer.step()

        if (epoch + 1) % 200 == 0 or epoch == 0:
            print(
                f"[DeepONet] Epoch {epoch + 1:4d}/{epochs:4d} | Rel L2 Loss: {loss.item():.6f}"
            )

    return model


def learn_ode_solution_operator(
    ode_system, param_range, n_samples=100, m=50, epochs=500
):
    """
    Generates dynamic trajectory datasets by sweeping physical parameter ranges,
    and trains a DeepONet to act as the solution operator mapping parameters to ODE solutions.
    """
    torch.manual_seed(42)
    np.random.seed(42)

    print(f"\n--- Learning solution operator for system: {ode_system.upper()} ---")

    # 1. Determine parameters to sweep
    param_name = list(param_range.keys())[0]
    p_min, p_max = param_range[param_name]

    # Define coordinate grid (time coordinates y)
    t_grid = np.linspace(0, 5.0, 100)  # 100 coordinate points
    n_points = len(t_grid)

    u_data = []  # branch inputs: parameters evaluated at m points
    y_data = []  # trunk inputs: time coordinates
    G_data = []  # G(u)(y): trajectories (e.g. x-component)

    import synthetic_systems

    # 2. Generate samples
    for i in range(n_samples):
        # Sample parameter value
        p_val = float(np.random.uniform(p_min, p_max))

        # Generate dynamic solver trajectory
        if ode_system.lower() == "lorenz":
            # Lorenz with varying rho
            sys_data = synthetic_systems.generate_lorenz(
                n_timesteps=n_points, dt=0.05, rho=p_val
            )
            traj = sys_data["x"]
        elif ode_system.lower() == "rossler" or ode_system.lower() == "rössler":
            sys_data = synthetic_systems.generate_rossler(
                n_timesteps=n_points, dt=0.05, c=p_val
            )
            traj = sys_data["x"]
        else:
            # Fallback Duffing
            sys_data = synthetic_systems.generate_duffing(n_timesteps=n_points, dt=0.05)
            traj = sys_data["x"]

        # Format as DeepONet shapes
        u_data.append(np.full(m, p_val))  # input function u(x) = p_val constant
        y_data.append(t_grid.reshape(-1, 1))  # coordinates
        G_data.append(traj.reshape(-1, 1))  # solutions

    u_data = np.array(u_data)  # (n_samples, m)
    y_data = np.array(y_data)  # (n_samples, n_points, 1)
    G_data = np.array(G_data)  # (n_samples, n_points, 1)

    # 3. Split into Train (80%) and Test (20%)
    split = int(n_samples * 0.8)
    u_train, u_test = u_data[:split], u_data[split:]
    y_train, y_test = y_data[:split], y_data[split:]
    G_train, G_test = G_data[:split], G_data[split:]

    # 4. Instantiate and Train DeepONet
    model = DeepONet(
        branch_input_dim=m, trunk_input_dim=1, hidden_dim=64, output_dim=10
    ).to(dtype=torch.get_default_dtype())
    train_deeponet(model, u_train, y_train, G_train, epochs=epochs, lr=0.002)

    # 5. Evaluate on unseen test operator functions
    model.eval()
    u_test_t = torch.tensor(u_test, dtype=torch.get_default_dtype())
    y_test_t = torch.tensor(y_test, dtype=torch.get_default_dtype())
    G_test_t = torch.tensor(G_test, dtype=torch.get_default_dtype())

    with torch.no_grad():
        pred_test = model(u_test_t, y_test_t)

    diff_norm = torch.norm(pred_test - G_test_t, p=2, dim=1)
    target_norm = torch.norm(G_test_t, p=2, dim=1)
    test_rel_l2 = float(torch.mean(diff_norm / (target_norm + 1e-8)).item())

    print(f"  [EVAL] Operator Unseen Test L2 Relative Error: {test_rel_l2:.4f}")

    return model, test_rel_l2


def apply_operator(model, u_new, y_grid):
    """
    Applies the learned operator to a new input function u_new.
    Returns the predicted values.
    """
    model.eval()
    if not isinstance(u_new, torch.Tensor):
        u_new = torch.tensor(u_new, dtype=torch.get_default_dtype())
    if not isinstance(y_grid, torch.Tensor):
        y_grid = torch.tensor(y_grid, dtype=torch.get_default_dtype())

    # Ensure dimensions are matched
    if len(u_new.shape) == 1:
        u_new = u_new.unsqueeze(0)  # (1, m)
    if len(y_grid.shape) == 1:
        y_grid = y_grid.reshape(1, -1, 1)  # (1, n, 1)
    elif len(y_grid.shape) == 2:
        y_grid = y_grid.unsqueeze(0)  # (1, n, 1)

    with torch.no_grad():
        pred = model(u_new, y_grid)

    return pred.squeeze(0).cpu().numpy()
