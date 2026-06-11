# README Unification Report

This report audits every `README` file currently present in the [ia-matematica-github](file:///c:/Users/Alvaro/Desktop/ia-matematica-github) repository to define a clear ownership and unification strategy.

---

## README Audits and Recommendations

| Archivo | Propósito | Necesario | Duplicado en | Acción recomendada |
| :--- | :--- | :---: | :--- | :--- |
| [README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/README.md) | Main repository entry point. Describes the multi-domain ecosystem, architecture, status, core technologies, and roadmap. | **Sí** | None | **KEEP** — Keep at repository root as the primary landing page and index. |
| [quantum/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/README.md) | Entry point for the Quantum Algorithm Discovery Engine (QADE) domain. Outlines QADE architecture, modules, and confirmed capabilities. | **Sí** | None | **KEEP** — Keep in [quantum/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum) as the domain-level entry point. |
| [docs/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/README.md) | Entry point for the cross-domain public documentation root. Lists executive entry points and directories. | **Sí** | None | **KEEP** — Keep in [docs/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs) as the documentation directory index. |
| [docs/qade/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/qade/README.md) | Curated public entry point for QADE due diligence and investor files. | **Parcial** | Significant overlap with [docs/QADE_DATA_ROOM_INDEX.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/QADE_DATA_ROOM_INDEX.md). | **MERGE** — Merge contents of [docs/QADE_DATA_ROOM_INDEX.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/QADE_DATA_ROOM_INDEX.md) here to create a single QADE portal index, then delete [docs/QADE_DATA_ROOM_INDEX.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/QADE_DATA_ROOM_INDEX.md). |
| [satellite/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/README.md) | Entry point for the AST-OS spacecraft thermal digital twin project. | **Sí** | None | **KEEP** — Retain as domain-level entry point, to be renamed to `satellite/README.md` during the planned rename. |
| [satellite/satellite/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/satellite/README.md) | Subfolder entry point for the Python package source tree of AST-OS. | **No** | Overlaps with boilerplate sub-READMEs. | **ARCHIVE** or **DELETE** — Contains generic templated text. Redundant. |
| [satellite/docs/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/README.md) | Documentation portal index for the satellite domain. | **No** | Generic boilerplate content. | **ARCHIVE** or **DELETE** — Redundant templated text. |
| [satellite/satellite/investor/INVESTOR_PACKAGE_README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/satellite/investor/INVESTOR_PACKAGE_README.md) | Index for AST-OS venture capital and incubator packages. | **Sí** | None | **KEEP** — Keep in its current sub-directory to organize business files. |
| [satellite/satellite/qualification/QUALIFICATION_PACKAGE_README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/satellite/qualification/QUALIFICATION_PACKAGE_README.md) | Index for the AST-OS space qualification and standards files. | **Sí** | None | **KEEP** — Keep in its current sub-directory to organize compliance files. |
| [mathematics/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/mathematics/README.md) | Entry point for the Mathematics domain. | **Sí** | None | **KEEP** — Keep as domain-level placeholder/roadmap index. |
| [physics/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/physics/README.md) | Entry point for the Physics neurosymbolic AI-for-science domain. | **Sí** | None | **KEEP** — Keep in [physics/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/physics) as the domain-level entry point. |
| [papers/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/papers/README.md) | Entry point for scientific manuscripts. | **Sí** | None | **KEEP** — Keep in [papers/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/papers) as the manuscripts index. |
| [datasets/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/datasets/README.md) | Entry point for the datasets directory. | **Sí** | None | **KEEP** — Keep in [datasets/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/datasets) as the datasets index. |
| [docs/archive/legacy_benchmark/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/archive/legacy_benchmark/README.md) | Explains the archiving of the legacy singular `benchmark/` folder. | **Sí** (trace) | None | **KEEP** — Keep in [docs/archive/legacy_benchmark/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/archive/legacy_benchmark) for audit trailing. |
| [docs/archive/root/README_AUDIT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/archive/root/README_AUDIT.md) | Historical audit of previous README structures. | **No** | None | **KEEP** — Retain in [docs/archive/root/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/archive/root) for historical traceability. |
| [docs/archive/root/README_REWRITTEN.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/archive/root/README_REWRITTEN.md) | Rewritten draft version of root README. | **No** | Root [README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/README.md) contains finalized content. | **KEEP** — Retain in [docs/archive/root/](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/archive/root) or delete. |
| [quantum/circuits/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/circuits/README.md) | Subfolder entry point for QADE circuit examples. | **No** | Generic boilerplate content. | **ARCHIVE** or **DELETE** — Redundant templated text. |
| [mathematics/symbolic/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/mathematics/symbolic/README.md) | Subfolder entry point for Symbolic Mathematics. | **No** | Generic boilerplate content. | **ARCHIVE** or **DELETE** — Redundant templated text. |
| [papers/qg/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/papers/qg/README.md) | Subfolder entry point for Quantum Gravity papers. | **No** | Generic boilerplate content. | **ARCHIVE** or **DELETE** — Redundant templated text. |
| [papers/thermal/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/papers/thermal/README.md) | Subfolder entry point for Spacecraft Thermal papers. | **No** | Generic boilerplate content. | **ARCHIVE** or **DELETE** — Redundant templated text. |

---

## Action Plan for README Unification

1. **Boilerplate Sub-README Cleanup**:
   Identify all sub-directory READMEs containing identical templated layout blocks (such as [quantum/circuits/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/circuits/README.md), [mathematics/symbolic/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/mathematics/symbolic/README.md), [papers/qg/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/papers/qg/README.md), [papers/thermal/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/papers/thermal/README.md), etc.). Archive or replace them with lightweight files showing only local custom content, to reduce developer noise.
2. **QADE Portal Consolidation**:
   Merge the due-diligence order from [docs/QADE_DATA_ROOM_INDEX.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/QADE_DATA_ROOM_INDEX.md) directly into [docs/qade/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/qade/README.md). This establishes a single, definitive entry point for investors and reviewers.
3. **AST-OS Rename Prep**:
   Move [satellite/README.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/README.md) to `satellite/README.md` once the parent folder name is corrected.
