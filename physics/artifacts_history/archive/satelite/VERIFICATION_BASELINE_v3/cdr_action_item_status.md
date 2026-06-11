# Spacecraft Thermal OS (AST-OS) - CDR Action Item Status Ledger

**Document ID**: AST-CDR-AI-LEDGER-002  
**Authority**: Configuration Management Lead / CDR Closure Board Chair  
**Baseline**: `VERIFICATION_BASELINE_v3`  
**Date**: 2026-05-31T14:41:02+01:00  

---

## 1. Closure Board Classification

| Action Item ID | Target Subsystem | Priority | Closure Criterion | Status | Evidence |
|---|---|:---:|---|:---:|---|
| `AI-CDR-01` | Repository Style | HIGH | `black --check .` returns zero differences | `OPEN` | `python -m black --check .` reports 13 files would be reformatted. |
| `AI-CDR-02` | Test Framework | HIGH | `pytest --cov=satellite` global coverage >= 80% | `CLOSED` | 335/335 tests pass; global coverage is 80.47210300429184%. |
| `AI-CDR-03` | Thermal Physics | MEDIUM | Flight heritage correlation MAE < 3.0 C after Starlink/Sentinel-2 calibration | `OPEN` | `RISK-HER-02` remains open; heritage models remain uncalibrated with >100 C class errors documented. |
| `AI-CDR-04` | Embedded Code | LOW | Pydantic V2 `Field(example=...)` warnings eliminated | `OPEN` | Pytest emits 18 `PydanticDeprecatedSince20` warnings from `backend/thermal_api.py`. |
| `AI-CDR-05` | Config Control | HIGH | Create and freeze `VERIFICATION_BASELINE_v3` | `CLOSED` | `VERIFICATION_BASELINE_v3` created, hashed, documented, and set read-only. |

---

## 2. Board Findings

### `AI-CDR-01` - Repository Style

Status: `OPEN`

Verification command:

```bash
python -m black --check .
```

Result: non-zero exit. Black reported 13 files requiring reformatting, including new test modules and pre-existing source files. The action cannot be closed without changing source formatting.

### `AI-CDR-02` - Test Coverage

Status: `CLOSED`

Verification command:

```bash
pytest --cov=satellite --cov-report=term-missing --cov-report=json:coverage_summary.json --tb=short -q
```

Result: 335 passed, 0 failed, 18 warnings, global coverage 80.47210300429184%. The CDR gate of >= 80% is met.

### `AI-CDR-03` - Flight Heritage Calibration

Status: `OPEN`

The board found no evidence that the required Starlink/Sentinel-2 Nelder-Mead calibration sweep has been completed. Existing verification records still classify `flight_heritage_compare.py` as `NEEDS_CALIBRATION`, with documented Starlink and Sentinel-2 offsets above 100 C.

### `AI-CDR-04` - Pydantic Warning Cleanup

Status: `OPEN`

Pytest still emits 18 `PydanticDeprecatedSince20` warnings from `backend/thermal_api.py` lines 254-313. The migration to `json_schema_extra` is not complete.

### `AI-CDR-05` - Baseline v3 Configuration Control

Status: `CLOSED`

The v3 baseline has been created as a separate configuration item. Historical modification of v3 is prohibited by `FREEZE_POLICY.md`; any later change must create `VERIFICATION_BASELINE_v4`.

