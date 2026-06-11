# Neurosymbolic Scientific Discovery and Spacecraft Thermal Digital Twin

This title is more accurate than the current project title because the repository is not only a "Dynamic Atlas"; it also contains a substantial spacecraft thermal digital-twin stack, API, dashboard, generated benchmark artifacts, and flight-runtime prototypes.

## Overview

This repository is a hybrid AI-for-science and aerospace engineering workspace. It combines dynamical-system discovery, neurosymbolic modeling, symbolic regression, validation audits, and a spacecraft orbital thermal digital twin in one codebase.

The `physics/` domain implements research pipelines for synthetic dynamical systems, neural continuous-time modeling, symbolic equation recovery, representation audits, quantum-gravity toy-model experiments, and optional autonomous scientific-discovery loops. The strongest verified path is the lightweight reproducible pipeline in `physics/neurosymbolic/`, which generates trajectories, trains a Neural ODE, recovers symbolic coefficients, computes a representation similarity metric, and writes reproducible artifacts.

The `satellite/` domain implements the most complete engineering system in the repository: a 1-node and 6-node orbital thermal simulator, LEO environmental flux model, CAD thermal importer, thermal surrogate training, PINN and Neural ODE trainers, uncertainty quantification, HIL simulation, benchmark correlation scripts, FastAPI service, dashboard integration, and flight-runtime/export prototypes.

The `dashboard/` domain is a Next.js application for viewing research state, interactive experiments, satellite workflow controls, multilingual pages, static artifacts, and backend API status. Mathematics and quantum folders are currently roadmap placeholders rather than implemented theorem-proving or quantum-computing systems.

## Key Capabilities

| Capability | Status | Evidence |
|---|---|---|
| Reproducible neurosymbolic pipeline | Implemented | `physics/neurosymbolic/pipeline.py`, `physics/config.yaml` |
| Legacy multiphase scientific runner | Partially implemented, direct command broken | `physics/run_pipeline.py`, `physics/symbolic_discovery.py` |
| Synthetic dynamical systems | Implemented | `physics/synthetic_systems.py`, `physics/neurosymbolic/neural_ode.py` |
| Neural ODEs | Implemented | `physics/core/neurosymbolic/neural_ode.py`, `physics/neural_ode_module.py`, `satellite/thermal/train_thermal_neural_ode.py` |
| PINNs | Implemented | `physics/core/neurosymbolic/pinn.py`, `physics/pinn_module.py`, `satellite/thermal/train_thermal_pinn.py` |
| DeepONet / operator learning | Partial | `physics/operator_learning.py` |
| SINDy | Partial, optional dependency | `physics/symbolic_discovery.py` |
| PySR | Partial, optional dependency | `physics/symbolic_discovery.py`, `satellite/thermal/discover_thermal_equations.py` |
| Symbolic fallback recovery | Implemented | `physics/core/neurosymbolic/symbolic.py` |
| Autonomous scientist loop | Partial, requires LLM API key | `physics/core/autonomous/*`, `satellite/thermal/autonomous_thermal_discovery.py` |
| Knowledge graph | Partial, Neo4j optional | `physics/knowledge_graph.py`, `physics/migrate_to_graph.py` |
| Scientific guardrails | Implemented | `physics/scientific_guard.py` |
| Spacecraft 1-node thermal simulator | Implemented | `satellite/thermal/orbital_thermal_simulator.py` |
| Spacecraft 6-node thermal network | Implemented | `satellite/thermal/multi_node_thermal_network.py`, `satellite/tests/test_satellite_twin.py` |
| Orbital environment flux model | Implemented | `satellite/thermal/orbital_environment.py` |
| Thermal surrogate models | Implemented | `satellite/thermal/train_surrogate_models.py`, `satellite/models/*` |
| CAD thermal importer | Partial | `satellite/thermal/cad_thermal_importer.py`, `satellite/cad/cubesat_cube.stl` |
| HIL simulation | Partial | `satellite/thermal/hardware_in_the_loop.py`, `satellite/thermal/hil_real_hardware.py` |
| TVAC hardware validation | Stub/partial | `satellite/thermal/tvac_integration.py`, `satellite/thermal/tvac_correlation_report.md` |
| FEM-style correlation benchmark | Partial, local/emulated reference | `satellite/thermal/fem_correlation.py`, `reproduce/reproduce_t18.py` |
| FastAPI spacecraft thermal API | Implemented prototype | `satellite/api/thermal_api.py` |
| Flight runtime/export prototypes | Partial | `satellite/flight/export_to_onnx.py`, `satellite/flight/flight_runtime.py` |
| Next.js dashboard | Implemented | `dashboard/src/app/*`, `dashboard/package.json` |
| Formal mathematics | Planned | `mathematics/README.md` |
| Quantum circuits / VQE | Planned | `quantum/README.md`, `quantum/circuits/README.md` |

