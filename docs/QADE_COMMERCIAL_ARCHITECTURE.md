# QADE Commercial Architecture -- Strategic Asset Audit

This document classifies all directories and modules in the repository into strategic commercialization categories for **QADE (Quantum Algorithm Discovery Engine)**.

---

## 1. Categorization Definitions

To focus engineering resources on productization, every module is classified into one of the following:

- **CORE_PRODUCT**: Core logic directly executed on the optimization API, compiler passes, pattern extraction, or layout mutation engine.
- **SUPPORTING_INFRASTRUCTURE**: Active utility code, simulators, database connections, and validation engines required to run or test the core product.
- **RESEARCH_BACKLOG**: Code representing future features, advanced symbolic regression, and algorithm search heuristics.
- **FROZEN**: Verified code maintained purely for regression testing. No active development allowed.
- **ARCHIVE_CANDIDATE**: Obsolete, mock, or simulated engines that should be moved out of the active codebase.

---

## 2. Global Asset Classification Matrix

| Directory / Module Path | Commercial Role | Direct API Value | Status / Recommendation |
| :--- | :--- | :---: | :--- |
| `quantum/optimization/` | **CORE_PRODUCT** | High | Active development. Transpilation & layout routing. |
| `quantum/evolution/` | **CORE_PRODUCT** | High | Active development. Gate sequence mutation. |
| `quantum/knowledge/` | **CORE_PRODUCT** | High | Active development. Pattern & motif extraction. |
| `quantum/graph/` | **CORE_PRODUCT** | High | Active development. Knowledge Graph caching structure. |
| `quantum/analysis/` | **SUPPORTING_INFRASTRUCTURE** | Medium | Active development. Predictive error heuristics. |
| `quantum/hardware/` | **SUPPORTING_INFRASTRUCTURE** | High | Active development. Real-device executor & calibration. |
| `quantum/simulation/` | **SUPPORTING_INFRASTRUCTURE** | Medium | Active development. Local cuQuantum simulation server. |
| `quantum/sandbox/` | **SUPPORTING_INFRASTRUCTURE** | High | Active development. Execution sandbox wrappers. |
| `quantum/reality_native/` | **RESEARCH_BACKLOG** | Medium | Maintain. Hardware-native theory discovery (Phase 3B/C). |
| `quantum/novel_physics/` | **RESEARCH_BACKLOG** | Medium | Maintain. Residual and impossible prediction checks. |
| `quantum/revision/` | **RESEARCH_BACKLOG** | Low | Maintain. Model surgery and failure attribution. |
| `quantum/theory/` | **FROZEN** | Low | Freeze. Basic algebraic model compression. |
| `quantum/evidence_audit/` | **FROZEN** | None | Freeze. DB sample sizing and consensus audits. |
| `quantum/external_audit/` | **ARCHIVE_CANDIDATE** | None | Archive. Review panel simulators. |
| `quantum/scientific_repro/` | **ARCHIVE_CANDIDATE** | None | Archive. GRADE score and consensus simulators. |

---

## 3. Product Action Plan

### 3.1. Main Core Product Team (Focus: 80% developer resources)
- ** transpile & Routing**: Integrate `pyzx_optimizer.py` and `evolution_engine.py` to form the core `/optimize` pipeline.
- **Pattern Caching**: Hook `quantum_pattern_extractor.py` directly into the database `knowledge_graph.py`. The compiler will query this graph to bypass genetic search.

### 3.2. Compiler Infrastructure Team (Focus: 20% developer resources)
- **Backend Sync**: Maintain `hardware_runner.py` and connect it to physical QPU calibration APIs to fetch error grids.
- **Explainability API**: Integrate `physics_baseline_library.py` and `impossible_prediction_generator.py` to output plain-text explanation strings indicating the physical reason (e.g. spectator crosstalk) behind the layout modifications.

### 3.3. Archive Execution
- **Move to Archive**: Create `quantum/archive/` and move the simulated reviewer panels (`quantum/scientific_reproduction/`, `quantum/external_audit/`) there. Disable their tests to accelerate standard test execution.
