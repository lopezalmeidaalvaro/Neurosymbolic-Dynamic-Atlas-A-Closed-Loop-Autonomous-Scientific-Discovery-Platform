# QADE Extraction Manifest

This manifest documents the files, directories, exclusions, dependencies, and evidence files necessary to extract the Quantum Algorithm Discovery Engine (QADE) from the `ia-matematica-github` monorepo into its own independent standalone repository.

## Archivos a incluir en qade-standalone/

Move or copy the following files and directories from `quantum/` into the root of the new repository:

```
quantum/                       →  qade/
  optimization/                →  qade/optimization/
  integration/                 →  qade/integration/
  sandbox/                     →  qade/sandbox/
  critics/                     →  qade/critics/
  evolution/                   →  qade/evolution/
  hardware/                    →  qade/hardware/
    run5_executor.py
    run6_executor.py
    run7_executor.py
    run8_executor.py           [NEW]
    run9_executor.py           [NEW]
    run10_executor.py          [NEW]
  diagnostics/                 →  qade/diagnostics/
    qft_routing_diagnosis.py   [NEW]
    placement_score_diagnosis.py
  tests/                       →  qade/tests/
    test_placement_freshness.py [NEW]
  cli.py                       →  qade/cli.py
  __init__.py                  →  qade/__init__.py
  pyproject.toml               →  pyproject.toml
  README.md                    →  README.md
```

*Note on package renaming:* When copying `quantum/` to the new repository as `qade/`, the user should update `pyproject.toml` packages search section:
```toml
[project.scripts]
qade = "qade.cli:main"
qade-compile = "qade.cli:compile_command_entry"
qade-benchmark = "qade.cli:benchmark_command_entry"
qade-validate = "qade.cli:validate_command_entry"

[tool.setuptools.packages.find]
where = ["."]
include = ["qade*"]
```

## Archivos a excluir (solo tienen sentido en el monorepo original)

These files and folders under the monorepo's `quantum/` directory cross-reference other domain components (like `core` orchestration or `physics` and `mathematics` registries) and must be excluded from the clean standalone repository:

1. **`quantum/plugin.py`**: Interacts with `core.domains.domain_registry.DomainRegistry` to load QADE as a domain plugin inside the monorepo.
2. **`quantum/interfaces/`**: Abstract wrappers integrating core base abstractions (`core.abstractions`).
3. **`quantum/factories/`**: Contains orchestration factory stubs (`core.orchestration.scientific_container.ScientificContainer`).
4. **`quantum/adapters/formal_verifier.py`**: Leverages types and classes from the `mathematics` domain (e.g. `QuantumEquivalenceIR`).
5. **`quantum/tests/test_quantum_domain.py`**: A test suite that exercises monorepo agent scientists and plugin loading.
6. **`quantum/benchmarks/benchmark_*.py`**: Benchmark scripts utilizing core dashboard logging classes (`core.observability.dashboard.KnowledgeDashboard`, `ExperimentLogger`).
7. **`quantum/law_validation/`**: Validates laws in a monorepo synthetic sandbox.
8. **`quantum/noise/`**, **`quantum/novel_physics/`**, **`quantum/qml/`**, **`quantum/reality_native/`**, **`quantum/revision/`**, **`quantum/simulation/`**, **`quantum/theory/`**, **`quantum/validation/`**: Monorepo-specific research modules and SQLite theory memories.

## Dependencias externas confirmadas

These packages are specified as standard dependencies in `pyproject.toml`:
*   `qiskit>=1.0.0`
*   `qiskit-ibm-runtime>=0.20.0`
*   `pyzx>=0.7.0`
*   `numpy>=1.24.0`
*   `scipy>=1.10.0`

Additional optional dependency groups are available for the REST API (`api`) and testing (`dev`).

## Archivos de evidencia a copiar (Hardware Runs)

To document validation history on real hardware, copy the following results and reports from `quantum/benchmarks/results/hardware_real/` to the `docs/hardware_runs/` directory in the new repository:
*   `hardware_results_20260618_141230.json` (Run 6 results)
*   `report_20260618_141230.md` (Run 6 report)
*   `run7_placement_log.txt` (Run 7 execution logs)
*   `hardware_results_20260622_220512.json` (Run 9 results)
*   `report_20260622_220512.md` (Run 9 report)
*   `compilation_metrics_20260625_011549.json` (Run 10 metrics)
*   `run8_placement_log.txt`, `run9_placement_log.txt`, `run10_placement_log.txt`
*   `docs/quantum/HARDWARE_VALIDATION_REPORT.md` (Cumulative execution logs - moved to `docs/quantum/` in monorepo)
*   `quantum/docs/QADE_MASTER_SUMMARY.md` (Standalone master summary document)
