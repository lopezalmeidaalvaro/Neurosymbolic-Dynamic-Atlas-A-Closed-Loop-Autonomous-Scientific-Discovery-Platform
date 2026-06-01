# config.py
from pathlib import Path
import sys

# Core Standalone Root Directory paths
ROOT_DIR = Path(__file__).resolve().parent
SATELLITE_DIR = ROOT_DIR / "satellite"
DASHBOARD_DIR = ROOT_DIR / "dashboard"
BACKEND_DIR = ROOT_DIR / "backend"

# Ensure all system directories are in sys.path for absolute imports
for directory in [ROOT_DIR, SATELLITE_DIR, SATELLITE_DIR / "thermal"]:
    dir_str = str(directory)
    if dir_str not in sys.path:
        sys.path.insert(0, dir_str)
