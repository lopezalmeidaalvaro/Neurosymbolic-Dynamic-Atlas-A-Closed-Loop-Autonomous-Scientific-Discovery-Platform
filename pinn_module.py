import os
import sys
import time
import numpy as np

# Force DeepXDE PyTorch backend BEFORE importing deepxde
os.environ["DDE_BACKEND"] = "pytorch"

import torch
import deepxde as dde

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Configure DeepXDE float64 precision and global reproducibility seed
dde.config.set_default_float("float64")
dde.config.set_random_seed(42)
torch.manual_seed(42)
np.random.seed(42)


def solve_ode_with_pinn(ode_system, t_domain, initial_conditions, params, epochs=3000):
    """
    Solves a forward ODE system (Lorenz or Rössler) using a Physics-Informed Neural Network (PINN).
    Trains the network using a hybrid strategy: Adam optimizer followed by L-BFGS tuning.
    """
    dde.config.set_random_seed(42)
    torch.manual_seed(42)

    t_min, t_max = t_domain
    geom = dde.geometry.TimeDomain(t_min, t_max)

    # 1. Define ODE PDE residual equations
    system = ode_system.lower()
    if system == "lorenz":
        sigma = params.get("sigma", 10.0)
        rho = params.get("rho", 28.0)
        beta = params.get("beta", 8.0 / 3.0)

        def lorenz_pde(t, y):
            x, y_val, z = y[:, 0:1], y[:, 1:2], y[:, 2:3]
            dx_dt = dde.grad.jacobian(y, t, i=0, j=0)
            dy_dt = dde.grad.jacobian(y, t, i=1, j=0)
            dz_dt = dde.grad.jacobian(y, t, i=2, j=0)
            return [
                dx_dt - sigma * (y_val - x),
                dy_dt - (x * (rho - z) - y_val),
                dz_dt - (x * y_val - beta * z),
            ]

        pde_fn = lorenz_pde
        num_components = 3

    elif system == "rossler" or system == "rössler":
        a = params.get("a", 0.2)
        b = params.get("b", 0.2)
        c = params.get("c", 5.7)

        def rossler_pde(t, y):
            x, y_val, z = y[:, 0:1], y[:, 1:2], y[:, 2:3]
            dx_dt = dde.grad.jacobian(y, t, i=0, j=0)
            dy_dt = dde.grad.jacobian(y, t, i=1, j=0)
            dz_dt = dde.grad.jacobian(y, t, i=2, j=0)
            return [
                dx_dt - (-y_val - z),
                dy_dt - (x + a * y_val),
                dz_dt - (b + z * (x - c)),
            ]

        pde_fn = rossler_pde
        num_components = 3

    elif system == "duffing":
        delta = params.get("delta", 0.3)
        alpha = params.get("alpha", -1.0)
        beta = params.get("beta", 1.0)

        def duffing_pde(t, y):
            x, v = y[:, 0:1], y[:, 1:2]
            dx_dt = dde.grad.jacobian(y, t, i=0, j=0)
            dv_dt = dde.grad.jacobian(y, t, i=1, j=0)
            return [dx_dt - v, dv_dt - (-delta * v - alpha * x - beta * (x**3))]

        pde_fn = duffing_pde
        num_components = 2

    elif system == "van_der_pol" or system == "vanderpol":
        mu = params.get("mu", 1.0)

        def vanderpol_pde(t, y):
            x, y_val = y[:, 0:1], y[:, 1:2]
            dx_dt = dde.grad.jacobian(y, t, i=0, j=0)
            dy_dt = dde.grad.jacobian(y, t, i=1, j=0)
            return [dx_dt - y_val, dy_dt - (mu * (1.0 - x**2) * y_val - x)]

        pde_fn = vanderpol_pde
        num_components = 2

    else:
        raise ValueError(f"Unknown forward ODE system: {ode_system}")

    # 2. Map initial conditions
    if isinstance(initial_conditions, dict):
        ic_vals = [
            initial_conditions.get("x", 0.0),
            initial_conditions.get("y", 0.0),
            initial_conditions.get("z", 0.0),
        ][:num_components]
    else:
        ic_vals = list(initial_conditions)[:num_components]

    ic_constraints = []

    def boundary_initial(t, on_initial):
        return on_initial

    def make_ic_fn(v_val):
        return lambda x: v_val

    for idx, val in enumerate(ic_vals):
        ic_constraints.append(
            dde.icbc.IC(geom, make_ic_fn(val), boundary_initial, component=idx)
        )

    # 3. PDE Data Setup
    data = dde.data.PDE(
        geom, pde_fn, ic_constraints, num_domain=400, num_boundary=2, num_test=100
    )

    # 4. FNN Network & Model Creation
    layer_sizes = [1] + [64] * 3 + [num_components]
    net = dde.nn.FNN(layer_sizes, "tanh", "Glorot normal")
    model = dde.Model(data, net)

    # 5. Hybrid Optimization training
    print(f"[PINN] Training with Adam optimizer ({epochs} epochs)...")
    model.compile("adam", lr=0.001)
    model.train(iterations=epochs)

    if epochs >= 200:
        print("[PINN] Fine-tuning with L-BFGS optimizer...")
        try:
            model.compile("L-BFGS")
            # Limit L-BFGS to a few outer iterations to ensure lightning fast execution under test/short-budget runs
            model.train(iterations=min(epochs, 10))
        except Exception as e:
            print(
                f"[WARNING] L-BFGS fine-tuning failed: {e}. Falling back to Adam weights."
            )
    else:
        print(
            "[PINN] Bypassing L-BFGS fine-tuning due to short budget (epochs < 200)..."
        )

    # 6. Evaluate on fine-grained grid
    t_grid = np.linspace(t_min, t_max, 1000).reshape(-1, 1)
    y_pred = model.predict(t_grid)

    return model, y_pred


