# Satellite Rename Plan

Generated: 2026-06-06

## Objective

Prepare a non-destructive migration from `satelite/` to `satellite/` while preserving all functionality.

## Current State

The root folder is named `satelite/`, but internal imports frequently use `satellite.*`. This means the code already expects a package named `satellite` in many places, but the filesystem root does not match the target public name.

## Folder Rename Strategy

1. Create a migration branch.
2. Run baseline tests from `satelite/` and record failures.
3. Use `git mv satelite satellite` only after import strategy is ready.
4. Add a temporary compatibility package or import shim if existing scripts still reference `satelite`.
5. Update README and documentation links after tests pass.
6. Keep old path references documented in a migration manifest.

## Import Rewrite Strategy

- Keep internal Python package imports as `satellite.*` where they already work.
- Replace filesystem documentation references from `satelite/` to `satellite/` after the physical rename.
- Audit `sys.path` or working-directory assumptions in satellite scripts.
- Replace `satelite -> physics` imports with optional plugin adapters before the rename if possible.

## Import Breakpoints Observed

| File | Target | Import |
| --- | --- | --- |
| satelite/plugin.py | core | core.domains.domain_registry |
| satelite/plugin.py | core | core.orchestration.scientific_container |
| satelite/satellite/run_warp_simulation.py | satellite | satellite.warp.warp_thermal_injection |
| satelite/satellite/run_warp_simulation.py | satellite | satellite.thermal.fdir_engine |
| satelite/tests/test_run_thermal_pipeline.py | satellite | satellite.run_thermal_pipeline |
| satelite/tests/test_run_thermal_pipeline.py | satellite | satellite.run_thermal_pipeline |
| satelite/physics/core/neurosymbolic/pinn.py | physics | physics.pinn_module |
| satelite/physics/core/neurosymbolic/__init__.py | physics | physics.core.neurosymbolic.pinn |
| satelite/physics/core/neurosymbolic/__init__.py | physics | physics.core.neurosymbolic.neural_ode |
| satelite/physics/core/neurosymbolic/__init__.py | physics | physics.core.neurosymbolic.symbolic |
| satelite/satellite/adcs/adcs_thermal_coupling.py | satellite | satellite.thermal.multi_node_thermal_network |
| satelite/satellite/autonomy/self_healing_twin.py | satellite | satellite.thermal.multi_node_thermal_network |
| satelite/satellite/estimation/nominal_ekf_validation.py | satellite | satellite.thermal.multi_node_thermal_network |
| satelite/satellite/estimation/nominal_ekf_validation.py | satellite | satellite.estimation.robust_los_ekf |
| satelite/satellite/estimation/robust_los_ekf.py | satellite | satellite.thermal.multi_node_thermal_network |
| satelite/satellite/flight/export_to_onnx.py | physics | physics.core.neurosymbolic.pinn |
| satelite/satellite/flight/export_to_onnx.py | satellite | satellite.thermal.train_surrogate_models |
| satelite/satellite/ops/mission_operations.py | satellite | satellite.thermal.multi_node_thermal_network |
| satelite/satellite/platform/thermal_os.py | satellite | satellite.thermal.multi_node_thermal_network |
| satelite/satellite/radiation/seu_analysis.py | satellite | satellite.thermal.train_surrogate_models |
| satelite/satellite/thermal/cavity_radiation_model.py | satellite | satellite.thermal.multi_node_thermal_network |
| satelite/satellite/thermal/discover_thermal_equations.py | physics | physics.core.neurosymbolic.symbolic |
| satelite/satellite/thermal/fdir_engine.py | satellite | satellite.thermal.multi_node_thermal_network |
| satelite/satellite/thermal/hil_real_hardware.py | satellite | satellite.thermal.multi_node_thermal_network |
| satelite/satellite/thermal/observability_analysis.py | satellite | satellite.thermal.multi_node_thermal_network |
| satelite/satellite/thermal/stiff_solver_benchmark.py | satellite | satellite.thermal.multi_node_thermal_network |
| satelite/satellite/thermal/train_thermal_neural_ode.py | physics | physics.core.neurosymbolic.neural_ode |
| satelite/satellite/thermal/train_thermal_neural_ode.py | physics | physics.experiment_versioning |
| satelite/satellite/thermal/train_thermal_pinn.py | physics | physics.core.neurosymbolic.pinn |
| satelite/satellite/thermal/train_thermal_pinn.py | physics | physics.experiment_versioning |
| satelite/satellite/thermal/transient_power_profiles.py | satellite | satellite.thermal.multi_node_thermal_network |
| satelite/satellite/uq/full_orbit_montecarlo.py | satellite | satellite.thermal.multi_node_thermal_network |
| satelite/satellite/validation/flight_heritage_compare.py | satellite | satellite.thermal.multi_node_thermal_network |
| satelite/satellite/warp/warp_thermal_injection.py | satellite | satellite.thermal.multi_node_thermal_network |

## Risk Analysis

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Scripts depend on running from satelite/ working directory | High | Test all benchmark and pytest commands before and after rename |
| Documentation links break | Medium | Use search/replace plus link audit |
| Python package resolution changes | High | Add package init/shim and run import smoke tests |
| Physics dependency remains | Medium | Make physics neurosymbolic models optional adapters |
| Verification baseline paths change | Medium | Keep migration manifest and do not modify baseline contents |

## Verification Checklist

- `pytest satelite/tests -q` before rename.
- `pytest satellite/tests -q` after rename.
- Run CAD, PINN, and TVAC benchmark scripts.
- Import `satellite.thermal.multi_node_thermal_network` from repository root.
- Validate dashboard links and verification portal links.
- Confirm no `satelite/` references remain except migration notes.
- Confirm QADE and physics tests are unaffected.

## Required Test Suite

- Satellite unit tests in `satelite/tests/`.
- Thermal benchmark scripts in `satelite/benchmarks/`.
- Import smoke tests for `satellite.*` modules.
- Repository-level tests that use shared `core/`.

## Expected Breakpoints

- Relative file paths in scripts.
- Markdown links and verification reports.
- Package imports when running scripts from inside versus outside the domain folder.
- Any generated artifacts that encode old paths.

## Recommendation

Do not rename until the `satelite -> physics` dependency is isolated and a compatibility shim strategy is agreed.
