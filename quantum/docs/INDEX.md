# Quantum Domain Knowledge Index

Welcome to the Quantum Algorithm Discovery Engine (QADE) documentation hub. This index serves as the navigation hub for all quantum-related dossiers and execution records.

---

## 1. Directory Structure

All files under `quantum/docs/` are listed below:

| File Name | Purpose | Ownership |
| :--- | :--- | :--- |
| [INDEX.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/docs/INDEX.md) | Central navigation hub. | `quantum` team |
| [QADE_TECHNICAL_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/docs/QADE_TECHNICAL_DOSSIER.md) | Technical overview of compiler subsystems, unrolling, genetic search, routing, and verification. | `compiler` leads |
| [QADE_BENCHMARK_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/docs/QADE_BENCHMARK_DOSSIER.md) | Compiler comparisons and physical hardware execution results (Run 5, Run 6, Run 7). | `validation` team |
| [QADE_PRODUCT_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/docs/QADE_PRODUCT_DOSSIER.md) | Market strategy, competitive moat, business vision, and ROI models. | `product` team |
| [HARDWARE_VALIDATION_REPORT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/docs/HARDWARE_VALIDATION_REPORT.md) | Detailed, raw cumulative physical execution logs on IBM processors. | `validation` team |
| [qade_one_pager.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/docs/qade_one_pager.md) | Single-page commercial summary. | `product` team |
| [roi_calculator.html](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/docs/roi_calculator.html) | Interactive HTML calculator for QPU cost savings. | `product` team |

---

## 2. Dependencies

The QADE compiler is packaged under `quantum/` and has the following dependencies:
*   **External dependencies**: `qiskit>=1.0.0`, `qiskit-ibm-runtime>=0.20.0`, `pyzx>=0.7.0`, `numpy`, `scipy`.
*   **System Dependencies**: Relies on daily calibration telemetry feeds from live IBM backends.

---

## 3. Recommended Reading Order

For engineers, investors, and reviewers, we recommend the following traversal:
1.  **Product Vision**: Start with [qade_one_pager.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/docs/qade_one_pager.md) and [QADE_PRODUCT_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/docs/QADE_PRODUCT_DOSSIER.md).
2.  **Technical Architecture**: Read [QADE_TECHNICAL_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/docs/QADE_TECHNICAL_DOSSIER.md).
3.  **Empirical Verification**: Review [QADE_BENCHMARK_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/docs/QADE_BENCHMARK_DOSSIER.md) and examine the detailed execution trace in [HARDWARE_VALIDATION_REPORT.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/docs/HARDWARE_VALIDATION_REPORT.md).
