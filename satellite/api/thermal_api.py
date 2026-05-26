#!/usr/bin/env python3
"""
Orbital Thermal Programmatic API Wrapper
Allows other pipelines or microservices to run spacecraft thermal simulations or load neural emulators.
Author: Alvaro Lopez Almeida
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from thermal.orbital_thermal_simulator import run_simulation

class SpacecraftThermalAPI:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(self.script_dir, "..", "models", "thermal_emulator.pth")
        self.meta_path = os.path.join(self.script_dir, "..", "models", "thermal_emulator_metadata.json")
        
    def solve_simulation(self, power, area, absorptivity, emissivity):
        """
        Runs the full LEO thermodynamic cycle solver.
        """
        telemetry = run_simulation(power, area, absorptivity, emissivity, num_orbits=2)
        temps = [p['Temp_C'] for p in telemetry]
        
        return {
            'telemetry': telemetry,
            'summary': {
                'min_temp': min(temps),
                'max_temp': max(temps),
                'avg_temp': round(sum(temps) / len(temps), 2),
                'status': 'optimal' if (min(temps) >= -20 and max(temps) <= 65) else ('critical' if (min(temps) < -40 or max(temps) > 85) else 'warning')
            }
        }
        
    def load_emulator_metadata(self):
        """
        Loads the trained PyTorch neural emulator metadata if it exists.
        """
        if os.path.exists(self.meta_path):
            with open(self.meta_path, 'r') as f:
                return json.load(f)
        return {'status': 'not_trained', 'error': 'Run train_thermal_emulator.py first.'}

# Quick test if run directly
if __name__ == '__main__':
    api = SpacecraftThermalAPI()
    result = api.solve_simulation(200.0, 2.0, 0.3, 0.8)
    print("\n[API Programmatic Run Success]")
    print(f" -> Stabilized Average Temperature: {result['summary']['avg_temp']}°C")
    print(f" -> Mission Safety State: {result['summary']['status'].upper()}")
