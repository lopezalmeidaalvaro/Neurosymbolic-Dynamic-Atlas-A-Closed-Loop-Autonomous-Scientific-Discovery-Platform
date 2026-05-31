# Capability Matrix

Status labels:

- FULLY IMPLEMENTED: Runnable local implementation and tests or generated outputs are present.
- PARTIALLY IMPLEMENTED: Meaningful code exists, but it depends on optional services, external credentials, incomplete integration, or generated/emulated inputs.
- STUB: Code path or document exists but is a placeholder, fallback, or demonstration.
- PLANNED: Documentation describes future work with little or no implementation.
- BROKEN: Main documented command or integration fails in the audited environment.

## Scientific And ML Capabilities

| Capability | Status | Evidence | Notes |
|---|---|---|---|
| Lightweight neurosymbolic pipeline | FULLY IMPLEMENTED | `physics/neurosymbolic/pipeline.py`, `physics/config.yaml` | Generates trajectories, trains a Neural ODE, recovers symbolic coefficients, computes linear CKA, writes metrics and plots. Works via `python -m physics.run_pipeline --system harmonic --config physics/config.yaml`. |
| Legacy multiphase physics runner | BROKEN as documented | `physics/run_pipeline.py`, `physics/symbolic_discovery.py` | `python physics/run_pipeline.py ...` fails in this environment due to `No module named 'physics'`. Module invocation works. |
| Synthetic dynamical systems | FULLY IMPLEMENTED | `physics/synthetic_systems.py`, `physics/neurosymbolic/neural_ode.py`, `physics/neurosymbolic/pipeline.py` | Lorenz, Rossler, Duffing, harmonic, and related generators are used by pipelines and tests. |
| Neural ODEs | FULLY IMPLEMENTED | `physics/core/neurosymbolic/neural_ode.py`, `physics/neural_ode_module.py`, `satellite/thermal/train_thermal_neural_ode.py` | Uses `torchdiffeq`; focused tests pass. |
| PINNs | FULLY IMPLEMENTED | `physics/core/neurosymbolic/pinn.py`, `physics/pinn_module.py`, `satellite/thermal/train_thermal_pinn.py` | Uses DeepXDE/PyTorch for forward and inverse ODE modes. Optional dependency must be installed. |
| DeepONet / operator learning | PARTIALLY IMPLEMENTED | `physics/operator_learning.py`, `physics/run_pipeline.py --operator_learning` | Model and training helper exist, but integration and testing are narrow. |
| SINDy | PARTIALLY IMPLEMENTED | `physics/symbolic_discovery.py`, `physics/core/neurosymbolic/symbolic.py` | SINDy path imports `pysindy`; deterministic Lasso fallback exists for some symbolic recovery. `pysindy` is not listed in root requirements. |
| PySR | PARTIALLY IMPLEMENTED | `physics/symbolic_discovery.py`, `satellite/thermal/discover_thermal_equations.py` | Uses PySR if available, falls back in physics. PySR/Julia not listed in root requirements. |
| Symbolic regression fallback | FULLY IMPLEMENTED | `physics/core/neurosymbolic/symbolic.py` | Deterministic Lasso library over constant, polynomial, cross, and trig terms. |
| Knowledge graph | PARTIALLY IMPLEMENTED | `physics/knowledge_graph.py`, `physics/migrate_to_graph.py` | Neo4j wrapper has schema, node, relationship, and report methods, but gracefully bypasses when Neo4j is unavailable. |
| SQLite scientific memory | PARTIALLY IMPLEMENTED | `physics/core/autonomous/autonomous_scientist.py`, `physics/experiment_versioning.py`, `physics/scientific_kb.db` | Local fallback storage exists. Coverage depends on which pipeline path is used. |
| Autonomous scientist | PARTIALLY IMPLEMENTED | `physics/core/autonomous/autonomous_scientist.py`, `hypothesis_engine.py`, `llm_reasoner.py`, `sandbox_executor.py`, `research_reporter.py` | Orchestrates hypothesis generation, sandbox execution, interpretation, and memory. Requires LLM API key for full operation. |
| LLM sandbox execution | PARTIALLY IMPLEMENTED | `physics/core/autonomous/sandbox_executor.py` | AST safety scan, Docker optional, local subprocess fallback. Generated code execution is constrained but not a full security boundary. |
| Scientific guardrails | FULLY IMPLEMENTED | `physics/scientific_guard.py` | Sanitizes overclaiming phrases and validates hypothesis structure. |
| Representation audits | PARTIALLY IMPLEMENTED | `physics/deep_representation_audit.py`, `physics/compute_cka_ecg.py`, `physics/core/validation/*` | Several audits and artifacts exist; some depend on datasets, optional libraries, or generated reports. |
| Uncertainty quantification | FULLY IMPLEMENTED in satellite, PARTIAL in physics | `satellite/thermal/uncertainty_engine.py`, `satellite/uq/full_orbit_montecarlo.py`, `physics/uncertainty_quantification.py` | Satellite UQ is more developed; physics UQ is present but less central. |
| ECG datasets and classifiers | PARTIALLY IMPLEMENTED | `physics/data/mitdb/*`, `physics/data/ucr/*`, `physics/train_ecg_models.py`, `physics/train_all_architectures_ptbxl.py` | Data and scripts exist. PTB-XL paths/models are present, but not fully verified in this audit. |
| Quantum gravity toy audits | PARTIALLY IMPLEMENTED | `physics/run_qg_pipeline.py`, `physics/qg_geometric_audit.py`, `physics/causal_layered_graph.py`, `physics/spin_network_model.py`, `physics/bec_analog_model.py` | Toy model generation and audits exist. Claims must remain model-specific. |
| Formal math / theorem proving | PLANNED | `mathematics/README.md`, `mathematics/symbolic/README.md` | Placeholder only. |
| Quantum circuits / VQE | PLANNED | `quantum/README.md`, `quantum/circuits/README.md` | Placeholder only. |

