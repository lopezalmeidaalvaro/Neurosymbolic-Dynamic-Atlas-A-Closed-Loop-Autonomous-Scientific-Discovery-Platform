# Core Split Strategy

Generated: 2026-06-06

## Objective

Determine what belongs in shared infrastructure, physics, quantum, and satellite so each domain can eventually be removable independently.

## Current Diagnosis

`core/` is small but strategically important. It provides abstractions, domain registry, orchestration, and observability. Most files are appropriate as shared infrastructure. The main architectural problem is a reverse dependency from `core/orchestration/scientist_factory.py` into `physics`.

## Files To Remain Shared

| Path | Reason |
| --- | --- |
| core/abstractions/base_critic.py | Generic interface used by quantum critics and potentially other domains |
| core/abstractions/base_hypothesis_generator.py | Generic hypothesis generator interface |
| core/abstractions/base_memory.py | Generic memory interface |
| core/abstractions/base_sandbox.py | Generic sandbox interface |
| core/domains/domain_registry.py | Domain-agnostic registration concept |
| core/domains/domain_spec.py | Domain metadata type |
| core/domains/plugin_loader.py | Generic plugin loading utility |
| core/orchestration/scientific_container.py | Generic dependency container if it remains domain-neutral |
| core/orchestration/domain_configuration.py | Generic configuration boundary |
| core/observability/* | Shared reporting/logging utilities if they do not import domains |

## Files To Rewrite

| Path | Problem | Rewrite Strategy |
| --- | --- | --- |
| core/orchestration/scientist_factory.py | Imports physics.core.autonomous.autonomous_scientist | Replace direct import with registry lookup, entry points, or injected factory callable |
| core/orchestration/scientific_container.py | Used by quantum and satellite plugins | Keep API stable but remove domain assumptions if any appear |
| core/observability/dashboard.py | Imported by QADE benchmarks | Keep domain-neutral or move dashboard-specific rendering out of core |

## Files To Move

No mandatory physical moves are recommended before decoupling. If a shared package is not desired, copy minimal abstractions into:

- `quantum/interfaces/` for QADE extraction.
- `physics/core/interfaces/` for physics-only operation.
- `satellite/satellite/interfaces/` for AST-OS extraction.

## Reverse Dependencies

| File | Target Domain | Import |
| --- | --- | --- |
| core/orchestration/scientist_factory.py | physics | physics.core.autonomous.autonomous_scientist |

## Domain Imports From Core

Core is imported by `quantum/`, `physics/`, `satellite/`, and root tests. This is acceptable only if `core/` becomes a real shared package. If the repository is split into independent repos, each domain must either depend on a versioned `ia_core` package or vendor the minimal interfaces.

## Recommended Split Model

Use a two-stage strategy:

1. **Short term:** Keep `core/` as `ia_core` style shared infrastructure and make it domain-neutral.
2. **Medium term:** Publish or vendor the minimal interfaces required by QADE.
3. **Long term:** Each domain owns its product logic; shared core only contains generic interfaces, registry, logging, and dependency injection.
