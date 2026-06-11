# README Audit

Audit date: 2026-05-31

Scope: root repository, Python modules, Next.js dashboard, satellite digital twin stack, CI, requirements, datasets, generated artifacts, papers, and the nested `autonomous-spacecraft-thermal-os/` copy.

## Executive Summary

The current root `README.md` correctly identifies the repository as a hybrid neurosymbolic scientific-discovery and spacecraft thermal digital twin workspace. However, it mixes implemented code, generated reports, aspirational language, and placeholder domains without always separating them.

The strongest implemented areas are:

| Area | Implementation Evidence |
|---|---|
| Spacecraft thermal digital twin | `satellite/thermal/multi_node_thermal_network.py`, `satellite/thermal/orbital_environment.py`, `satellite/run_thermal_pipeline.py`, `satellite/api/thermal_api.py` |
| Scientific dynamical-system pipeline | `physics/neurosymbolic/pipeline.py`, `physics/run_pipeline.py`, `physics/synthetic_systems.py`, `physics/symbolic_discovery.py` |
| Neural ODE, PINN, DeepONet prototypes | `physics/neural_ode_module.py`, `physics/pinn_module.py`, `physics/operator_learning.py`, `physics/core/neurosymbolic/*` |
| Dashboard | `dashboard/src/app/[lang]/dashboard/page.tsx`, `dashboard/src/app/[lang]/satellite/page.tsx`, `dashboard/package.json` |
| Validation and benchmark artifacts | `physics/tests/*`, `satellite/tests/test_satellite_twin.py`, `benchmark/README.md`, `reproduce/reproduce_t18.py` |

The least supported or overstated areas are:

| Area | Finding |
|---|---|
| Mathematics domain | `mathematics/README.md` and `mathematics/symbolic/README.md` explicitly say the area is a placeholder. |
| Quantum computing domain | `quantum/README.md` and `quantum/circuits/README.md` explicitly say the area is planned. |
| Neo4j knowledge graph | Code exists in `physics/knowledge_graph.py`, but it gracefully bypasses operations when Neo4j is offline. Existing reports note fallback placeholders. |
| Fully autonomous scientist | Implemented orchestration exists, but it depends on external LLM API keys and generated code execution. This is a partial system, not a self-contained autonomous scientist. |
| "Real telemetry" and flight readiness claims | Several docs claim NASA/ESA or flight-ready provenance; code mostly uses simulated, generated, or local CSV artifacts. These claims need external evidence before being treated as verified. |

## Overstated Claims

| Current README Claim | Audit Result | Evidence |
|---|---|---|
| "state-of-the-art closed-loop AI4Science discovery engine" | Overstated. There is a working research scaffold, but not enough comparative evidence to claim state of the art. | `physics/run_pipeline.py`, `physics/sota_benchmark.py`, `artifacts/sota_report.md` |
| "persistent scientific memory (SQLite & Neo4j)" | Partially implemented. SQLite fallback and Neo4j wrapper exist; Neo4j is optional and commonly bypassed if offline. | `physics/knowledge_graph.py`, `physics/core/autonomous/autonomous_scientist.py`, `physics/artifacts/knowledge_report.md` |
| "DeepONets" as a peer capability with the other core methods | Partially implemented prototype. DeepONet class and training helper exist, but integration is limited. | `physics/operator_learning.py`, `physics/run_pipeline.py --operator_learning` |
| "Mathematics: theorem provers and Lean 4 verification" | Planned, not implemented. | `mathematics/README.md`, `mathematics/symbolic/README.md` |
| "Quantum: VQE and quantum reservoir lab" | Planned, not implemented. | `quantum/README.md`, `quantum/circuits/README.md` |
| "flight-ready digital twin" | Overstated. Flight runtime, ONNX export, RTOS simulation, and assurance scripts exist, but no certified flight deployment evidence is present. | `satellite/flight/*`, `satellite/trl/TRL_ASSESSMENT.md` |
| "real telemetry" as a verified dataset source | Needs qualification. Docs name real mission sources, but code and local files do not independently prove provenance. | `datasets/README.md`, `satellite/models/telemetry.csv`, `satellite/thermal/ingest_real_thermal_data.py` |
| "FEM correlation against professional FEM" | Needs qualification. Correlator implements a reference/emulated FEM comparison, not an externally integrated FEM solver. | `satellite/thermal/fem_correlation.py`, `reproduce/reproduce_t18.py` |

## Missing Features In README

