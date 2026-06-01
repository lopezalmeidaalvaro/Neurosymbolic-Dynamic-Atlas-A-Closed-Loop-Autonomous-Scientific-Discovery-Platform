#!/usr/bin/env python3
"""
Phase 3: Warp Thermal Injection Wrapper
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import re
import numpy as np
from pathlib import Path

# Add satellite root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from satellite.thermal.multi_node_thermal_network import ThermalNetwork

def load_optimized_parameters(root_dir=None):
    """
    Dynamically loads the optimized warp parameters from the symbolic regression output file.
    Compiles the text expression safely using python's built-in compiler, handling
    any arbitrary equation format returned by PySR (e.g. including x0, tanh, etc.).
    """
    if root_dir is None:
        root_dir = Path(__file__).resolve().parents[3]
    
    eq_txt_path = Path(root_dir) / "physics" / "warp" / "optimized_metric_equation.txt"
    csv_path = Path(root_dir) / "physics" / "warp" / "data" / "optimized_bubble.csv"
    
    # Default fallback function (in case file reading fails)
    def default_func(r):
        # Analytical approximation f(r) = 0.5 - 0.5 * tanh((r - 0.5)/0.2)
        return 0.5 - 0.5 * np.tanh((r - 0.5) / 0.2)
        
    eval_func = default_func
    
    if eq_txt_path.exists():
        try:
            with open(eq_txt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            
            # Prepare mathematical string: replace variable x0 with r
            expr_str = content.replace("x0", "r")
            
            # Setup safe local symbols dictionary
            safe_dict = {
                "r": 0.0,
                "tanh": np.tanh,
                "exp": np.exp,
                "square": np.square,
                "cube": lambda x: x**3,
                "pow": np.power,
                "np": np
            }
            
            # Pre-compile the expression to verify correctness and enhance performance
            code = compile(expr_str, "<string>", "eval")
            
            def compiled_eval(r_val):
                # Handle scalar or numpy array input
                if isinstance(r_val, (int, float, np.float64)):
                    safe_dict["r"] = r_val
                    return float(eval(code, {"__builtins__": {}}, safe_dict))
                else:
                    # Array evaluation
                    res = []
                    for val in r_val:
                        safe_dict["r"] = val
                        res.append(eval(code, {"__builtins__": {}}, safe_dict))
                    return np.array(res)
                    
            eval_func = compiled_eval
            print(f"[+] warp_thermal_injection: Compilada con éxito la ecuación simbólica: {content}")
            return eval_func
        except Exception as e:
            print(f"[!] Error al compilar optimized_metric_equation.txt: {e}. Usando fallback.")
            
    # Fallback to CSV fitting
    if csv_path.exists():
        try:
            import pandas as pd
            from scipy.optimize import curve_fit
            
            df = pd.read_csv(csv_path)
            X = df["r"].values
            y = df["f_r"].values
            
            def model(r, R, s):
                return (np.tanh(s * (r + R)) - np.tanh(s * (r - R))) / (2 * np.tanh(s * R))
                
            popt, _ = curve_fit(model, X, y, p0=[0.5, 4.0], bounds=([0.1, 0.5], [0.9, 15.0]))
            R_fit, sigma_fit = popt
            
            def csv_func(r):
                return model(r, R_fit, sigma_fit)
                
            eval_func = csv_func
            print(f"[+] warp_thermal_injection: Parámetros ajustados dinámicamente desde CSV: R_fit={R_fit:.4f}, sigma_fit={sigma_fit:.4f}")
            return eval_func
        except Exception as e:
            print(f"[!] Fallback a ajuste de CSV fallido: {e}. Usando valores por defecto.")
            
    print(f"[!] No se detectaron archivos de optimización métrica. Usando función aproximada heurística.")
    return eval_func

def df_dr_analytical(r, eval_func, h=1e-5):
    """
    Computes df/dr using high-precision central numerical differences.
    Works generically for any compiled or analytical function.
    """
    return (eval_func(r + h) - eval_func(r - h)) / (2.0 * h)

class WarpThermalNetwork(ThermalNetwork):
    """
    LEO Spacecraft Multi-Node Thermal Network with Warp Field exotic energy thermal injection.
    Nodes:
      0: CPU (Main heat source)
      1: Battery
      2: Payload
      3: Structure (Bus)
      4: Radiator (Space dissipation)
      5: Solar Panels (Solar absorption)
    """
    def __init__(self, alpha=50.0, warp_fluctuation=0.0, root_dir=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alpha = alpha  # In Watts
        self.warp_fluctuation = warp_fluctuation  # Dynamic fluctuation factor
        
        # Spacecraft radial nodes grid layout
        self.r_nodes = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        
        # Load parameters evaluation function
        self.eval_func = load_optimized_parameters(root_dir)
        
    def get_q_warp(self, r):
        """
        Computes Q_warp(r) = alpha * (df/dr)^2
        """
        df_dr = df_dr_analytical(r, self.eval_func)
        # Apply scaling alpha and incorporate dynamic warp fluctuations
        return self.alpha * (df_dr ** 2) * (1.0 + self.warp_fluctuation)
        
    def dTdt(self, T_vector, t, Q_solar, use_cavity_radiation=False):
        """
        Solves the rate of change of temperature for each node, incorporating 
        the scalar exotic energy thermal injection field Q_warp(r).
        """
        # 1. Compute default thermodynamic derivatives (conduction, space radiation, solar)
        dT = super().dTdt(T_vector, t, Q_solar, use_cavity_radiation=use_cavity_radiation)
        
        # 2. Add warp energy stress scalar field heat injection Q_warp(r) to each node
        for i in range(6):
            q_w = self.get_q_warp(self.r_nodes[i])
            dT[i] += q_w / self.C[i]
            
        return dT

if __name__ == "__main__":
    net = WarpThermalNetwork(alpha=50.0)
    print("=== WARP THERMAL SOLVER INITIALIZATION SUCCESS ===")
    for i, name in enumerate(net.node_names):
        qw = net.get_q_warp(net.r_nodes[i])
        print(f" -> Nodo {i} ({name:10s}): Coordenada r={net.r_nodes[i]:.1f} | Inyección Q_warp={qw:7.4f} W")
