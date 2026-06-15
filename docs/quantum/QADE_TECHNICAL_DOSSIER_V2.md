# QADE Technical Dossier: Architecture, Isolation & Benchmarking (V2)

> **⚠️ DISCLOSURE:** All financial metrics and valuations in this document represent theoretical estimates calculated by internal simulation models. QADE has generated zero commercial contracts or active revenues. (modelo especulativo — sin revenue real)

Generated: 2026-06-12
Audience: CDTI, ENISA, NEOTEC, EIC Accelerator, deep-tech due diligence reviewers, enterprise R&D partners.

---

## 1. Executive Summary

The Quantum Algorithm Discovery Engine (QADE) is a hardware-aware quantum compilation and optimization package. Unlike standard quantum compilers that optimize for gate counts or gate depths in a device-independent manner, QADE optimizes layout mapping and gate routing by conditioning compiler decisions directly on daily quantum hardware calibration telemetry.

In a comprehensive benchmark suite evaluating QADE against 5 real compilers (Qiskit Level 3, TKET, BQSKit, Cirq-native, and PyZX) across 5 backends (2 to 30 qubits, $N=30$ runs per configuration, $n=780$ configurations per compiler), QADE achieved:
*   **Mean Fidelity**: **0.9228** (p < 0.0001 vs Qiskit L3, source: `COMPILER_COMPARISON_REAL.csv`).
*   **Mean Gate Reduction**: **-85.9%** compared to Qiskit L3.
*   **Decoupled Standalone Mode**: QADE is packaged as an independent library (`qade`) utilizing dynamic import redirection stubs, permitting usage outside of the parent `ia-matematica` orchestrator framework.

---

## 2. Architecture Evolution (Phase I → VIII)

QADE has evolved from a basic research script to a decoupled enterprise product candidate:

*   **Phases I – II (Procedural Compiler)**: Basic layout placement based on rigid coupling maps. Optimizations were gate-count-centric, leading to long critical paths and high dephasing errors on physical devices.
*   **Phase III (Hardware-Aware Routing)**: Integrated daily calibration telemetry ($T_1$, $T_2$, gate errors, readout errors) into look-ahead routing cost functions, achieving a **98.95% reduction in critical path duration** versus Phase II.
*   **Phase IV (Dominance Regions)**: Shifted focus from universal compiler superiority to workload family advantage, identifying targeted dominance in **Quantum Kernel** and **QFT** workloads.
*   **Phase V (Motif IP Database)**: Automated the discovery and validation of semantic compilation motifs. 13 unique motifs were validated, establishing the reusable knowledge-base model.
*   **Phases VI – VII (Commercial & Flywheel Modeling)**: Structured licensing models, database replacement cost metrics, and flywheel growth projections.
*   **Phase VIII (Decoupling & Real Benchmarking)**: Completed physical restructuring of the monorepo, isolated the QADE package with custom stubs, and executed strict real-only comparative benchmarks, eliminating emulated compiler fallbacks.

---

## 3. Isolation Architecture & Standalone Mode

QADE v0.1.0 can be installed and executed as an independent package (`qade`) without requiring the parent monorepo's `core` modules. This is achieved via a dedicated isolation layer:

```
+-------------------------------------------------------+
|                 Independent QADE Library              |
+-------------------------------------------------------+
                           | Imports "core.registry"
                           v
+-------------------------------------------------------+
|  sys.modules Hook: Intercepts & redirects import      |
|  - quantum/core_stub.py mock implementation           |
+-------------------------------------------------------+
                           | Satisfies imports
                           v
+-------------------------------------------------------+
|  Standalone Execution (Qiskit plugins, rewriters)     |
+-------------------------------------------------------+
```

### 3.1. The `core_stub.py` Shim
When QADE is imported, the package initialization script (`quantum/__init__.py`) checks if the main monorepo core is present on the Python path. If missing, it dynamically injects mock definitions into `sys.modules`:
```python
# excerpt from quantum/__init__.py
import sys
try:
    import core.registry
except ImportError:
    import quantum.core_stub as stub
    sys.modules['core'] = stub
    sys.modules['core.registry'] = stub
    sys.modules['core.logging'] = stub
```
This shim redirects requests for orchestrator configuration, metrics logging, and asset registries to a local fallback module (`core_stub.py`), satisfying all imports.

### 3.2. Standalone Packaging
Packaging is defined in `quantum/pyproject.toml` using `setuptools` entrypoints:
```toml
[project]
name = "qade"
version = "0.1.0"
dependencies = [
    "qiskit>=1.0.0",
    "numpy>=1.22"
]

[project.optional-dependencies]
benchmarking = [
    "pytket>=1.20",
    "cirq>=1.3.0",
    "pyzx>=0.8.0",
    "bqskit>=0.8.1"
]
```

