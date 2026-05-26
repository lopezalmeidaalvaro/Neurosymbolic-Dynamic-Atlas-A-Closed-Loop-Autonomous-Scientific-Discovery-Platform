# Migration Log — Repository Reorganization & Upgrade

This document records the comprehensive reorganization, path corrections, and graphical upgrades performed in this repository to establish a modular, multi-domain scientific architecture.

---

## 1. Directory Structure Restructuring

The repository has been restructured from a single flat layout into **6 distinct logical domains** at the root level. All directories and documentation have been standardized in **English**.

### Relocated Components

| Original Location | New Location | Description |
| :--- | :--- | :--- |
| `dashboard/app/`, `dashboard/components/`, etc. | `dashboard/src/...` | Relocated Next.js source code inside the `src/` directory to adhere to Next.js architectural standards. |
| `core/` (empirical, validation, etc.) | `physics/core/` | Moved all modular neurosymbolic pipeline utilities. |
| `autonomous_scientist.py`, `llm_reasoner.py`, `sandbox_executor.py` | `physics/core/autonomous/...` | Grouped all LLM-driven autonomous researcher modules. |
| `checkpoints/` | `physics/models/` | Relocated pre-trained model weights (`.pth` files) for ResNet, LSTM, Neural ODEs. |
| `data/` | `physics/data/` | Unified all dynamic and ECG datasets. |
| `figures/` | `physics/figures/` | Relocated generated visual assets. |
| `*.py` in root (SINDY, PINN, benchmarks, sweeps) | `physics/...` | Cleaned up root workspace by moving all pipeline scripts inside `physics/`. |
| `tests/`, `test_phase*.py`, `test_ev3_stability.py` | `physics/tests/...` | Unified all unit and integration test scripts. |
| LaTeX paper files in root | `papers/system/` | Grouped scientific papers. The `physics/papers/` folder has a mirror copy. |
| *None* | `satellite/` | Created the new orbital thermal simulation domain (Phase T). |
| *None* | `mathematics/symbolic/` | Created the placeholder for future formal mathematics verification. |
| *None* | `quantum/circuits/` | Created the placeholder for future quantum reservoir computing models. |

---

## 2. Path Resolutions & Imports Protection

To ensure all scripts can run standalone inside the relocated directories:
1. **Imports Protection:** Prepended `sys.path.insert(0, os.path.dirname(__file__))` to all relocated Python scripts under `physics/` and `physics/core/autonomous/` to protect relative module imports.
2. **Central Path Resolution:** Modified `physics/core/io/artifact_manager.py` to use a 4-level parent directory query to locate `PROJECT_ROOT` and redirect `LEGACY_ARTIFACTS_DIR` to `physics/artifacts/`.
3. **Checkpoints Path Redirect:** Updated all weights loading/saving references from `"checkpoints/"` to `"models/"` across all scripts, matching the new structural directory layout.
4. **TypeScript Aliases:** Modified `dashboard/tsconfig.json` to map `"@/*"` to `["./src/*"]` ensuring flawless typescript import resolution.

---

## 3. Next.js Dashboard Upgrades

1. **Domain Selector Component (`DomainSelector.tsx`):**
   - Added a drop-down selector next to the breadcrumbs in the Header navbar, visible in both Simple and Expert complexity modes.
   - Provides seamless switching between **Physics**, **Satellite**, **Mathematics**, and **Quantum Lab** domains.
   - Features sleek Framer Motion dropdown scale/fade animations and customized glowing borders matching the dark-theme aesthetic.
2. **Spacecraft Thermal Digital Twin (`ThermalDigitalTwin`):**
   - Implemented at `dashboard/src/app/[lang]/satellite/page.tsx`.
   - Runs a real-time 1-node orbital thermal dynamics Euler integrator directly inside React/TypeScript (solving 3 orbits in under $1\text{ms}$ on slider drag to avoid start transients).
   - Provides interactive sliders for **Internal Power ($P$)**, **Radiator Area ($A$)**, **Absorptivity ($\alpha$)**, and **Emissivity ($\epsilon$)**.
   - Integrates a Recharts responsive line chart plotting orbit temperature profiles against critical safety limits (freeze at $-40^\circ\text{C}$, burnout at $85^\circ\text{C}$).
   - Displays real-time avionics health diagnostics (`OPTIMAL`, `WARNING`, `CRITICAL`).
3. **Domain Routing & Placeholders:**
   - Implemented localized routing segments under `dashboard/src/app/[lang]/` for `physics/`, `satellite/`, `mathematics/`, and `quantum/` with correct breadcrumbs and locales.
   - Created root-level redirect files inside `dashboard/src/app/` to handle localized rewrites.

---

## 4. Spacecraft Thermal Simulator (Python)

Created a fully operational physical simulator under `satellite/`:
1. `satellite/thermal/orbital_thermal_simulator.py`: Solves orbital LEO thermal cycles, prints reports, and exports telemetry as CSV and PNG plots.
2. `satellite/thermal/train_thermal_emulator.py`: Gathers synthetic simulation datasets and trains a surrogate Multi-Layer Perceptron (MLP) in PyTorch to emulate spacecraft thermal equilibrium bounds.
3. `satellite/api/thermal_api.py`: Integrates a programmatic interface class for other microservices.
4. `satellite/README.md`: Explains the physical equations and CLI configurations.
