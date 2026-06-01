# AST-OS cFS Integration Testing Workspace

This workspace contains integration test suites to validate CCSDS packet routing, Software Bus message exchanges, and long-term cyclic execution stability of the hardened **AST-OS cFS Flight Application**.

---

## 1. Directory Structure

```text
integration_tests/
├── test_cfs_integration.py     # Python integration test suite
└── README.md                    # This document
```

---

## 2. Command Line Execution

Analysts can run the entire integration suite using the Python `unittest` framework:

```bash
python integration_tests/test_cfs_integration.py
```

---

## 3. Test Cases Validated

* **`test_app_registers_with_executive`**: Verifies successful registration of task ID `ASTOS_TLM_APP` inside cFE Executive Services.
* **`test_app_subscribes_to_commands`**: Verifies Software Bus pipe subscriptions on telemetry sensor port `0x0801` and commands port `0x1801`.
* **`test_app_publishes_telemetry`**: Verifies periodic telemetry frame broadcast at nominal **$10 \text{ Hz}$** frequencies.
* **`test_app_survives_1000_cycles`**: Runs $1,000$ simulated inference sweeps to verify zero memory leaks and complete task scheduling stability.
