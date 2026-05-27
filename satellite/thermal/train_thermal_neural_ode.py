#!/usr/bin/env python3
"""
Train Thermal Neural ODE - Parameterizes the thermal derivative function with a neural network and solves it via torchdiffeq.
Author: Alvaro Lopez Almeida
"""

import os
import time
import json
import pickle
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torchdiffeq import odeint

# Set seed for reproducibility
np.random.seed(42)
torch.manual_seed(42)

class ODEFunc(nn.Module):
    """
    ODE function network: maps [T, power, area, emissivity] -> dT/dt.
    Input size: 4
    Output size: 1
    Uses 2 hidden layers of 64 neurons with Tanh activation.
    """
    def __init__(self):
        super(ODEFunc, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(4, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )
        self.params = None  # Placeholder for [power, area, emissivity] tensors during integration
        
    def forward(self, t, y):
        # y is the state of shape [batch, 1] representing scaled temperature
        # self.params is the parameter set of shape [batch, 3] representing scaled physical params
        if self.params is None:
            raise ValueError("Parameters (self.params) must be set prior to running forward integration.")
            
        inputs = torch.cat([y, self.params], dim=-1)
        return self.net(inputs)

def train_neural_ode():
    print("Initializing Neural ODE training...")
    
    # Device Configuration
    if torch.cuda.is_available():
        device = "cuda"
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
    
    # Save model
    models_dir = "../models"
    os.makedirs(models_dir, exist_ok=True)
    torch.save(func.state_dict(), os.path.join(models_dir, "neural_ode_thermal.pth"))
    print(f"Neural ODE model successfully saved to {os.path.join(models_dir, 'neural_ode_thermal.pth')}")

if __name__ == "__main__":
    train_neural_ode()
