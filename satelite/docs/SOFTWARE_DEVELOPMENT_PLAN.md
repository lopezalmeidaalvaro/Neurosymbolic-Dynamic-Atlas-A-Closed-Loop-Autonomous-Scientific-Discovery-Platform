# Software Development Plan (SDP) — ASTOS Thermal OS

This Software Development Plan (SDP) defines the lifecycle, environment, standards, and management rules governing the development of the **AST-OS Spacecraft Onboard Thermal OS** platform, fully conforming to **ECSS-E-ST-40C** (Space Engineering: Software) standards.

---

## 1. Scope
The scope of this SDP encompasses the development, testing, qualification, and certification of the onboard **AST-OS cFS Application** and its coupled **Model Predictive Control (MPC)** and **Extended Kalman Filter (EKF)** state estimation physics engines.

---

## 2. Software Life Cycle (ECSS-E-ST-40C)

The software lifecycle is structured into distinct, formal ECSS phases:

```text
  Phase B: Req. Definition ──> Phase C: Design & Arch ──> Phase D: Coding & Unit Test ──> Phase E: System Integration
        [SRR / PDR]                   [CDR]                      [TRR]                        [QRR / FAR]
```

1. **Phase B: Software Requirements Definition**:
   - Compiles the Software Requirements Specification (SRS), establishing physical thermodynamic limits, time-bounded iterations, and memory footprints. Approved at **PDR** (Preliminary Design Review).
2. **Phase C: Software Design and Architecture**:
   - Mappings of cFS application pipelines and neural surrogate network designs. Approved at **CDR** (Critical Design Review).
3. **Phase D: Coding and Unit Testing**:
   - Clean C coding, static compliance scans (MISRA-C), and Unity unit testing checks. Approved at **TRR** (Test Readiness Review).
4. **Phase E: Software Verification & System Integration**:
   - Hardware-in-the-Loop (HIL) checks, thermal-vacuum (TVAC) validations, and final qualification. Approved at **QRR** (Qualification Readiness Review).

---

## 3. Development Environment
* **Onboard Compiler**: Target-specific cross-compilers (`sparc-rtems-gcc` for SPARC LEON3 processors, `arm-none-eabi-gcc` for ARM Cortex-M7).
* **Onboard RTOS**: Core Flight System (cFS) operating under **RTEMS v5.0** or **VxWorks v7.0** real-time kernels.
* **Ground Twin Stack**: Python 3.10+, PyTorch 2.0+ (surrogate neural training), OpenMDAO (multidisciplinary optimizer).

---

## 4. Coding Standards
* **Flight Software (C)**: Strictly conforms to **MISRA-C:2012** coding guidelines. No dynamic memory recursion, explicit integer sizing (`<stdint.h>`), and mandatory bracket enclosures.
* **Ground/Automation Software (Python)**: strictly PEP8 compliant.

---

## 5. Configuration Management
* **Version Control**: Git repository with branch protections.
* **Branching Strategy**:
  - `main` / `master`: Only production-grade, flight-qualified releases.
  - `develop`: Nightly builds under active integration testing.
  - `feature/tXX`: Isolated task branches requiring passing CI pipelines and double-peer reviews before merging.

---

## 6. Verification & Validation Strategy
* **Static Analysis**: Continuous scans using `cppcheck` with MISRA-C rulesets and SonarQube quality gates.
* **Unit Testing**: Unity C framework testing of mathematical cores with $\ge 90\%$ code coverage.
* **Integration Testing**: CCSDS Software Bus packet loop validations and simulated telemetry fault injections.
* **HIL Testing**: Validating MPC WCET execution latency ($<1 \text{ ms}$) on target microcontrollers under thermal shadow cycles.

---

## 7. Risk Management

| Risk ID | Technical Risk Description | Probability | Severity | Mitigation Strategy |
| --- | --- | :---: | :---: | --- |
| **RSK-01** | Single Event Upset (SEU) memory corruption in neural weights. | **Medium** | **High** | Implement Hamming(7,4) EDAC and SHA-256 Flash Golden copy reload checks. |
| **RSK-02** | MPC execution overruns the 100ms task scheduling window. | **Low** | **High** | Constrain the MPC horizon to $N=5$ and utilize discrete flat loops with zero recursion. |
| **RSK-03** | Transient temperature forecast NaNs due to uncalibrated capacities. | **Medium** | **Medium** | Calibrate nodal capacities based on structural wet masses ($C_p \cdot M$) at initialization. |
| **RSK-04** | Louver actuator wear due to high-frequency PID oscillation. | **High** | **Medium** | Transition to MPC incorporating mechanical actuator wear penalties. |
| **RSK-05** | Telemetry packet dropouts during ground communications sync. | **Medium** | **Low** | Implement robust big-endian CCSDS sequence counts and EKF telemetry filters. |

---

## 8. Deliverables
1. Onboard flight C application (`astos_cfs_app/`).
2. Standalone testing frameworks (Unity unit tests + Python integration).
3. Public Verification Portal and MDO Optimizers.
4. Software development, verification, and traceability documentation.
