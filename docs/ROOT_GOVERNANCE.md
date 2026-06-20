# Repository Root Governance

This document establishes the official structure for the repository root to prevent pollution and enforce clear domain ownership of code, data, and documentation assets.

## Root Policy (Mandatory)

The repository root is allowed to contain ONLY the folders and files listed below. Any other entry is considered root pollution and will fail the automated CI checks.

### Allowed Root Directories

- **`.github/`**: CI/CD workflows and GitHub configurations.
- **`.agent/`**: Custom agent customizations, rules, and skills configurations.
- **`quantum/`**: Core QADE quantum compiler module and REST API.
- **`physics/`**: Physics engine, calibration analysis, and simulation code.
- **`satellite/`**: AST-OS satellite operations domain.
- **`mathematics/`**: Mathematical verification engine (Lean 4 integration).
- **`core/`**: Shared core systems, domains, plugins, and helper scripts.
- **`dashboard/`**: User observability dashboard.
- **`docs/`**: Centralized documentation and reports.
- **`papers/`**: Scientific research papers and publications.
- **`tests/`**: Root test suites.
- **`config/`**: Shared project configuration files.

### Allowed Root Files

- **`README.md`**: Main repository guide.
- **`LICENSE`**: Project licensing terms.
- **`CHANGELOG.md`**: Chronological log of notable changes.
- **`pyproject.toml`**: Python build system configuration.
- **`requirements.txt`**: Main Python package dependencies.
- **`.gitignore`**: Git file exclusion patterns.
- **`.pre-commit-config.yaml`**: Pre-commit hooks configuration.

---

## Forbidden Root Entries

The following files and folders must **NEVER** live in the repository root. They must be placed inside their respective domain folders (e.g., `quantum/`, `physics/`, `satellite/`):

- **JSON / CSV files** (e.g., `*.json`, `*.csv`): Must live in `[domain]/artifacts/`.
- **Markdown reports** (e.g., `PHASE*.md`, `REPORT*.md`, `AUDIT*.md`): Must live in `docs/[domain]/`.
- **Temporary folder / scripts** (e.g., `artifacts/`, `benchmarks/`, `reproduce/`, `scripts/`, `mlops/`, `app/`): These must either live under `core/`, `quantum/`, or `physics/` under strict domain ownership.

---

## Automatic CI Enforcement

A pre-commit and push check runs via GitHub Actions (`.github/workflows/root-clean.yml`) running `python core/scripts/check_root_clean.py` to ensure complete compliance. Any additions to the root that are not explicitly authorized in the allowed lists will break the build.
