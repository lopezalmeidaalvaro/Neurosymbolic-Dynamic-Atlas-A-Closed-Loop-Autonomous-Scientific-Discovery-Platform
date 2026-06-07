# QADE Extraction Progress Report

Generated: 2026-06-06

## Executive Summary

QADE moved from planning-only isolation to a partially executed standalone boundary. The benchmark implementation now lives under `quantum/benchmarks/`, QADE has a local interface package, and the shared core factory no longer statically imports physics.

Current extraction score: **84/100**.

## Completed Decoupling

| Change | Status | Evidence |
| --- | --- | --- |
| Removed static `core -> physics` import | Done | `core/orchestration/scientist_factory.py` now lazy-loads orchestrator class |
| Added QADE-local interfaces | Done | `quantum/interfaces/__init__.py` |
| Replaced QADE source imports from `core.abstractions` | Done | critic, generator, memory, and sandbox modules use `quantum.interfaces` |
| Added QADE package marker | Done | `quantum/__init__.py` |
| Added QADE requirements file | Done | `quantum/requirements.txt` |
| Encapsulated benchmark implementation | Done | `quantum/benchmarks/phase_suite.py` and `quantum/benchmarks/run_all.py` |

## Remaining Coupling

| Dependency | Status | Extraction Impact |
| --- | --- | --- |
| `quantum/plugin.py` and factories use `core.domains` / `core.orchestration` | Open | Needs local registry or published `ia_core` package |
| Some legacy benchmark modules use `core.observability` | Open | Replace with QADE-local reporting or optional dependency |
| `quantum/tests/test_quantum_domain.py` imports physics orchestrator | Open | Move to repository integration tests for standalone extraction |
| Baseline import graph still records historical edges | Open | Regenerate `IMPORT_GRAPH.csv` after migration branch validation |

## Extraction Verdict

QADE is now separable for benchmark execution and core optimization work, but not yet a fully clean standalone package. The remaining blockers are shared registry/orchestration utilities and legacy integration tests, not physics or satellite production dependencies.
