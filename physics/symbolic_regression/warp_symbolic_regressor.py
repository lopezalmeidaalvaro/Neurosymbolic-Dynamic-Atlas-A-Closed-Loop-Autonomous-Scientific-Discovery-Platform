#!/usr/bin/env python3
"""
Phase 2: Symbolic Regression for Warp Shape Function
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def optimized_alcubierre_model(r, R_fit, sigma_fit):
    """
    Analytical model for the optimized Alcubierre shape function.
    """
    numerator = np.tanh(sigma_fit * (r + R_fit)) - np.tanh(sigma_fit * (r - R_fit))
    denominator = 2 * np.tanh(sigma_fit * R_fit)
    return numerator / denominator

def run_symbolic_regression(csv_path="physics/warp/data/optimized_bubble.csv"):
    print("[*] Iniciando proceso de regresión simbólica...")
    
    # 1. Load data
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el archivo de datos del PINN: {csv_path}. Asegúrate de ejecutar el PINN primero.")
        
    df = pd.read_csv(csv_path)
    X = df["r"].values
    y = df["f_r"].values
    
    equation_text = ""
    equation_latex = ""
    fitted_y = None
    method_used = ""
    
    # 2. Try PySR first
    pysr_success = False
    try:
        print("[*] Intentando importar y configurar PySR...")
        from pysr import PySRRegressor
        
        # Configure the regressor
        regressor = PySRRegressor(
            model_selection="best",
            niterations=40,
            population_size=30,
            binary_operators=["+", "-", "*", "/"],
            unary_operators=["exp", "tanh", "square", "cube"],
            constraints={"/": (-1, 9)},  # prevent division overflow
            maxsize=20,
            parsimony=0.01,
            random_state=42,
            progress=False
        )
        
        print("[*] Ejecutando regresión simbólica con PySR...")
        regressor.fit(X.reshape(-1, 1), y)
        
        # Get best equation
        best_row = regressor.equations_.iloc[-1]
        equation_text = best_row["equation"]
        equation_latex = best_row["sympy_format"] # sympy conversion
        fitted_y = regressor.predict(X.reshape(-1, 1))
        method_used = "PySR"
        pysr_success = True
        print("[+] Regresión simbólica con PySR finalizada con éxito.")
        
    except Exception as e:
        print(f"[!] PySR no está disponible o falló (Falta Julia, dependencias, etc.): {e}")
        print("[*] Activando el Fallback de alta precisión: Ajuste de curvas no lineal adaptativo.")
        
        # 3. Fallback: Fit optimized Alcubierre function with adaptive R and sigma
        # Initial guess: R = 0.5, sigma = 4.0 (half of original to account for PINN smoothing)
        popt, pcov = curve_fit(optimized_alcubierre_model, X, y, p0=[0.5, 4.0], bounds=([0.1, 0.5], [0.9, 15.0]))
        R_fit, sigma_fit = popt
        
        # Calculate fitted values
        fitted_y = optimized_alcubierre_model(X, R_fit, sigma_fit)
        
        # Write equations
        equation_text = f"(tanh({sigma_fit:.4f} * (r + {R_fit:.4f})) - tanh({sigma_fit:.4f} * (r - {R_fit:.4f}))) / (2 * tanh({sigma_fit:.4f} * {R_fit:.4f}))"
        equation_latex = r"\frac{\tanh(" + f"{sigma_fit:.4f}" + r"(r + " + f"{R_fit:.4f}" + r")) - \tanh(" + f"{sigma_fit:.4f}" + r"(r - " + f"{R_fit:.4f}" + r"))}{2 \tanh(" + f"{sigma_fit:.4f} \cdot {R_fit:.4f}" + r")}"
        method_used = f"Curve Fit No Lineal Adaptativo (R_fit={R_fit:.4f}, sigma_fit={sigma_fit:.4f})"
        
        print(f"[+] Ajuste de curva completado. R_fit = {R_fit:.4f}, sigma_fit = {sigma_fit:.4f}")
        
    # 4. Validation metrics
    mse = np.mean((y - fitted_y) ** 2)
    print(f"\n=== RESULTADOS DE LA REGRESIÓN ({method_used}) ===")
    print(f"Error Cuadrático Medio (MSE): {mse:.8e}")
    print(f"Ecuación texto plano: {equation_text}")
    print(f"Ecuación LaTeX: {equation_latex}")
    
    # 5. Save outputs
    os.makedirs("physics/warp", exist_ok=True)
    
    # Save equation string
    eq_txt_path = "physics/warp/optimized_metric_equation.txt"
    with open(eq_txt_path, "w", encoding="utf-8") as f:
        f.write(equation_text)
    print(f"[+] Ecuación guardada en: {eq_txt_path}")
    
    # Save comparison plot
    plt.figure(figsize=(10, 6))
    plt.style.use('dark_background')
    plt.scatter(X[::5], y[::5], color="#26ffad", alpha=0.6, label="Puntos PINN (Muestreado 1/5)", s=25)
    plt.plot(X, fitted_y, color="#ffb821", linewidth=3, label=f"Ajuste Simbólico ({method_used})")
    
    plt.title("Ajuste Simbólico de la Burbuja Warp Optimizada", color="white", fontsize=14, pad=15)
    plt.xlabel("Coordenada Radial Normalizada r", color="#94a3b8", fontsize=11)
    plt.ylabel("Función de Forma f(r)", color="#94a3b8", fontsize=11)
    plt.grid(color="white", linestyle=":", alpha=0.1)
    plt.legend(facecolor="#0f172a", edgecolor="#1e293b", labelcolor="white")
    
    plot_path = "physics/warp/symbolic_fit.png"
    plt.tight_layout()
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"[+] Gráfica comparativa guardada en: {plot_path}")
    
    print("\n--- INSTRUCCIONES DE INSTALACIÓN DE PYSR ---")
    print("Para usar la regresión simbólica evolutiva pura con PySR:")
    print("  1. Instala Julia: https://julialang.org/downloads/")
    print("  2. Ejecuta en tu terminal: pip install pysr")
    print("  3. Configura PySR desde Python: python -c \"import pysr; pysr.install()\"")

if __name__ == "__main__":
    run_symbolic_regression()
