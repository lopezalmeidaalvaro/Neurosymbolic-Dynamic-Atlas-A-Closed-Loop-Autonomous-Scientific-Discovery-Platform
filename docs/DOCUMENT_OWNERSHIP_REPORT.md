# Document Ownership Report

This report enforces that every markdown document has a clear owning location. 

---

## 1. Documentos en raíz que deben moverse (con destino propuesto)

| Documento en Raíz | Destino Propuesto | Justificación |
| :--- | :--- | :--- |
| [ARCHITECTURE_REPORT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/ARCHITECTURE_REPORT.md) | [docs/ARCHITECTURE_REPORT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/ARCHITECTURE_REPORT.md) | System architecture overview. Merging into [docs/REPOSITORY_AUDIT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/REPOSITORY_AUDIT.md) is recommended. |
| [AUDIT_REPORT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/AUDIT_REPORT.md) | [docs/archive/AUDIT_REPORT_2026-05-28.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/archive/AUDIT_REPORT_2026-05-28.md) | Historical record of code fixes. |
| [CAPABILITY_MATRIX.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/CAPABILITY_MATRIX.md) | [docs/CAPABILITY_MATRIX.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/CAPABILITY_MATRIX.md) | Ecosystem-wide capability scorecard. Merge with [docs/CAPABILITIES.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/CAPABILITIES.md) is recommended. |
| [KNOWLEDGE_OBSERVABILITY_REPORT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/KNOWLEDGE_OBSERVABILITY_REPORT.md) | `benchmarks/reports/KNOWLEDGE_OBSERVABILITY_REPORT.md` | Update script output paths in generator modules (`core/observability/dashboard.py` and `quantum/benchmarks/benchmark_causal_audit.py`). |
| [METRICS.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/METRICS.md) | `satellite/reports/METRICS.md` | Core metrics sheet for the AST-OS spacecraft digital twin project. |
| [MIGRATION_LOG.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/MIGRATION_LOG.md) | [docs/archive/MIGRATION_LOG.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/archive/MIGRATION_LOG.md) | Historical migration record. |
| [PHASE_GAP_ANALYSIS.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/PHASE_GAP_ANALYSIS.md) | `physics/docs/PHASE_GAP_ANALYSIS.md` (or [docs/research/PHASE_GAP_ANALYSIS.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/research/PHASE_GAP_ANALYSIS.md)) | Internal gap analysis planning for Physics. |
| [PROJECT_POSITIONING.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/PROJECT_POSITIONING.md) | [docs/PROJECT_POSITIONING.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/PROJECT_POSITIONING.md) | Grant and investment strategic positioning rules. |
| [task.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/task.md) | [docs/archive/physics_tasks/task_phase_40.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/archive/physics_tasks/task_phase_40.md) | Physics Phase 40.0 ephemeral task. |
| [walkthrough.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/walkthrough.md) | [docs/archive/physics_tasks/walkthrough_phase_40.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/archive/physics_tasks/walkthrough_phase_40.md) | Physics Phase 40.0 ephemeral walkthrough. |
| [geometry_optimization_report.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/geometry_optimization_report.md) | `DELETE_CANDIDATE` | Redundant copy of generated [satellite/reports/geometry_optimization_report.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/reports/geometry_optimization_report.md). |
| [hil_report.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/hil_report.md) | `DELETE_CANDIDATE` | Redundant copy of generated [satellite/reports/hil_report.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/reports/hil_report.md). |

---

## 2. Documentos ya en ubicación correcta

The following documents are located in permitted directories and do not need to be moved:

* **Repository Root**:
  - [README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/README.md)
  - `LICENSE`
  - [CHANGELOG.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/CHANGELOG.md)
* **Permitted Directory [docs/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs)**:
  - All curated QADE dossiers ([QADE_TECHNICAL_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/QADE_TECHNICAL_DOSSIER.md), [QADE_GRANT_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/QADE_GRANT_DOSSIER.md), [QADE_IP_ASSET_REGISTER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/QADE_IP_ASSET_REGISTER.md), etc.).
  - All consolidation and audit reports ([DOCUMENTATION_CONSOLIDATION_REPORT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/DOCUMENTATION_CONSOLIDATION_REPORT.md), [REPOSITORY_EXECUTIVE_STATUS.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/REPOSITORY_EXECUTIVE_STATUS.md), [REPOSITORY_FINAL_STATUS_REPORT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/REPOSITORY_FINAL_STATUS_REPORT.md), etc.).
* **Permitted Directory [benchmarks/reports/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/reports)**:
  - All generated QADE benchmark reports ([COMPILER_COMPARISON_REPORT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/reports/COMPILER_COMPARISON_REPORT.md), [CALIBRATION_AWARE_REPORT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/reports/CALIBRATION_AWARE_REPORT.md), [PLACEMENT_ABLATION_REPORT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/reports/PLACEMENT_ABLATION_REPORT.md), [ROUTING_COMPARISON_REPORT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/reports/ROUTING_COMPARISON_REPORT.md), etc.).

---

## 3. Links rotos potenciales por los movimientos propuestos

Moving files from root to `docs/` and `docs/archive/` will break references in:
- [README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/README.md) (referencing `ARCHITECTURE_REPORT.md` and `MIGRATION_LOG.md`).
- [docs/DOCUMENTATION_CONSOLIDATION_REPORT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/DOCUMENTATION_CONSOLIDATION_REPORT.md) (referencing root copies of domain reports).
- [docs/DOCUMENT_INVENTORY.csv](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/DOCUMENT_INVENTORY.csv) (which tracks document paths).
- Any internal links within `physics/` and `satellite/` modules pointing to root documents.

---

## 4. Plan de actualización de referencias

1. **Update Root README**:
   Change references from `[Architecture Report](ARCHITECTURE_REPORT.md)` to `[Architecture Report](docs/ARCHITECTURE_REPORT.md)` (or remove if merged) and `[Repository Migration Plan](REPOSITORY_MIGRATION_PLAN.md)` to `[Repository Migration Plan](docs/REPOSITORY_MIGRATION_PLAN.md)`.
2. **Move CSV Inventories to Permitted `docs/manifests/`**:
   The inventory CSV files (e.g. [docs/DOCUMENT_INVENTORY.csv](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/DOCUMENT_INVENTORY.csv), [docs/GENERATED_ARTIFACT_INVENTORY.csv](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/GENERATED_ARTIFACT_INVENTORY.csv), [docs/ARCHIVE_MANIFEST.csv](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/ARCHIVE_MANIFEST.csv), [docs/DELETE_MANIFEST.csv](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/DELETE_MANIFEST.csv)) currently live in the root of [docs/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs). They should be moved to [docs/manifests/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/manifests) (which is a permitted location).
3. **Update Inventory Indexes**:
   Execute a search-and-replace sweep in [docs/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/README.md) and root [README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/README.md) to update links from `docs/*.csv` to `docs/manifests/*.csv`.
4. **Update Script Outputs**:
   Modify output parameters in `geometry_topology_optimizer.py`, `hardware_in_the_loop.py`, and `dashboard.py` to target their respective domain directories instead of standard CWD writing.
