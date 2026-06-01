#!/usr/bin/env python3
"""
Dashboard Application Main Entry Point
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import dash
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dashboard.warp_page import app as warp_app

# Define base application launcher
app = warp_app

if __name__ == "__main__":
    print("\n========================================================")
    print("🚀 INICIANDO DASHBOARD CIENTÍFICO DE VISUALIZACIÓN WARP 🚀")
    print("========================================================")
    print("  -> Servidor ejecutándose en local en el puerto 8050")
    print("  -> URL de acceso: http://127.0.0.1:8050")
    print("========================================================\n")
    app.run(debug=True, port=8050)
