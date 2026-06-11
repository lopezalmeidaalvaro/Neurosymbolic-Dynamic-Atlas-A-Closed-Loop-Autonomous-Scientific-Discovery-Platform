# Phase VIII: Dependency Audit Report

This report presents a recursive import scan across the `quantum/`, `benchmarks/`, and `tests/` directories to map coupling to other domains (`physics`, `satellite`, `dashboard`, `core`) and specify isolation remedies.

---

## 1. Domain Coupling Summary

| Source Path | Imports to `physics/` | Imports to `satellite/` | Imports to `dashboard/` | Imports to `core/` | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `quantum/` (Core Logic) | None | None | None | None | **Fully Isolated** |
| `quantum/benchmarks/` | None | None | None | `core.observability` | **Observable Coupling** |
| `quantum/factories/` | None | None | None | `core.orchestration` | **Interface Coupling** |
| `quantum/interfaces/` | None | None | None | `core.abstractions` | **Abstraction Coupling** |
| `quantum/tests/` | `physics.core` (1 import) | None | None | `core.abstractions`, `core.orchestration` | **Test Verification Coupling** |
| `benchmarks/` (Root) | None | None | None | None | **Isolated** |
| `tests/` (Root) | None | None | None | None | **Isolated** |

---

## 2. Detailed Import Analysis

### 2.1 Coupling to `physics/`
*   **Import Reference**: `from physics.core.autonomous.autonomous_scientist import AutonomousScientist`
*   **File Location**: [test_quantum_domain.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/tests/test_quantum_domain.py#L13)
*   **Impact**: Non-blocking. This import is restricted exclusively to a unit test verifying integration of the quantum domain scientist under the root orchestration engine. It does not couple QADE's production compilation logic to physics.
*   **Remedy**: Acknowledge as legacy/integration test coupling; no refactoring required for QADE package standalone usage.

### 2.2 Coupling to `satellite/` / `satellite/`
*   **Import Reference**: None.
*   **Impact**: 100% isolated. No module under `quantum/`, `benchmarks/`, or `tests/` references satellite components.

### 2.3 Coupling to `dashboard/`
*   **Import Reference**: None.
*   **Impact**: 100% isolated. No module references the user interface dashboard directory directly.

### 2.4 Coupling to `core/`
The package `quantum/` depends on `core/` for abstractions and telemetry:
1.  **Abstractions**: `quantum/interfaces/__init__.py` imports base classes:
    *   `core.abstractions.base_critic.BaseCritic`
    *   `core.abstractions.base_hypothesis_generator.BaseHypothesisGenerator`
    *   `core.abstractions.base_memory.BaseMemory`
    *   `core.abstractions.base_sandbox.BaseSandbox`
2.  **Container & Factory**: `quantum/factories/quantum_factory.py` imports `ScientificContainer`.
3.  **Observability/Telemetry**: `quantum/benchmarks/` scripts import `ExperimentLogger`, `DocumentationManager`, and `KnowledgeDashboard` from `core.observability` to log discovery runs.

---

## 3. Coupling Remedies & Package Isolation Strategy

To ensure QADE can be installed and executed as a standalone quantum optimization package (`qade`) without requiring the full research monorepo `core` module:
*   **QADE Core Stub (`quantum/core_stub.py`)**: We will introduce a compatibility stub that mocks `ExperimentLogger`, `DocumentationManager`, and `ScientificContainer` if they are not importable. This allows the package to operate gracefully with local logging fallbacks.
*   **Optional Integration**: When QADE is executed within the full monorepo, it dynamically detects and binds to the real `core` module to log telemetry.
