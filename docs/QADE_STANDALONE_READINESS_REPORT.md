# QADE Standalone Readiness Report

Generated: 2026-06-06

## Readiness Score

Standalone readiness: **84/100**.

## Installed Boundary

| Requirement | Status | Evidence |
| --- | --- | --- |
| Package marker | Done | `quantum/__init__.py` |
| Dependency manifest | Done | `quantum/requirements.txt` |
| Domain-local interfaces | Done | `quantum/interfaces/__init__.py` |
| Domain-owned benchmark CLI | Done | `python -m quantum.benchmarks.run_all` |
| Root compatibility command | Done | `python run_all_benchmarks.py` |
| Benchmarks compatibility command | Done | `python benchmarks/run_all_benchmarks.py` |

## Recommended Standalone Install Flow

```bash
pip install -r quantum/requirements.txt
python -m quantum.benchmarks.run_all
pytest quantum/tests/test_hardware_aware_optimization.py quantum/tests/test_qiskit_plugin.py -q
```

## Remaining Work

- Convert `core.domains` and `core.orchestration` dependencies into either `ia_core` package dependencies or QADE-local registry adapters.
- Move repository-level physics orchestration tests out of `quantum/tests/`.
- Add packaging metadata once the distribution name and versioning policy are chosen.
- Regenerate import graph after final package split.

## Verdict

QADE is ready for a controlled extraction branch and benchmark smoke testing as a product module. It is not yet ready to publish as a completely independent PyPI-style package without the remaining registry/orchestration split.