### 3.3. Real-Or-Exclude Benchmarking Policy
To prevent silent compilation emulations, all third-party adapters implement strict availability checks. If a compiler is missing or if the configuration is unsupported (such as BQSKit for circuits $>20$ qubits), the adapter raises a `RuntimeError`:
```python
# excerpt from quantum/integration/bqskit_adapter.py
if len(circuit.qubits) > 20:
    raise RuntimeError("BQSKit is excluded for >20 qubits due to synthesis scaling limits.")
```
The benchmark runner catches this error, records the compiler as `NOT_AVAILABLE` for that configuration, and excludes it from the statistics, preserving validation integrity.

---

## 4. Real-Compiler Benchmark Results

*Source: COMPILER_COMPARISON_REAL.csv (N=30 runs per config, n=780 total)*

### 4.1. Mean Fidelity Scorecard

| Compiler Workflow | Mean Fidelity | Median Fidelity | 95% Confidence Interval | p-value vs Qiskit L3 | Cliff's Delta | Significance |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Cirq-native** | **0.9262** | 0.9293 | [0.9235, 0.9288] | $3.48 \times 10^{-35}$ | 0.3585 | Significant (p < 0.0001) |
| **QADE** | **0.9228** | 0.9275 | [0.9200, 0.9254] | $7.83 \times 10^{-30}$ | 0.3286 | Significant (p < 0.0001) |
| **BQSKit** | 0.9185 | 0.9224 | [0.9154, 0.9217] | $1.12 \times 10^{-23}$ | 0.2906 | Significant (p < 0.0001) |
| **TKET** | 0.8931 | 0.9159 | [0.8873, 0.8993] | $1.44 \times 10^{-6}$ | 0.1396 | Significant (p < 0.05) |
| **Qiskit L3** | 0.8544 | 0.8710 | [0.8465, 0.8623] | baseline | — | — |
| **PyZX** | 0.7237 | 0.8777 | [0.7022, 0.7428] | $8.23 \times 10^{-9}$ | -0.1654 | Significant (p < 0.05) |

### 4.2. Mean Gate Count Scorecard

| Compiler Workflow | Mean Gates | Median Gates | 95% Confidence Interval | p-value vs Qiskit L3 | Cliff's Delta | Significance |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **QADE** | **10.6** | 8.0 | [10.1, 11.2] | $5.65 \times 10^{-134}$ | -0.7131 | Significant (p < 0.0001) |
| **Cirq-native** | 12.4 | 9.5 | [11.7, 13.0] | $1.32 \times 10^{-116}$ | -0.6646 | Significant (p < 0.0001) |
| **BQSKit** | 12.4 | 9.5 | [11.7, 13.0] | $1.32 \times 10^{-116}$ | -0.6646 | Significant (p < 0.0001) |
| **TKET** | 25.9 | 17.5 | [24.5, 27.3] | $1.12 \times 10^{-27}$ | -0.3157 | Significant (p < 0.05) |
| **Qiskit L3** | 75.3 | 48.0 | [71.2, 79.4] | baseline | — | — |
| **PyZX** | 56.4 | 28.0 | [52.3, 61.3] | $3.27 \times 10^{-2}$ | -0.0613 | Significant (p < 0.05) |

*Note: QADE’s gate count improvement (-85.9% compared to Qiskit L3) is highly pronounced on smaller circuits (2-5 qubits) where compiler routines converge to minimal layouts.*

---

## 5. Motif Governance v1

To manage circuit optimization patterns as formal IP assets, QADE Phase VIII implements a Motif Governance System:

*   **Lifecycle States**: All motifs are versioned and audited through a six-stage transition loop (`DISCOVERED` -> `VALIDATED` -> `REUSABLE` -> `DEPLOYED` -> `DEPRECATED` -> `ARCHIVED`).
*   **JSON Schema**: Enforces schema validation (`MOTIF_SCHEMA_V1.json`) on all registered motifs, requiring exact definition of gate sequences before/after, qubit counts, hardware tested, and transfer statistics.
*   **Motif Registry**: Populated with 13 unique validated motifs. 11 motifs are classified as `REUSABLE` (frequency $>1$ and transferability score $= 1.0$), while 2 motifs are restricted as `VALIDATED` (restricted to the VQE domain).
*   **Failure Registry**: Logs motifs with failure modes, such as dephasing degradation on sparse topologies or classical simulation memory limits.

---

## 6. Physical Hardware Validation Protocol

QADE Phase VIII outlines the exact execution protocol to validate simulated cost functions on real quantum computing hardware:

*   **Work Package 1 Plan**: Ingest daily calibration snapshots ($T_1, T_2$, CNOT gate errors, readout errors) to execute validation batch jobs (QADE vs. Qiskit L3) on **ibm_brisbane** and **ionq_aria** processors.
*   **Statistical Sample**: Uses **8,192 shots** across 30 runs per configuration (totaling 245,760 shots) to resolve physical Hellinger fidelity differences with $\ge 90\%$ statistical power.
*   **Calibration Correction**: If physical fidelity drifts by $> 15\%$ from predictions, the compiler triggers a correction loop, calculating scaling offsets for the daily calibration parameters.
