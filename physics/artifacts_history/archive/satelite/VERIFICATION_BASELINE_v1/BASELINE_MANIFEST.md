# VERIFICATION BASELINE v1 — Configuration Manifest

**Document ID**: AST-CM-BASELINE-v1-MANIFEST  
**Authority**: Configuration Management Lead  
**Baseline Date**: 2026-05-30T15:00:00+01:00  
**Baseline Frozen**: YES — This baseline is immutable. All future changes require `VERIFICATION_BASELINE_v2`.

---

## 1. Configuration Identification

| Field | Value |
|---|---|
| **Baseline Version** | `v1` |
| **Baseline Date** | 2026-05-30 15:00 UTC+1 |
| **Repository** | `autonomous-spacecraft-thermal-os` |
| **Branch** | `main` |
| **Commit Hash (Full)** | `16269c8010c907d0f3a3028a4ecbd67b2db780c4` |
| **Commit Hash (Short)** | `16269c8` |
| **Commit Message** | `feat: Enhance thermal API and streaming modules with SQLite integration and timezone support` |
| **Commit Date** | 2026-05-30 13:11:33 +0100 |
| **Uncommitted Changes** | 251 files (Black formatting + parametric corrections pending commit) |

---

## 2. Verification Summary

| Metric | Count |
|---|---|
| **Total Requirements Audited** | **18** |
| **Requirements PASS** | **17** (94.4%) |
| **Requirements FAIL** | **0** (0.0%) |
| **Requirements UNKNOWN** | **1** (5.6%) |
| **Total Unit Tests** | **29** |
| **Tests Passed** | **29** |
| **Tests Failed** | **0** |
| **Flake8 Critical Errors** | **0** |
| **Black Format Compliance** | **116/120** (96.7%) |
| **Destructive Scenarios Executed** | **10/10** |
| **Destructive Recoveries** | **5/5** |

---

## 3. Open Risks

| Risk ID | Requirement | Status | Description |
|---|---|---|---|
| `RISK-EKF-01` | `REQ-EKF-01` | **OPEN_RISK** | Extended Kalman Filter convergence accuracy (`<= 2.0°C`) cannot be verified — no standalone EKF residual CSV log exists. Kalman variables are computed inline without persistent output. |

---

## 4. Baseline Artifacts

| # | Artifact | Description | Source | SHA-256 Integrity |
|---|---|---|---|---|
| 1 | `verification_dashboard.csv` | Master requirements ledger with 18 requirements (17 PASS, 0 FAIL, 1 UNKNOWN) | Repository root | Frozen at baseline creation |
| 2 | `verification_dashboard.md` | Human-readable dashboard with status scorecard | Artifact store | Frozen at baseline creation |
| 3 | `fail_resolution_report.md` | Chief Systems Engineer resolution report for 4 corrected FAIL requirements | Artifact store | Frozen at baseline creation |
| 4 | `regression_campaign_report.md` | Post-correction regression campaign (pytest, flake8, black, destructive) | Artifact store | Frozen at baseline creation |
| 5 | `BASELINE_MANIFEST.md` | This document | Generated at baseline creation | — |
| 6 | `ACCEPTANCE_STATUS.md` | Readiness classification and gate assessment | Generated at baseline creation | — |

---

## 5. Traceability to Source Evidence

All metrics in this baseline are dynamically computed from raw CSV telemetry files. No hardcoded or manually entered values.

| Requirement | Evidence File | Column / Formula |
|---|---|---|
| REQ-THERM-01 | `datasets/orbital_simulation_results.csv` | `max(T_CPU_C)` = 27.07°C |
| REQ-THERM-02 | `datasets/orbital_simulation_results.csv` | `min(T_Battery_C)` = 5.63°C, `max(T_Battery_C)` = 22.39°C |
| REQ-THERM-03 | `datasets/orbital_simulation_results.csv` | `max(row_max - row_min)` over internal bus nodes = 16.09°C |
| REQ-HIL-01 | `datasets/hil_results.csv` | `mean(abs(error))` = 2.71°C |
| REQ-FEM-01..04 | `datasets/fem_correlation_results.csv` | RMSE, MAE, R², Speedup columns |
| REQ-LAT-01..03 | `latency_breakdown.csv` | `internal_ms` column |
| REQ-ROB-01..02 | `destructive_campaign_results.csv` | SCEN-004, SCEN-010 recovery status |

---

## 6. Freeze Policy

> [!CAUTION]
> **THIS BASELINE IS IMMUTABLE.**
>
> Effective 2026-05-30T15:00:00+01:00, the following rules are in force:
>
> 1. **No modification** of any file inside `VERIFICATION_BASELINE_v1/`.
> 2. **No overwriting** of historical metrics, results, or evidence artifacts.
> 3. **No alteration** of requirement statuses without creating a new baseline.
> 4. All future verification activities must create `VERIFICATION_BASELINE_v2/` (or higher).
> 5. This baseline serves as the **permanent historical record** for the current verification state of AST-OS.

---

## 7. Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| Configuration Management Lead | _________________________ | 2026-05-30 | ☐ Pending |
| Verification & Validation Lead | _________________________ | __________ | ☐ Pending |
| Chief Systems Engineer | _________________________ | __________ | ☐ Pending |
| Project Manager | _________________________ | __________ | ☐ Pending |
