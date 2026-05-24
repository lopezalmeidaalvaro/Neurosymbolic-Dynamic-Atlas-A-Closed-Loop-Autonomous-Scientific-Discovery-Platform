"""Small Neural ODE implementation used by the reproducible pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import torch
from torchdiffeq import odeint


class ODEFunc(torch.nn.Module):
    """Multilayer perceptron parameterizing an autonomous vector field.

    Args:
        input_dim: State-space dimensionality.
        hidden_dim: Width of hidden layers.
        num_layers: Number of hidden layers.

    Returns:
        A PyTorch module mapping ``x`` to ``dx/dt``.

    Raises:
        ValueError: If dimensions or layer counts are invalid.
    """

    def __init__(self, input_dim: int, hidden_dim: int = 32, num_layers: int = 2):
        super().__init__()
        if input_dim <= 0:
            raise ValueError("input_dim must be positive.")
        if hidden_dim <= 0:
            raise ValueError("hidden_dim must be positive.")
        if num_layers <= 0:
            raise ValueError("num_layers must be positive.")

        layers: list[torch.nn.Module] = [
            torch.nn.Linear(input_dim, hidden_dim),
            torch.nn.Tanh(),
        ]
        for _ in range(num_layers - 1):
            layers.extend([torch.nn.Linear(hidden_dim, hidden_dim), torch.nn.Tanh()])
        layers.append(torch.nn.Linear(hidden_dim, input_dim))
        self.net = torch.nn.Sequential(*layers)

    def forward(self, t: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        """Evaluate the vector field.

        Args:
            t: Scalar integration time supplied by ``torchdiffeq``.
            x: State tensor with shape ``(batch, input_dim)``.

        Returns:
            Derivative tensor with the same shape as ``x``.

        Raises:
            RuntimeError: If tensor shapes are incompatible with the network.
        """
        del t
        return self.net(x)


@dataclass
class NeuralODEModel:
    """Trainable Neural ODE wrapper with loss-history tracking.

    Args:
        input_dim: State-space dimensionality.
        hidden_dim: Width of hidden layers.
        num_layers: Number of hidden layers.
        method: Numerical solver passed to ``torchdiffeq.odeint``.

    Returns:
        A model capable of fitting and forecasting continuous trajectories.

    Raises:
        ValueError: If model dimensions are invalid.
    """

    input_dim: int
    hidden_dim: int = 32
    num_layers: int = 2
    method: str = "rk4"
    loss_history: list[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize the internal vector-field network.

        Args:
            None.

        Returns:
            None.

        Raises:
            ValueError: If constructor arguments are invalid.
        """
        self.ode_func = ODEFunc(self.input_dim, self.hidden_dim, self.num_layers).to(
            dtype=torch.float64
        )

    def forward(self, x0: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """Integrate the learned ODE from an initial state.

        Args:
            x0: Initial state with shape ``(batch, input_dim)``.
            t: One-dimensional tensor of integration times.

        Returns:
            Predicted trajectory with shape ``(len(t), batch, input_dim)``.

        Raises:
            RuntimeError: If integration fails.
        """
        return odeint(self.ode_func, x0, t, method=self.method)

    def fit(
        self,
        t: np.ndarray | torch.Tensor,
        trajectory: np.ndarray | torch.Tensor,
        epochs: int = 50,
        lr: float = 1e-2,
    ) -> list[float]:
        """Fit the Neural ODE to a single observed trajectory.

        Args:
            t: One-dimensional time grid.
            trajectory: Observed states with shape ``(n_steps, input_dim)``.
            epochs: Number of Adam optimization steps.
            lr: Adam learning rate.

        Returns:
            Per-epoch mean squared error losses.

        Raises:
            ValueError: If input shapes, epoch count, or learning rate are invalid.
        """
        if epochs <= 0:
            raise ValueError("epochs must be positive.")
        if lr <= 0:
            raise ValueError("lr must be positive.")

        t_tensor = torch.as_tensor(t, dtype=torch.float64)
        y_tensor = torch.as_tensor(trajectory, dtype=torch.float64)
        if t_tensor.ndim != 1:
            raise ValueError("t must be one-dimensional.")
        if y_tensor.ndim != 2 or y_tensor.shape[1] != self.input_dim:
            raise ValueError("trajectory must have shape (n_steps, input_dim).")
        if y_tensor.shape[0] != t_tensor.shape[0]:
            raise ValueError("t and trajectory must have matching step counts.")

        target = y_tensor.unsqueeze(1)
        x0 = target[0]
        optimizer = torch.optim.Adam(self.ode_func.parameters(), lr=lr)
        loss_fn = torch.nn.MSELoss()

        self.loss_history = []
        self.ode_func.train()
        for _ in range(epochs):
            optimizer.zero_grad()
            prediction = self.forward(x0, t_tensor)
            loss = loss_fn(prediction, target)
            loss.backward()
            optimizer.step()
            self.loss_history.append(float(loss.detach().cpu().item()))
        return self.loss_history

    def predict(
        self, x0: np.ndarray | torch.Tensor, t: np.ndarray | torch.Tensor
    ) -> np.ndarray:
        """Forecast a trajectory from an initial state.

        Args:
            x0: Initial state with shape ``(input_dim,)`` or ``(1, input_dim)``.
            t: One-dimensional time grid.

        Returns:
            Forecast trajectory as a NumPy array with shape ``(len(t), input_dim)``.

        Raises:
            ValueError: If input dimensions are invalid.
        """
        x0_tensor = torch.as_tensor(x0, dtype=torch.float64)
        t_tensor = torch.as_tensor(t, dtype=torch.float64)
        if x0_tensor.ndim == 1:
            x0_tensor = x0_tensor.unsqueeze(0)
        if x0_tensor.ndim != 2 or x0_tensor.shape[1] != self.input_dim:
            raise ValueError("x0 must have shape (input_dim,) or (1, input_dim).")
        if t_tensor.ndim != 1:
            raise ValueError("t must be one-dimensional.")

        self.ode_func.eval()
        with torch.no_grad():
            prediction = self.forward(x0_tensor, t_tensor)
        return prediction.squeeze(1).cpu().numpy()


def generate_harmonic_oscillator(
    n_steps: int = 80, dt: float = 0.05
) -> tuple[np.ndarray, np.ndarray]:
    """Generate a unit harmonic oscillator trajectory.

    Args:
        n_steps: Number of trajectory samples.
        dt: Time step between samples.

    Returns:
        Tuple ``(t, x)`` where ``t`` has shape ``(n_steps,)`` and ``x`` has
        shape ``(n_steps, 2)`` containing position and velocity.

    Raises:
        ValueError: If ``n_steps`` or ``dt`` is not positive.
    """
    if n_steps <= 1:
        raise ValueError("n_steps must be greater than one.")
    if dt <= 0:
        raise ValueError("dt must be positive.")

    t = np.arange(n_steps, dtype=float) * dt
    x = np.column_stack([np.cos(t), -np.sin(t)])
    return t, x
