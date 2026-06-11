# Domain Dependency Report

Generated: 2026-06-06

## Summary

The target architecture requires each domain to be independently removable. The current repository is close for dashboard/, mathematics/, and papers/, but not for physics/, quantum/, satellite/, or shared core/.

## Domain Import Edges

| Source Domain | Imported Domain | Count |
| --- | --- | --- |
| quantum | quantum | 691 |
| physics | physics | 160 |
| physics | core | 85 |
| quantum | core | 34 |
| root | quantum | 29 |
| benchmarks | quantum | 29 |
| satellite | satellite | 22 |
| tests | core | 20 |
| core | core | 13 |
| tests | quantum | 11 |
| satellite | physics | 10 |
| tests | physics | 9 |
| physics | satellite | 3 |
| satellite | core | 2 |
| core | physics | 1 |
| quantum | physics | 1 |

## Cross-Domain Imports Detected

| Representative File | Source | Target | Import |
| --- | --- | --- | --- |
| physics/physical_lab_interface.py | physics | satellite | satellite.thermal.fdir_engine |
| physics/physical_lab_interface.py | physics | satellite | satellite.thermal.hardware_in_the_loop |
| core/orchestration/scientist_factory.py | core | physics | physics.core.autonomous.autonomous_scientist |
| quantum/plugin.py | quantum | core | core.domains.domain_registry |
| quantum/sandbox/qiskit_quantum_sandbox.py | quantum | core | core.abstractions.base_sandbox |
| satellite/plugin.py | satellite | core | core.domains.domain_registry |
| satellite/satellite/thermal/train_thermal_pinn.py | satellite | physics | physics.core.neurosymbolic.pinn |
| satellite/satellite/thermal/train_thermal_neural_ode.py | satellite | physics | physics.core.neurosymbolic.neural_ode |
| benchmarks/run_all_benchmarks.py | benchmarks | quantum | quantum.optimization.* |

## Hidden Dependencies

- core/ is nominally shared infrastructure but imports physics in scientist_factory.py, creating reverse coupling.
- quantum/ uses core abstractions for plugin, sandbox, memory, critic, and observability behavior.
- physics/ uses root core modules and satellite lab-interface imports.
- satellite/ imports physics.core.neurosymbolic for PINN/Neural ODE training and uses internal imports under package name satellite.* despite the root folder being satellite/.

## Circular / Risky Dependencies

```text
core -> physics
physics -> core

satellite -> physics
physics -> satellite
```

## Domain Isolation Recommendations

1. Quantum: move QADE benchmarks into quantum/benchmarks or expose a domain-local CLI. Replace direct core imports with quantum interfaces or package core as ia_core.
2. Physics: convert root core imports into either relative physics.core imports or a stable shared package. Remove direct satellite imports from lab interfaces through a protocol.
3. Satellite: rename folder to satellite/, then replace physics imports with local surrogate interfaces.
4. Dashboard: keep standalone; consume static artifacts or APIs only.
5. Mathematics: consume exported specifications only.
6. Papers: keep as pure documentation.
7. Core: if core is shared, it must not import any domain.

## Target Independence Contract

| Domain | Removable Today? | Reason |
| --- | --- | --- |
| dashboard/ | Mostly yes | No Python imports into it; UI consumes static artifacts |
| mathematics/ | Yes | Documentation-only |
| papers/ | Yes | Documentation-only |
| quantum/ | No | Root benchmarks and tests import it |
| physics/ | No | Shared core and satellite modules import physics |
| satellite/ | No | Naming mismatch and physics coupling |
| core/ | No | Shared dependency for physics and quantum |
