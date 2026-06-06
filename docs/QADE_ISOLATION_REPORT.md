# QADE Isolation Report

Generated: 2026-06-06

## Goal

If `quantum/` is extracted into a separate repository, QADE must still function and remain independently installable.

## Current Status

QADE is mostly isolated from product domains outside `core/`. The import graph shows no production imports from QADE into `dashboard/`, `papers/`, `mathematics/`, or `satelite/`. The only `quantum -> physics` edge appears in `quantum/tests/test_quantum_domain.py`, not in the QADE optimization modules.

Observed cross-domain targets from `quantum/`:

| Target Domain | Import Count |
| --- | --- |
| core | 34 |
| physics | 1 |

## Blocking Dependencies

| Dependency | Evidence | Severity | Why It Blocks Extraction |
| --- | --- | --- | --- |
| core abstractions | quantum/critics, generators, memory, sandbox import core.abstractions | High | A standalone QADE repo would need these interfaces or a shared package |
| core observability | multiple quantum/benchmarks import core.observability | Medium | Benchmark/report tooling depends on shared logging and documentation utilities |
| core domain registry | quantum/plugin.py and tests import core.domains | Medium | Plugin registration needs either local registry or external ia_core dependency |
| core orchestration | quantum/factories imports core.orchestration.scientific_container | Medium | Factory wiring needs a local equivalent or dependency injection package |
| root benchmark runner | run_all_benchmarks.py imports quantum modules from repository root | High | Extraction needs a QADE-owned CLI/entrypoint |
| physics in test only | quantum/tests/test_quantum_domain.py imports physics.core.autonomous.autonomous_scientist | Low-Medium | This test becomes an integration test outside standalone QADE |

## Non-Blocking Domains

| Domain | Status | Comment |
| --- | --- | --- |
| physics/ | Not required for production QADE | Only test-level dependency observed from quantum into physics |
| satelite/ / satellite/ | No direct QADE dependency observed | QADE extraction does not require satellite code |
| dashboard/ | No direct QADE dependency observed | Dashboard may present QADE artifacts but QADE does not import it |
| papers/ | No runtime dependency | Documentation only |
| mathematics/ | No runtime dependency | Future formal verification can consume exported motifs/specs |

## Required Refactors

1. Create a minimal `quantum/interfaces/` package containing `BaseCritic`, `BaseSandbox`, `BaseMemory`, and `BaseHypothesisGenerator`, or publish `core/abstractions` as `ia_core`.
2. Move QADE benchmark runner into `quantum/benchmarks/run_all.py` with a root compatibility shim.
3. Replace benchmark observability imports with QADE-local reporting utilities or optional `ia_core.observability`.
4. Split `quantum/tests/test_quantum_domain.py` into a standalone QADE test and a repository-level integration test.
5. Add QADE package metadata and dependency extras for Qiskit, PyZX, TKET, BQSKit, Cirq, and benchmark tools.

## Migration Strategy

- **Step 1:** Add QADE-local CLI without removing existing root runner.
- **Step 2:** Copy or vendor minimal core abstractions into QADE-local interfaces.
- **Step 3:** Replace imports in QADE source with local interfaces while keeping compatibility aliases.
- **Step 4:** Move root-only integration tests out of standalone QADE suite.
- **Step 5:** Build a clean temporary checkout containing only `quantum/`, `benchmarks/` outputs needed for QADE, and minimal package metadata.
- **Step 6:** Run focused QADE tests and benchmark smoke tests.

## Final Independence Score

Current QADE independence score: **72/100**.

Target score after refactors: **92/100**.

Rationale: product QADE code is not meaningfully coupled to physics, satellite, dashboard, papers, or mathematics. The main remaining blocker is shared `core/` and root benchmark orchestration.
