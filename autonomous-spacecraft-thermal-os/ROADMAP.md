# AST-OS Mission Milestone & Qualification Roadmap

This document outlines the flight qualification steps, NewSpace software assurance schedules, and upcoming features designed to progress AST-OS from its current ground-tested stage to active orbital operations.

---

## 📈 Technology Readiness Level (TRL) Progress

```text
  TRL-4 (Lab Concept)  ──► TRL-5 (Component Demo) ──► TRL-6 (System HIL/TVAC) ──► TRL-7 (Space Demo) ──► TRL-9 (Flight Qualified)
     [Completed]               [Completed]               [Current Status]            [Planned 2027]           [Planned 2028]
```

* **TRL-4 / TRL-5 (Physics Sandbox Validation):** Verified multi-node transient integration mathematical models against textbook lumped-capacitance scenarios. Tested the 3D voxelizer parser on Cubesat STL geometric designs.
* **TRL-6 (System TVAC & HIL Integration - CURRENT):** Completed 30-minute Hardware-in-the-Loop emulations under dynamic gradient-descent parameter calibration. Verified ECSS-E-ST-31C thermal margin margins compliance across 10 critical Gilmore-Karam correlation scenarios with RMSE < 0.374°C.
* **TRL-7 (Space Demonstration Payload):** Planned orbital testing of the PINN/Neural ODE surrogate models aboard a commercial 3U CubeSat demonstration flight.
* **TRL-9 (Fully Flight Qualified):** Integration of AST-OS FDIR as the primary autonomic subsystem for active NewSpace commercial LEO constellation missions.

---

## 📅 Qualification Milestone Timeline

### Phase 1: Ground Operations & Hardening (Q3 2026 - Q4 2026)
* [x] **Standalone Stack Separation:** Isolate the full spacecraft pipeline and scientific dashboard into AST-OS standalone repository.
* [x] **FastAPI SLA Hardening:** Deploy secure SQLite API key validation, slides-window rate limiting, and timewise daily rotating JSON logging systems.
* [ ] **Pytest CI/CD Integration:** Configure GitHub Actions execution pipelines to run `tests/` coverage checks automatically on new code integrations.

### Phase 2: Hardware-in-the-Loop (HIL) Enhancements (Q1 2027)
* [ ] **Physical I/O Interfaces:** Expand `satellite/flight/rtos_runtime_sim.py` to communicate directly with physical sensor microcontrollers via Serial (UART) or CAN bus telemetry.
* [ ] **Dynamic Lamar Control:** Integrate custom active lamar/shutter control equations inside the closed-loop thermal solver module.

### Phase 3: In-Orbit Demonstration Flight (Q3 2027)
* [ ] **LEO Launch Campaign:** Integration of AST-OS flight binary with the primary spacecraft command computer (ARM Cortex-M7 RTOS runtime).
* [ ] **Telemetry Ingestion In-Orbit:** Stream actual orbital temperature telemetry back to our scientific observatory dashboard, matching actual orbital sensor values with Digital Twin predictions in real-time.
