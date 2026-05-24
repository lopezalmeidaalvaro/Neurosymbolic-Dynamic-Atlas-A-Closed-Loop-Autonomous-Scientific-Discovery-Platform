import os
import sys
import numpy as np
import torch
import deepxde as dde

# Ensure PyTorch backend for DeepXDE
os.environ["DDE_BACKEND"] = "pytorch"

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from neural_ode_module import NeuralODEModel

def extract_neural_ode_features(signal, t=None, model_path=None):
    """
    Fits a minimal Neural ODE on a 1D signal and extracts 8 deep structural features:
    1. Total parameters count.
    2. L2 norm of the last layer weights.
    3. Effective dimension (singular values > 0.01) of the last layer.
    4. Reconstruction MSE of the predicted trajectory.
    5. Mean value of the predicted trajectory.
    6. Standard deviation of the predicted trajectory.
    7. L2 norm of the first layer weights.
    8. Effective dimension (singular values > 0.01) of the first layer.
    """
    try:
        signal = np.array(signal, dtype=np.float64).flatten()
        if len(signal) < 5:
            return np.full(8, np.nan)

        if t is None:
            t = np.linspace(0.0, len(signal) * 0.01, len(signal))
        else:
            t = np.array(t, dtype=np.float64).flatten()

        # Reshape signal to (n_timesteps, 1)
        X_obs = signal.reshape(-1, 1)

        # Initialize lightweight Neural ODE
        torch.manual_seed(42)
        model = NeuralODEModel(input_dim=1, hidden_dim=16, num_layers=2)
        
        # Fit for a tiny number of epochs for high-speed feature extraction
        model.fit(t, X_obs, epochs=50, lr=0.01)

        # 1. Total parameters count
        num_params = float(sum(p.numel() for p in model.ode_func.parameters()))

        # Get weights of layers
        # layers in Sequential: [Linear, Tanh, Linear]
        first_layer = model.ode_func.net[0]
        last_layer = model.ode_func.net[-1]

        # 2. L2 norm of last layer
        last_norm = float(torch.norm(last_layer.weight).item())

        # 3. Effective dimension of last layer (singular values > 0.01)
        W_last = last_layer.weight.detach().cpu().numpy()
        S_last = np.linalg.svd(W_last, compute_uv=False)
        eff_dim_last = float(np.sum(S_last > 0.01))

        # Predict trajectory
        pred = model.predict(signal[0:1], t).flatten()

        # 4. Reconstruction MSE
        rec_error = float(np.mean((pred - signal) ** 2))

        # 5. Mean value of pred
        pred_mean = float(np.mean(pred))

        # 6. Standard deviation of pred
        pred_std = float(np.std(pred))

        # 7. L2 norm of first layer
        first_norm = float(torch.norm(first_layer.weight).item())

        # 8. Effective dimension of first layer
        W_first = first_layer.weight.detach().cpu().numpy()
        S_first = np.linalg.svd(W_first, compute_uv=False)
        eff_dim_first = float(np.sum(S_first > 0.01))

        features = [
            num_params,
            last_norm,
            eff_dim_last,
            rec_error,
            pred_mean,
            pred_std,
            first_norm,
            eff_dim_first
        ]
        return np.array(features, dtype=np.float64)

    except Exception as e:
        print(f"  [ev3_neural WARNING] Neural ODE feature extraction failed: {e}")
        return np.full(8, np.nan)

