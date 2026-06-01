import os
import torch
import torch.nn as nn
from torchdiffeq import odeint


class SharedODEFunc(nn.Module):
    """
    MLP network mapping state x to its derivative dx/dt = f(t, x).
    Supports additional time-invariant parameter inputs concatenated with the state.
    """

    def __init__(self, input_dim=4, hidden_dim=64, num_layers=3, extra_dim=0):
        super().__init__()
        self.input_dim = input_dim
        self.extra_dim = extra_dim
        self.params = (
            None  # Placeholder for parameter tensors (e.g. [power, area, emissivity])
        )

        layers = []
        layers.append(nn.Linear(input_dim + extra_dim, hidden_dim))
        layers.append(nn.Tanh())
        for _ in range(num_layers - 1):
            layers.append(nn.Linear(hidden_dim, hidden_dim))
            layers.append(nn.Tanh())
        layers.append(nn.Linear(hidden_dim, input_dim))

        self.net = nn.Sequential(*layers)

    def forward(self, t, y):
        # f(t, y) is time-invariant here as standard for autonomous ODEs
        if self.extra_dim > 0:
            if self.params is None:
                raise ValueError(
                    "Parameters (self.params) must be set prior to running forward integration."
                )
            inputs = torch.cat([y, self.params], dim=-1)
        else:
            inputs = y
        return self.net(inputs)


class SharedNeuralODEModel:
    """
    Wrapper model implementing Neural Ordinary Differential Equations (Neural ODEs).
    """

    def __init__(self, input_dim, hidden_dim=64, num_layers=3, extra_dim=0):
        self.ode_func = SharedODEFunc(input_dim, hidden_dim, num_layers, extra_dim).to(
            dtype=torch.get_default_dtype()
        )
        self.input_dim = input_dim

    def forward(self, x0, t, method="rk4"):
        return odeint(self.ode_func, x0, t, method=method)
