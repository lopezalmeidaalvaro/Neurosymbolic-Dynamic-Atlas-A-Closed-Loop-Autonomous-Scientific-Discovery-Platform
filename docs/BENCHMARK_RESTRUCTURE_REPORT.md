# Benchmark Restructure Report

Generated: 2026-06-06

## Goal

Move QADE benchmark orchestration behind a quantum-owned entrypoint while preserving existing root commands.

## Completed Changes

| Path | Role |
| --- | --- |
| `quantum/benchmarks/phase_suite.py` | QADE-owned benchmark implementation |
| `quantum/benchmarks/run_all.py` | Domain-local CLI module |
| `run_all_benchmarks.py` | Root compatibility shim |
| `benchmarks/run_all_benchmarks.py` | Historical benchmark compatibility shim |

## Commands

Primary command:

```bash
python -m quantum.benchmarks.run_all
```

Compatibility commands:

```bash
python run_all_benchmarks.py
python benchmarks/run_all_benchmarks.py
```

## Rationale

QADE can now be benchmarked from inside the `quantum` package without relying on a root-level implementation file. Existing scripts that call the previous root commands still work through shims.

## Rollback

The implementation remains available in `quantum/benchmarks/phase_suite.py`. Reverting the shims would only require restoring the prior runner files from git history; no generated benchmark evidence was removed.
