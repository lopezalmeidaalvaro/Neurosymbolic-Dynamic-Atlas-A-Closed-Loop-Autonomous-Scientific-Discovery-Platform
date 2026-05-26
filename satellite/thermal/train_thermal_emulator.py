#!/usr/bin/env python3
"""
Thermal Neural Emulator Trainer for LEO Satellites
Trains a PyTorch neural network to predict the orbital temperature profile (min/max/average)
Author: Alvaro Lopez Almeida
"""

import os
import sys
import random
import json

# Add parent directory to path to allow importing the simulator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orbital_thermal_simulator import run_simulation

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

class ThermalEmulator(nn.Module if PYTORCH_AVAILABLE else object):
    def __init__(self):
        if not PYTORCH_AVAILABLE:
            return
        super().__init__()
        # Input: [Power, Area, Absorptivity, Emissivity]
        # Output: [MinTemp, MaxTemp, AvgTemp]
        self.net = nn.Sequential(
            nn.Linear(4, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 3)
        )
        
    def forward(self, x):
        return self.net(x)

def generate_dataset(size=60):
    print(f"[*] Generating {size} synthetic orbital thermal profiles...")
    dataset = []
    
    for i in range(size):
        # Sample realistic engineering ranges
        power = random.uniform(50.0, 800.0)      # W
        area = random.uniform(1.0, 8.0)         # m2
        absorptivity = random.uniform(0.1, 0.9)  # alpha
        emissivity = random.uniform(0.1, 0.9)    # epsilon
        
        telemetry = run_simulation(power, area, absorptivity, emissivity, num_orbits=2)
        
        temps = [pt['Temp_C'] for pt in telemetry]
        min_t = min(temps)
        max_t = max(temps)
        avg_t = sum(temps) / len(temps)
        
        dataset.append({
            'inputs': [power, area, absorptivity, emissivity],
            'outputs': [min_t, max_t, avg_t]
        })
        
    print(f"[+] Dataset generation complete. Created {len(dataset)} samples.")
    return dataset

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "..", "models", "thermal_emulator.pth")
    meta_path = os.path.join(script_dir, "..", "models", "thermal_emulator_metadata.json")
    
    if not PYTORCH_AVAILABLE:
        print("[!] PyTorch is not available. Skipping emulator neural training.")
        print("[!] Generating metadata JSON placeholder to ensure API compatibility.")
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
        with open(meta_path, 'w') as f:
            json.dump({"pytorch": "missing", "emulator": "simulated"}, f, indent=2)
        return

    # Generate synthetic training data
    data = generate_dataset(40)
    
    # Format PyTorch tensors
    inputs = torch.tensor([item['inputs'] for item in data], dtype=torch.float32)
    targets = torch.tensor([item['outputs'] for item in data], dtype=torch.float32)
    
    # Scale inputs/outputs simple Z-score / MinMax for training stability
    # Here we use raw inputs since MLP is small and values are stable
    model = ThermalEmulator()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    print("[*] Training orbital thermal neural network emulator...")
    model.train()
    
    epochs = 400
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 50 == 0:
            print(f" -> Epoch {epoch+1}/{epochs} | Loss: {loss.item():.4f}")
            
    print("[+] Training completed successfully.")
    
    # Save checkpoints
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    torch.save(model.state_dict(), model_path)
    print(f"[+] Discovered thermal emulator weights saved to: {model_path}")
    
    # Save training metadata
    metadata = {
        'status': 'trained',
        'epochs': epochs,
        'final_loss': float(loss.item()),
        'features': ['Power_W', 'Area_m2', 'Absorptivity', 'Emissivity'],
        'targets': ['Min_Temp_C', 'Max_Temp_C', 'Avg_Temp_C']
    }
    
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"[+] Emulator metadata saved to: {meta_path}")

if __name__ == '__main__':
    main()
