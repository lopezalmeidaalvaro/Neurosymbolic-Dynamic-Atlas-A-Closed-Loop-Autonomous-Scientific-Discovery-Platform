# PHASE 8: Monorepo Repository Map

This document establishes the official layout and mapping for the `ia-matematica-github` repository following the Phase VIII restructuring and packaging.

---

## 1. Directories That Remain Exactly As They Are

The following directories maintain their original structure and logic, preserving source code integrity:
*   [quantum/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/): Core QADE platform logic, optimization algorithms, and tests. Now packaged independently.
*   [physics/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/physics/): Neurosymbolic dynamics pipeline, Neural ODEs, and physiological representation audits.
*   [satellite/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/): Spacecraft thermal digital twin backend, EKF calibration, and HIL simulation (spelled `satellite` in the filesystem).
*   [mathematics/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/mathematics/): Formal math and research agendas.
*   [dashboard/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/dashboard/): Next.js web observability dashboard (built and verified).
*   [core/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/core/): Monorepo orchestration framework and registry-based factory definitions.
*   [tests/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/tests/): Root monorepo integration test suites.
*   [.github/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/.github/): Action workflows (dashboard sync, pytest, and newly added QADE CI).
*   [.agent/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/.agent/): Local AI developer configuration.

---

## 2. Directories Reorganized Internally

*   [docs/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/): Reorganized into four domain subfolders:
    *   [docs/quantum/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/quantum/): QADE user documentation, index, and technical dossier.
    *   [docs/physics/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/physics/): Neurosymbolic pipeline and dynamic discovery guides. Original `PHASE30` through `PHASE39` files are archived here, and their findings are consolidated.
    *   [docs/satellite/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/satellite/): AST-OS spacecraft digital twin documentation.
    *   [docs/mathematics/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/mathematics/): Formal methods agendas.
*   [papers/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/papers/): Organized into four academic publishing folders:
    *   [papers/quantum/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/papers/quantum/): Contains QADE TQE paper.
    *   [papers/physics/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/papers/physics/): Contains dynamical systems TPAMI manuscript.
    *   [papers/satellite/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/papers/satellite/): Contains AST-OS TAES digital twin manuscript.
    *   [papers/mathematics/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/papers/mathematics/): Contains compiler formal verification position paper.
*   [benchmarks/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/): Emulated and real compiler run scripts. Regenerable cache and outputs are cleaned.

---

## 3. Root Files Classification

*   `README.md`: Remains in the root, updated to act as the monorepo entry point.
*   `LICENSE`: Remains in the root.
*   `CHANGELOG.md`: Remains in the root, tracking project iterations.
*   `requirements.txt` / `requirements-dev.txt` / `requirements_lock.txt`: Remain in the root.
*   `pyproject.toml` (root): Remains in the root.
*   `run_all_benchmarks.py`: Replaced by a compatibility shim redirecting to the modular benchmark runner.
*   `config.py`: Remains in root.
*   `.gitignore`: Updated to ignore regenerable benchmark artifacts.

### 3.1 Historical MD Files
*   `PHASE30` through `PHASE39` markdown files: Merged into the main document [QG_COMPLETE_AUDIT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/physics/quantum_gravity/QG_COMPLETE_AUDIT.md). The original files are archived in [docs/physics/archive/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/physics/archive/).
*   `PHASE8` audit reports: Remain temporarily in the root for ease of review. They can be moved to [docs/quantum/archive/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/quantum/archive/) after validation.
*   `.json` config/report dumps: Retained in root temporarily; scheduled to be classified under their respective domains progressively.

---

## 4. Other Directories Scheduled for Reorganization

*   `artifacts/`: Classified between `quantum/benchmarks/` (quantum data dumps) and `physics/` (representation outputs).
*   `figures/`: Mapped to `docs/quantum/figures/` or `docs/physics/figures/`.
*   `data/`: Mapped to `physics/data/`.
*   `datasets/`: Mapped to `physics/datasets/`.
*   `databases/`: Unified under `quantum/` or `physics/` database instances.
*   `outputs/`: Cleared, with `.gitignore` updated to block future commits.
*   `results/`: Redistributed into domain results folders.
*   `reproduce/`: Reorganized into `quantum/reproduce/` and `satellite/reproduce/`.
*   `plugins/`: Consolidated in `core/plugins/`.
