# Failure Mode, Effects, and Criticality Analysis (FMECA)

This document contains a formal hazard register outlining the top 5 operational space hazards, their effects, and engineered safety mitigations.

---

## Top 5 Space Hazards & FMECA Register

### 1. Payload Overheating (OV-H)
* **Description**: High-load instrumentation/CPU operations exceed allowable thermal bounds ($T_{	ext{cpu}} > 85^\circ	ext{C}$).
* **Causal Factor**: Solar radiation spikes, consecutive imaging tasks, or radiator louver blockage.
* **Operational Effect**: Instrument degradation, data corruption, or physical semiconductor melting.
* **Probability / Severity**: Low / Critical
* **Mitigation Strategy**:
  - Simulated Annealing active thermal-aware scheduling prevents back-to-back high-load tasks.
  - Active louver open controls and automatic CPU duty cycle throttling.
  - Hard temperature interrupter re-entry into safe-mode if CPU exceeds 80°C.

### 2. Telemetry Sensor Corruption / Failure (SE-F)
* **Description**: Spacecraft thermistors suffer wire breaks or heavy-ion reading corruption.
* **Causal Factor**: Launch vibrations structural stress or Single Event Transients.
* **Operational Effect**: State Estimator (EKF) divergence, triggering false heater/radiator controls.
* **Probability / Severity**: Medium / Major
* **Mitigation Strategy**:
  - Directed FDIR causal graph isolation (`networkx`) checks sensors against redundant channels.
  - EKF ignores corrupted channels and switches to safe default state vectors.

### 3. State Estimator (EKF) Divergence (EKF-D)
* **Description**: Augmented EKF parameter predictions drift from physical reality.
* **Causal Factor**: Unmodeled structural alterations or massive radiator degradation.
* **Operational Effect**: Loss of look-ahead thermal feasibility check safety, leading to secondary failures.
* **Probability / Severity**: Low / Major
* **Mitigation Strategy**:
  - Self-Evolving Digital Twin runs online incremental learning (SGD) on flight telemetry to calibrate parameter drifts in real-time.
  - L2 weight regularization prevents catastrophic forgetting.

### 4. Single Event Upsets (SEU) in Weight Memory
* **Description**: Heavy-ion cosmic rays flip bit values in memory storage.
* **Causal Factor**: Solar particle storms or cosmic rays.
* **Operational Effect**: Neural network weights corruption, causing invalid control/prediction behaviors.
* **Probability / Severity**: High / Major
* **Mitigation Strategy**:
  - High-reliability Hamming(7,4) error-correcting codecs protect neural weights in memory.
  - Triple Modular Redundancy (TMR) runs three parallel model runs with majority voting.
  - Continuous SHA-256 integrity watchdog checks weights and re-flashes from write-protected ROM.

### 5. Single Event Latch-Up (SEL) in Logic Controllers
* **Description**: Ionizing radiation creates parasitic short circuits, causing high current surges.
* **Causal Factor**: Heavy-ion cosmic rays.
* **Operational Effect**: High thermal dissipation inside CPU, leading to thermal runaway and permanent hardware destruction.
* **Probability / Severity**: Low / Critical
* **Mitigation Strategy**:
  - External watchdog monitor checks execution loops against nominal WCET bounds.
  - Overcurrent circuits trigger immediate power cuts and re-flash model weights from secure Flash backup.
