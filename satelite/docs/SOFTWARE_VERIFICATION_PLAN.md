# Software Verification Plan (SVP) — ASTOS Thermal OS

This Software Verification Plan (SVP) details the testing methods, frameworks, and formal test cases designed to verify the functional correctness and reliability of the **AST-OS Spacecraft Onboard Thermal OS** platform.

---

## 1. Verification Objectives
* Assert that the C-based neural MLP surrogate predictions match PyTorch targets within $10^{-4}$ tolerance.
* Verify EKF parameter calibration loops correctly track structural emissivity decays.
* Assert that the Hamming(7,4) EDAC and SHA-256 integrity checkers successfully intercept and repair memory corruptions.
* Verify that the MPC controller WCET execution is bounded under $1.0 \text{ ms}$ and satisfies safety thermal limits ($T_{\text{CPU}} < 85.0^\circ\text{C}$).

---

## 2. Verification Methods

### A. Unit Testing
* **Framework**: Unity C Framework.
* **Scope**: Compiles and executes C test binaries directly verifying math cores, EDAC bits, EKF steps, and command validation limits.
* **Target Coverage**: $\ge 90\%$ code coverage for flight software.

### B. Integration Testing
* **Scope**: Evaluates cFS application registrations, Software Bus subscriptions, CCSDS packet formats, and 1,000-cycle execution survival using simulated flight telemetry feeds.

### C. Hardware-in-the-Loop (HIL) Testing
* **Scope**: Executing the hardened C binaries on an STM32H7 microcontroller target coupled with physical thermal-vacuum (TVAC) sensor emulators to profile exact scheduler jitter and execution latencies.

### D. Static Code Analysis
* **Scope**: MISRA-C:2012 ruleset compliance checking using `cppcheck` and SonarQube quality gates.

---

## 3. Test Cases Specification (20 Qualification Cases)

| Test Case ID | Subsystem | Verification Method | Description / Verification Criteria | Status |
| --- | --- | :---: | --- | :---: |
| **TC-UNIT-001** | MLP Core | Test (Unity) | Verify MLP outputs match PyTorch baseline under nominal 15W load. | **PASS** |
| **TC-UNIT-002** | MLP Core | Test (Unity) | Verify MLP outputs match PyTorch under extreme 30W load. | **PASS** |
| **TC-UNIT-003** | EKF Core | Test (Unity) | Verify EKF step converges emissivity to 0.693 under degradation. | **PASS** |
| **TC-UNIT-004** | EKF Core | Test (Unity) | Verify EKF rejects unphysical negative observations ($T < -273$ C). | **PASS** |
| **TC-UNIT-005** | EDAC Core | Test (Unity) | Verify Hamming(7,4) successfully corrects single-bit flips in weights. | **PASS** |
| **TC-UNIT-006** | EDAC Core | Test (Unity) | Verify Hamming(7,4) detects multi-bit flips in a weight byte. | **PASS** |
| **TC-UNIT-007** | Integrity | Test (Unity) | Verify SHA-256 hash successfully flags memory segment corruptions. | **PASS** |
| **TC-UNIT-008** | Integrity | Test (Unity) | Verify Flash Golden copy reload successfully recovers corrupted RAM. | **PASS** |
| **TC-UNIT-009** | Commands | Test (Unity) | Verify NOOP command increments accepted command counter by 1. | **PASS** |
| **TC-UNIT-010** | Commands | Test (Unity) | Verify SETPARAM command dynamically updates CPU temperature bounds. | **PASS** |
| **TC-UNIT-011** | Commands | Test (Unity) | Verify SETPARAM rejects invalid out-of-bounds inputs ($T_{limit} < 0$). | **PASS** |
| **TC-UNIT-012** | Exceptions | Analysis | Verify division-by-zero bounds intercept and block unphysical EKF states. | **PASS** |
| **TC-UNIT-013** | Exceptions | Analysis | Verify stack depth checker successfully catches simulated overflows. | **PASS** |
| **TC-UNIT-014** | Exceptions | Analysis | Verify task cycle execution watch dog successfully catches timeouts. | **PASS** |
| **TC-INT-001** | cFS Bus | Test (Python) | Verify AST-OS cFS App successfully registers with Executive Services. | **PASS** |
| **TC-INT-002** | cFS Bus | Test (Python) | Verify App successfully subscribes to Software Bus command topics. | **PASS** |
| **TC-INT-003** | cFS Bus | Test (Python) | Verify CCSDS telemetry packets are published at the expected 10 Hz. | **PASS** |
| **TC-INT-004** | cFS Bus | Test (Python) | Verify App survives 1,000 continuous cycles without crashes. | **PASS** |
| **TC-MPC-001** | MPC Core | Test (Unity) | Verify MPC WCET execution latency on target remains strictly $< 1.0\text{ ms}$. | **PASS** |
| **TC-MPC-002** | MPC Core | Test (Unity) | Verify MPC satisfies $T_{\text{CPU}} < 85^\circ\text{C}$ constraint under transient load. | **PASS** |

---

## 4. Pass/Fail Criteria
* **Unit Tests**: 100% of cases must pass. Zero regression errors allowed.
* **Code Coverage**: $\ge 90\%$ statement coverage for `astos_app.c` and `mpc_controller.c`.
* **Static Analysis**: Zero high-priority MISRA-C:2012 violations.
* **Integrity**: 100% recovery of memory segment bitflips via EDAC/Flash reloads.
