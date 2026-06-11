# AST-OS Software Architecture & Dependency Graph

This document registers the modular relationships, software couplings, data integration loops, and ML dependencies of the standalone **Autonomous Spacecraft Thermal OS (AST-OS)** platform.

---

## 1. System-Level Architecture & Coupling Loops

AST-OS is composed of highly decoupled, modular subsystems that exchange information dynamically during LEO orbital simulations. The following Mermaid diagram maps the data flows and couplings:

```mermaid
graph TD
    %% Subsystems Configuration
    subgraph PhysicsCore [1. Thermodynamic Physics Core]
        A["multi_node_thermal_network.py<br/>(6-Node Lumped-Capacitance Solver)"]
        B["orbital_environment.py<br/>(Eclipse Shadows & Solar Flux Models)"]
        C["cavity_radiation_model.py<br/>(Inter-nodal Cavity Factors)"]
    end

    subgraph AvionicsEmulation [2. Avionics & Flight Software]
        D["rtos_runtime_sim.py<br/>(RTOS Emulation & Thread Watching)"]
        E["self_healing_twin.py / fdir_engine.py<br/>(FDIR Hazard Mitigation Checkers)"]
    end

    subgraph ADCS_Estimation [3. Attitude & Estimation]
        F["adcs_thermal_coupling.py<br/>(Quaternion Body Rotations)"]
        G["robust_los_ekf.py<br/>(Line-of-Sight Sensor Correction)"]
    end

    subgraph ACCELERATOR_LAYER [4. Neural Surrogates & AI]
        H["physics.core.neurosymbolic<br/>(PINNs / Neural ODEs Core)"]
        I["train_surrogate_models.py<br/>(Random Forest / MLP Pickles)"]
    end

    subgraph API_SERVING [5. API Endpoint Serving]
        J["backend/thermal_api.py<br/>(FastAPI Server / SQLite Store)"]
    end

    %% Couplings & Exchanging Data
    B -->|LEO Solar/Nadir Vectors| F
    F -->|Coupled Exposed Faces Heat Loads| A
    C -->|Inter-nodal Radiation Exchange| A
    A -->|Transient Nodal Temperatures| G
    G -->|Corrected Attitude Drift| D
    A -->|Avionics Hotspots| E
    E -->|Safety Throttling Commands| D
    D -->|Modulated CPU Core Dissipation| A
    
    %% AI Pipeline Data Flow
    A -->|Bulk Orbit Telemetry Datasets| I
    I -->|Pre-trained Surrogate weights| J
    H -->|PINN/Neural ODE Checkpoints| J

    classDef core fill:#0b132b,stroke:#1c2541,color:#5bc0be;
    classDef flight fill:#1c2541,stroke:#3a506b,color:#ffffff;
    classDef adcs fill:#3a506b,stroke:#5bc0be,color:#ffffff;
    classDef ai fill:#0b2545,stroke:#134074,color:#8da9c4;
    classDef api fill:#1d2d44,stroke:#3e5c76,color:#f0ebd8;

    class A,B,C core;
    class D,E flight;
    class F,G adcs;
    class H,I ai;
    class J api;
```

---

## 2. API Telemetry & Interface Data Integration

The FastAPI backend acts as a highly structured API gateway, loading pre-trained weights and serving the Next.js scientific observatory.

```mermaid
sequenceDiagram
    autonumber
    participant Client as Next.js Dashboard Client
    participant API as FastAPI Backend (Server)
    participant DB as SQLite database (auth.db)
    participant RF as Random Forest Pickles (models/)
    participant ODE as Coupled Nodal Solver (satellite/)

    Client->>API: POST /v1/auth/login (Username, Password)
    API->>DB: Query User credentials
    DB-->>API: Return User details and tier info
    API-->>Client: Returns API Key (masked)

    Client->>API: GET /v1/simulate?power=30&area=0.15&emissivity=0.85 (Header: X-API-Key)
    API->>DB: Check rate limits (Sliding-window check)
    DB-->>API: OK (pro user limit: 1000 req/min)
    
    alt Load cached result (TTL 60s)
        API-->>Client: Return cached transient JSON
    else Solver integration required
        API->>ODE: Run Coupled 6-Node LEO Solver (Euler + RK45)
        ODE-->>API: Return transient arrays (CPU, Battery, Radiator, Panels)
        API-->>Client: Returns transient nodal temperature JSON
    end

    Client->>API: POST /v1/predict (Power, Area, Emissivity)
    API->>RF: Predict peak temperature & time to critical
    RF-->>API: Returns inference predictions and uncertainty bounds
    API-->>Client: Return JSON prediction results
```

