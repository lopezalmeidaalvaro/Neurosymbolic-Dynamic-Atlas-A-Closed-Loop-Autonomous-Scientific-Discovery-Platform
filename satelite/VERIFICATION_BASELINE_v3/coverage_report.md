# Spacecraft Thermal OS (AST-OS) - Test Coverage Verification Report

**Document ID**: AST-VV-COV-002  
**Authority**: Verification & Validation Lead / CDR Closure Board  
**Baseline**: `VERIFICATION_BASELINE_v3`  
**Date**: 2026-05-31T14:41:02+01:00  

---

## 1. Executive Summary

The CDR Closure Board re-ran the coverage campaign against the current workspace before freezing `VERIFICATION_BASELINE_v3`.

Command executed:

```bash
pytest --cov=satellite --cov-report=term-missing --cov-report=json:coverage_summary.json --tb=short -q
```

Result:

| Metric | Value |
|---|---:|
| Tests collected/executed | 335 |
| Tests passed | 335 |
| Tests failed | 0 |
| Warnings | 18 |
| Statements | 1398 |
| Covered statements | 1125 |
| Missed statements | 273 |
| Global coverage | 80.47210300429184% |
| Coverage gate | >= 80% |
| Verdict | PASS |

Action item `AI-CDR-02` is therefore classified as `CLOSED`.

---

## 2. Module Coverage

| Module | Statements | Missed | Coverage | Status |
|---|---:|---:|---:|---|
| `satellite/autonomy/fault_recovery_ai.py` | 104 | 10 | 90% | PASS |
| `satellite/autonomy/mission_planner.py` | 147 | 58 | 61% | FAIL |
| `satellite/comms/protocol_test.py` | 61 | 14 | 77% | BORDERLINE |
| `satellite/comms/space_protocol_stack.py` | 77 | 0 | 100% | PASS |
| `satellite/run_thermal_pipeline.py` | 47 | 1 | 98% | PASS |
| `satellite/tests/test_satellite_twin.py` | 68 | 7 | 90% | PASS |
| `satellite/thermal/cad_thermal_importer.py` | 225 | 11 | 95% | PASS |
| `satellite/thermal/geometry_topology_optimizer.py` | 186 | 156 | 16% | FAIL |
| `satellite/thermal/material_library.py` | 63 | 7 | 89% | PASS |
| `satellite/thermal/multi_node_thermal_network.py` | 186 | 2 | 99% | PASS |
| `satellite/thermal/orbital_environment.py` | 125 | 4 | 97% | PASS |
| `satellite/thermal/uncertainty_engine.py` | 109 | 3 | 97% | PASS |
| **TOTAL** | **1398** | **273** | **80%** | **PASS** |

---

## 3. Residual Coverage Notes

The global gate is met, but two module-level weak spots remain for post-CDR hardening:

| Area | Coverage | Residual finding |
|---|---:|---|
| `satellite/thermal/geometry_topology_optimizer.py` | 16% | Pareto sweep and report generation paths remain weakly covered. |
| `satellite/autonomy/mission_planner.py` | 61% | Report generation and several schedule edge paths remain weakly covered. |

These do not block `AI-CDR-02` because the formal CDR action required global package coverage >= 80%, which is now satisfied.

---

## 4. Warning Ledger

All 18 warnings originate from Pydantic V2 deprecation notices in `backend/thermal_api.py` where `Field(..., example=...)` remains in use. This keeps `AI-CDR-04` classified as `OPEN`.

---

## 5. Evidence

Primary machine-readable evidence is frozen as:

- `coverage_summary.json`
- `.coverage` generated in the working directory before baseline freeze, with summarized results captured in this report

