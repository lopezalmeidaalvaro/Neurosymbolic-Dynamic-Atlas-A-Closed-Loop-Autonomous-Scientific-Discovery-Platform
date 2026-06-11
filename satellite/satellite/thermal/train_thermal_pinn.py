#!/usr/bin/env python3
"""
Train Thermal PINN - Trains a Physics-Informed Neural Network to model satellite temperature.
Author: Alvaro Lopez Almeida
"""

import os
import sys
from pathlib import Path

# Add project root and register config paths
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config

import time
import json
import pickle
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim

from physics.core.neurosymbolic.pinn import SharedPINNNet
from physics.experiment_versioning import ExperimentTracker, get_git_commit_hash

# Set seed for reproducibility
np.random.seed(42)
torch.manual_seed(42)

# Use SharedPINNNet imported from the shared neurosymbolic library
PINNNet = SharedPINNNet


def train_pinn():
    print("Initializing PINN training...")

    # Device Configuration
    if torch.cuda.is_available():
        device = "cuda"
        torch.cuda.empty_cache()
        use_amp = True
        batch_size = 256
        print("Using GPU (CUDA) with Mixed Precision.")
    else:
        device = "cpu"
        use_amp = False
        batch_size = 64
        print("Using CPU.")

    # Load dataset
    script_dir = Path(__file__).resolve().parent
    dataset_path = script_dir / "thermal_dataset.csv"
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {dataset_path}. Run generate_thermal_dataset.py first."
        )

    df = pd.read_csv(dataset_path)

    # Reconstruct trajectories
    times_list = []
    temps_list = []
    params_list = []

    for idx, row in df.iterrows():
        t_prof = json.loads(row["time_profile"])
        temp_prof = json.loads(row["temperature_profile"])
        p = row["power"]
        a = row["area"]
        e = row["emissivity"]

        for t_val, temp_val in zip(t_prof, temp_prof):
            times_list.append(t_val)
            # Convert to Kelvin for physical consistency
            temps_list.append(temp_val + 273.15)
            params_list.append([p, a, e])

    X_data = np.zeros((len(times_list), 4))
    X_data[:, 0] = times_list
    X_data[:, 1:] = params_list
    y_data = np.array(temps_list).reshape(-1, 1)

    # Normalize inputs for neural network stability
    # Scale: t/3600, power/50, area/0.5, emissivity
    X_norm = X_data.copy()
    X_norm[:, 0] = X_norm[:, 0] / 3600.0
    X_norm[:, 1] = X_norm[:, 1] / 50.0
    X_norm[:, 2] = X_norm[:, 2] / 0.5

    # Keep output in scaled Kelvin (e.g. divide by 300 to keep it near 1)
    y_norm = y_data / 300.0

    # Convert to tensors
    X_tensor = torch.FloatTensor(X_norm).to(device)
    y_tensor = torch.FloatTensor(y_norm).to(device)

    pinn = PINNNet().to(device)

    # Define physical constants for physics loss
    stefan_boltzmann = 5.67e-8
    ambient_temp_K = 2.7
    heat_capacity = 500.0

    optimizer = optim.Adam(pinn.parameters(), lr=0.001)
    scaler = torch.cuda.amp.GradScaler() if use_amp else None

    # Sample collocation points for physics loss
    t_physics = np.random.uniform(0.0, 3600.0, 1000)
    p_physics = np.random.uniform(5.0, 50.0, 1000)
    a_physics = np.random.uniform(0.01, 0.50, 1000)
    e_physics = np.random.uniform(0.10, 0.95, 1000)

    X_phys = np.stack([t_physics, p_physics, a_physics, e_physics], axis=1)
    X_phys_norm = X_phys.copy()
    X_phys_norm[:, 0] /= 3600.0
    X_phys_norm[:, 1] /= 50.0
    X_phys_norm[:, 2] /= 0.5

    X_phys_tensor = torch.FloatTensor(X_phys_norm).to(device)
    X_phys_tensor.requires_grad = True

    print("Training PINN with Adam (2000 epochs equivalent)...")
    t_start = time.time()

    # Training Loop (Adam)
    epochs = 2000
    for epoch in range(epochs):
        optimizer.zero_grad()

        # 1. Data Loss
        idx = np.random.choice(len(X_norm), batch_size)
        X_batch = X_tensor[idx]
        y_batch = y_tensor[idx]

        y_pred = pinn(X_batch)
        loss_data = torch.mean((y_pred - y_batch) ** 2)

        # 2. Physics Loss
        y_phys = (
            pinn(X_phys_tensor) * 300.0
        )  # Denormalize output for physical equations

        # Compute dT/dt using autograd
        dT_dnorm = torch.autograd.grad(
            y_phys,
            X_phys_tensor,
            grad_outputs=torch.ones_like(y_phys),
            create_graph=True,
            retain_graph=True,
        )[0]

        # dT/dt = dT/d(t/3600) * (1/3600)
        dT_dt = dT_dnorm[:, 0:1] / 3600.0

        # Retrieve denormalized parameters
        p_phys_val = X_phys_tensor[:, 1:2] * 50.0
        a_phys_val = X_phys_tensor[:, 2:3] * 0.5
        e_phys_val = X_phys_tensor[:, 3:4]

        # ODE Residual: dT/dt - (power - emissivity * sigma * area * (T^4 - T_amb^4)) / heat_capacity = 0
        Q_rad = (
            e_phys_val * stefan_boltzmann * a_phys_val * (y_phys**4 - ambient_temp_K**4)
        )
        residual = dT_dt - (p_phys_val - Q_rad) / heat_capacity
        loss_physics = torch.mean(residual**2)

        # 3. Energy Boundary Loss (at t=0, Temp should equal 293.15 K)
        # Create t=0 batch
        X_t0 = X_batch.clone()
        X_t0[:, 0] = 0.0
        y_t0_pred = pinn(X_t0) * 300.0
        loss_energy = torch.mean((y_t0_pred - 293.15) ** 2)

        # Total Loss
        loss = loss_data + loss_physics + 0.1 * loss_energy

        if use_amp:
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            optimizer.step()

        if (epoch + 1) % 500 == 0:
            print(
                f" -> Epoch {epoch+1}/{epochs} | Loss: {loss.item():.6f} (Data: {loss_data.item():.6f}, Physics: {loss_physics.item():.6f}, Energy: {loss_energy.item():.6f})"
            )

    t_train = time.time() - t_start
    print(f"Adam training complete in {t_train:.2f} seconds.")

    # ----------------------------------------------------
    # Fine-tuning with L-BFGS
    # ----------------------------------------------------
    print("Fine-tuning PINN with L-BFGS (500 iterations equivalent)...")
    optimizer_lbfgs = optim.LBFGS(pinn.parameters(), lr=0.1, max_iter=500)

    def closure():
        optimizer_lbfgs.zero_grad()
        y_pred = pinn(X_tensor[:1000])
        loss_data = torch.mean((y_pred - y_tensor[:1000]) ** 2)

        y_phys = pinn(X_phys_tensor) * 300.0
        dT_dnorm = torch.autograd.grad(
            y_phys,
            X_phys_tensor,
            grad_outputs=torch.ones_like(y_phys),
            create_graph=True,
        )[0]
        dT_dt = dT_dnorm[:, 0:1] / 3600.0

        p_phys_val = X_phys_tensor[:, 1:2] * 50.0
        a_phys_val = X_phys_tensor[:, 2:3] * 0.5
        e_phys_val = X_phys_tensor[:, 3:4]

        Q_rad = (
            e_phys_val * stefan_boltzmann * a_phys_val * (y_phys**4 - ambient_temp_K**4)
        )
        residual = dT_dt - (p_phys_val - Q_rad) / heat_capacity
        loss_physics = torch.mean(residual**2)

        loss = loss_data + loss_physics
        loss.backward()
        return loss

    optimizer_lbfgs.step(closure)
    print("L-BFGS fine-tuning complete.")

    # Evaluate model performance
    pinn.eval()
    with torch.no_grad():
        t_inf_start = time.time()
        y_pred_scaled = pinn(X_tensor).cpu().numpy()
        t_inf = ((time.time() - t_inf_start) / len(X_tensor)) * 1000.0  # ms per sample

        y_pred_K = y_pred_scaled * 300.0
        y_true_K = y_data

        rmse = np.sqrt(np.mean((y_pred_K - y_true_K) ** 2))

    print(f"PINN Metrics: RMSE = {rmse:.4f}°C/K, Latency = {t_inf:.4f} ms")

    # Track the experiment
    tracker = ExperimentTracker(
        storage_path=os.path.join(
            str(config.ROOT_DIR), "physics", "artifacts", "experiments.db"
        )
    )
    hyperparams = {
        "epochs": epochs,
        "batch_size": batch_size,
        "heat_capacity": heat_capacity,
        "stefan_boltzmann": stefan_boltzmann,
        "learning_rate": 0.001,
    }
    results = {
        "rmse": float(rmse),
        "latency_ms": float(t_inf),
        "training_time_sec": float(t_train),
    }
    run_id = tracker.log_experiment(
        system="satellite_thermal",
        module="train_thermal_pinn",
        seed=42,
        hyperparameters=hyperparams,
        results=results,
    )

    git_hash = get_git_commit_hash()

    # Save model under versioned filename and standard canonical path
    models_dir = "../models"
    os.makedirs(models_dir, exist_ok=True)

    versioned_filename = f"pinn_thermal_{git_hash}_{run_id[:8]}.pth"
    torch.save(pinn.state_dict(), os.path.join(models_dir, versioned_filename))
    torch.save(pinn.state_dict(), os.path.join(models_dir, "pinn_thermal.pth"))
    print(
        f"PINN model successfully versioned & saved to {os.path.join(models_dir, versioned_filename)}"
    )
    print(
        f"PINN model successfully saved to {os.path.join(models_dir, 'pinn_thermal.pth')}"
    )


if __name__ == "__main__":
    train_pinn()
