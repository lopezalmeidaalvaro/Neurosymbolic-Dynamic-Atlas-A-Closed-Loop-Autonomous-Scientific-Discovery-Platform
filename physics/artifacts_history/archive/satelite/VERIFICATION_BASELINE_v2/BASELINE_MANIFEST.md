# VERIFICATION BASELINE v2 — Configuration Manifest

**Document ID**: AST-CM-BASELINE-v2-MANIFEST  
**Authority**: Configuration Management Lead  
**Baseline Date**: 2026-05-31T16:00:00+01:00  
**Baseline Frozen**: YES — Immutable Baseline.

---

## 1. Configuration Identification

| Field | Value |
|---|---|
| **Baseline Version** | `v2` |
| **Baseline Date** | 2026-05-31 16:00 UTC+1 |
| **Repository** | `autonomous-spacecraft-thermal-os` |
| **Branch** | `main` |
| **Commit Hash (Full)** | `16269c8010c907d0f3a3028a4ecbd67b2db780c4` |
| **Commit Hash (Short)** | `16269c8` |

---

## 2. Verification Summary

| Metric | Count |
|---|---|
| **Total Requirements Audited** | **18** |
| **Requirements PASS** | **18** (100.0%) |
| **Requirements FAIL** | **0** (0.0%) |
| **Requirements UNKNOWN** | **0** (0.0%) |
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
| `RISK-HER-02` | — | **OPEN** | Historical comparison curves (ISS, Starlink, Sentinel-2) are uncalibrated, exhibiting errors $>100^\circ\text{C}$ due to initial parameter offsets. |

---

## 4. Baseline Artifacts & Integrity hashes

| # | Artifact | Description | Source | SHA-256 Integrity |
|---|---|---|---|---|
| 1 | `verification_dashboard.csv` | Config file | Baseline store | `9a1b4472dcd6e2d4d3c7e30536185b01ce37ecffc3c5c15ef67ff5b7b72558d1` |
| 2 | `verification_dashboard.md` | Config file | Baseline store | `2951ec0f482a3bebe2112cb4761785c35d912d4fddb80b0ee207c85a35886798` |
| 3 | `fail_resolution_report.md` | Config file | Baseline store | `9f8da206d44a1e2adadb48a21fd6bc5eeca243e4885770828f5a45a5e2a9668c` |
| 4 | `regression_campaign_report.md` | Config file | Baseline store | `0f1fb8418f88eceb73a69ff48b590d2c58956e80d25297940f79ef2ee462dd45` |
| 5 | `ekf_residuals.csv` | Config file | Baseline store | `e7b24566e06c61a977508c78428672fbe27e8f19fed38c34327469b013855a23` |
| 6 | `ekf_validation_report.md` | Config file | Baseline store | `7730bdd147a58bf09ffd536e461de2f9291bf7df94247b98344d650abff5e1c4` |

---

## 5. Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| Configuration Management Lead | _________________________ | 2026-05-31 | ☐ Pending |
| Lead Estimation & Navigation Engineer | _________________________ | 2026-05-31 | ☐ Pending |
