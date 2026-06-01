#!/usr/bin/env python3
"""
Train Surrogate Models - Trains fast emulators (RF, XGBoost, MLP) to predict thermal metrics.
Author: Alvaro Lopez Almeida
"""

import os
import time
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Try to import XGBoost, fallback to scikit-learn Gradient Boosting if not available
try:
    import xgboost as xgb

    HAS_XGBOOST = True
except ImportError:
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.multioutput import MultiOutputRegressor

    HAS_XGBOOST = False

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Set seed for reproducibility
np.random.seed(42)
torch.manual_seed(42)


# Define PyTorch MLP architecture
class ThermalMLP(nn.Module):
    def __init__(self):
        super(ThermalMLP, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(3, 32), nn.ReLU(), nn.Linear(32, 16), nn.ReLU(), nn.Linear(16, 2)
        )

    def forward(self, x):
        return self.net(x)


def train_surrogate():
    print("Starting surrogate model training...")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(script_dir, "thermal_dataset.csv")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(
            f"Dataset not found at {dataset_path}. Run generate_thermal_dataset.py first."
        )

    df = pd.read_csv(dataset_path)

    # Features and targets
    X = df[["power", "area", "emissivity"]].values
    y = df[["max_temp", "time_to_critical"]].values

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Scale data for MLP stability
    scaler_X = StandardScaler()
    scaler_y = StandardScaler()

    X_train_scaled = scaler_X.fit_transform(X_train)
    X_test_scaled = scaler_X.transform(X_test)

    y_train_scaled = scaler_y.fit_transform(y_train)
    y_test_scaled = scaler_y.transform(y_test)

    # Models directory
    models_dir = "../models"
    os.makedirs(models_dir, exist_ok=True)

    # Save scalers
    with open(os.path.join(models_dir, "scaler_X.pkl"), "wb") as f:
        pickle.dump(scaler_X, f)
    with open(os.path.join(models_dir, "scaler_y.pkl"), "wb") as f:
        pickle.dump(scaler_y, f)

    metrics = {}

    # ----------------------------------------------------
    # Model 1: RandomForest
    # ----------------------------------------------------
    print("\n -> Training RandomForest Regressor...")
    rf_model = RandomForestRegressor(
        n_estimators=100, max_depth=None, random_state=42, n_jobs=-1
    )

    t_start = time.time()
    rf_model.fit(X_train, y_train)
    t_train = (time.time() - t_start) * 1000.0  # ms

    # Latency test
    t_lat_start = time.time()
    rf_pred = rf_model.predict(X_test)
    t_lat = ((time.time() - t_lat_start) / len(X_test)) * 1000.0  # ms per sample

    rf_rmse = float(np.sqrt(mean_squared_error(y_test, rf_pred)))
    rf_mae = float(mean_absolute_error(y_test, rf_pred))
    rf_r2 = float(r2_score(y_test, rf_pred))

    metrics["RandomForest"] = {
        "RMSE": rf_rmse,
        "MAE": rf_mae,
        "R2": rf_r2,
        "latency_ms": t_lat,
        "train_time_ms": t_train,
    }

    # Save RF model
    with open(os.path.join(models_dir, "surrogate_rf.pkl"), "wb") as f:
        pickle.dump(rf_model, f)
    print(f"RandomForest: R2={rf_r2:.4f}, RMSE={rf_rmse:.4f}, Latency={t_lat:.4f} ms")

    # ----------------------------------------------------
    # Model 2: XGBoost (or GradientBoostingRegressor fallback)
    # ----------------------------------------------------
    if HAS_XGBOOST:
        print("\n -> Training XGBoost Regressor...")
        xgb_model = xgb.XGBRegressor(
            n_estimators=100, max_depth=6, random_state=42, n_jobs=-1
        )
        t_start = time.time()
        xgb_model.fit(X_train, y_train)
        t_train = (time.time() - t_start) * 1000.0  # ms

        t_lat_start = time.time()
        xgb_pred = xgb_model.predict(X_test)
        t_lat = ((time.time() - t_lat_start) / len(X_test)) * 1000.0  # ms per sample
    else:
        print("\n -> Training GradientBoosting Regressor (XGBoost Fallback)...")
        # Multi-output wrapper for standard GradientBoosting
        gbr_base = GradientBoostingRegressor(
            n_estimators=100, max_depth=6, random_state=42
        )
        xgb_model = MultiOutputRegressor(gbr_base)
        t_start = time.time()
        xgb_model.fit(X_train, y_train)
        t_train = (time.time() - t_start) * 1000.0  # ms

        t_lat_start = time.time()
        xgb_pred = xgb_model.predict(X_test)
        t_lat = ((time.time() - t_lat_start) / len(X_test)) * 1000.0  # ms per sample

    xgb_rmse = float(np.sqrt(mean_squared_error(y_test, xgb_pred)))
    xgb_mae = float(mean_absolute_error(y_test, xgb_pred))
    xgb_r2 = float(r2_score(y_test, xgb_pred))

    metrics["XGBoost"] = {
        "RMSE": xgb_rmse,
        "MAE": xgb_mae,
        "R2": xgb_r2,
        "latency_ms": t_lat,
        "train_time_ms": t_train,
    }

    # Save XGB/GBR model
    with open(os.path.join(models_dir, "surrogate_xgb.pkl"), "wb") as f:
        pickle.dump(xgb_model, f)
    print(f"XGBoost: R2={xgb_r2:.4f}, RMSE={xgb_rmse:.4f}, Latency={t_lat:.4f} ms")

    # ----------------------------------------------------
    # Model 3: PyTorch MLP [3 -> 32 -> 16 -> 2]
    # ----------------------------------------------------
    print("\n -> Training PyTorch MLP...")

    # Data loaders
    train_dataset = TensorDataset(
        torch.FloatTensor(X_train_scaled), torch.FloatTensor(y_train_scaled)
    )
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    mlp = ThermalMLP()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(mlp.parameters(), lr=0.001)

    t_start = time.time()
    mlp.train()
    for epoch in range(100):
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = mlp(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

    t_train = (time.time() - t_start) * 1000.0  # ms

    # Evaluate
    mlp.eval()
    with torch.no_grad():
        t_lat_start = time.time()
        mlp_pred_scaled = mlp(torch.FloatTensor(X_test_scaled)).numpy()
        t_lat = ((time.time() - t_lat_start) / len(X_test)) * 1000.0  # ms per sample

        # Invert scaling for metrics
        mlp_pred = scaler_y.inverse_transform(mlp_pred_scaled)

    mlp_rmse = float(np.sqrt(mean_squared_error(y_test, mlp_pred)))
    mlp_mae = float(mean_absolute_error(y_test, mlp_pred))
    mlp_r2 = float(r2_score(y_test, mlp_pred))

    metrics["MLP"] = {
        "RMSE": mlp_rmse,
        "MAE": mlp_mae,
        "R2": mlp_r2,
        "latency_ms": t_lat,
        "train_time_ms": t_train,
    }

    # Save PyTorch MLP
    torch.save(mlp.state_dict(), os.path.join(models_dir, "surrogate_mlp.pth"))
    print(f"MLP: R2={mlp_r2:.4f}, RMSE={mlp_rmse:.4f}, Latency={t_lat:.4f} ms")

    # ----------------------------------------------------
    # Recommendations and overall analysis
    # ----------------------------------------------------
    max_r2 = max(rf_r2, xgb_r2, mlp_r2)
    recommendation = ""
    if max_r2 > 0.99:
        recommendation = "Dinámica simple. PINN innecesaria."
    elif max_r2 < 0.95:
        recommendation = "Se recomienda PINN/Neural ODE (Fase T3)."
    else:
        recommendation = "R2 en rango intermedio. PINN/Neural ODE opcional."

    metrics_summary = {
        "models": metrics,
        "best_r2": max_r2,
        "recommendation": recommendation,
    }

    # Save metrics JSON
    with open(os.path.join(models_dir, "surrogate_metrics.json"), "w") as f:
        json.dump(metrics_summary, f, indent=4)

    print("\n--- Training Completed ---")
    print(f"Metrics saved to {os.path.join(models_dir, 'surrogate_metrics.json')}")
    print(f"Recommendation: {recommendation}")


if __name__ == "__main__":
    train_surrogate()
