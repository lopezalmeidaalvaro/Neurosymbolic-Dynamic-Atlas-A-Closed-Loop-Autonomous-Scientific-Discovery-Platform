#!/usr/bin/env python3
"""
Orbital Thermal Twin FastAPI Server
Allows querying surrogate model predictions, physical ODE simulations, Pareto fronts, and symbolic equations.
Author: Alvaro Lopez Almeida
"""

import os
import sys
import time
import json
import pickle
import numpy as np
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure parents in path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from thermal.thermal_server_model import ThermalServerModel

app = FastAPI(
    title="Spacecraft Thermal Digital Twin API",
    description="Provides real-time dynamic thermal simulations and AI-accelerated surrogate modeling.",
    version="2.0.0"
)

# Enable CORS for Next.js dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(SCRIPT_DIR, "..", "models")
THERMAL_DIR = os.path.join(SCRIPT_DIR, "..", "thermal")

# Loaded Models and Scalers
SURROGATE_MODEL = None
SCALER_X = None
SCALER_Y = None
MODEL_METRICS = None

# In-Memory Cache with 60s TTL
CACHE = {}
CACHE_TTL_SEC = 60

class PredictionRequest(BaseModel):
    power: float = Field(..., ge=5.0, le=50.0, description="Internal power generation in Watts.")
    area: float = Field(..., ge=0.01, le=0.50, description="Radiator area in m².")
    emissivity: float = Field(..., ge=0.10, le=0.95, description="Surface emissivity.")

@app.on_event("startup")
def load_models_on_startup():
    global SURROGATE_MODEL, SCALER_X, SCALER_Y, MODEL_METRICS
    print("Loading models and scalers...")
    
    # Load RandomForest model as primary surrogate
    rf_path = os.path.join(MODELS_DIR, "surrogate_rf.pkl")
    scaler_x_path = os.path.join(MODELS_DIR, "scaler_X.pkl")
    scaler_y_path = os.path.join(MODELS_DIR, "scaler_y.pkl")
    metrics_path = os.path.join(MODELS_DIR, "surrogate_metrics.json")
    
    if os.path.exists(rf_path):
        with open(rf_path, "rb") as f:
            SURROGATE_MODEL = pickle.load(f)
        print(" -> Primary RF surrogate model loaded.")
        
    if os.path.exists(scaler_x_path) and os.path.exists(scaler_y_path):
        with open(scaler_x_path, "rb") as f:
            SCALER_X = pickle.load(f)
        with open(scaler_y_path, "rb") as f:
            SCALER_Y = pickle.load(f)
        print(" -> Preprocessing scalers loaded.")
        
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            MODEL_METRICS = json.load(f)
        print(" -> Models metrics loaded.")

def get_cached_result(cache_key: str):
    """
    Checks and retrieves valid cache entries.
    """
    if cache_key in CACHE:
        cached_data, timestamp = CACHE[cache_key]
        if time.time() - timestamp < CACHE_TTL_SEC:
            return cached_data
    return None

def set_cached_result(cache_key: str, data):
    """
    Stores data in-cache with the current timestamp.
    """
    CACHE[cache_key] = (data, time.time())

@app.get("/health")
def health_check():
    """
    Server health status.
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "models_loaded": SURROGATE_MODEL is not None
    }

@app.post("/predict")
def predict_thermal_metrics(req: PredictionRequest):
    """
    Uses the trained AI surrogate model to predict peak temperature and time to critical.
    """
    if SURROGATE_MODEL is None:
        raise HTTPException(status_code=503, detail="Surrogate models are not loaded on server.")
        
    # Validation of parameter boundaries (already validated by Pydantic Model)
    features = np.array([[req.power, req.area, req.emissivity]])
    
    try:
        # RandomForest trained on raw unscaled features
        pred = SURROGATE_MODEL.predict(features)[0]
        
        return {
            "max_temp_c": float(pred[0]),
            "time_to_critical_sec": float(pred[1]) if pred[1] >= 0 else None,
            "inference_mode": "AI Surrogate (Random Forest)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/simulate")
def run_numerical_simulation(
    power: float = Query(..., ge=5.0, le=50.0),
    area: float = Query(..., ge=0.01, le=0.50),
    emissivity: float = Query(..., ge=0.10, le=0.95),
    heat_capacity: float = Query(500.0, ge=100.0, le=2000.0),
    initial_temp: float = Query(293.15, ge=100.0, le=400.0)
):
    """
    Solves the lumped capacitance thermal differential equation in real time.
    """
    cache_key = f"sim_{power}_{area}_{emissivity}_{heat_capacity}_{initial_temp}"
    cached = get_cached_result(cache_key)
    if cached:
        return cached
        
    try:
        model = ThermalServerModel(
            power=power,
            area=area,
            emissivity=emissivity,
            heat_capacity=heat_capacity,
            initial_temp=initial_temp
        )
        sim_res = model.simulate(duration=3600.0, dt=10.0)
        
        response = {
            "time": sim_res["time"],
            "temperature": sim_res["temperature"],
            "max_temp_c": sim_res["max_temp"],
            "time_to_critical_sec": sim_res["time_to_critical"],
            "temperature_map_2D": sim_res["temperature_map_2D"],
            "steady_state_temp_c": model.steady_state_temp() - 273.15,
            "inference_mode": "Physical LEO Solver (Euler Integration)"
        }
        
        set_cached_result(cache_key, response)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@app.get("/models")
def get_surrogate_metrics():
    """
    Returns the training performance metrics of all trained surrogate emulators.
    """
    if MODEL_METRICS is None:
        raise HTTPException(status_code=404, detail="Surrogate model metrics file not found.")
    return MODEL_METRICS

@app.get("/optimal")
def get_optimal_design():
    """
    Fetches the Pareto-optimal radiator configuration specs.
    """
    cache_key = "optimal_design"
    cached = get_cached_result(cache_key)
    if cached:
        return cached
        
    optimal_path = os.path.join(THERMAL_DIR, "optimal_design.json")
    if not os.path.exists(optimal_path):
        raise HTTPException(status_code=404, detail="Optimal design specs file not found. Run optimize_radiator_design.py first.")
        
    with open(optimal_path, "r") as f:
        data = json.load(f)
        
    set_cached_result(cache_key, data)
    return data

@app.get("/equations")
def get_discovered_equations():
    """
    Lists the mathematical candidates discovered via symbolic regression.
    """
    cache_key = "discovered_equations"
    cached = get_cached_result(cache_key)
    if cached:
        return cached
        
    eq_path = os.path.join(THERMAL_DIR, "thermal_equations.csv")
    if not os.path.exists(eq_path):
        raise HTTPException(status_code=404, detail="Discovered equations CSV file not found. Run discover_thermal_equations.py first.")
        
    import pandas as pd
    df = pd.read_csv(eq_path)
    data = df.to_dict(orient="records")
    
    set_cached_result(cache_key, data)
    return data

if __name__ == "__main__":
    import uvicorn
    # If run directly as a script
    uvicorn.run(app, host="0.0.0.0", port=8000)
