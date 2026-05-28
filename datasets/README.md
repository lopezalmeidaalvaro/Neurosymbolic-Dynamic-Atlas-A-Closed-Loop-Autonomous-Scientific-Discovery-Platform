# Scientific Datasets Specification & Provenance Catalog

This document registers the cryptographic integrity hashes, parameters, and provenance history for all synthetic, telemetry, and experimental datasets utilized in the **Neurosymbolic Dynamic Atlas** and the **Spacecraft Orbital Thermal Digital Twin**.

---

## 🛰️ 1. Spacecraft Thermal Domain Datasets

These datasets represent transient thermal runs, environmental sweeps, EKF HIL outputs, and Gilmore-Karam correlation matrices.

### 1.1 Bulk Orbital Simulation results (`orbital_simulation_results.csv`)
* **Relative Path:** [orbital_simulation_results.csv](../satellite/thermal/orbital_simulation_results.csv)
* **Cryptographic Hash (SHA256):** `8d18ad98eb6c18f504a41defc54e4162deb9cad2c51f52a231ac9c1788a4025a`
* **Source Origin Tag:** `Numerical simulation (transient FEM)`
* **Metadata & Parameters:**
  * **Duration:** 5,400 seconds (1 full orbit).
  * **Integration Steps:** 10.0 seconds interval ($dt$).
  * **Nodes:** 6 isothermal coupled elements.
  * **Input load power:** 15.0W CPU power, area 0.15 m², emissivity 0.85.
* **Provenance:**
  * Generated procedurally inside the physics sandbox by executing `satellite/thermal/multi_node_thermal_network.py` under circular LEO boundary flux models (eclipse shadows, solar beta angle at 0, Earth albedo constant). No filtering applied.

### 1.2 HIL Closed-Loop Calibration Telemetry (`hil_results.csv`)
* **Relative Path:** [hil_results.csv](../satellite/thermal/hil_results.csv)
* **Cryptographic Hash (SHA256):** `bb13cf427515342d87ab96ce807dfbd830c82bf9f563434bd1eecee5cc3ed5bb`
* **Source Origin Tag:** `HIL simulated`
* **Metadata & Parameters:**
  * **Duration:** 1,800 seconds (30 minutes real-time run).
  * **Sampling Interval:** 5.0 seconds.
  * **Estimation Adapter:** Online Extended Kalman Filter (EKF).
* **Provenance:**
  * Extracted during Phase T17 HIL loop calibration run on the hardware emulator. Captures the dynamic parameter convergence ($C \to 500\text{ J/K}$ and $\epsilon \to 0.98$) under synthetic sensor noise ($\sigma = 0.5^\circ\text{C}$).

### 1.3 3D CAD Mesh Voxelized Telemetry (`cad_simulation_results.csv`)
* **Relative Path:** [cad_simulation_results.csv](../satellite/thermal/cad_simulation_results.csv)
* **Cryptographic Hash (SHA256):** `269417a3b269001ddc5032272dd3485caec229f1feac13f088727d4abc102256`
* **Source Origin Tag:** `CAD synthetic geometry`
* **Metadata & Parameters:**
  * **Resolution:** $1\text{ cm}^3$ voxel cell size.
  * **Voxel Shape:** 3U Cubesat Structure (10×10×10 cm Cube, 1,000 occupied nodes).
  * **Heat Loading:** 15.0 W core load at node index (4,4,4).
* **Provenance:**
  * Extracted in Phase T19 by running the 3D grid voxelizer on raw text-STL file `satellite/cad/cubesat_cube.stl`. Performs boundary exposed radiating face mapping and conductive coupling network solving.

### 1.4 Gilmore-Karam FEM Correlation Suite Matrix (`fem_correlation_results.csv`)
* **Relative Path:** [fem_correlation_results.csv](../satellite/thermal/fem_correlation_results.csv)
* **Cryptographic Hash (SHA256):** `d4702078a35516b35db1c5a9bd357dc9388267e965d00c1a30db36c1a58f0eb9`
* **Source Origin Tag:** `Derived from T18 validation`
* **Metadata & Parameters:**
  * **Test Cases:** 10 standardized boundary extremes configurations.
  * **Variables:** Solved transient digital twin values vs emulated professional FEA transient thermal diffusion low-pass values.
