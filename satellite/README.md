# Satellite Domain — Orbital Thermal Digital Twin

This directory houses the **LEO Spacecraft Orbital Thermal Simulator** (Phase T) and its **Neural Surrogate Emulator**.

## Physical Mathematical Model

The simulator solves the spacecraft's thermodynamic heat balance equation numerically (using the Euler method):

$$m C_p \frac{dT}{dt} = Q_{\text{solar}}(t) + Q_{\text{earth}}(t) + P_{\text{internal}} - \sigma \epsilon A T(t)^4$$

Where:
- $m C_p = 135000 \text{ J/K}$ (thermal capacity of a $150\text{ kg}$ aluminum satellite body).
- $P_{\text{internal}}$ is the controllable internal electrical power (heat dissipation by avionics).
- $Q_{\text{solar}}(t)$ is the incident solar flux in Low Earth Orbit (LEO), modeled with eclipse shadow phases ($\approx 40\%$ of the $94.6\text{ minutes}$ orbital cycle).
- $Q_{\text{earth}}(t)$ is the Earth infrared radiation absorbed by the spacecraft ($230\text{ W/m}^2$).
- $\sigma = 5.67 \times 10^{-8} \text{ W/m}^2\text{K}^4$ is the Stefan-Boltzmann constant.
- $A$ is the radiator surface area, $\epsilon$ is the infrared emissivity, and $\alpha$ is the solar absorptivity.

---

## Directory Structure

```
satellite/
├── thermal/             # Physical simulator and Neural network emulator
│   ├── orbital_thermal_simulator.py  # Numerical LEO solver (CLI + Plotting)
│   └── train_thermal_emulator.py     # Trains PyTorch MLP surrogate emulator
├── api/                 # Programmatic Python API
│   └── thermal_api.py   # API integration class
├── models/              # Saved PyTorch models, CSV telemetry and cycle plots
│   └── telemetry.csv    # Stabilized orbit telemetry CSV
└── README.md            # This documentation file
```

---

## Quick Start & Usage

### 1. Run the Numerical Simulation (CLI)
Execute the numerical orbital simulator by adjusting sliders as arguments:
```bash
python thermal/orbital_thermal_simulator.py --power 250 --area 3.0 --absorptivity 0.3 --emissivity 0.85
```

This will:
- Solve LEO thermodynamics.
- Print a scientific diagnostic report.
- Save stabilized orbit telemetry to `models/telemetry.csv`.
- Save a beautiful thermal cycle plot to `models/thermal_simulation.png` (if `matplotlib` is installed).

### 2. Train the Neural Emulator (Surrogate)
Train a multi-layer perceptron in PyTorch to emulate the physical model:
```bash
python thermal/train_thermal_emulator.py
```
This trains the neural network to instantly predict the spacecraft's peak and minimum temperatures, saving the weights to `models/thermal_emulator.pth`.

### 3. Programmatic API
Integrate the simulator into other scripts:
```python
from api.thermal_api import SpacecraftThermalAPI

api = SpacecraftThermalAPI()
results = api.solve_simulation(power=200, area=2.5, absorptivity=0.3, emissivity=0.8)
print("Peak Temp:", results['summary']['max_temp'])
```
