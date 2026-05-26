import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import os
import random
import numpy as np
import pandas as pd

# Ensure UTF-8 output encoding for Windows terminal
import sys
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def simulate_bec_flow(n_grid=100, L=10.0, v0=1.0, c_sound=0.5, width=2.0) -> dict:
    """
    Modelo de flujo BEC 1D con métrica acústica efectiva. 
    No resuelve la ecuación de Gross-Pitaevskii completa; usa un perfil de velocidad analítico.
    """
    x_grid = np.linspace(-L / 2, L / 2, n_grid)
    v_profile = v0 * np.tanh(x_grid / width)
    density_profile = np.ones_like(x_grid) # Constant density baseline

    # Horizon positions exist where |v(x)| = c_sound.
    # v0 * tanh(x_H/width) = +/- c_sound  =>  x_H = +/- width * arctanh(c_sound/v0)
    horizon_positions = []
    if v0 > c_sound:
        val = c_sound / v0
        # Bounded to avoid numerical errors near singularity
        if val < 1.0:
            x_h = float(width * np.arctanh(val))
            horizon_positions = [-x_h, x_h]

    # Effective acoustic metric components: ds^2 = -(c^2 - v^2)dt^2 - 2v dt dx + dx^2
    g_00 = -(c_sound**2 - v_profile**2)
    g_01 = -v_profile
    g_11 = np.ones_like(x_grid)

    metric_effective = {
        "g_00": g_00.tolist(),
        "g_01": g_01.tolist(),
        "g_11": g_11.tolist()
    }

    return {
        "x_grid": x_grid.tolist(),
        "v_profile": v_profile.tolist(),
        "density_profile": density_profile.tolist(),
        "horizon_positions": horizon_positions,
        "metric_effective": metric_effective
    }

def compute_analog_hawking_temperature(horizon_pos, v_profile, c_sound, dx) -> float:
    """
    Computes analog Hawking temperature numerically at the horizon:
    T_H = kappa / (2 * pi)
    where the surface gravity is kappa = c_sound * |dv/dx|_{x_H}
    """
    v_profile = np.array(v_profile)
    n_grid = len(v_profile)
    
    # Reconstruct grid using dx to find closest index to horizon_pos
    x_grid = np.linspace(-dx * n_grid / 2, dx * n_grid / 2, n_grid)
    idx = np.argmin(np.abs(x_grid - horizon_pos))
    
    # Bound index to compute central finite difference
    idx = max(1, min(n_grid - 2, idx))
    dv_dx = (v_profile[idx + 1] - v_profile[idx - 1]) / (2.0 * dx)
    
    kappa = c_sound * np.abs(dv_dx)
    T_H = kappa / (2.0 * np.pi)
    
    return float(T_H)

def generate_bec_ensemble(n_configs=200, v0_range=(0.5, 2.0), c_sound_range=(0.3, 1.0)) -> pd.DataFrame:
    """
    Generates an ensemble of BEC flows with varying v0 and c_sound parameters.
    """
    np.random.seed(42)
    random.seed(42)
    
    results = []
    n_grid = 200
    L = 10.0
    dx = L / n_grid
    
    for c in range(n_configs):
        v0 = random.uniform(*v0_range)
        c_sound = random.uniform(*c_sound_range)
        
        sim = simulate_bec_flow(n_grid=n_grid, L=L, v0=v0, c_sound=c_sound, width=2.0)
        horizons = sim["horizon_positions"]
        
        # We compute Hawking temperature for the black hole horizon (positive x, representing the outflow horizon)
        t_hawking = 0.0
        has_horizon = len(horizons) > 0
        
        if has_horizon:
            # Recompute Hawking temperature for the BH horizon (x > 0)
            bh_horizon = max(horizons)
            t_hawking = compute_analog_hawking_temperature(bh_horizon, sim["v_profile"], c_sound, dx)
            
        results.append({
            "config_id": c,
            "v0": v0,
            "c_sound": c_sound,
            "has_horizon": int(has_horizon),
            "num_horizons": len(horizons),
            "horizon_pos_1": float(horizons[0]) if has_horizon else np.nan,
            "horizon_pos_2": float(horizons[1]) if has_horizon else np.nan,
            "hawking_temperature": t_hawking
        })
        
    return pd.DataFrame(results)

def generate_bec_dataset(n_configs=500, output_path="data/bec_ensemble.csv") -> pd.DataFrame:
    """
    Generates a BEC flow dataset of 500 configs and saves it to a CSV.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = generate_bec_ensemble(n_configs=n_configs)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated BEC dataset and saved to: {output_path}")
    return df

if __name__ == "__main__":
    print("Testing BEC analog model...")
    # Generate flow
    sim = simulate_bec_flow(n_grid=100, L=10.0, v0=1.5, c_sound=0.6, width=2.0)
    print(f"Horizons found at: {sim['horizon_positions']}")
    
    if len(sim["horizon_positions"]) > 0:
        bh_horizon = max(sim["horizon_positions"])
        dx = 10.0 / 100
        temp = compute_analog_hawking_temperature(bh_horizon, sim["v_profile"], 0.6, dx)
        print(f"BH Horizon analogue Hawking temperature: {temp:.6f} K")
        
    # Generate a small ensemble
    df = generate_bec_dataset(n_configs=10, output_path="data/test_bec_ensemble.csv")
    print(df.head())
