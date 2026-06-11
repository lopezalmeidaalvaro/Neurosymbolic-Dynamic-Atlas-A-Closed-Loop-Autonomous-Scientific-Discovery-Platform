# QADE Extraction Certificate

Generated: 2026-06-07

## Current Extraction Readiness (%)

**91%** for the QADE benchmark/optimization product bundle.

## Can QADE Be Separated Today?

**YES**, if extracted as a product bundle containing `quantum/` plus required benchmark result inputs.

QADE is not yet a completely independent ecosystem plugin package because some optional domain-registration and legacy integration paths still depend on `core/` or repository-level tests.

## Extraction Simulation Results

| Simulation | Result | Notes |
| --- | --- | --- |
| `quantum/` only import smoke | PASS | QADE modules and benchmark runner import without `core/` or `physics/`. |
| `quantum/` only benchmark execution | FAIL EXPECTED | Phase VII requires Phase V/VI benchmark artifacts. |
| `quantum/` + `benchmarks/results/` benchmark execution | PASS | `python -m quantum.benchmarks.run_all` completed successfully in a temp extraction. |
| Extracted focused QADE tests | PASS | `python -m pytest quantum/tests/test_hardware_aware_optimization.py quantum/tests/test_qiskit_plugin.py -q`: 4 passed. |
| Dependency import smoke | PASS | `qiskit`, `numpy`, `pandas`, `networkx`, `scipy`, and `pytest` imported. |

## Required Folders

| Folder | Required | Reason |
| --- | --- | --- |
| `quantum/` | Yes | QADE source, tests, benchmark runner, optimization modules |
| `benchmarks/results/` | Yes for current Phase VII runner | Contains Phase V/VI inputs consumed by the current benchmark suite |
| `benchmarks/reports/` | Recommended | Raw generated report store and reproducibility context |
| `docs/qade/` | Recommended | Curated QADE documentation index |
| `docs/QADE_*.md` and phase reports | Recommended | Investor/grant/data-room evidence |

## Required Dependencies

From `quantum/requirements.txt`:

- qiskit
- numpy
- pandas
- networkx
- scipy
- pytest

Optional integrations used by adapters or broader benchmarks include PyZX, TKET, BQSKit, Cirq, and provider-specific runtime packages.

## Remaining Blockers

| Blocker | Severity | Impact |
| --- | --- | --- |
| `quantum/plugin.py` uses `core.domains` | Medium | Blocks standalone plugin registration unless `ia_core` is included or local registry adapter is added. |
| Some legacy benchmark files reference `core.observability` | Low-Medium | Does not block current `quantum.benchmarks.run_all`, but affects older scripts. |
| `quantum/tests/test_quantum_domain.py` is repository integration test | Low-Medium | Should move outside standalone QADE tests. |
| Packaging metadata incomplete | Medium | Need distribution name, versioning, extras, and CLI entry point for release. |

## Risk Assessment

Overall extraction risk: **Medium-Low**.

The core optimization and benchmark product can be separated now. The remaining risk is mostly packaging discipline, optional adapters, and legacy integration boundaries.

## Recommended Extraction Strategy

1. Create a clean QADE repository containing `quantum/`, `benchmarks/results/`, selected `benchmarks/reports/`, and curated `docs/qade/` evidence.
2. Add package metadata and a console script for `qade-benchmarks`.
3. Keep `core.domains` behavior either as an `ia_core` dependency or replace it with a QADE-local registry.
4. Move repository integration tests out of the standalone QADE test suite.
5. Run `python -m pytest ...` rather than bare `pytest` in the extracted checkout unless packaging install has already occurred.

## Estimated Effort For Full Separation

**2-4 engineering days** for a clean standalone package with metadata, test selection, local registry adapter, and reproducibility bundle.

## Certificate Verdict

QADE is extractable today as a standalone product bundle. Full package-grade separation still requires registry/orchestration cleanup and packaging metadata.
