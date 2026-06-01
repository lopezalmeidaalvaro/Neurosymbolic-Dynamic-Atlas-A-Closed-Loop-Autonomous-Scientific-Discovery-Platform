# AST-OS Software Development and Qualification Documentation

This folder contains the formal software development, verification, and traceability documentation required for space-grade qualification conforming to **ECSS-E-ST-40C** and **ECSS-E-ST-31C** standards.

---

## 1. Documentation Index

| Qualification Document | Description / Reference | Format |
| --- | --- | :---: |
| **[SOFTWARE_DEVELOPMENT_PLAN.md](SOFTWARE_DEVELOPMENT_PLAN.md)** | Outlines the development lifecycle, target cross-compiler environments, Git branching rules, and technical risk mitigations. | Markdown |
| **[SOFTWARE_VERIFICATION_PLAN.md](SOFTWARE_VERIFICATION_PLAN.md)** | Outlines static analysis, unit testing, and HIL validation methods, specifying **20 formal test cases**. | Markdown |
| **[REQUIREMENTS_TRACEABILITY_MATRIX.csv](REQUIREMENTS_TRACEABILITY_MATRIX.csv)** | Traceability matrix mapping **15 system requirements** to their corresponding test case IDs and PASS status. | CSV |

---

## 2. Injected Memory & Control Benchmarks

For hardened execution metrics and algorithm comparisons, please refer to the following reports compiled inside the codebase:
* **[check_misra.py](file:///c:/Users/Alvaro/Desktop/autonomous-spacecraft-thermal-os/astos_cfs_app/check_misra.py)**: MISRA-C compliance auditor script.
* **[misra_report.txt](file:///c:/Users/Alvaro/Desktop/autonomous-spacecraft-thermal-os/astos_cfs_app/misra_report.txt)**: Flagged coding standards violations and recommendations.
* **[fault_injection_report.md](file:///c:/Users/Alvaro/Desktop/autonomous-spacecraft-thermal-os/astos_cfs_app/fault_injection_report.md)**: Statistics from the 1,000-cycle radiation upset simulation.
* **[mpc_benchmark.md](file:///c:/Users/Alvaro/Desktop/autonomous-spacecraft-thermal-os/astos_cfs_app/mpc_benchmark.md)**: Performance comparative results between classical PID and predictive MPC.
