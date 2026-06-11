# Satellite Rename Plan

Generated: 2026-06-06

## Objective

Prepare a non-destructive migration from `satellite/` to `satellite/` while preserving all functionality.

## Current State

The root folder is named `satellite/`, but internal imports frequently use `satellite.*`. This means the code already expects a package named `satellite` in many places, but the filesystem root does not match the target public name.

## Folder Rename Strategy

1. Create a migration branch.
2. Run baseline tests from `satellite/` and record failures.
3. Use `git mv satellite satellite` only after import strategy is ready.
4. Add a temporary compatibility package or import shim if existing scripts still reference `satellite`.
5. Update README and documentation links after tests pass.
6. Keep old path references documented in a migration manifest.

## Import Rewrite Strategy

- Keep internal Python package imports as `satellite.*` where they already work.
- Replace filesystem documentation references from `satellite/` to `satellite/` after the physical rename.
- Audit `sys.path` or working-directory assumptions in satellite scripts.
- Replace `satellite -> physics` imports with optional plugin adapters before the rename if possible.

## Import Breakpoints Observed

| File | Target | Import |
| --- | --- | --- |
| satellite/plugin.py | core | core.domains.domain_registry |
| satellite/plugin.py | core | core.orchestration.scientific_container |
| satellite/satellite/run_warp_simulation.py | satellite | satellite.warp.warp_thermal_injection |
| satellite/satellite/run_warp_simulation.py | satellite | satellite.thermal.fdir_engine |
| satellite/tests/test_run_thermal_pipeline.py | satellite | satellite.run_thermal_pipeline |
| satellite/tests/test_run_thermal_pipeline.py | satellite | satellite.run_thermal_pipeline |
| satellite/physics/core/neurosymbolic/pinn.py | physics | physics.pinn_module |
| satellite/physics/core/neurosymbolic/__init__.py | physics | physics.core.neurosymbolic.pinn |
| satellite/physics/core/neurosymbolic/__init__.py | physics | physics.core.neurosymbolic.neural_ode |
| satellite/physics/core/neurosymbolic/__init__.py | physics | physics.core.neurosymbolic.symbolic |
| satellite/satellite/adcs/adcs_thermal_coupling.py | satellite | satellite.thermal.multi_node_thermal_network |
| satellite/satellite/autonomy/self_healing_twin.py | satellite | satellite.thermal.multi_node_thermal_network |
| satellite/satellite/estimation/nominal_ekf_validation.py | satellite | satellite.thermal.multi_node_thermal_network |
| satellite/satellite/estimation/nominal_ekf_validation.py | satellite | satellite.estimation.robust_los_ekf |
| satellite/satellite/estimation/robust_los_ekf.py | satellite | satellite.thermal.multi_node_thermal_network |
| satellite/satellite/flight/export_to_onnx.py | physics | physics.core.neurosymbolic.pinn |
| satellite/satellite/flight/export_to_onnx.py | satellite | satellite.thermal.train_surrogate_models |
| satellite/satellite/ops/mission_operations.py | satellite | satellite.thermal.multi_node_thermal_network |
| satellite/satellite/platform/thermal_os.py | satellite | satellite.thermal.multi_node_thermal_network |
| satellite/satellite/radiation/seu_analysis.py | satellite | satellite.thermal.train_surrogate_models |
| satellite/satellite/thermal/cavity_radiation_model.py | satellite | satellite.thermal.multi_node_thermal_network |
| satellite/satellite/thermal/discover_thermal_equations.py | physics | physics.core.neurosymbolic.symbolic |
| satellite/satellite/thermal/fdir_engine.py | satellite | satellite.thermal.multi_node_thermal_network |
| satellite/satellite/thermal/hil_real_hardware.py | satellite | satellite.thermal.multi_node_thermal_network |
| satellite/satellite/thermal/observability_analysis.py | satellite | satellite.thermal.multi_node_thermal_network |
| satellite/satellite/thermal/stiff_solver_benchmark.py | satellite | satellite.thermal.multi_node_thermal_network |
| satellite/satellite/thermal/train_thermal_neural_ode.py | physics | physics.core.neurosymbolic.neural_ode |
| satellite/satellite/thermal/train_thermal_neural_ode.py | physics | physics.experiment_versioning |
| satellite/satellite/thermal/train_thermal_pinn.py | physics | physics.core.neurosymbolic.pinn |
| satellite/satellite/thermal/train_thermal_pinn.py | physics | physics.experiment_versioning |
| satellite/satellite/thermal/transient_power_profiles.py | satellite | satellite.thermal.multi_node_thermal_network |
| satellite/satellite/uq/full_orbit_montecarlo.py | satellite | satellite.thermal.multi_node_thermal_network |
| satellite/satellite/validation/flight_heritage_compare.py | satellite | satellite.thermal.multi_node_thermal_network |
| satellite/satellite/warp/warp_thermal_injection.py | satellite | satellite.thermal.multi_node_thermal_network |

## Risk Analysis

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Scripts depend on running from satellite/ working directory | High | Test all benchmark and pytest commands before and after rename |
| Documentation links break | Medium | Use search/replace plus link audit |
| Python package resolution changes | High | Add package init/shim and run import smoke tests |
| Physics dependency remains | Medium | Make physics neurosymbolic models optional adapters |
| Verification baseline paths change | Medium | Keep migration manifest and do not modify baseline contents |

## Verification Checklist

- `pytest satellite/tests -q` before rename.
- `pytest satellite/tests -q` after rename.
- Run CAD, PINN, and TVAC benchmark scripts.
- Import `satellite.thermal.multi_node_thermal_network` from repository root.
- Validate dashboard links and verification portal links.
- Confirm no `satellite/` references remain except migration notes.
- Confirm QADE and physics tests are unaffected.

## Required Test Suite

- Satellite unit tests in `satellite/tests/`.
- Thermal benchmark scripts in `satellite/benchmarks/`.
- Import smoke tests for `satellite.*` modules.
- Repository-level tests that use shared `core/`.

## Expected Breakpoints

- Relative file paths in scripts.
- Markdown links and verification reports.
- Package imports when running scripts from inside versus outside the domain folder.
- Any generated artifacts that encode old paths.

## Recommendation

Do not rename until the `satellite -> physics` dependency is isolated and a compatibility shim strategy is agreed.