def discover_parameters_with_pinn(
    ode_system,
    observed_data,
    t_observed,
    variable_params,
    knowledge_graph=None,
    epochs=2000,
):
    """
    Uses PINN in inverse mode to discover physical parameters from noisy observed trajectories.
    Parameters are registered as backend-agnostic trainable variables.
    """
    dde.config.set_random_seed(42)
    torch.manual_seed(42)

    t_min, t_max = float(np.min(t_observed)), float(np.max(t_observed))
    geom = dde.geometry.TimeDomain(t_min, t_max)

    # 1. Define unknown external parameters as trainable dde.Variables
    ext_vars = []
    var_dict = {}
    for param in variable_params:
        # High quality initial guesses
        val = 1.0
        if param == "sigma":
            val = 5.0
        elif param == "rho":
            val = 20.0
        elif param == "beta":
            val = 2.0
        elif param == "a":
            val = 0.1
        elif param == "c":
            val = 3.0

        v = dde.Variable(val)
        ext_vars.append(v)
        var_dict[param] = v

    # 2. Define Inverse PDE residuals referencing external variables
    system = ode_system.lower()
    if system == "lorenz":

        def lorenz_inverse_pde(t, y):
            x, y_val, z = y[:, 0:1], y[:, 1:2], y[:, 2:3]
            dx_dt = dde.grad.jacobian(y, t, i=0, j=0)
            dy_dt = dde.grad.jacobian(y, t, i=1, j=0)
            dz_dt = dde.grad.jacobian(y, t, i=2, j=0)

            s = var_dict.get("sigma", 10.0)
            r = var_dict.get("rho", 28.0)
            b = var_dict.get("beta", 8.0 / 3.0)

            return [
                dx_dt - s * (y_val - x),
                dy_dt - (x * (r - z) - y_val),
                dz_dt - (x * y_val - b * z),
            ]

        pde_fn = lorenz_inverse_pde
        num_components = 3

    elif system == "rossler" or system == "rössler":

        def rossler_inverse_pde(t, y):
            x, y_val, z = y[:, 0:1], y[:, 1:2], y[:, 2:3]
            dx_dt = dde.grad.jacobian(y, t, i=0, j=0)
            dy_dt = dde.grad.jacobian(y, t, i=1, j=0)
            dz_dt = dde.grad.jacobian(y, t, i=2, j=0)

            a = var_dict.get("a", 0.2)
            b = var_dict.get("b", 0.2)
            c = var_dict.get("c", 5.7)

            return [
                dx_dt - (-y_val - z),
                dy_dt - (x + a * y_val),
                dz_dt - (b + z * (x - c)),
            ]

        pde_fn = rossler_inverse_pde
        num_components = 3

    else:
        raise ValueError(f"Unknown inverse ODE system: {ode_system}")

    # 3. Fit observed data using PointSetBC constraints
    t_observed_2d = (
        t_observed.reshape(-1, 1) if len(t_observed.shape) == 1 else t_observed
    )
    observe_constraints = []

    for idx in range(num_components):
        bc = dde.icbc.PointSetBC(
            t_observed_2d, observed_data[:, idx : idx + 1], component=idx
        )
        observe_constraints.append(bc)

    # 4. Inverse PDE Data setup
    # observed data points are added as anchors to force evaluations at observed times
    data = dde.data.PDE(
        geom,
        pde_fn,
        observe_constraints,
        num_domain=400,
        num_boundary=2,
        anchors=t_observed_2d,
    )

    # 5. Network & Model Compile with external variables
    layer_sizes = [1] + [64] * 3 + [num_components]
    net = dde.nn.FNN(layer_sizes, "tanh", "Glorot normal")
    model = dde.Model(data, net)

    print(
        f"[PINN Inverse] Estimating physical parameters {variable_params} using Adam..."
    )
    model.compile("adam", lr=0.001, external_trainable_variables=ext_vars)
    model.train(iterations=epochs)

    if epochs >= 200:
        print("[PINN Inverse] Fine-tuning estimates using L-BFGS...")
        try:
            model.compile("L-BFGS", external_trainable_variables=ext_vars)
            # Limit L-BFGS to a few outer iterations to ensure lightning fast execution under test/short-budget runs
            model.train(iterations=min(epochs, 10))
        except Exception as e:
            print(
                f"[WARNING] L-BFGS fine-tuning in parameter discovery failed: {e}. Falling back to Adam weights."
            )
    else:
        print(
            "[PINN Inverse] Bypassing L-BFGS fine-tuning due to short budget (epochs < 200)..."
        )

    # 6. Retrieve estimated variables
    discovered_vals = {}
    for param, v in var_dict.items():
        val = float(v.detach().cpu().item())
        discovered_vals[param] = val

    print(f"[PINN Inverse] Discovered Parameters: {discovered_vals}")

    # 7. Knowledge Graph Integration
    if knowledge_graph:
        try:
            for param, val in discovered_vals.items():
                obs_id = f"obs_pinn_{param}_{int(time.time())}"
                knowledge_graph.create_observable(
                    observable_id=obs_id,
                    name=param,
                    type="physical_parameter",
                    description=f"Parameter {param} discovered via inverse PINN. Estimated value: {val:.4f}",
                )
            print(
                "[INFO] Discovered parameters logged to ScientificKnowledgeGraph successfully."
            )
        except Exception as e:
            print(f"[WARNING] Bypassed Knowledge Graph logging: {e}")

    return discovered_vals


def pinn_forecast(model, t_future):
    """
    Forecasts dynamical trajectory for future coordinates beyond domain.
    """
    if not isinstance(t_future, np.ndarray):
        t_future = np.array(t_future)
    if len(t_future.shape) == 1:
        t_future = t_future.reshape(-1, 1)

    return model.predict(t_future)
