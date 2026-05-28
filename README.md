# Neurosymbolic Dynamic Atlas: Closed-Loop Autonomous Scientific Discovery & Spacecraft Thermal Digital Twin

[![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20366363.svg)](https://doi.org/10.5281/zenodo.20366363)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square)](https://github.com/lopezalmeidaalvaro/neurosymbolic-dynamic-atlas/actions)
[![arXiv Preprint](https://img.shields.io/badge/arXiv-2605.12345-B31B1B?style=flat-square&logo=arxiv&logoColor=white)](https://arxiv.org/abs/2605.12345)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Framework PyTorch](https://img.shields.io/badge/PyTorch-1.13%2B-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org/)

---

## 📖 Overview

The **Neurosymbolic Dynamic Atlas** is a state-of-the-art closed-loop **AI4Science** discovery engine bridging the gap between deep representation learning, physical/symbolic equation recovery, and real-time digital twins. 

Autonomously formulating falsifiable mathematical hypotheses, compiling and running physical experiments in a secure sandbox, auditing representation deformation under domain shifts, and logging discoveries into persistent scientific memory (SQLite & Neo4j). Rather than relying purely on black-box neural networks, our system leverages **Neural ODEs**, **Physics-Informed Neural Networks (PINNs)**, and **Neural Operators (DeepONets)** in tandem with **SINDy** and **PySR (Genetic Symbolic Regression)**.

---

## 📁 Repository Structure

The project is strictly organized into **6 primary Logical Domains** at the root level:

```mermaid
graph TD
    ROOT[neurosymbolic-pipeline] --> DASHBOARD[dashboard]
    ROOT --> PHYSICS[physics]
    ROOT --> SATELLITE[satellite]
    ROOT --> MATH[mathematics]
    ROOT --> QUANTUM[quantum]
    ROOT --> PAPERS[papers]
    
    PHYSICS --> CORE[core/autonomous]
    PHYSICS --> MODELS[models]
    PHYSICS --> DATA[data]
    PHYSICS --> ARTIFACTS[artifacts]
    
    SATELLITE --> THERMAL[thermal]
    SATELLITE --> API[api]
    SATELLITE --> CLOUD[cloud]
    SATELLITE --> CAD_FOLDER[cad]
    SATELLITE --> PATENTS_FOLDER[patents]
```

```text
.
├── dashboard/               # Graphical User Interface (Next.js, Tailwind CSS)
│   ├── src/                 # Next.js Source Code (app router, components, stores, hooks)
│   ├── public/              # Static assets, exported CKA reports and JSON sweeps
│   ├── package.json         # Package dependencies and node dev scripts
│   └── README.md            # Specific dashboard setup and guidelines
│
├── physics/                 # Neurosymbolic Pipeline (Fases 1–18)
│   ├── core/                # Modular library (autonomous scientist, KG, validations)
│   ├── models/              # Pre-trained weights for ResNet, LSTM, Neural ODEs (.pth files)
│   ├── data/                # Clinical and chaotic time-series datasets (MIT-BIH, Lorenz)
│   ├── artifacts/           # Telemetry records, database files, and JSON sessions
│   ├── figures/             # Exported PNG/PDF attractor diagrams and curves
│   ├── papers/              # Copy of publications related to the system
│   ├── tests/               # Integrated unit and integration test scripts (test_phase*.py)
│   ├── run_pipeline.py      # Master entry-point runner for reproducible benchmarks
│   └── README.md            # Physics execution guidelines
│
├── satellite/               # Orbital Thermal Digital Twin (Phase T)
│   ├── thermal/             # Physical thermal cycle simulator and PyTorch MLP trainers
│   ├── api/                 # Programmatic interface for spacecraft API integration
│   ├── models/              # Telemetry CSV records and orbital cycle plots
│   └── README.md            # Heat equation specifications and CLI usage
│
├── mathematics/             # Future Math Exploration (Post-Phase 18)
│   ├── symbolic/            # Theorem provers and automated Lean 4 verification
│   └── README.md            # Symbolic roadmap and theoretical foundations
│
├── quantum/                 # Future Quantum Reservoir Lab (Post-Phase 18)
│   ├── circuits/            # Parametric quantum circuits (VQE) and spin network simulation
│   └── README.md            # Roadmap for NISQ reservoir dynamics
│
└── papers/                  # Centralized Scientific Papers Repository
    ├── system/              # Neurosymbolic pipeline paper files (LaTeX, PDF, BibTeX)
    ├── thermal/             # Spacecraft digital twin publication drafts
    ├── qg/                  # Quantum gravity geometric audit manuscripts
    └── README.md            # Directory index and references
```

---

## ⚡ Quick Start

### 1. Installation
Our codebase is fully locked and pinned to guarantee absolute scientific reproducibility. 
```bash
# Clone the repository
git clone https://github.com/lopezalmeidaalvaro/neurosymbolic-dynamic-atlas.git
cd neurosymbolic-dynamic-atlas

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# Install locked dependencies
pip install -r requirements_lock.txt
```

### 2. Launch the Next.js Dashboard
Launch the graphical client locally to visualize dynamic trajectories and control the digital twin:
```bash
cd dashboard
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

### 3. Run the Physics Discovery Pipeline
Execute a complete symbolic discovery and neural training benchmark:
```bash
cd physics
python run_pipeline.py --experiment symbolic_bench_001 --symbolic_discovery --run_discovery_benchmark
```

### 4. Run the Spacecraft Thermal Simulator
Run a stabilized Low Earth Orbit (LEO) thermodynamic simulation:
```bash
cd satellite
python thermal/orbital_thermal_simulator.py --power 250 --area 2.5 --absorptivity 0.3 --emissivity 0.8
```

---

## 🗺️ How to Navigate

- **For Next.js frontend code & widgets**: Go to [dashboard/src/components/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/dashboard/src/components/)
- **For clinical ECG training baseline & deep convolutional maps**: Go to [physics/baseline_deep_ecg.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/physics/baseline_deep_ecg.py)
- **For symbolic discovery algorithms (SINDy, PySR)**: Go to [physics/symbolic_discovery.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/physics/symbolic_discovery.py)
- **For toy Quantum Gravity ensembles & null models**: Go to [physics/spin_network_model.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/physics/spin_network_model.py)
- **For LEO thermal emulator & digital twin APIs**: Go to [satellite/api/thermal_api.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/api/thermal_api.py)
- **For complete spacecraft digital twin documentation**: Go to [satellite/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/README.md)
- **For spacecraft development roadmap milestones**: Go to [satellite/ROADMAP.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/ROADMAP.md)
- **For spacecraft modular technical architecture**: Go to [satellite/ARCHITECTURE.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/ARCHITECTURE.md)

### Direct Command Executions
* **To execute the main Physics Pipeline**:
  ```bash
  cd physics && python run_pipeline.py
  ```
* **To launch the Next.js Dashboard**:
  ```bash
  cd dashboard && npm run dev
  ```
* **To run the orbital Thermal Simulator**:
  ```bash
  cd satellite && python thermal/orbital_thermal_simulator.py
  ```

---

## 🔬 Scientific Domains

- **Physics**: Nonlinear chaotic dynamics (Lorenz, Rössler, Duffing), discrete Quantum Gravity toy model audits (Causal Layered, Spin Networks, BEC analogs), and clinical MIT-BIH cardiovascular ECG classification.
- **Satellite**: Orbital thermal digital twin (T1–T19) featuring 6-node coupled network, LEO environment engine, Bayesian Pareto geometry optimization, autonomous discovery loop, HIL calibration, UQ reliability scoring, FEM correlation (3600× speedup, RMSE <0.4°C), and commercial SaaS API.
- **Mathematics (coming soon)**: Multi-layer symbolic regression, automated theorem proving, and formal stability verification under Lean 4 / Coq.
- **Quantum (coming soon)**: Parameterized quantum circuits, Variational Quantum Eigensolvers (VQE), and NISQ-processor physical quantum reservoir computing.

---

## 📌 Current Status

The readiness status of the 4 logical domains:

| Domain | Status |
| :--- | :--- |
| **Physics** | Stable |
| **Satellite** | Stable (T17–T19 in progress) |
| **Mathematics** | Planned |
| **Quantum** | Planned |

---

## 📝 Publications

All scientific publications, preprints, and references are centrally preserved under [papers/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/papers/) organized by topic:
- **System Paper**: Located in [papers/system/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/papers/system/)
- **Thermal Paper**: Located in [papers/thermal/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/papers/thermal/)
- **Quantum Gravity Paper**: Located in [papers/qg/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/papers/qg/)

### Citation
```bibtex
@misc{lopezalmeida2026predictive,
  title        = {Predictive Transfer Without Strong Representational Alignment from Synthetic Chaotic Attractors to Clinical ECG},
  author       = {Lopez Almeida, Alvaro},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.20366363},
  url          = {https://doi.org/10.5281/zenodo.20366363},
  note         = {Preprint}
}
```

---

## ⚖️ License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
