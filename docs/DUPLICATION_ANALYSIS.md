# Duplication Analysis Report

This report documents all duplicated, overlapping, and redundant documentation and generated artifacts found across the `ia-matematica-github` repository, specifying their overlap percentage and recommended cleanup actions.

---

## 1. Duplication Matrix

| Source File | Duplicate/Overlapping File | Overlap % | Recommended Action | Justification |
| :--- | :--- | :---: | :---: | :--- |
| `satellite/reports/geometry_optimization_report.md` | `geometry_optimization_report.md` (root) | 100% | **DELETE (root copy)** | The root copy is a redundantly committed generated output from the topology optimizer script. |
| `satellite/reports/hil_report.md` | `hil_report.md` (root) | 100% | **DELETE (root copy)** | Redundant copy of the generated HIL test run report committed to the root. |
| `satellite/reports/hil_report.md` | `satellite/hil_report.md` | 100% | **DELETE (duplicate)** | Unnecessary duplicate in the parent directory. |
| `satellite/reports/hil_report.md` | `satellite/satellite/thermal/hil_report.md` | 100% | **DELETE (duplicate)** | Duplicate committed within the source package sub-directory. |
| `satellite/reports/cad_optimization_report.md` | `satellite/satellite/thermal/cad_optimization_report.md` | 100% | **DELETE (duplicate)** | Redundant duplicate inside the thermal code folder. |
| `satellite/reports/thermal_os_final_report.md` | `satellite/satellite/platform/thermal_os_final_report.md` | 100% | **DELETE (duplicate)** | Redundant duplicate inside the platform code folder. |
| `satellite/README.md` | `satellite/satellite/README.md` | 90% | **DELETE** | Both files contain overlapping templated boilerplate text. Retain parent `README.md` only. |
| `satellite/README.md` | `satellite/docs/README.md` | 90% | **DELETE** | Redundant templated boilerplate documentation index. |
| `satellite/reports/METRICS.md` (to be created) | `METRICS.md` (root) | 100% | **MOVE** | The root `METRICS.md` is the canonical metrics sheet for AST-OS and must be moved to the satellite domain. |
| `satellite/VERIFICATION_BASELINE_v4/` | `satellite/VERIFICATION_BASELINE_v1/`, `_v2/`, `_v3/` | 85% | **ARCHIVE** | Historical test and verification baselines. Archive v1, v2, and v3 under `docs/archive/satellite_baselines/` and keep v4 as the active canonical baseline. |
| `satellite/reports/ecss_margins_summary.md` | `satellite/reports/operational_validation_report.md` | 40% | **KEEP** | Overlap in calculated margins, but the reports serve different validation stages (compliance vs mission ops). |

---

## 2. Unification Strategy

To prevent future duplicates:
1.  **Local Output Enforcement**: Update all Python scripts (e.g. `geometry_topology_optimizer.py` and `hardware_in_the_loop.py`) to output reports exclusively to their domain subfolders (`satellite/reports/`) rather than the root directory.
2.  **Strict `.gitignore` Boundaries**: Configure git to ignore transient output paths (`outputs/`, `results/`, `*.log`).