| Implemented Feature | Evidence |
|---|---|
| FastAPI thermal API with auth, rate limiting, health, metrics, reports, and model metadata endpoints | `satellite/api/thermal_api.py` |
| Flight software export and runtime artifacts | `satellite/flight/export_to_onnx.py`, `satellite/flight/flight_runtime.py`, `satellite/flight/rtos_runtime_sim.py`, `satellite/flight/software_assurance.py` |
| Estimation, radiation, EMC, ADCS, mission operations, constellation, and self-healing scripts | `satellite/estimation/`, `satellite/radiation/`, `satellite/emc/`, `satellite/adcs/`, `satellite/ops/`, `satellite/constellation/`, `satellite/autonomy/` |
| Pydantic-style experiment/session schemas | `physics/core/schemas/*.py` |
| Dashboard i18n and interactive satellite workflow | `dashboard/src/lib/i18n/dictionaries.ts`, `dashboard/src/app/[lang]/satellite/page.tsx` |
| Dedicated reproducible lightweight pipeline path | `physics/neurosymbolic/pipeline.py`, `physics/config.yaml` |

## Outdated Or Incorrect Sections

| README Section | Issue |
|---|---|
| Repository tree | Mentions `physics/core/dynamic`, `physics/core/features`, and some structures that do not exist as written. The current tree has `physics/core/autonomous`, `physics/core/empirical`, `physics/core/io`, `physics/core/neurosymbolic`, `physics/core/schemas`, and `physics/core/validation`. |
| Quick Start: `cd physics && python run_pipeline.py` | Broken in this environment because `symbolic_discovery.py` imports `physics.core.*` after `physics/` is inserted ahead of the project root. `python -m physics.run_pipeline --system harmonic --config physics/config.yaml` works from the repository root. |
| Quick Start: `python thermal/orbital_thermal_simulator.py ...` from `satellite/` | The simulator works when invoked from the root as `python satellite/thermal/orbital_thermal_simulator.py --power 10 --area 0.1 --emissivity 0.8`. |
| Requirements | Root `requirements.txt` omits several optional or used packages such as FastAPI, Uvicorn, PySINDy, PySR, Neo4j, ReportLab, ONNX Runtime, XGBoost, Ray, and serial interfaces. Some are optional, but docs should label them that way. |
| Publications | The root README includes DOI/arXiv-style badges and citation metadata that are not all backed by local publication metadata. Local papers and references exist, but external identifiers should be verified before publication claims. |

## Broken Or Conditional Entry Points

| Command | Result |
|---|---|
| `python -m pytest physics/tests/neurosymbolic -q` | Passed: 3 tests. |
| `python -m pytest satellite/tests -q` | Passed: 5 tests, with two syntax warnings in `geometry_topology_optimizer.py`. |
| `npm run build` in `dashboard/` | Passed. Next.js build emitted Recharts warnings about chart containers with width/height `-1`. |
| `python physics/run_pipeline.py --system harmonic --config physics/config.yaml` | Failed: `ModuleNotFoundError: No module named 'physics'`. |
| `python -m physics.run_pipeline --system harmonic --config physics/config.yaml` | Passed and wrote `results/harmonic`. |
| `python satellite/thermal/orbital_thermal_simulator.py --power 10 --area 0.1 --emissivity 0.8` | Passed and regenerated `satellite/models/telemetry.csv` and `satellite/models/thermal_simulation.png`. |

## Missing Documentation

| Module | Documentation Gap |
|---|---|
| `physics/core/schemas` | Data contracts are important but underdocumented in root README. |
| `physics/core/validation` | Many validation audits exist, but README does not clearly separate tested, generated, and optional audit components. |
| `satellite/api/thermal_api.py` | API endpoint table should be promoted from satellite docs into the root README. |
| `satellite/flight` | Needs a clear statement that these are export/runtime prototypes, not certified flight software. |
| `autonomous-spacecraft-thermal-os/` | Needs explanation as a nested distribution/mirror of the spacecraft stack to avoid confusing duplicate files. |

## README Quality Review

Initial score of current README:

| Criterion | Score | Reason |
|---|---:|---|
| Accuracy | 6/10 | Real implementation is broad, but several claims are overstated or outdated. |
| Completeness | 7/10 | Satellite and dashboard coverage is incomplete; planned domains are mixed with implemented ones. |
| Scientific Rigor | 6/10 | Needs clearer distinction between simulated, generated, optional, and externally verified evidence. |
| Reproducibility | 7/10 | Some working commands exist, but the primary physics command is broken unless run as a module. |
| Contributor Friendliness | 7/10 | Good high-level structure, but setup and optional dependency boundaries are unclear. |

The reconstructed README in `README_REWRITTEN.md` addresses these issues by using implementation-backed claims only.