* **Provenance:**
  * Mapped in Phase T18 by running `fem_correlation.py`. Outlines case parameters, peak errors, correlation $R^2$, RMSE, and speedup multipliers.

### 1.5 Historical Mission Telemetry Calibration Ingestion (`telemetry.csv`)
* **Relative Path:** [telemetry.csv](../satellite/models/telemetry.csv)
* **Cryptographic Hash (SHA256):** `843587e6725eb1dd2b4e0fbd8c6944b2d38df1afef029118e0f1de1e19ee5ee1`
* **Source Origin Tag:** `Real telemetry`
* **Provenance:**
  * Ingested from NASA Cubesat mission records, ESA OPS-SAT telemetry archives, and public Kaggle databases. Features normalized columns: Area, Emissivity, Power, Peak Temperature.

### 1.6 Core Surrogates Training & Test Datasets
* **Training Path:** [thermal_dataset.csv](../satellite/thermal/thermal_dataset.csv)
  * **Hash:** `7006a21fb2cc2f53e54dbfc50858790106fbc3e4ca83e6a05cc7939cc9fa4b23`
  * **Tag:** `CAD synthetic geometry`
* **Testing Path:** [thermal_dataset_test.csv](../satellite/thermal/thermal_dataset_test.csv)
  * **Hash:** `2d0790c1349520e46ad044bda0914e3f990ae18c28151eeabb2c1264cb475787`
  * **Tag:** `CAD synthetic geometry`
* **Provenance:**
  * procedurally generated in Phase T4 by executing grid-searches across Area ($[0.01, 0.5]$), Emissivity ($[0.05, 0.98]$), and Power ($[5, 50]$), storing exact outputs for ML surrogate training.

---

## 🔬 2. Physics & Strange Attractor Domain Datasets

These datasets represent quantum gravity BEC toy models, causal layered ensembles, and chaotic strange attractor time-series.

### 2.1 Quantum Gravity BEC Analog Ensemble (`bec_ensemble.csv`)
* **Relative Path:** [bec_ensemble.csv](../physics/data/bec_ensemble.csv)
* **Cryptographic Hash (SHA256):** `08e5aced51411f922eb93f8fa972a49f8819516b43656abdd98e8913795e280c`
* **Source Origin Tag:** `Numerical simulation (transient FEM)`
* **Metadata & Parameters:** Modeled Bose-Einstein Condensate analog gravity flow parameters (density, acoustic metric curvature).

### 2.2 Causal Layered Spin Network Ensembles (`causal_layered_ensemble.csv`)
* **Relative Path:** [causal_layered_ensemble.csv](../physics/data/causal_layered_ensemble.csv)
* **Cryptographic Hash (SHA256):** `6eb86002e3257920bcf2149e1a8434a2d9208decf1851c6b895df5b32cfc211a`
* **Source Origin Tag:** `Numerical simulation (transient FEM)`
* **Metadata & Parameters:** Mapped shortest-path geodetic curvature matrices inside causal layered graph ensembles.

### 2.3 Spin Network Lattice (`spin_network_ensemble.csv`)
* **Relative Path:** [spin_network_ensemble.csv](../physics/data/spin_network_ensemble.csv)
* **Cryptographic Hash (SHA256):** `5a0ca7ac95541ae267ab2c8cb130de647f78e90b011f60ffd3c855abd694bd50`
* **Source Origin Tag:** `Numerical simulation (transient FEM)`

### 2.4 Unified Physics Features Space (`qg_unified_features.csv`)
* **Relative Path:** [qg_unified_features.csv](../physics/data/qg_unified_features.csv)
* **Cryptographic Hash (SHA256):** `dfffe635471ec06458b038da027be9f1d3e348db980ae18d539beb90d242371c`
* **Source Origin Tag:** `Derived from T18 validation`
* **Metadata:** 8D Amplitude-Invariant feature vectors mapping `perm_entropy`, `spectral_entropy`, etc. for alignment testing.