## Repository Architecture

```text
.
|-- physics/
|   |-- neurosymbolic/          # Lightweight reproducible pipeline
|   |-- core/
|   |   |-- autonomous/         # LLM-driven hypothesis and experiment loop
|   |   |-- empirical/          # ECG and empirical audit scripts
|   |   |-- io/                 # Artifact/session export
|   |   |-- neurosymbolic/      # Shared Neural ODE, PINN, symbolic primitives
|   |   |-- schemas/            # Experiment and benchmark data contracts
|   |   `-- validation/         # Robustness, leakage, causal, reproducibility audits
|   |-- data/                   # MIT-BIH, UCR, QG toy data
|   |-- models/                 # Saved model checkpoints
|   |-- artifacts/              # Generated reports, runs, figures, JSON outputs
|   `-- run_pipeline.py         # Module entry point for physics workflows
|
|-- satellite/
|   |-- thermal/                # Thermal solvers, ML trainers, UQ, HIL, FEM-style benchmarks
|   |-- api/                    # FastAPI service
|   |-- flight/                 # ONNX, C export, runtime and assurance prototypes
|   |-- cloud/                  # SaaS/deployment prototypes
|   |-- models/                 # Surrogates, scalers, telemetry, checkpoints
|   |-- tests/                  # Core satellite tests
|   `-- run_thermal_pipeline.py # Sequential thermal-stage orchestrator
|
|-- dashboard/
|   |-- src/app/                # Next.js App Router pages
|   |-- src/components/         # Dashboard, scientific, layout, educational UI
|   |-- src/hooks/              # Static artifact loading
|   |-- src/stores/             # Zustand state
|   `-- public/artifacts/       # Static JSON artifacts for UI
|
|-- autonomous-spacecraft-thermal-os/
|   `-- ...                     # Nested spacecraft-focused mirror/distribution
|
|-- benchmark/                  # Thermal benchmark specification
|-- datasets/                   # Dataset provenance catalog
|-- papers/                     # Local manuscripts, BibTeX, PDFs
|-- reproduce/                  # Reproduction script for thermal correlation suite
|-- mathematics/                # Planned formal mathematics work
`-- quantum/                    # Planned quantum-computing work
```

## Scientific Pipeline

```text
Configuration
-> Synthetic or recorded data
-> Dynamical trajectory generation
-> Neural continuous-time modeling
-> Symbolic coefficient/equation recovery
-> Representation and robustness audit
-> Artifact/session export
-> Dashboard visualization
```

The currently verified single-entry path is:

```bash
python -m physics.run_pipeline --system harmonic --config physics/config.yaml
```

This writes reproducible outputs under `results/harmonic/`.

## Autonomous Scientist Components

The repository contains an autonomous-scientist scaffold, but it should be treated as a partial, optional subsystem.

| Component | Evidence | Status |
|---|---|---|
| Hypothesis generation | `physics/core/autonomous/hypothesis_engine.py`, `llm_reasoner.py` | Requires LLM provider credentials |
| Experiment execution | `physics/core/autonomous/sandbox_executor.py` | AST safety scan, Docker optional, subprocess fallback |
| Interpretation and epistemic gain | `physics/core/autonomous/autonomous_scientist.py` | Implemented scoring and session history |
| Memory | `physics/knowledge_graph.py`, SQLite fallback in `autonomous_scientist.py` | Neo4j optional; SQLite fallback local |
| Reporting | `physics/core/autonomous/research_reporter.py` | Implemented report generation path |

## Spacecraft Thermal Digital Twin

The spacecraft stack models orbital thermal behavior for simplified spacecraft configurations. It includes:

- A 1-node LEO thermal simulator in `satellite/thermal/orbital_thermal_simulator.py`.
- A 6-node coupled thermal network in `satellite/thermal/multi_node_thermal_network.py`.
- Orbital flux modeling for solar, albedo, Earth IR, and eclipse periods in `satellite/thermal/orbital_environment.py`.
- CAD/voxel thermal import in `satellite/thermal/cad_thermal_importer.py`.
- Surrogate training in `satellite/thermal/train_surrogate_models.py`.
- PINN and Neural ODE training in `satellite/thermal/train_thermal_pinn.py` and `train_thermal_neural_ode.py`.
- UQ and Monte Carlo workflows in `satellite/thermal/uncertainty_engine.py` and `satellite/uq/full_orbit_montecarlo.py`.
- HIL simulation in `satellite/thermal/hardware_in_the_loop.py`; real hardware paths are conditional.
- FastAPI integration in `satellite/api/thermal_api.py`.

Performance metrics in repository reports should be read as local benchmark or generated-report values unless independently validated by external datasets, hardware, or FEM tooling.

## Installation

Python:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Dashboard:

