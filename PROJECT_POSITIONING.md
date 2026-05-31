# Project Positioning

## True Project Identity

This repository is best described as a hybrid research infrastructure project combining:

1. A neurosymbolic dynamical-systems research pipeline.
2. A spacecraft orbital thermal digital twin and engineering simulation stack.
3. A dashboard for presenting experiments, telemetry, benchmarks, and satellite interactions.
4. A collection of generated scientific reports, papers, benchmark artifacts, and roadmap documents.

The project is not primarily a theorem-proving mathematics project or a quantum-computing project. Those folders currently function as roadmap placeholders.

## Category Weighting

| Category | Estimated Contribution | Evidence |
|---|---:|---|
| Spacecraft thermal digital twin framework | 35% | `satellite/thermal/*`, `satellite/api/thermal_api.py`, `satellite/flight/*`, `satellite/tests/test_satellite_twin.py`, many satellite reports and model artifacts |
| Neurosymbolic AI and scientific discovery infrastructure | 25% | `physics/neurosymbolic/*`, `physics/core/neurosymbolic/*`, `physics/symbolic_discovery.py`, `physics/core/autonomous/*` |
| Research and benchmark infrastructure | 20% | `physics/tests/*`, `satellite/tests/*`, `benchmark/README.md`, `datasets/README.md`, `reproduce/reproduce_t18.py`, CI workflows |
| Dashboard and communication layer | 10% | `dashboard/src/app/*`, `dashboard/src/components/*`, `dashboard/public/artifacts/*` |
| Autonomous scientist | 5% | `physics/core/autonomous/*`, `satellite/thermal/autonomous_thermal_discovery.py`; meaningful but conditional on LLM/API/sandbox and narrower than the full repo |
| Quantum gravity toy-model simulation | 3% | `physics/qg_*`, `physics/causal_layered_graph.py`, `physics/spin_network_model.py`, `physics/bec_analog_model.py` |
| Formal mathematics and quantum computing roadmap | 2% | `mathematics/README.md`, `quantum/README.md`; explicitly planned placeholders |

## Best Public Positioning

Recommended title:

`Neurosymbolic Scientific Discovery and Spacecraft Thermal Digital Twin`

Recommended one-sentence identity:

This repository is a research-grade Python and Next.js workspace for dynamical-system discovery, symbolic model recovery, and spacecraft orbital thermal digital-twin simulation, with implemented neural, symbolic, validation, API, dashboard, and reproducibility components.

## Audience Fit

| Audience | What Is Real Today |
|---|---|
| Researchers | Dynamical-system generation, Neural ODE/PINN/DeepONet prototypes, symbolic recovery, CKA-style audits, generated papers and reports. |
| ML engineers | PyTorch models, `torchdiffeq`, DeepXDE, sklearn, model artifacts, training scripts, reproducibility tests. |
| Physics scientists | ODE systems, thermal balance equations, orbital radiative fluxes, symbolic equations, uncertainty and validation scripts. |
| Aerospace engineers | 1-node and 6-node thermal models, LEO environment, HIL simulation, CAD thermal importer, ECSS-style reports, flight-runtime prototypes. |
| Open source contributors | Python tests, Next.js dashboard, CI, clear module boundaries, several optional dependency gaps to clean up. |
| Investors / industry reviewers | A broad prototype stack with demos, API, dashboard, and validation reports, but not certified flight software or externally proven FEM/telemetry validation. |

## Risk-Adjusted Claims

Use:

- "Implements a spacecraft thermal digital twin prototype."
- "Includes Neural ODE, PINN, DeepONet, and symbolic regression components."
- "Provides generated benchmark artifacts and reproducibility scripts."
- "Includes optional autonomous scientist and Neo4j memory integrations."
- "Includes dashboard and API prototypes."

Avoid unless externally verified:

- "Flight ready."
- "State of the art."
- "NASA/ESA validated."
- "Professional FEM verified" without explaining the local/emulated reference.
- "Autonomous scientist" without noting LLM/API dependency.
- "Quantum computing platform" or "formal theorem proving system."

## Recommended Roadmap Framing

Implemented:

- Thermal solvers, orbital environment, FastAPI, dashboard, surrogate models, Neural ODE, PINN, symbolic recovery fallback, tests, CI, generated benchmark artifacts.

In progress:

- Dependency consolidation, documented module entry points, stronger API/dashboard integration, optional Neo4j and LLM workflows, flight-runtime validation.

Planned:

- Formal theorem proving, quantum circuits, hardware DAQ/TVAC integration, certified flight software path, externally sourced telemetry and FEM validation packages.
