# VERIFICATION BASELINE v3 - Configuration Manifest

**Document ID**: AST-CM-BASELINE-v3-MANIFEST  
**Authority**: Configuration Management Lead / CDR Closure Board Chair  
**Baseline Date**: 2026-05-31T14:41:02+01:00  
**Baseline Frozen**: YES - immutable historical baseline  

---

## 1. Configuration Identification

| Field | Value |
|---|---|
| Baseline Version | `v3` |
| Repository | `autonomous-spacecraft-thermal-os` |
| Branch | `master` |
| Commit Hash (Full) | `3b72ba8773423d9886cf0cf85756ad429caec56f` |
| Commit Hash (Short) | `3b72ba8` |
| Worktree State At Freeze | `DIRTY` |
| Freeze Rule | Future changes must create `VERIFICATION_BASELINE_v4`; v3 must not be modified in place. |

Note: the repository had uncommitted/generated evidence at freeze time. Baseline integrity is therefore governed by the file-level SHA-256 hashes below, not by commit hash alone.

---

## 2. Compliance Summary

| Metric | Value |
|---|---:|
| Total Requirements | 18 |
| Requirements PASS | 18 |
| Requirements FAIL | 0 |
| Requirements UNKNOWN | 0 |
| Total Tests | 335 |
| Tests Passed | 335 |
| Tests Failed | 0 |
| Pytest Warnings | 18 |
| Global Coverage | 80.47210300429184% |
| Coverage Gate | PASS, >= 80% |
| EKF Status | PASS |
| FDIR Status | PASS |
| HIL Status | PASS |
| Formal CDR Classification | `CDR_WITH_ACTIONS` |

---

## 3. CDR Action Closure Summary

| Action Item | Status | Closure Basis |
|---|:---:|---|
| `AI-CDR-01` | `OPEN` | Black formatting gate failed; 13 files would be reformatted. |
| `AI-CDR-02` | `CLOSED` | Coverage campaign passed: 335/335 tests, 80.47210300429184% global coverage. |
| `AI-CDR-03` | `OPEN` | Flight heritage calibration remains unverified; `RISK-HER-02` remains open. |
| `AI-CDR-04` | `OPEN` | 18 Pydantic V2 deprecation warnings remain. |
| `AI-CDR-05` | `CLOSED` | `VERIFICATION_BASELINE_v3` created, documented, hashed, and set read-only. |

Open CDR actions: 3 (`AI-CDR-01`, `AI-CDR-03`, `AI-CDR-04`).  
Closed CDR actions: 2 (`AI-CDR-02`, `AI-CDR-05`).

---

## 4. Open Risks

| Risk ID | Status | Description | Blocking Impact |
|---|:---:|---|---|
| `RISK-HER-02` | `OPEN` | Historical comparison curves for Starlink/Sentinel-2 remain uncalibrated, with documented >100 C class offsets. | Blocks `READY_FOR_CDR` and `READY_FOR_FRR`; keeps `AI-CDR-03` open. |

---

## 5. v2 vs v3 Delta

| Area | v2 | v3 | Delta |
|---|---:|---:|---:|
| Requirements PASS | 18 | 18 | 0 |
| Requirements FAIL | 0 | 0 | 0 |
| Requirements UNKNOWN | 0 | 0 | 0 |
| Tests Passed | 29 | 335 | +306 |
| Global Coverage | Not frozen as passing evidence; post-v2 audit was 48% | 80.47210300429184% | Gate met |
| Open Risks | 1 | 1 | 0 |
| Closed CDR Actions | 0 | 2 | +2 |
| Open CDR Actions | 5 | 3 | -2 |

Full comparison is frozen in `CDR_V2_V3_COMPARISON.md`.

---

## 6. Baseline Artifacts And SHA-256 Integrity Hashes

The table excludes `BASELINE_MANIFEST.md` itself. The manifest hash is recorded in `SHA256SUMS.txt`.

| # | Artifact | Size (bytes) | SHA-256 |
|---:|---|---:|---|
| 1 | `cdr_action_item_status.md` | 2805 | `68db03d113055d0b1fc5e62769a19432c9c7e086052e8d3d9d46f50462330879` |
| 2 | `CDR_READINESS_REVIEW.md` | 10018 | `591be7ab5cc30dbf4ac594b2b9e7e16f1791b516c02ae447dbd141699ade739a` |
| 3 | `CDR_STATUS.md` | 2430 | `d5ef848ae02143b82657a5a88475ba60422066b30d4195564c6ba209647f31a6` |
| 4 | `CDR_V2_V3_COMPARISON.md` | 2475 | `7e72e4b02c47540f27a5ee3d029c8c81faa6eb6b5f7c18279b138031f38ad40c` |
| 5 | `coverage_report.md` | 2900 | `fda8e624c529ddd59efa4b8c8c925c16c3d5d40c4ecfbc00250db950598be823` |
| 6 | `coverage_summary.json` | 66777 | `544f3f74a5bc7e8656a75b3cb846e942a0cc20125d752c80986f7d9e79f98460` |
| 7 | `ekf_residuals.csv` | 1861823 | `e7b24566e06c61a977508c78428672fbe27e8f19fed38c34327469b013855a23` |
| 8 | `ekf_validation_report.md` | 4020 | `7730bdd147a58bf09ffd536e461de2f9291bf7df94247b98344d650abff5e1c4` |
| 9 | `fail_resolution_report.md` | 10127 | `9f8da206d44a1e2adadb48a21fd6bc5eeca243e4885770828f5a45a5e2a9668c` |
| 10 | `FREEZE_POLICY.md` | 1038 | `4b65e08836f3d3a38b400a448679f0becd4fa60810aff643ac112a0a5ca1d4b5` |
| 11 | `regression_campaign_report.md` | 8721 | `0f1fb8418f88eceb73a69ff48b590d2c58956e80d25297940f79ef2ee462dd45` |
| 12 | `verification_dashboard.csv` | 4037 | `9a1b4472dcd6e2d4d3c7e30536185b01ce37ecffc3c5c15ef67ff5b7b72558d1` |
| 13 | `verification_dashboard.md` | 2909 | `2951ec0f482a3bebe2112cb4761785c35d912d4fddb80b0ee207c85a35886798` |

---

## 7. Freeze Declaration

`VERIFICATION_BASELINE_v3` is frozen as read-only evidence. Historical modification is prohibited.

Any subsequent update, correction, additional evidence, action closure, formatting change, calibration result, or hash refresh must be performed in a new directory:

`VERIFICATION_BASELINE_v4`

