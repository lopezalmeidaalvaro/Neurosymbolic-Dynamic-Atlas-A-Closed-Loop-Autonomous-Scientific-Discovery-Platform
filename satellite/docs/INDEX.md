# Satellite Domain Knowledge Index

Welcome to the Satellite (AST-OS) Domain documentation hub. This index serves as the navigation hub for all spacecraft thermal operating system, mission profile, and embedded verification dossiers.

---

## 1. Directory Structure

All files under `satellite/docs/` are listed below:

| File Name | Purpose | Ownership |
| :--- | :--- | :--- |
| [INDEX.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/INDEX.md) | Central navigation hub. | `satellite` team |
| [ASTOS_TECHNICAL_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/ASTOS_TECHNICAL_DOSSIER.md) | Technical overview of digital twin, voxelization, and conductive/radiative solvers. | `thermal` leads |
| [ASTOS_MISSION_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/ASTOS_MISSION_DOSSIER.md) | Mission orbit simulations, LEO/SSO thermal sweeps, and safety mode protocols. | `operations` leads |
| [ASTOS_VALIDATION_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/ASTOS_VALIDATION_DOSSIER.md) | Hardware-in-the-Loop (HIL) ARM Cortex target tests, TVAC alignments, and FDIR verification. | `validation` leads |
| [REQUIREMENTS_TRACEABILITY_MATRIX.csv](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/REQUIREMENTS_TRACEABILITY_MATRIX.csv) | Requirements mapping matrix CSV. | `systems` engineering |
| [SOFTWARE_DEVELOPMENT_PLAN.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/SOFTWARE_DEVELOPMENT_PLAN.md) | Software lifecycle development guide. | `systems` engineering |
| [SOFTWARE_VERIFICATION_PLAN.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/SOFTWARE_VERIFICATION_PLAN.md) | Testing and verification protocol guide. | `systems` engineering |
| [analog_experiment_design.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/analog_experiment_design.md) | Analogue simulation validation layouts. | `thermal` leads |

---

## 2. Dependencies

The AST-OS spacecraft engine modules are located under `satellite/` and have the following dependencies:
*   **External dependencies**: `numpy`, `scipy`, `pandas` (for telemetry logs), `pytest`.
*   **Target Compilation Dependencies**: Cross-compilers for ARM Cortex-M microcontrollers.

---

## 3. Recommended Reading Order

For systems engineers, operations reviewers, and verification leads, we recommend the following traversal:
1.  **Software Lifecycle Plans**: Read [SOFTWARE_DEVELOPMENT_PLAN.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/SOFTWARE_DEVELOPMENT_PLAN.md) and [SOFTWARE_VERIFICATION_PLAN.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/SOFTWARE_VERIFICATION_PLAN.md).
2.  **Digital Twin Architecture**: Read [ASTOS_TECHNICAL_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/ASTOS_TECHNICAL_DOSSIER.md).
3.  **Orbit Mission Profiles**: Read [ASTOS_MISSION_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/ASTOS_MISSION_DOSSIER.md).
4.  **HIL Embedded Verification**: Review [ASTOS_VALIDATION_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satellite/docs/ASTOS_VALIDATION_DOSSIER.md) to inspect real-time latency and vacuum chamber accuracy.