## Spacecraft Digital Twin Capabilities

| Capability | Status | Evidence | Notes |
|---|---|---|---|
| 1-node orbital thermal simulator | FULLY IMPLEMENTED | `satellite/thermal/orbital_thermal_simulator.py`, `satellite/models/telemetry.csv` | Verified command completed locally. |
| 6-node coupled thermal network | FULLY IMPLEMENTED | `satellite/thermal/multi_node_thermal_network.py`, `satellite/tests/test_satellite_twin.py` | Uses `scipy.integrate.solve_ivp`, conductance matrix, radiation, hotspots, gradients. Tests pass. |
| Orbital environment model | FULLY IMPLEMENTED | `satellite/thermal/orbital_environment.py` | Computes circular LEO parameters, solar eclipse, albedo, Earth IR, and coupled simulation. |
| CAD thermal importer | PARTIALLY IMPLEMENTED | `satellite/thermal/cad_thermal_importer.py`, `satellite/cad/cubesat_cube.stl` | STL/voxel workflow and reports exist; CAD scope is simplified. |
| Surrogate models | FULLY IMPLEMENTED | `satellite/thermal/train_surrogate_models.py`, `satellite/models/surrogate_rf.pkl`, `surrogate_xgb.pkl`, `surrogate_mlp.pth` | RF/XGBoost/MLP artifacts and metrics exist. XGBoost is an optional dependency. |
| Thermal PINN training | FULLY IMPLEMENTED | `satellite/thermal/train_thermal_pinn.py`, `satellite/models/pinn_thermal.pth` | Uses shared PINN core and saves trained model artifact. |
| Thermal Neural ODE training | FULLY IMPLEMENTED | `satellite/thermal/train_thermal_neural_ode.py`, `satellite/models/neural_ode_thermal.pth` | Uses shared Neural ODE core and `torchdiffeq`. |
| Geometry/topology optimization | FULLY IMPLEMENTED | `satellite/thermal/geometry_topology_optimizer.py`, `geometry_pareto_front.csv`, `geometry_optimal_design.json` | Random/active search and Pareto outputs exist. |
| Autonomous thermal discovery | PARTIALLY IMPLEMENTED | `satellite/thermal/autonomous_thermal_discovery.py`, `satellite/patents/thermal_equations_candidates.md` | Proposes and tests hypotheses with symbolic fitting; should be described as a local discovery loop, not patent validation. |
| Hardware-in-the-loop | PARTIALLY IMPLEMENTED | `satellite/thermal/hardware_in_the_loop.py`, `satellite/thermal/base_hil.py`, `satellite/thermal/hil_real_hardware.py` | Synthetic HIL is implemented. Real hardware path is conditional on serial/DAQ availability. |
| TVAC integration | STUB/PARTIAL | `satellite/thermal/tvac_integration.py`, `satellite/thermal/tvac_correlation_report.md` | Report states demonstration-only placeholder requiring hardware DAQ. |
| FEM correlation benchmark | PARTIALLY IMPLEMENTED | `satellite/thermal/fem_correlation.py`, `reproduce/reproduce_t18.py` | Implements reference/emulated FEM correlation; does not integrate a commercial FEM solver. |
| Closed-loop thermal control | FULLY IMPLEMENTED prototype | `satellite/thermal/closed_loop_thermal_control.py` | Predictive controller, burnout probability, and action decisions exist. |
| Constellation modeling | FULLY IMPLEMENTED prototype | `satellite/thermal/constellation_modeler.py`, `satellite/constellation/cooperative_ai.py` | Parallel thermal jobs and cooperative constellation simulation scripts exist. |
| Material aging | FULLY IMPLEMENTED prototype | `satellite/thermal/material_aging.py`, `satellite/thermal/material_library.py` | Degradation and material comparison scripts exist. |
| ECSS compliance reporting | PARTIALLY IMPLEMENTED | `satellite/thermal/ecss_compliance.py` | Computes margins and report output; PDF has fallback placeholder behavior if ReportLab is missing. |
| HPC acceleration | PARTIALLY IMPLEMENTED | `satellite/thermal/hpc_acceleration.py` | Uses multiprocessing, optional Ray/GPU, and surrogate timing. Some paths are benchmark stubs. |
| Flight runtime / ONNX / C export | PARTIALLY IMPLEMENTED | `satellite/flight/export_to_onnx.py`, `satellite/flight/flight_runtime.py`, `satellite/flight/surrogate_mlp_inference.c` | Export/runtime artifacts exist; no certification evidence. |
| FastAPI thermal API | FULLY IMPLEMENTED prototype | `satellite/api/thermal_api.py` | Auth, usage, predict, simulate, models, optimal, equations, reports, health, metrics, status, version endpoints. |
| SaaS HTTP server | PARTIALLY IMPLEMENTED | `satellite/cloud/deploy_saas.py` | Lightweight server with predict/optimize and commercial asset generation; Stripe/billing is a stub. |
| Production deployment orchestration | STUB | `satellite/cloud/deploy_production.py` | Described as command stub/logger. |

