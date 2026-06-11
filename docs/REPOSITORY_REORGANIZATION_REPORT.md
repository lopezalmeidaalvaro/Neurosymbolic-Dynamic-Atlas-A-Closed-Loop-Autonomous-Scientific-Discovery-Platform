# Repository Reorganization Report

This report documents the completed reorganization of the `ia-matematica-github` repository into a clean, domain-driven monorepo layout.

---

## 1. Migration Actions Taken

### 1.1 Files & Directories Moved

*   **Satellite Rename**: Physically renamed `satelite/` to `satellite/` to fix spelling inconsistencies and conform to standard naming.
*   **Configs Reorganization**: Renamed `configs/` to `config/` (singular) and moved root configuration files (`Dockerfile.ci`, `pytest.ini`, `requirements-dev.txt`, `requirements_lock.txt`, `config.py`) into it.
*   **Physics Domain consolidation**:
    *   Moved `data/` to `physics/data/`.
    *   Moved `databases/` to `physics/databases/`.
    *   Moved `datasets/` to `physics/datasets/`.
    *   Moved all root `.json` files (excluding satellite JSONs) to `physics/artifacts/`.
    *   Moved root `.db` files (`reality_native.db`, `theory_memory.db`, `evidence_memory.db`) to `physics/databases/`.
*   **Satellite Domain consolidation**:
    *   Moved `METRICS.md` to `satellite/reports/METRICS.md`.
    *   Moved `cad_thermal_network.json` and `geometry_optimal_design.json` to `satellite/`.
*   **Quantum Benchmarks consolidation**:
    *   Moved root `benchmarks/` content (`checkpoints/`, `compilers/`, `reports/`, `results/`, and script configs) to `quantum/benchmarks/`.
*   **Shared Infrastructure**:
    *   Moved mathematical plugins (`plugins/sturm_roots.py`, etc.) to `core/plugins/`.
    *   Moved root `figures/` contents to `docs/physics/figures/`.
    *   Moved `reproduce/` contents to `physics/reproduce/` and `satellite/reproduce/`.
    *   Moved root reports and audits (`ARCHITECTURE_REPORT.md`, etc.) to `docs/`.
    *   Moved Phase 8 audit files (`PHASE8_*`) to `docs/quantum/archive/`.

### 1.2 Files Merged
*   **Quantum Gravity Audits**: Merged `PHASE30_*.md` through `PHASE39_*.md` into a single unified audit document [QG_COMPLETE_AUDIT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/physics/quantum_gravity/QG_COMPLETE_AUDIT.md).

### 1.3 Files Archived
*   Moved original `PHASE30_*.md` to `PHASE39_*.md` files to [docs/physics/archive/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/physics/archive/).
*   Moved redundant historical satellite baselines (`VERIFICATION_BASELINE_v1`, `_v2`, `_v3`) to `docs/archive/satellite_baselines/`.
*   Moved historical reviews (`CDR_READINESS_REVIEW.md`, `ekf_validation_report.md`) to `docs/archive/satellite_baselines/`.

### 1.4 Files Deleted
*   Deleted root level duplicates `geometry_optimization_report.md` and `hil_report.md`.
*   Deleted duplicate files in satellite domain (`satellite/hil_report.md`, `satellite/satellite/thermal/hil_report.md`, `satellite/satellite/thermal/cad_optimization_report.md`, `satellite/satellite/platform/thermal_os_final_report.md`).
*   Deleted boilerplate READMEs (`satellite/satellite/README.md`, `satellite/docs/README.md`).
*   Deleted redundant duplicate reports: `black_compliance_report.md`, `cdr_final_review_board_report.md`, `flight_heritage_calibration_report.md`, `pydantic_migration_report.md` (retaining `VERIFICATION_BASELINE_v4` versions).
*   Deleted empty generated directories `results/` and `outputs/` from root.

---

## 2. Final Directory Tree (Root Layout)

Following reorganization, the repository root contains **ONLY** the 17 allowed folders/files:

```
ia-matematica-github/
|-- .github/             # GitHub Actions workflows
|-- .agent/              # AI agent configurations
|-- quantum/             # QADE platform, optimization modules, packaged tests
|-- physics/             # Neurosymbolic discovery, CKA audits, data, databases
|-- satellite/           # AST-OS digital twin, simulations, reports, reproduce
|-- mathematics/         # Formal verification, Lean 4 agendas
|-- core/                # Monorepo orchestrator, core stubs, core plugins
|-- dashboard/           # Observability frontend package
|-- docs/                # Consolidated documentation and archives
|-- papers/              # Academic publications and drafts
|-- tests/               # Monorepo-level shared tests
|-- config/              # Centralized Docker, pytest, requirements, config
|-- README.md            # Entrypoint documentation
|-- LICENSE              # Project license
|-- CHANGELOG.md         # Project changelog
|-- pyproject.toml       # Standalone packaging configurations
`-- requirements.txt     # Global python requirements
```

---

## 3. Remaining Issues

1.  **Numpy 2.0 Binary Compatibility**: The user's local python environment exhibits a binary incompatibility error (`ValueError: numpy.dtype size changed`) when loading `scikit-learn` in `test_research_infrastructure.py` and `test_uncertainty_pbox.py`. This is an environment issue and does not impact the QADE codebase or packaging architecture.