def extract_pinn_features(signal, t=None, system_hint=None):
    """
    Fits a simple physics decay model (dx/dt + k*x = 0) on a 1D signal using PINN,
    and extracts 8 physical features:
    1. Discovered decay parameter 'k' value.
    2. Trajectory fit error (MSE).
    3. Mean absolute value of the physical residual.
    4. Standard deviation of the physical residual.
    5. Fit error at the initial condition.
    6. Fit error at the final timestep.
    7. Standard deviation of the predicted trajectory.
    8. Numeric derivative variance.
    """
    try:
        signal = np.array(signal, dtype=np.float64).flatten()
        if len(signal) < 5:
            return np.full(8, np.nan)

        if t is None:
            t = np.linspace(0.0, len(signal) * 0.01, len(signal))
        else:
            t = np.array(t, dtype=np.float64).flatten()

        t_2d = t.reshape(-1, 1)
        X_obs = signal.reshape(-1, 1)

        # 1. Setup TimeDomain
        t_min, t_max = float(t[0]), float(t[-1])
        geom = dde.geometry.TimeDomain(t_min, t_max)

        # 2. Setup Unknown parameter k (trainable)
        k = dde.Variable(1.0)

        # 3. Setup first-order decay PDE
        def decay_pde(t_in, x_in):
            dx_dt = dde.grad.jacobian(x_in, t_in, i=0, j=0)
            return [dx_dt + k * x_in]

        # 4. Setup PointSetBC to fit observed data points
        bc = dde.icbc.PointSetBC(t_2d, X_obs, component=0)

        # 5. PDE Data Setup
        data = dde.data.PDE(geom, decay_pde, [bc], num_domain=30, num_boundary=2, anchors=t_2d)

        # 6. Network and Model (FNN with 1 hidden layer)
        net = dde.nn.FNN([1, 16, 1], "tanh", "Glorot normal")
        model = dde.Model(data, net)

        # 7. Compile and Train with Adam (50 iterations for extreme speed)
        model.compile("adam", lr=0.01, external_trainable_variables=[k])
        model.train(iterations=50)

        # 8. Retrieve features
        k_val = float(k.detach().cpu().item())
        pred = model.predict(t_2d).flatten()

        # 1. Discovered k
        feat_k = k_val

        # 2. Fit error
        fit_error = float(np.mean((pred - signal) ** 2))

        # 3. Numeric derivative and residual evaluation
        dx_dt_numeric = np.gradient(pred, t)
        residual = dx_dt_numeric + k_val * pred
        res_mean = float(np.mean(np.abs(residual)))

        # 4. Standard deviation of residual
        res_std = float(np.std(residual))

        # 5. Fit error at start
        start_error = float((pred[0] - signal[0]) ** 2)

        # 6. Fit error at end
        end_error = float((pred[-1] - signal[-1]) ** 2)

        # 7. Std of predictions
        pred_std = float(np.std(pred))

        # 8. Variance of numerical derivative
        deriv_var = float(np.var(dx_dt_numeric))

        features = [
            feat_k,
            fit_error,
            res_mean,
            res_std,
            start_error,
            end_error,
            pred_std,
            deriv_var
        ]
        return np.array(features, dtype=np.float64)

    except Exception as e:
        print(f"  [ev3_neural WARNING] PINN feature extraction failed: {e}")
        return np.full(8, np.nan)

def extract_ev3_scientific(signal, use_neural_ode=True, use_pinn=True):
    """
    Combines EV3_DEEP (68D) with Neural ODE features (8D) and PINN features (8D)
    to obtain a comprehensive space of ~84 dimensions (EV3_SCIENTIFIC).
    """
    from core.autonomous.latent_snapshot_exporter import extract_ev3_deep
    
    # 1. Base EV3_DEEP vector (68D)
    try:
        ev3_deep = extract_ev3_deep(signal)
    except Exception as e:
        print(f"  [ev3_neural WARNING] extract_ev3_deep failed: {e}")
        ev3_deep = np.full(68, np.nan)

    # 2. Neural ODE Features (8D)
    if use_neural_ode:
        node_feats = extract_neural_ode_features(signal)
    else:
        node_feats = np.full(8, np.nan)

    # 3. PINN Features (8D)
    if use_pinn:
        pinn_feats = extract_pinn_features(signal)
    else:
        pinn_feats = np.full(8, np.nan)

    # Clean non-finite elements
    node_feats = [float(f) if np.isfinite(f) else np.nan for f in node_feats]
    pinn_feats = [float(f) if np.isfinite(f) else np.nan for f in pinn_feats]

    return np.concatenate([
        ev3_deep,
        node_feats,
        pinn_feats
    ])
