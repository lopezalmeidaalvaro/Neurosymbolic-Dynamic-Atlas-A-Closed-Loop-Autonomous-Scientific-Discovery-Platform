# VERIFICATION BASELINE v4 - Configuration Manifest

**Document ID**: AST-CM-BASELINE-v4-MANIFEST  
**Authority**: Configuration Management Lead / CDR Closure Board Chair  
**Baseline Date**: 2026-05-31  
**Baseline Frozen**: YES - immutable historical baseline  

---

## 1. Configuration Identification

| Field | Value |
|---|---|
| Baseline Version | `v4` |
| Repository | `autonomous-spacecraft-thermal-os` |
| Branch | `master` |
| Commit Hash (Full) | `3b72ba8773423d9886cf0cf85756ad429caec56f` |
| Commit Hash (Short) | `3b72ba8` |
| Worktree State At Freeze | `DIRTY` |
| Classification | `READY_FOR_CDR` |
| Freeze Rule | Future changes must create `VERIFICATION_BASELINE_v5`; v4 must not be modified in place. |

Note: the worktree includes uncommitted/generated verification evidence at freeze time. File-level SHA-256 hashes are the controlling integrity mechanism for this baseline.

---

## 2. Verification Summary

| Metric | Value |
|---|---:|
| Total Requirements | 18 |
| Requirements PASS | 18 |
| Requirements FAIL | 0 |
| Requirements UNKNOWN | 0 |
| Total Tests | 335 |
| Tests Passed | 335 |
| Tests Failed | 0 |
| Total Pytest Warnings | 0 |
| PydanticDeprecatedSince20 Warnings | 0 |
| Global Coverage | 80.47210300429184% |
| Coverage Gate | PASS, >= 80% |
| Black Compliance | PASS, 100% |
| EKF Status | PASS |
| FDIR Status | PASS |
| HIL Status | PASS |
| Flight Heritage Status | PASS |

---

## 3. Action Closure Summary

| Action Item | Status | Closure Basis |
|---|:---:|---|
| `AI-CDR-01` | `CLOSED` | `python -m black --check .` returns zero differences. |
| `AI-CDR-02` | `CLOSED` | 335/335 tests pass; global coverage remains 80.47210300429184%. |
| `AI-CDR-03` | `CLOSED` | ISS, Starlink, and Sentinel-2 calibrated with worst post-calibration MAE 0.0621 C. |
| `AI-CDR-04` | `CLOSED` | All 18 Pydantic deprecated `example=` fields migrated; pytest warnings are 0. |
| `AI-CDR-05` | `CLOSED` | `VERIFICATION_BASELINE_v4` created, documented, hashed, and set read-only. |

Open CDR actions: **0**.

---

## 4. Risk Summary

| Risk ID | Status | Description |
|---|:---:|---|
| `RISK-HER-02` | `CLOSED` | Flight heritage calibration now satisfies MAE < 3.0 C for ISS, Starlink, and Sentinel-2. |

Open CDR-blocking risks: **0**.

---

## 5. Baseline Artifacts And SHA-256 Integrity Hashes

The table excludes `BASELINE_MANIFEST.md` itself. The manifest hash is recorded in `SHA256SUMS.txt`.

| # | Artifact | Size (bytes) | SHA-256 |
|---:|---|---:|---|
| 1 | `BASELINE_CERTIFICATE.md` | 776 | `f5f822385a87cac9f499f95f69da26e1859494465c440fa2809325235642ca00` |
| 2 | `black_compliance_report.md` | 1680 | `e6db9b22237e5e8660ba728324ae3b4a5c82d5052f17a2d147b8d0b85d377b99` |
| 3 | `cdr_action_item_status.md` | 990 | `6095b8d1ad80881af2b7916f609e16d0049badb19e7b4142d355ee81d8207557` |
| 4 | `cdr_final_review_board_report.md` | 3270 | `50182ee377211288701f9e7919b18b2af5e6913afc5b72f1ce15f3ccce19421f` |
| 5 | `CDR_STATUS.md` | 1355 | `2885572cef166881012a044b4666d19ee8ecdc8168c12bf023245f51fe7b2028` |
| 6 | `coverage_summary.json` | 66777 | `977197f8553bddf48086d07419343c18ce3746bec595179cdc42288ecec9faaa` |
| 7 | `ekf_residuals.csv` | 1861823 | `e7b24566e06c61a977508c78428672fbe27e8f19fed38c34327469b013855a23` |
| 8 | `ekf_validation_report.md` | 4020 | `7730bdd147a58bf09ffd536e461de2f9291bf7df94247b98344d650abff5e1c4` |
| 9 | `fail_resolution_report.md` | 10127 | `9f8da206d44a1e2adadb48a21fd6bc5eeca243e4885770828f5a45a5e2a9668c` |
| 10 | `flight_heritage_calibration_report.md` | 3391 | `83679cc98db0bdfe3eb2eab1c29462f840acbbb47ddca1c7fbf8d555acad1c1b` |
| 11 | `flight_heritage_calibration_results.csv` | 2304 | `94a4044e249399eb5773f5c18d4e15e914d75d0d7f389b8a8a6dcd4a698e17eb` |
| 12 | `FREEZE_POLICY.md` | 901 | `268c2cec4243dc8192b622ad6613f3f3d64eef53ebf148c4505a23df9d1dd252` |
| 13 | `heritage_comparison.csv` | 2304 | `94a4044e249399eb5773f5c18d4e15e914d75d0d7f389b8a8a6dcd4a698e17eb` |
| 14 | `heritage_report.md` | 5602 | `6788cf5e0b928f1cb9cb2bf2afe20c2cf0dacc7eb876fe67895c09b374949db1` |
| 15 | `pydantic_migration_report.md` | 1286 | `edca49e3a9b336d7ba5322da75fe2c73efe2f28cb9ccbc17cc505b8a5e3c968f` |
| 16 | `regression_campaign_report_v3.md` | 8721 | `0f1fb8418f88eceb73a69ff48b590d2c58956e80d25297940f79ef2ee462dd45` |
| 17 | `verification_dashboard.csv` | 4037 | `9a1b4472dcd6e2d4d3c7e30536185b01ce37ecffc3c5c15ef67ff5b7b72558d1` |
| 18 | `verification_dashboard.md` | 2909 | `2951ec0f482a3bebe2112cb4761785c35d912d4fddb80b0ee207c85a35886798` |

---

## 6. Baseline Decision

The board certifies `VERIFICATION_BASELINE_v4` as the CDR closure baseline and recommends AST-OS classification:

`READY_FOR_CDR`

