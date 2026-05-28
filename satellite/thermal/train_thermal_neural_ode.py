#!/usr/bin/env python3
"""
Train Thermal Neural ODE - Parameterizes the thermal derivative function with a neural network and solves it via torchdiffeq.
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
from torchdiffeq import odeint

from physics.core.neurosymbolic.neural_ode import SharedODEFunc
from physics.experiment_versioning import ExperimentTracker, get_git_commit_hash

# Set seed for reproducibility
np.random.seed(42)
torch.manual_seed(42)

# Use SharedODEFunc imported from the shared neurosymbolic library
ODEFunc = lambda: SharedODEFunc(input_dim=1, extra_dim=3, hidden_dim=64, num_layers=2)

def train_neural_ode():
    print("Initializing Neural ODE training...")
    
    # Device Configuration
    if torch.cuda.is_available():
        device = "cuda"
        torch.cuda.empty_cache()
        print("Using GPU (CUDA).")
    else:
        device = "cpu"
        print("Using CPU.")
        
    # Load dataset
    dataset_path = "thermal_dataset.csv"
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}. Run generate_thermal_dataset.py first.")
        
    df = pd.read_csv(dataset_path)
    
    # We will train on a subset of 50 configurations to ensure fast integration and no memory/CPU bottlenecks
    n_train = min(50, len(df))
    df_subset = df.iloc[:n_train]
    
    # Reconstruct trajectories
    times_list = []
    temps_list = []
    params_list = []
    
    for idx, row in df_subset.iterrows():
        t_prof = json.loads(row["time_profile"])
        temp_prof = json.loads(row["temperature_profile"])
        p = row["power"]
        a = row["area"]
        e = row["emissivity"]
        
        times_list.append(t_prof)
        # Convert to Kelvin and scale
        temps_list.append([temp_val + 273.15 for temp_val in temp_prof])
        params_list.append([p, a, e])
        
    # Standardize time steps (since they are all identical from 0 to 3600 with dt=10)
    t_steps = np.array(times_list[0]) / 3600.0  # normalized time
    t_tensor = torch.FloatTensor(t_steps).to(device)
    
    # Convert inputs
    # Shape: [batch, steps, 1]
    y_true_np = np.array(temps_list).reshape(n_train, -1, 1) / 300.0  # scaled Kelvin
    y_true_tensor = torch.FloatTensor(y_true_np).to(device)
    
    # Params
    params_np = np.array(params_list)
    params_norm = params_np.copy()
    params_norm[:, 0] /= 50.0  # power
    params_norm[:, 1] /= 0.5   # area
    params_tensor = torch.FloatTensor(params_norm).to(device)
    
    # Initialize function and optimizer
    func = ODEFunc().to(device)
    optimizer = optim.Adam(func.parameters(), lr=0.01)
    
    func.params = params_tensor
    
    # y0 is initial temperature (t=0) for each batch element
    # Shape: [batch, 1]
    y0 = y_true_tensor[:, 0, :]
    
    print("Training Neural ODE with dopri5 solver (300 epochs)...")
    t_start = time.time()
    
    # Training Loop
    epochs = 300
    for epoch in range(epochs):
        optimizer.zero_grad()
        
        # Integrate forward in time
        # odeint expects func to return dy/dt, y0 is starting state, t_tensor are time integration steps
        # Output shape of odeint: [steps, batch, 1]
        pred_y_steps = odeint(func, y0, t_tensor, method="dopri5")
        
        # Permute shape back to [batch, steps, 1] to match targets
        pred_y = pred_y_steps.permute(1, 0, 2)
        
        loss = torch.mean((pred_y - y_true_tensor) ** 2)
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 50 == 0:
            print(f" -> Epoch {epoch+1}/{epochs} | Loss: {loss.item():.6f}")
            
    t_train = time.time() - t_start
    print(f"Neural ODE training complete in {t_train:.2f} seconds.")
    
    # Speedup and validation analysis
    func.eval()
    with torch.no_grad():
        t_int_start = time.time()
        # Test full numerical trajectory resolution using trained Neural ODE function
        pred_y_steps = odeint(func, y0, t_tensor, method="dopri5")
        t_int = (time.time() - t_int_start) * 1000.0  # ms
        
        # Denormalize output
        pred_y_K = (pred_y_steps.permute(1, 0, 2).cpu().numpy()) * 300.0
        true_y_K = y_true_np * 300.0
        
        rmse = np.sqrt(np.mean((pred_y_K - true_y_K) ** 2))
        
    print(f"Neural ODE Evaluation: RMSE = {rmse:.4f}°C/K, Inference latency for batch = {t_int:.2f} ms")
    
    # Track the experiment
    tracker = ExperimentTracker(storage_path="../../physics/artifacts/experiments.db")
    hyperparams = {
        "epochs": epochs,
        "n_train_configs": n_train,
        "solver_method": "dopri5",
        "learning_rate": 0.01
    }
    results = {
        "rmse": float(rmse),
        "latency_ms": float(t_int),
        "training_time_sec": float(t_train)
    }
    run_id = tracker.log_experiment(
        system="satellite_thermal",
        module="train_thermal_neural_ode",
        seed=42,
        hyperparameters=hyperparams,
        results=results
    )
    
    git_hash = get_git_commit_hash()
    
    # Save model
    models_dir = "../models"
    os.makedirs(models_dir, exist_ok=True)
    
    versioned_filename = f"neural_ode_thermal_{git_hash}_{run_id[:8]}.pth"
    torch.save(func.state_dict(), os.path.join(models_dir, versioned_filename))
    torch.save(func.state_dict(), os.path.join(models_dir, "neural_ode_thermal.pth"))
    print(f"Neural ODE model successfully versioned & saved to {os.path.join(models_dir, versioned_filename)}")
    print(f"Neural ODE model successfully saved to {os.path.join(models_dir, 'neural_ode_thermal.pth')}")

if __name__ == "__main__":
    train_neural_ode()
