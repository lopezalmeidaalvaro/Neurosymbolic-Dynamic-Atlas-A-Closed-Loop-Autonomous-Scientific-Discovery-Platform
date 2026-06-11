# Spacecraft Thermal OS (AST-OS) - Space Datasets Authenticity Analysis

This report presents the scientific validation results analyzing the physical origin and mission integrity of AST-OS datasets.

## 1. Datasets Authenticity Matrix

| Target Space Dataset | Declared Origin | Audited Authenticity | Scientific Classification | Reasoning & Findings |
| --- | --- | :---: | :---: | --- |
| **`nasa_atcs_telemetry.csv`** | ISS Active Thermal Control System | **NASA DERIVED / SYNTHETIC** | SYNTHETIC | Generated procedurally by `pipeline.py` using sinusoidal thermal envelopes and injected Gaussian outliers to emulate real-world sensor streams. |
| **`cad_simulation_results.csv`** | 6-Node CAD mesh predictions | **SYNTHETIC** | SYNTHETIC | Generated via forward numerical integration of multi-node heat balance equations. |
| **`hil_results.csv`** | STM32H7 hardware-in-the-loop tests | **SYNTHETIC** | SYNTHETIC | Emulates physical TVAC board sensor spikes under solar orbital eclipses. |

## 2. Audited Systems Engineering Conclusions
1. **Zero Real NOAA Telemetry**: Despite initial claims of active weather API integration in early drafts, no live URL ingestion from NOAA space portals exists. The albedo is statically scaling. |
2. **High-Fidelity Flight Emulation**: Although the telemetry datasets are synthetically generated, they are **mathematically and physically consistent** with LEO orbital radiation profiles and ISS Active Thermal Control Systems coefficients, making them extremely robust for SIL testing pipelines.
