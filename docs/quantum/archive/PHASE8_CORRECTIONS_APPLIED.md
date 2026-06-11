# QADE Phase VIII Corrections Applied Report

This report summarizes the modifications and additions applied to the repository to transition QADE benchmarks from emulated/fallback results to a strict real-execution paradigm, while correcting documentation and commercial positioning.

---

## Part A: Real-Execution Benchmarking Enhancements

### 1. Requirements and Installation
*   **Created [`quantum/requirements_benchmarking.txt`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/requirements_benchmarking.txt):** Explicitly defines version-controlled benchmark dependencies for Qiskit, TKET, BQSKit, Cirq, and PyZX.
*   **Created [`quantum/install_benchmark_deps.sh`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/install_benchmark_deps.sh):** Script to automate pip installations and verify compiler availability.

### 2. Adapters Refactoring
*   **Modified [`quantum/integration/bqskit_adapter.py`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/integration/bqskit_adapter.py):** Removed the hardcoded 5-qubit limit. It now dynamically queries maximum qubit capabilities from configuration and raises a `RuntimeError` rather than silently falling back to Qiskit L3 transpilation.
*   **Modified [`quantum/integration/cirq_adapter.py`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/integration/cirq_adapter.py):** Implemented a real [`compile_with_cirq`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/integration/cirq_adapter.py) function using native Cirq optimization passes (`eject_phased_paulis`, `drop_negligible_operations`, and `drop_empty_moments`). It now raises a `RuntimeError` if Cirq is not installed, eliminating format-only conversions from benchmarking.
*   **Modified [`quantum/integration/tket_adapter.py`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/integration/tket_adapter.py):** Changed to throw a `RuntimeError` when pytket is not installed, preventing silent emulation via Qiskit L3.
*   **Modified [`quantum/integration/pyzx_adapter.py`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/integration/pyzx_adapter.py):** Changed to throw a `RuntimeError` when pyzx is not installed, preventing fallback to the internal algebraic cancel pass.

### 3. Pipeline Integration
*   **Modified [`quantum/benchmarks/benchmark_all_compilers.py`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/benchmarks/benchmark_all_compilers.py):**
    *   Imports `compile_with_cirq`.
    *   Updated the compile workflow to handle `RuntimeError` exceptions from adapters and return `None` (excluding the compiler from results rather than emulating it).
    *   Added [`verify_compiler_availability`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/benchmarks/benchmark_all_compilers.py) to dynamically check dependencies before execution.
    *   Configured the runner to execute each configuration `30` times (`minimum_runs_per_configuration = 30`) to build statistical significance.
    *   Enforced the p-value constraint in `generate_markdown_report()`, restricting phrases like "outperforms" or "beats" unless $p < 0.05$ (calculated via Mann-Whitney U test vs Qiskit L3).
    *   Added a separate registry section for compilers not available for testing.
*   **Created [`quantum/benchmarks/compiler_capability_detection.py`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/benchmarks/compiler_capability_detection.py):** Probes each compiler and writes capabilities (e.g. max qubits) to [`benchmarks/results/COMPILER_CAPABILITIES.json`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/results/COMPILER_CAPABILITIES.json) to eliminate hardcoded thresholds.
*   **Created [`quantum/benchmarks/statistical_validation.py`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/benchmarks/statistical_validation.py):** Evaluates mean, median, standard deviation, 95% bootstrap confidence intervals, Cliff's delta effect sizes, and MWU p-values, outputting [`benchmarks/reports/STATISTICAL_VALIDATION_REPORT.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/reports/STATISTICAL_VALIDATION_REPORT.md).
*   **Created [`quantum/benchmarks/rerun_with_real_compilers.py`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/benchmarks/rerun_with_real_compilers.py):** Orchestrates capability detection, verification, unified benchmarking, statistical validation, and documentation updates in one automated flow.

---

## Part B: Commercial Positioning and Disclosures

### 1. Document Disclosures
*   **Modified [`benchmarks/reports/PHASE6_INVESTOR_SUMMARY.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/reports/PHASE6_INVESTOR_SUMMARY.md):** Added financial simulation warnings to prevent speculative valuations from being presented as active revenues.
*   **Modified [`benchmarks/reports/PHASE7_EXECUTIVE_SUMMARY.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/reports/PHASE7_EXECUTIVE_SUMMARY.md):** Added simulation warnings to the flywheel and long-term enterprise valuation projections.
*   **Modified [`docs/QADE_GRANT_DOSSIER.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/QADE_GRANT_DOSSIER.md):** Added the standard disclosure banner to protect Cdti/Enisa grant applications.

### 2. Disclosures and Sync
*   **Created [`quantum/BENCHMARK_DISCLOSURE.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/BENCHMARK_DISCLOSURE.md):** Detailed technical disclosure explaining compiler policies, logical vs physical fidelity constraints, and simulated financial metrics.
*   **Created [`quantum/benchmarks/update_docs_from_results.py`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/benchmarks/update_docs_from_results.py):** Dynamically updates [`README.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/README.md), [`quantum/README.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/README.md), and [`quantum/BENCHMARK_DISCLOSURE.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/BENCHMARK_DISCLOSURE.md) with updated leaderboards and statistical results from the latest benchmark run.
*   **Modified [`README.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/README.md):** Rewrote the results summary to focus on QADE's real value (fidelity-aware qubit placement rather than gate count reduction) and reference the strict benchmarking rules.
