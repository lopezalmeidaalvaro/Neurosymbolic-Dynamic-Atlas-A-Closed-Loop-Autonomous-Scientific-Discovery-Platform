# v2 vs v3 Baseline Comparison

**Document ID**: AST-CM-v2-v3-COMPARE  
**Authority**: Configuration Management Lead / CDR Closure Board  
**Date**: 2026-05-31T14:41:02+01:00  

---

## Summary

| Area | `VERIFICATION_BASELINE_v2` | `VERIFICATION_BASELINE_v3` | Delta |
|---|---:|---:|---|
| Total requirements | 18 | 18 | 0 |
| Requirements PASS | 18 | 18 | 0 |
| Requirements FAIL | 0 | 0 | 0 |
| Requirements UNKNOWN | 0 | 0 | 0 |
| Total tests | 29 | 335 | +306 |
| Tests passed | 29 | 335 | +306 |
| Tests failed | 0 | 0 | 0 |
| Global coverage | Not baselined in v2; post-v2 audit found 48% | 80.47210300429184% | Gate now met |
| Open risks | 1 | 1 | 0 |
| Closed CDR actions | 0/5 at readiness review | 2/5 | +2 |
| Open CDR actions | 5/5 at readiness review | 3/5 | -2 |

---

## Requirements

No requirements changed between v2 and v3. The dashboard remains 18 PASS, 0 FAIL, 0 UNKNOWN.

`REQ-EKF-01` remains PASS based on the nominal EKF evidence in `ekf_validation_report.md` and raw residual evidence in `ekf_residuals.csv`.

---

## Coverage

v2 did not freeze a successful coverage artifact. The later `coverage_report.md` identified 48% global coverage over 29 tests, below the 80% CDR gate.

v3 freezes a successful coverage campaign:

- 335 tests passed
- 1398 statements measured
- 1125 statements covered
- 273 statements missed
- 80.47210300429184% global statement coverage

This closes `AI-CDR-02`.

---

## Tests

The test campaign expanded from 29 tests in v2 to 335 tests in v3. The v3 run passed without failures.

Residual warning count remains 18, all Pydantic V2 deprecation warnings from `backend/thermal_api.py`; this keeps `AI-CDR-04` open.

---

## Risks

| Risk ID | v2 Status | v3 Status | Change |
|---|:---:|:---:|---|
| `RISK-HER-02` | OPEN | OPEN | No evidence of completed Starlink/Sentinel-2 calibration sweep. |

`RISK-EKF-01` remains closed by v2/v3 EKF evidence.

---

## CDR Actions

| Action | v2 Readiness Status | v3 Closure Status | Change |
|---|:---:|:---:|---|
| `AI-CDR-01` | OPEN | OPEN | Not closed; Black now reports 13 files requiring reformatting. |
| `AI-CDR-02` | IN_PROGRESS | CLOSED | Closed by 80.47210300429184% coverage and 335/335 passing tests. |
| `AI-CDR-03` | OPEN | OPEN | Not closed; flight heritage calibration remains unverified. |
| `AI-CDR-04` | OPEN | OPEN | Not closed; 18 Pydantic warnings remain. |
| `AI-CDR-05` | OPEN | CLOSED | Closed by creation and freeze of `VERIFICATION_BASELINE_v3`. |

