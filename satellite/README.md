# AST-OS — Aerospace Spacecraft Thermal Operating System

AST-OS is a spacecraft thermal digital twin and software-in-the-loop (SIL/HIL) simulation stack. It voxelizes physical CAD geometries, constructs thermal node resistance models, and executes flight orbital thermal sweeps to monitor critical payloads and runs FDIR safety controls.

## Folder Structure

- **`backend/`**: Thermal resistance network solvers, view-factor calculations, and telemetry ingestion endpoints.
- **`dashboard/`**: Grafana telemetry configuration dashboards and visualizers.
- **`datasets/`**: View-factor matrices and reference simulation profiles.
- **`docs/`**: Consolidated dossiers and technical plans.
- **`tests/`**: embedded hardware-in-the-loop and verification test suites.
- **`verification/`**: Transient calibration vacuum data baselines.

## Consolidated Dossiers

Refer to the domain documentation under `satellite/docs/`:
- **[Knowledge Index](docs/INDEX.md)**: Navigation hub for the domain.
- **[ASTOS_TECHNICAL_DOSSIER](docs/ASTOS_TECHNICAL_DOSSIER.md)**: Digital twin architecture, conductance view-factor calculations, and network solvers.
- **[ASTOS_VALIDATION_DOSSIER](docs/ASTOS_VALIDATION_DOSSIER.md)**: HIL real-time latency verification under ECSS limits and chamber test calibration.
- **[ASTOS_MISSION_DOSSIER](docs/ASTOS_MISSION_DOSSIER.md)**: SSO and LEO orbital profiles, pointing configurations, and safety safe mode recovery protocols.