---

## 3. Deep Software Module Breakdowns

### 1. `satellite/adcs/adcs_thermal_coupling.py`
* **Purpose:** Computes spacecraft pointing mode quaternions (Nadir-pointing, Sun-pointing, and Slew/spinning) to dynamically determine solar absorption and Earth infrared incident heat fluxes on the 6 exposed spacecraft faces.
* **Imports:**
  - `satellite.thermal.multi_node_thermal_network` (specifically `ThermalNetwork` and `SIGMA`)
  - `config` (to register paths)

### 2. `satellite/autonomy/self_healing_twin.py` & `fdir_engine.py`
* **Purpose:** Onboard Failure Detection, Isolation, and Recovery (FDIR) loops. Detects avionics sensor anomalies, structural radiator cracks, or heater failures, modulating spacecraft operations to prevent hardware burnout.
* **Imports:**
  - `satellite.thermal.multi_node_thermal_network` (isothermal simulation states)
  - `physics.core.neurosymbolic.pinn` (compares real sensor temperatures against PINN constraints to isolate sensor drifts)

### 3. `satellite/estimation/robust_los_ekf.py`
* **Purpose:** Formulates the attitude quaternion and gyro drift Extended Kalman Filter, dynamically adjusting state covariance variables based on active thermal expansion models.
* **Imports:**
  - `satellite.thermal.multi_node_thermal_network`
  - `config`

### 4. `satellite/thermal/`
* **Core Simulator scripts:**
  - `multi_node_thermal_network.py`: Solves the transient coupled nodal equations.
  - `orbital_environment.py`: Models circular LEO orbits flux variables.
  - `geometry_topology_optimizer.py`: Handles radiator Bayesian multi-objective topological optimizations.
  - `hardware_in_the_loop.py` & `hil_real_hardware.py`: Standard HIL calibration matrices.
* **AI Training scripts:**
  - `train_thermal_pinn.py`: PINN training utilizing PyTorch custom conservation losses.
  - `train_thermal_neural_ode.py`: Neural ODE solver optimizing trajectory gradients via `torchdiffeq`.
  - `train_surrogate_models.py`: RandomForest, XGBoost, and MLP regression models.
* **Dependencies:**
  - `physics.core.neurosymbolic` (PINN models, ODE nets, SINDy sparse identifiers)
  - `physics.experiment_versioning` (`ExperimentTracker` integration logging runs)

### 5. `physics/`
* **Purpose:** Isolated, nested physics emulators directory serving the spacecraft simulator stack.
* **Modules:**
  - `physics.core.neurosymbolic.pinn`: Exposes `SharedPINNNet`.
  - `physics.core.neurosymbolic.neural_ode`: Exposes `SharedODEFunc` and `SharedNeuralODEModel`.
  - `physics.core.neurosymbolic.symbolic`: Exposes `deterministic_symbolic_recovery`.
  - `physics.experiment_versioning`: Exposes `ExperimentTracker` and git decorators.

---

## 4. Critical ML & Data Model Coupling

During FastAPI server startup (`backend/thermal_api.py`), several pre-trained machine learning checkpoints and preprocessing scalers are loaded into memory to support ultra-low latency sub-millisecond AI surrogate inference:

```text
  [FastAPI Backend Start]
           │
           ├───► Loads "satellite/models/surrogate_rf.pkl" (Random Forest Model)
           ├───► Loads "satellite/models/scaler_X.pkl" (StandardScaler inputs)
           ├───► Loads "satellite/models/scaler_y.pkl" (StandardScaler outputs)
           └───► Loads "satellite/models/surrogate_metrics.json" (Benchmark scores)
```

If the PyTorch emulators are activated, the following checkpoints are loaded dynamically:
* `satellite/models/pinn_thermal.pth`: State dict loading weights into `SharedPINNNet`.
* `satellite/models/neural_ode_thermal.pth`: State dict loading weights into `SharedODEFunc`.
* `satellite/flight/surrogate.onnx`: Compiled ONNX model for high-efficiency C-inference and microcontroller integrations.
* `satellite/flight/pinn_thermal.onnx`: Compiled PINN in ONNX format.
