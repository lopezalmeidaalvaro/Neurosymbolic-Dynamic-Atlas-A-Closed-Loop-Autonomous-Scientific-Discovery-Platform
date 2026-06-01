# Spacecraft Thermal OS (AST-OS) - Mock & Synthetic Pattern Detection Report

This report presents the findings of a hostile static analysis pattern scan looking for hardcoded seeds, mocks, dummy endpoints, and placeholders.

## 1. Scanner Results Summary

| Codebase File Asset | Primary Classification | Found Mock Patterns | First Match Location |
| --- | :---: | :---: | --- |
| **[cfs_integration_report.md](cfs_integration_report.md)** | MOCKED | 2 | Line 13 (mock): 3. **Hardware-in-the-Loop Validation**: **Pending**. Standard desktop mock inter |
| **[README.md](README.md)** | SYNTHETIC | 2 | Line 11 (synthetic): > AST-OS is designed as a software-in-the-loop laboratory prototyping ecosystem. |
| **[run_hostile_audit.py](run_hostile_audit.py)** | MOCKED | 57 | Line 4 (mock): # Description: Automatically audits files, checks executability, checks mocks, |
| **[astos_cfs_app/astos_app.c](astos_cfs_app/astos_app.c)** | MOCKED | 14 | Line 19 (simulated): /* Running simulated execution status */ |
| **[astos_cfs_app/astos_app.h](astos_cfs_app/astos_app.h)** | MOCKED | 2 | Line 17 (mock): /* cFS API / Service mock wrappers if building standalone, otherwise standard cF |
| **[astos_cfs_app/fault_injection.py](astos_cfs_app/fault_injection.py)** | SYNTHETIC | 8 | Line 98 (simulated): # 2. Encode Golden copy into static FLASH simulated memory |
| **[astos_cfs_app/fault_injection_report.md](astos_cfs_app/fault_injection_report.md)** | SYNTHETIC | 3 | Line 3 (simulated): This report presents the metrics of the **AST-OS cFS Hardened Runtime** under a  |
| **[astos_cfs_app/integration_tests/README.md](astos_cfs_app/integration_tests/README.md)** | SYNTHETIC | 1 | Line 32 (simulated): * **`test_app_survives_1000_cycles`**: Runs $1,000$ simulated inference sweeps t |
| **[astos_cfs_app/integration_tests/test_cfs_integration.py](astos_cfs_app/integration_tests/test_cfs_integration.py)** | SYNTHETIC | 1 | Line 51 (simulated): # Packet received: 0.1s simulated delay |
| **[astos_cfs_app/unit_tests/run_tests.py](astos_cfs_app/unit_tests/run_tests.py)** | SYNTHETIC | 3 | Line 61 (simulated): # 2. Simulated Onboard App State |
| **[benchmarks/run_cad_benchmark.py](benchmarks/run_cad_benchmark.py)** | SYNTHETIC | 8 | Line 24 (random.seed): np.random.seed(42) |
| **[benchmarks/run_pinn_benchmark.py](benchmarks/run_pinn_benchmark.py)** | SYNTHETIC | 3 | Line 20 (random.seed): np.random.seed(42) |
| **[benchmarks/run_tvac_benchmark.py](benchmarks/run_tvac_benchmark.py)** | SYNTHETIC | 2 | Line 17 (random.seed): np.random.seed(42) |
| **[docs/SOFTWARE_DEVELOPMENT_PLAN.md](docs/SOFTWARE_DEVELOPMENT_PLAN.md)** | SYNTHETIC | 1 | Line 57 (simulated): * **Integration Testing**: CCSDS Software Bus packet loop validations and simula |
| **[docs/SOFTWARE_VERIFICATION_PLAN.md](docs/SOFTWARE_VERIFICATION_PLAN.md)** | SYNTHETIC | 2 | Line 23 (simulated): * **Scope**: Evaluates cFS application registrations, Software Bus subscriptions |
| **[openmdao_integration/components.py](openmdao_integration/components.py)** | MOCKED | 3 | Line 11 (mock): # Safe mock implementation if openmdao is not installed in the execution sandbox |
| **[physics/core/neurosymbolic/neural_ode.py](physics/core/neurosymbolic/neural_ode.py)** | MOCKED | 1 | Line 15 (placeholder): self.params = None  # Placeholder for parameter tensors (e.g. [power, area, emis |
| **[real_telemetry_pipeline/pipeline.py](real_telemetry_pipeline/pipeline.py)** | SYNTHETIC | 7 | Line 23 (random.seed): np.random.seed(42) |
| **[reports/aging_report.md](reports/aging_report.md)** | SYNTHETIC | 1 | Line 20 (simulated): âœ… **SAFE:** Nodal temperatures remain within legal safety envelopes for the si |
| **[reports/closed_loop_report.md](reports/closed_loop_report.md)** | SYNTHETIC | 1 | Line 20 (simulated): We simulated the controller under nominal, heavy processing load, and seasonal s |
| **[reports/constellation_report.md](reports/constellation_report.md)** | SYNTHETIC | 1 | Line 9 (simulated): We simulated a symmetric cubesat constellation: |
| **[reports/experiment_report.md](reports/experiment_report.md)** | SYNTHETIC | 1 | Line 6 (simulated): > **SIMULATED EXPERIMENT â€” Hardware required for validation** |
| **[reports/tvac_correlation_report.md](reports/tvac_correlation_report.md)** | MOCKED | 1 | Line 55 (placeholder): *DEMONSTRATION ONLY â€” Certified placeholder. Requires hardware DAQ connection. |
| **[reproduce/reproduce_t18.py](reproduce/reproduce_t18.py)** | SYNTHETIC | 2 | Line 14 (random.seed): np.random.seed(42) |
| **[satellite/ARCHITECTURE.md](satellite/ARCHITECTURE.md)** | SYNTHETIC | 1 | Line 80 (synthetic): Runs a real-time calibration loop connecting physical thermal sensors (or a synt |
| **[satellite/README.md](satellite/README.md)** | SYNTHETIC | 2 | Line 175 (synthetic): *(If run on standard workstations without sensors, the script falls back to a hi |
| **[satellite/WHITEPAPER.md](satellite/WHITEPAPER.md)** | SYNTHETIC | 1 | Line 69 (simulated): By training the neural network $\text{NN}_{\theta}$ on simulated orbits, the sol |
| **[satellite/adcs/adcs_thermal_coupling.py](satellite/adcs/adcs_thermal_coupling.py)** | SYNTHETIC | 2 | Line 21 (random.seed): np.random.seed(42) |
| **[satellite/api/thermal_api.py](satellite/api/thermal_api.py)** | SYNTHETIC | 1 | Line 510 (simulated): "optimization_algorithm": "Simulated Annealing (Global convergence)", |
| **[satellite/autonomy/evolving_twin_report.md](satellite/autonomy/evolving_twin_report.md)** | SYNTHETIC | 1 | Line 7 (simulated): A 30-day orbit degradation timeline was simulated under Semilla 42: |
| **[satellite/autonomy/fault_recovery_ai.py](satellite/autonomy/fault_recovery_ai.py)** | SYNTHETIC | 2 | Line 17 (random.seed): random.seed(seed) |
| **[satellite/autonomy/fault_recovery_report.md](satellite/autonomy/fault_recovery_report.md)** | SYNTHETIC | 1 | Line 7 (simulated): An intensive 7-day LEO orbit campaign was simulated. **10 separate hardware faul |
| **[satellite/autonomy/mission_planner.py](satellite/autonomy/mission_planner.py)** | SYNTHETIC | 7 | Line 7 (simulated): Uses Simulated Annealing to maximize priority-weighted mission success. |
| **[satellite/autonomy/planner_report.md](satellite/autonomy/planner_report.md)** | SYNTHETIC | 2 | Line 7 (simulated): A 5400-second LEO orbital timeline was optimized using **Simulated Annealing** u |
| **[satellite/autonomy/rl_thermal_control.py](satellite/autonomy/rl_thermal_control.py)** | SYNTHETIC | 3 | Line 25 (random.seed): random.seed(seed) |
| **[satellite/autonomy/self_evolving_twin.py](satellite/autonomy/self_evolving_twin.py)** | SYNTHETIC | 3 | Line 46 (random.seed): random.seed(seed) |
| **[satellite/autonomy/self_healing_twin.py](satellite/autonomy/self_healing_twin.py)** | SYNTHETIC | 3 | Line 22 (random.seed): np.random.seed(42) |
| **[satellite/cloud/deploy_production.py](satellite/cloud/deploy_production.py)** | SYNTHETIC | 1 | Line 19 (simulated): print("[!] Docker CLI not detected locally. Using simulated build sandbox.") |
| **[satellite/cloud/deploy_saas.py](satellite/cloud/deploy_saas.py)** | MOCKED | 1 | Line 25 (mock): # Business database (In-memory mock database) |
| **[satellite/comms/model_update.py](satellite/comms/model_update.py)** | MOCKED | 4 | Line 18 (mock): # Mock class to permit type annotations |
| **[satellite/comms/state_sync.py](satellite/comms/state_sync.py)** | SYNTHETIC | 1 | Line 92 (np.random): onboard_ekf[idx] = eps + np.random.normal(0, 0.005) |
| **[satellite/constellation/cooperative_ai.py](satellite/constellation/cooperative_ai.py)** | SYNTHETIC | 4 | Line 18 (random.seed): np.random.seed(42) |
| **[satellite/constellation/swarm_intelligence.py](satellite/constellation/swarm_intelligence.py)** | SYNTHETIC | 2 | Line 61 (random.seed): random.seed(seed) |
| **[satellite/constellation/swarm_report.md](satellite/constellation/swarm_report.md)** | SYNTHETIC | 1 | Line 7 (simulated): A 10-satellite LEO constellation was simulated over a **30-day mission timeline* |
| **[satellite/demo/run_demo.py](satellite/demo/run_demo.py)** | MOCKED | 3 | Line 4 (simulated): Executes a premium, cinematic 12-step simulated timeline of orbital telemetry, |
| **[satellite/emc/emc_analysis.py](satellite/emc/emc_analysis.py)** | SYNTHETIC | 2 | Line 19 (random.seed): np.random.seed(42) |
| **[satellite/estimation/robust_los_ekf.py](satellite/estimation/robust_los_ekf.py)** | MOCKED | 4 | Line 21 (random.seed): np.random.seed(42) |
| **[satellite/flight/export_to_onnx.py](satellite/flight/export_to_onnx.py)** | MOCKED | 9 | Line 180 (dummy): dummy_mlp_input = torch.randn(1, 3) |
| **[satellite/flight/flight_runtime.py](satellite/flight/flight_runtime.py)** | SYNTHETIC | 3 | Line 17 (random.seed): np.random.seed(42) |
| **[satellite/flight/radiation_hardened_ai.py](satellite/flight/radiation_hardened_ai.py)** | SYNTHETIC | 3 | Line 18 (simulated): # Simulated floating point weights for the CPU thermal node |
| **[satellite/flight/radiation_hardened_report.md](satellite/flight/radiation_hardened_report.md)** | SYNTHETIC | 2 | Line 7 (simulated): We simulated a heavy ion strike injecting a bit-flip into the model weight array |
| **[satellite/flight/rtos_runtime_sim.py](satellite/flight/rtos_runtime_sim.py)** | MOCKED | 6 | Line 20 (random.seed): np.random.seed(42) |
| **[satellite/flight/software_assurance.py](satellite/flight/software_assurance.py)** | MOCKED | 1 | Line 210 (mock): # Check if the C file exists. If not, generate a mock or run the ONNX exporter t |
| **[satellite/ops/mission_operations.py](satellite/ops/mission_operations.py)** | SYNTHETIC | 3 | Line 22 (random.seed): np.random.seed(42) |
| **[satellite/platform/thermal_os.py](satellite/platform/thermal_os.py)** | SYNTHETIC | 4 | Line 20 (random.seed): np.random.seed(42) |
| **[satellite/qualification/gap_analysis.md](satellite/qualification/gap_analysis.md)** | MOCKED | 1 | Line 21 (mock): > 2. **Sensores de Temperatura de Vuelo**: Sustituir los mocks del termistor de  |
| **[satellite/qualification/hazard_analysis.md](satellite/qualification/hazard_analysis.md)** | SYNTHETIC | 1 | Line 15 (simulated): - Simulated Annealing active thermal-aware scheduling prevents back-to-back high |
| **[satellite/qualification/qualification_package.py](satellite/qualification/qualification_package.py)** | SYNTHETIC | 1 | Line 77 (simulated): - Simulated Annealing active thermal-aware scheduling prevents back-to-back high |
| **[satellite/qualification/trl6_package.py](satellite/qualification/trl6_package.py)** | MOCKED | 1 | Line 121 (mock): f.write("> 2. **Sensores de Temperatura de Vuelo**: Sustituir los mocks del term |
| **[satellite/radiation/radiation_qualification.py](satellite/radiation/radiation_qualification.py)** | SYNTHETIC | 1 | Line 236 (simulated): f.write("Simulated heavy ion flux under extreme solar weather (1.0e5 particles/c |
| **[satellite/radiation/radiation_qualification_report.md](satellite/radiation/radiation_qualification_report.md)** | SYNTHETIC | 1 | Line 16 (simulated): Simulated heavy ion flux under extreme solar weather (1.0e5 particles/cm²/day) o |
| **[satellite/radiation/seu_analysis.py](satellite/radiation/seu_analysis.py)** | SYNTHETIC | 10 | Line 26 (random.seed): np.random.seed(42) |
| **[satellite/structural/structural_analysis_report.md](satellite/structural/structural_analysis_report.md)** | SYNTHETIC | 1 | Line 7 (simulated): The spacecraft structure was subjected to a simulated launch load profile from * |
| **[satellite/structural/vibration_thermal_coupling.py](satellite/structural/vibration_thermal_coupling.py)** | MOCKED | 2 | Line 125 (mock): # Mock vibration stress calculated via three-sigma load factors |
| **[satellite/tests/cad_benchmarks.py](satellite/tests/cad_benchmarks.py)** | SYNTHETIC | 9 | Line 30 (random.seed): np.random.seed(42) |
| **[satellite/tests/destructive_testing_suite.py](satellite/tests/destructive_testing_suite.py)** | SYNTHETIC | 3 | Line 324 (random.seed): - **Core ML Modules** (`train_thermal_pinn.py`, `self_evolving_twin.py`, `rl_the |
| **[satellite/tests/metric_rebuild_suite.py](satellite/tests/metric_rebuild_suite.py)** | MOCKED | 10 | Line 168 (fake): # 1. fake_claims.md |
| **[satellite/tests/test_satellite_twin.py](satellite/tests/test_satellite_twin.py)** | MOCKED | 4 | Line 27 (random.seed): np.random.seed(42) |
| **[satellite/thermal/aging_report.md](satellite/thermal/aging_report.md)** | SYNTHETIC | 1 | Line 20 (simulated): âœ… **SAFE:** Nodal temperatures remain within legal safety envelopes for the si |
| **[satellite/thermal/autonomous_thermal_discovery.py](satellite/thermal/autonomous_thermal_discovery.py)** | MOCKED | 7 | Line 30 (random.seed): np.random.seed(42) |
| **[satellite/thermal/base_hil.py](satellite/thermal/base_hil.py)** | SYNTHETIC | 3 | Line 13 (random.seed): np.random.seed(42) |
| **[satellite/thermal/cad_thermal_importer.py](satellite/thermal/cad_thermal_importer.py)** | MOCKED | 6 | Line 18 (random.seed): np.random.seed(42) |
| **[satellite/thermal/closed_loop_report.md](satellite/thermal/closed_loop_report.md)** | SYNTHETIC | 1 | Line 20 (simulated): We simulated the controller under nominal, heavy processing load, and seasonal s |
| **[satellite/thermal/closed_loop_thermal_control.py](satellite/thermal/closed_loop_thermal_control.py)** | SYNTHETIC | 3 | Line 27 (random.seed): np.random.seed(42) |
| **[satellite/thermal/constellation_modeler.py](satellite/thermal/constellation_modeler.py)** | SYNTHETIC | 7 | Line 30 (random.seed): np.random.seed(42) |
| **[satellite/thermal/constellation_report.md](satellite/thermal/constellation_report.md)** | SYNTHETIC | 1 | Line 9 (simulated): We simulated a symmetric cubesat constellation: |
| **[satellite/thermal/discover_thermal_equations.py](satellite/thermal/discover_thermal_equations.py)** | SYNTHETIC | 2 | Line 24 (random.seed): np.random.seed(42) |
| **[satellite/thermal/ecss_compliance.py](satellite/thermal/ecss_compliance.py)** | MOCKED | 4 | Line 24 (random.seed): np.random.seed(42) |
| **[satellite/thermal/experimental_validation.py](satellite/thermal/experimental_validation.py)** | MOCKED | 18 | Line 16 (random.seed): np.random.seed(42) |
| **[satellite/thermal/experiment_report.md](satellite/thermal/experiment_report.md)** | SYNTHETIC | 1 | Line 6 (simulated): > **SIMULATED EXPERIMENT â€” Hardware required for validation** |
| **[satellite/thermal/fdir_engine.py](satellite/thermal/fdir_engine.py)** | SYNTHETIC | 5 | Line 18 (random.seed): np.random.seed(42) |
| **[satellite/thermal/fem_correlation.py](satellite/thermal/fem_correlation.py)** | SYNTHETIC | 4 | Line 18 (random.seed): np.random.seed(42) |
| **[satellite/thermal/generate_thermal_dataset.py](satellite/thermal/generate_thermal_dataset.py)** | SYNTHETIC | 6 | Line 3 (simulated): Generate Thermal Dataset - Samples configuration parameters and generates simula |
| **[satellite/thermal/geometry_topology_optimizer.py](satellite/thermal/geometry_topology_optimizer.py)** | SYNTHETIC | 4 | Line 17 (random.seed): np.random.seed(42) |
| **[satellite/thermal/hardware_in_the_loop.py](satellite/thermal/hardware_in_the_loop.py)** | SYNTHETIC | 2 | Line 16 (random.seed): np.random.seed(42) |
| **[satellite/thermal/hil_real_hardware.py](satellite/thermal/hil_real_hardware.py)** | SYNTHETIC | 6 | Line 17 (random.seed): np.random.seed(42) |
| **[satellite/thermal/hpc_acceleration.py](satellite/thermal/hpc_acceleration.py)** | MOCKED | 9 | Line 25 (random.seed): np.random.seed(42) |
| **[satellite/thermal/ingest_orbital_telemetry.py](satellite/thermal/ingest_orbital_telemetry.py)** | SYNTHETIC | 8 | Line 28 (random.seed): np.random.seed(42) |
| **[satellite/thermal/ingest_real_thermal_data.py](satellite/thermal/ingest_real_thermal_data.py)** | SYNTHETIC | 3 | Line 14 (random.seed): np.random.seed(42) |
| **[satellite/thermal/material_aging.py](satellite/thermal/material_aging.py)** | SYNTHETIC | 3 | Line 32 (random.seed): np.random.seed(42) |
| **[satellite/thermal/multi_node_thermal_network.py](satellite/thermal/multi_node_thermal_network.py)** | SYNTHETIC | 2 | Line 14 (random.seed): np.random.seed(42) |
| **[satellite/thermal/observability_analysis.py](satellite/thermal/observability_analysis.py)** | SYNTHETIC | 2 | Line 23 (random.seed): np.random.seed(42) |
| **[satellite/thermal/optimize_radiator_design.py](satellite/thermal/optimize_radiator_design.py)** | SYNTHETIC | 9 | Line 15 (random.seed): np.random.seed(42) |
| **[satellite/thermal/orbital_thermal_simulator.py](satellite/thermal/orbital_thermal_simulator.py)** | SYNTHETIC | 1 | Line 132 (simulated): parser.add_argument("--orbits", type=int, default=3, help="Number of simulated o |
| **[satellite/thermal/scientific_benchmark.py](satellite/thermal/scientific_benchmark.py)** | SYNTHETIC | 1 | Line 81 (np.random): fem_temps.append(twin_val + bias + np.random.normal(0, 0.05)) |
| **[satellite/thermal/stiff_solver_benchmark.py](satellite/thermal/stiff_solver_benchmark.py)** | SYNTHETIC | 2 | Line 24 (random.seed): np.random.seed(42) |
| **[satellite/thermal/thermal_server_model.py](satellite/thermal/thermal_server_model.py)** | SYNTHETIC | 1 | Line 98 (np.random): noise = np.random.normal(0.0, 0.01 * np.abs(T_media_C), size=(grid_size, grid_si |
| **[satellite/thermal/train_surrogate_models.py](satellite/thermal/train_surrogate_models.py)** | SYNTHETIC | 2 | Line 33 (random.seed): np.random.seed(42) |
| **[satellite/thermal/train_thermal_emulator.py](satellite/thermal/train_thermal_emulator.py)** | MOCKED | 4 | Line 44 (synthetic): print(f"[*] Generating {size} synthetic orbital thermal profiles...") |
| **[satellite/thermal/train_thermal_neural_ode.py](satellite/thermal/train_thermal_neural_ode.py)** | SYNTHETIC | 2 | Line 29 (random.seed): np.random.seed(42) |
| **[satellite/thermal/train_thermal_pinn.py](satellite/thermal/train_thermal_pinn.py)** | SYNTHETIC | 7 | Line 28 (random.seed): np.random.seed(42) |
| **[satellite/thermal/transient_power_profiles.py](satellite/thermal/transient_power_profiles.py)** | SYNTHETIC | 6 | Line 23 (random.seed): np.random.seed(42) |
| **[satellite/thermal/tvac_correlation_report.md](satellite/thermal/tvac_correlation_report.md)** | MOCKED | 1 | Line 55 (placeholder): *DEMONSTRATION ONLY â€” Certified placeholder. Requires hardware DAQ connection. |
| **[satellite/thermal/tvac_integration.py](satellite/thermal/tvac_integration.py)** | MOCKED | 4 | Line 24 (random.seed): np.random.seed(42) |
| **[satellite/thermal/uncertainty_engine.py](satellite/thermal/uncertainty_engine.py)** | SYNTHETIC | 7 | Line 14 (random.seed): np.random.seed(42) |
| **[satellite/thermal/validate_thermal_model.py](satellite/thermal/validate_thermal_model.py)** | SYNTHETIC | 8 | Line 13 (random.seed): np.random.seed(42) |
| **[satellite/trl/TRL_ASSESSMENT.md](satellite/trl/TRL_ASSESSMENT.md)** | SYNTHETIC | 1 | Line 36 (simulated): - **HIL Emulation**: Real-time HIL calibration using a simulated/ESP32 physical  |
| **[satellite/tvac/tvac_automation.py](satellite/tvac/tvac_automation.py)** | MOCKED | 4 | Line 83 (mock): # Inter-node conduction mock (simple lumped thermal mass heat-rates) |
| **[satellite/tvac/tvac_qualification_report.md](satellite/tvac/tvac_qualification_report.md)** | SYNTHETIC | 1 | Line 4 (simulated): > Thermal Vacuum Chamber (TVAC) qualification confirms payload performance under |
| **[satellite/uq/full_orbit_montecarlo.py](satellite/uq/full_orbit_montecarlo.py)** | SYNTHETIC | 13 | Line 23 (random.seed): np.random.seed(42) |
| **[satellite/validation/fem_correlation_layer.py](satellite/validation/fem_correlation_layer.py)** | MOCKED | 14 | Line 286 (mock): val_es = esatan_cond_map.get((na, nb), val_int * 0.98) # close mockup |
| **[satellite/validation/flight_heritage_compare.py](satellite/validation/flight_heritage_compare.py)** | SYNTHETIC | 5 | Line 21 (random.seed): np.random.seed(42) |
| **[satellite/validation/telemetry_assimilation.py](satellite/validation/telemetry_assimilation.py)** | MOCKED | 8 | Line 32 (mock): Falls back to highly-realistic local mocks if offline or rate-limited. |
| **[tests/test_components.py](tests/test_components.py)** | SYNTHETIC | 1 | Line 39 (simulated): Asserts that the Simulated Annealing mission planner optimizes timelines success |
| **[verification/benchmark_status.md](verification/benchmark_status.md)** | SYNTHETIC | 2 | Line 16 (synthetic): | **`telemetry_assimilation.py`** | **SYNTHETIC** | Medium | No | No | Uses hex  |
| **[verification/calibration_requirements.md](verification/calibration_requirements.md)** | SYNTHETIC | 1 | Line 59 (hardcoded): Applying these calibrated configurations will match the real transient profiles  |
| **[verification/fake_claims.md](verification/fake_claims.md)** | MOCKED | 5 | Line 3 (hardcoded): This document exposes discrepancies, modeling margins, and hardcoded technical c |
| **[verification/index.md](verification/index.md)** | MOCKED | 5 | Line 10 (synthetic): > This portal serves as a scientifically honest, fully audited repository detail |
| **[verification/known_limitations.md](verification/known_limitations.md)** | MOCKED | 4 | Line 3 (mock): This document explicitly logs the known limitations, mocked routes, and uncalibr |
| **[verification/reproducibility.md](verification/reproducibility.md)** | SYNTHETIC | 2 | Line 12 (random.seed): - **NumPy**: `>=1.26.0` (Consistent random seed tracking via `np.random.seed(42) |
| **[verification/reproducibility_scorecard.md](verification/reproducibility_scorecard.md)** | MOCKED | 1 | Line 31 (fake): While the **autonomy, EKF state trackers, and neural surrogates are highly rigor |
| **[verification/synthetic_vs_real.md](verification/synthetic_vs_real.md)** | SYNTHETIC | 3 | Line 35 (synthetic): - **Classification**: **SYNTHETIC EMULATION** |
| **[verification/trl_assessment.md](verification/trl_assessment.md)** | MOCKED | 3 | Line 14 (synthetic): - **Why it is not TRL 5 (Validation in relevant environment)**: The system curre |
| **[verification/verified_claims_only.md](verification/verified_claims_only.md)** | SYNTHETIC | 1 | Line 28 (simulated): - **Simulated Annealing Mission Planner**: |

## 2. Hostile V&V Observations
1. **FastAPI Billing Integrations**: **MOCKED**. The `/stripe/webhook` route in the existing FastAPI is a dummy endpoint printed to logs. It does not hit Stripe API. This is upgraded to production-ready SaaS integration in Sprint B.
2. **Physical Telemetry Feeds**: **SYNTHETIC**. The ISS ATCS dataset (`nasa_atcs_telemetry.csv`) is generated procedurally by `generate_curated_nasa_telemetry` inside `pipeline.py`. It uses sinusoidal baselines and injected Gaussian noise, styled beautifully to mimic a real mission, but is technically synthetic.
3. **Nelder-Mead & PINN Solvers**: **SYNTHETIC**. The physical TVAC optimization steps and neural network residuals are executed inside clean, self-contained mathematical models, verified for precision convergence under static random seeds (42).
