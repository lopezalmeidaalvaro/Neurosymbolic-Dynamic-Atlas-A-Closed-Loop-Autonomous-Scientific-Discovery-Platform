# Repository Migration Plan

This document outlines the step-by-step migration plan for transforming the repository into a clean, domain-oriented monorepo.

---

## 1. Migration Overview

The migration separates the monorepo into clean, isolated domain folders while keeping root-level configuration minimal.

### Domain Reorganization Rules:
*   **quantum/**: QADE compilation platform, adapters, and benchmarks.
*   **physics/**: Continuous-time Neural ODEs, PINNs, physiological ECG representation audits, and datasets/artifacts.
*   **satellite/**: AST-OS thermal digital twin models, EKF, and HIL simulation (renamed from `satelite`).
*   **mathematics/**: Formal verification agendas and Lean 4 frameworks.
*   **core/**: Registry-based orchestration factory and shared infrastructure.
*   **dashboard/**: Frontend UI package.
*   **config/**: Centralized global configuration files (Docker, pytest, requirements, etc.).
*   **docs/** / **papers/** / **tests/**: Centralized documentation, academic manuscripts, and test suites.

---

## 2. Step-by-Step Execution Sequence

### Step 2.1: Physical Folder Rename
1.  Verify satellite dependencies and import paths.
2.  Rename `satelite/` to `satellite/` physically using `git mv` or file move wrappers.
3.  Update internal package directories to resolve `satellite.*` namespaces.

### Step 2.2: Root Configuration Reorganization
1.  Create `config/` directory.
2.  Move `Dockerfile.ci` to `config/Dockerfile.ci`.
3.  Move `pytest.ini` to `config/pytest.ini` and update the test paths:
    ```ini
    testpaths =
        physics/tests
        satellite/tests
        quantum/tests
        tests
    ```
4.  Move `requirements-dev.txt` and `requirements_lock.txt` to `config/`.
5.  Move `config.py` to `config/config.py` and update `Path(__file__).resolve().parent` to `.parent.parent` to preserve relative root detection.

### Step 2.3: Scientific Artifacts & Generated Outputs Purge
1.  Move root `data/` to `physics/data/`.
2.  Move root `databases/` to `physics/databases/`.
3.  Move root `datasets/` to `physics/datasets/`.
4.  Move root `figures/` to `docs/physics/figures/`.
5.  Move root `.json` files to `physics/artifacts/` (excluding `cad_thermal_network.json` and `geometry_optimal_design.json` which belong to `satellite/`).
6.  Move root `.db` databases to `physics/databases/`.
7.  Delete root `outputs/` and `results/` folders (only empty or generated outputs).

### Step 2.4: Benchmarks Reorganization
1.  Move root `benchmarks/checkpoints/`, `compilers/`, `reports/`, and `results/` into `quantum/benchmarks/`.
2.  Delete root `run_all_benchmarks.py` compatibility shim, replacing it with modular QADE execution `python -m quantum.benchmarks.run_all`.

---

## 3. Path Compatibility Matrix

| Old Path | New Path | Action |
| :--- | :--- | :---: |
| `satelite/` | `satellite/` | RENAME |
| `configs/` | `config/` | RENAME |
| `Dockerfile.ci` | `config/Dockerfile.ci` | MOVE |
| `pytest.ini` | `config/pytest.ini` | MOVE |
| `config.py` | `config/config.py` | MOVE |
| `data/` | `physics/data/` | MOVE |
| `databases/` | `physics/databases/` | MOVE |
| `datasets/` | `physics/datasets/` | MOVE |
| `figures/` | `docs/physics/figures/` | MOVE |
| `plugins/` | `core/plugins/` | MOVE |
| `reproduce/` | `physics/reproduce/` and `satellite/reproduce/` | MOVE |
| `benchmarks/` | `quantum/benchmarks/` | MOVE |
| `results/` / `outputs/` | — | DELETE (Generated) |

---

## 4. Verification Checklist

- [ ] Execute `pytest -c config/pytest.ini` to verify all domain tests pass.
- [ ] Verify standalone QADE import works:
  ```bash
  python -c "import sys; sys.path.insert(0, 'quantum/'); import quantum; print(quantum.__benchmark_fidelity__)"
  ```
- [ ] Confirm the root folder contains only the 17 allowed folders/files.