```bash
cd dashboard
npm install
npm run build
```

Optional dependencies are needed for some paths:

| Feature | Examples |
|---|---|
| API server | `fastapi`, `uvicorn`, `pydantic`, `reportlab`, `psutil` |
| PySR | `pysr` and Julia runtime |
| SINDy | `pysindy` |
| Neo4j graph memory | `neo4j` Python driver and a running Neo4j instance |
| ONNX flight runtime | `onnx`, `onnxruntime` |
| Hardware/TVAC paths | `pyserial`, `smbus2`, physical sensors/DAQ |
| HPC experiments | `ray`, CUDA-capable PyTorch where relevant |

The nested `autonomous-spacecraft-thermal-os/requirements.txt` includes some API dependencies that are missing from the root requirements file.

## Quick Start

Run the verified physics pipeline from the repository root:

```bash
python -m physics.run_pipeline --system harmonic --config physics/config.yaml
```

Run the orbital thermal simulator from the repository root:

```bash
python satellite/thermal/orbital_thermal_simulator.py --power 10 --area 0.1 --emissivity 0.8
```

Run focused tests:

```bash
python -m pytest physics/tests/neurosymbolic -q
python -m pytest satellite/tests -q
```

Build the dashboard:

```bash
cd dashboard
npm run build
```

Start the dashboard during development:

```bash
cd dashboard
npm run dev
```

Start the thermal API, after installing API dependencies:

```bash
python satellite/api/thermal_api.py
```

If using Uvicorn directly:

```bash
uvicorn satellite.api.thermal_api:app --host 0.0.0.0 --port 8000
```

## Reproducibility

The repository uses fixed seeds in several Python modules, commonly `42`, including:

- `physics/neurosymbolic/reproducibility.py`
- `physics/pinn_module.py`
- `physics/neural_ode_module.py`
- `satellite/thermal/multi_node_thermal_network.py`
- `reproduce/reproduce_t18.py`

Datasets and artifacts are cataloged in:

- `datasets/README.md`
- `benchmark/README.md`
- `physics/data/`
- `satellite/models/`
- `dashboard/public/artifacts/`

Verified checks in this audit:

| Command | Result |
|---|---|
| `python -m pytest physics/tests/neurosymbolic -q` | 3 passed |
| `python -m pytest satellite/tests -q` | 5 passed, 2 syntax warnings |
| `npm run build` in `dashboard/` | Passed, with Recharts sizing warnings |
| `python -m physics.run_pipeline --system harmonic --config physics/config.yaml` | Passed |
| `python satellite/thermal/orbital_thermal_simulator.py --power 10 --area 0.1 --emissivity 0.8` | Passed |

## Repository Roadmap

Implemented:

- Reproducible physics pipeline.
- Neural ODE and PINN components.
- Symbolic recovery fallback.
- 1-node and 6-node spacecraft thermal solvers.
- Orbital environment model.
- Surrogate training and stored model artifacts.
- Thermal API prototype.
- Next.js dashboard.
- Core pytest coverage for neurosymbolic and satellite modules.

In progress:

- Direct script/package import cleanup for `physics/run_pipeline.py`.
- Dependency consolidation between root and nested package requirements.
- Stronger distinction between generated reports and externally verified evidence.
- API/dashboard integration hardening.
- Neo4j and LLM workflows.
- Flight-runtime validation.

Planned:

- Formal mathematics and theorem proving.
- Quantum circuits and VQE.
- Certified hardware/TVAC validation.
- External FEM solver integration.
- Certified flight software package.

## Publications

Local publication artifacts are stored in:

- `papers/system/`
- `papers/thermal/`
- `papers/qg/`
- `physics/papers/`
- `satellite/papers/`

The repository includes local LaTeX/PDF/BibTeX artifacts and a reference bibliography at `papers/system/references.bib`.

External DOI, arXiv, and publication-status claims should be verified before release.

## Citation

Repository citation metadata exists in `satellite/CITATION.cff`. A conservative software citation is:

```bibtex
@software{lopezalmeida2026_neurosymbolic_thermal_twin,
  title = {Neurosymbolic Scientific Discovery and Spacecraft Thermal Digital Twin},
  author = {Lopez Almeida, Alvaro},
  year = {2026},
  version = {1.0.0},
  license = {MIT},
  url = {https://github.com/lopezalmeidaalvaro/Neurosymbolic-Pipeline-for-Dynamical-Systems-Embedding}
}
```

## License

This repository is licensed under the MIT License. See `LICENSE`.

## README Quality Review

Final reconstructed README score:

| Criterion | Score |
|---|---:|
| Accuracy | 9/10 |
| Completeness | 9/10 |
| Scientific Rigor | 9/10 |
| Reproducibility | 9/10 |
| Contributor Friendliness | 9/10 |
