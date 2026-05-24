import os
import sys
import numpy as np
import torch
from torchdiffeq import odeint

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure global reproducibility
torch.manual_seed(42)
np.random.seed(42)


class ODEFunc(torch.nn.Module):
    """
    MLP network mapping state x to its derivative dx/dt = f(t, x).
    Architecture: [input_dim, hidden_dim, ..., input_dim] with Tanh activations.
    """

    def __init__(self, input_dim, hidden_dim=64, num_layers=3):
        super().__init__()
        torch.manual_seed(42)

        layers = []
        # Input layer
        layers.append(torch.nn.Linear(input_dim, hidden_dim))
        layers.append(torch.nn.Tanh())

        # Hidden layers
        for _ in range(num_layers - 1):
            layers.append(torch.nn.Linear(hidden_dim, hidden_dim))
            layers.append(torch.nn.Tanh())

        # Output layer
        layers.append(torch.nn.Linear(hidden_dim, input_dim))

        self.net = torch.nn.Sequential(*layers)

    def forward(self, t, x):
        # f(t, x) is time-invariant here as standard for autonomous ODEs
        return self.net(x)


class NeuralODEModel:
    """
    Wrapper model implementing Neural Ordinary Differential Equations (Neural ODEs)
    using torchdiffeq for continuous-time integration.
    """

    def __init__(self, input_dim, hidden_dim=64, num_layers=3):
        torch.manual_seed(42)
        self.ode_func = ODEFunc(input_dim, hidden_dim, num_layers).to(
            dtype=torch.get_default_dtype()
        )
        self.input_dim = input_dim

    def forward(self, x0, t):
        """
        Integrates the ODE forward in time starting from x0 using the RK4 solver.
        """
        return odeint(self.ode_func, x0, t, method="rk4")

    def fit(self, t, X_obs, epochs=500, lr=0.001):
        """
        Trains the ODEFunc parameters using standard Adam optimizer to minimize
        MSE between predicted integration trajectory and observed trajectory.
        """
        torch.manual_seed(42)

        if not isinstance(t, torch.Tensor):
            t = torch.tensor(t, dtype=torch.get_default_dtype())
        if not isinstance(X_obs, torch.Tensor):
            X_obs = torch.tensor(X_obs, dtype=torch.get_default_dtype())

        # If X_obs is 2D (n_timesteps, input_dim), unsqueeze to 3D (n_timesteps, 1, input_dim)
        if len(X_obs.shape) == 2:
            X_obs_3d = X_obs.unsqueeze(1)
        else:
            X_obs_3d = X_obs

        # Initial condition: first timestep
        x0 = X_obs_3d[0]  # (batch_size, input_dim)

        optimizer = torch.optim.Adam(self.ode_func.parameters(), lr=lr)
        loss_fn = torch.nn.MSELoss()

        self.ode_func.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            # Predict full trajectory
            pred = self.forward(x0, t)  # (n_timesteps, batch_size, input_dim)
            loss = loss_fn(pred, X_obs_3d)
            loss.backward()
            optimizer.step()

            if (epoch + 1) % 100 == 0 or epoch == 0:
                print(
                    f"[Neural ODE] Epoch {epoch + 1:3d}/{epochs:3d} | Loss (MSE): {loss.item():.6f}"
                )

        return self

    def predict(self, x0, t):
        """
        Predicts trajectory in evaluation mode (no gradients tracked).
        Returns prediction as a numpy array.
        """
        self.ode_func.eval()

        if not isinstance(x0, torch.Tensor):
            x0 = torch.tensor(x0, dtype=torch.get_default_dtype())
        if not isinstance(t, torch.Tensor):
            t = torch.tensor(t, dtype=torch.get_default_dtype())

        # Ensure x0 has batch dimension
        if len(x0.shape) == 1:
            x0 = x0.unsqueeze(0)

        with torch.no_grad():
            pred = self.forward(x0, t)

        # Squeeze batch size 1 for single-trajectory output
        return pred.squeeze(1).cpu().numpy()

    def save(self, path):
        """
        Saves the model weights to disk.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(self.ode_func.state_dict(), path)
        print(f"[INFO] Neural ODE weights saved successfully to: {path}")

    def load(self, path):
        """
        Loads the model weights from disk.
        """
        self.ode_func.load_state_dict(torch.load(path))
        print(f"[INFO] Neural ODE weights loaded successfully from: {path}")


def train_neural_ode_on_system(system_name, n_timesteps=1000, epochs=300):
    """
    Generates synthetic trajectories, trains a Neural ODE on the first half (T),
    forecasts the second half (2*T), and computes long-term prediction relative L2 error.
    """
    torch.manual_seed(42)
    np.random.seed(42)

    print(f"\n--- Training Neural ODE on system: {system_name.upper()} ---")

    # Import local synthetic system generators
    import synthetic_systems

    # 1. Generate full trajectory
    name = system_name.lower()
    if name == "lorenz":
        sys_data = synthetic_systems.generate_lorenz(n_timesteps=n_timesteps, dt=0.01)
        X = np.stack([sys_data["x"], sys_data["y"], sys_data["z"]], axis=1)
    elif name == "rossler" or name == "rössler":
        sys_data = synthetic_systems.generate_rossler(n_timesteps=n_timesteps, dt=0.01)
        X = np.stack([sys_data["x"], sys_data["y"], sys_data["z"]], axis=1)
    elif name == "duffing":
        sys_data = synthetic_systems.generate_duffing(n_timesteps=n_timesteps, dt=0.01)
        X = np.stack([sys_data["x"], sys_data["v"]], axis=1)
    elif name == "van_der_pol" or name == "vanderpol":
        sys_data = synthetic_systems.generate_vanderpol(
            n_timesteps=n_timesteps, dt=0.01
        )
        X = np.stack([sys_data["x"], sys_data["y"]], axis=1)
    elif name == "logistic":
        sys_data = synthetic_systems.generate_logistic(n_timesteps=n_timesteps, r=3.9)
        X = sys_data["x"].reshape(-1, 1)  # 1D map
    else:
        raise ValueError(f"Unknown system name: {system_name}")

    # 2. Divide into Train (first T steps) and Forecast (unseen T steps)
    train_len = n_timesteps // 2
    X_train = X[:train_len]
    t_train = np.arange(train_len) * 0.01

    # 3. Initialize and fit Neural ODE
    input_dim = X.shape[1]
    model = NeuralODEModel(input_dim=input_dim, hidden_dim=64, num_layers=3)
    model.fit(t_train, X_train, epochs=epochs, lr=0.001)

    # 4. Predict long-term trajectory (full 2*T steps)
    t_full = np.arange(n_timesteps) * 0.01
    X_pred = model.predict(X[0], t_full)

    # 5. Evaluate relative L2 error on unseen test half
    X_test = X[train_len:]
    X_pred_test = X_pred[train_len:]

    relative_l2_error = np.linalg.norm(X_test - X_pred_test) / (
        np.linalg.norm(X_test) + 1e-8
    )
    print(f"  [EVAL] Unseen Forecasting Relative L2 Error: {relative_l2_error:.4f}")

    # 6. Save model parameters
    output_path = f"artifacts/neural_ode_{name}.pth"
    model.save(output_path)

    return model, float(relative_l2_error)