## Dashboard And Tooling

| Capability | Status | Evidence | Notes |
|---|---|---|---|
| Next.js dashboard | FULLY IMPLEMENTED | `dashboard/package.json`, `dashboard/src/app/*`, `dashboard/src/components/*` | `npm run build` passed. |
| Dashboard satellite workflow | FULLY IMPLEMENTED frontend, PARTIAL backend dependency | `dashboard/src/app/[lang]/satellite/page.tsx`, `satellite/api/thermal_api.py` | UI polls `localhost:8000` and simulates offline state. |
| Internationalization | FULLY IMPLEMENTED | `dashboard/src/lib/i18n/dictionaries.ts`, `[lang]` routes | English and Spanish routes build. |
| CI | PARTIALLY IMPLEMENTED | `.github/workflows/pytest.yml`, `.github/workflows/dashboard_auto_sync.yml` | Python matrix and dashboard build workflow exist. Requirements gaps may affect CI if optional tests expand. |
| Docker | PARTIALLY IMPLEMENTED | `Dockerfile.ci`, `satellite/Dockerfile`, `satellite/cloud/docker-compose.yml`, `autonomous-spacecraft-thermal-os/docker-compose.yml` | Multiple Docker assets exist; not fully verified in this audit. |

## Verification Performed

| Check | Result |
|---|---|
| `python -m pytest physics/tests/neurosymbolic -q` | 3 passed |
| `python -m pytest satellite/tests -q` | 5 passed, 2 syntax warnings |
| `npm run build` in `dashboard/` | Passed, with Recharts width/height warnings |
| `python -m physics.run_pipeline --system harmonic --config physics/config.yaml` | Passed |
| `python satellite/thermal/orbital_thermal_simulator.py --power 10 --area 0.1 --emissivity 0.8` | Passed |
