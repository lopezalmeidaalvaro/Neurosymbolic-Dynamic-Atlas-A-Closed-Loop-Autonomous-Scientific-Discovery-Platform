# Satellite Rename Readiness Report

Generated: 2026-06-06

## Decision

Do not rename `satelite/` to `satellite/` in this execution. Readiness is not high enough for a safe physical folder rename without additional compatibility wrappers and test coverage.

## Evidence From Import Inventory

| Signal | Value |
| --- | ---: |
| Import edges from `satelite/` | 34 |
| Edges targeting `satellite` namespace | 22 |
| Edges targeting `physics` | 10 |
| Edges targeting `core` | 2 |

## Risk Assessment

| Risk | Level | Reason |
| --- | --- | --- |
| Package path confusion | High | Folder is `satelite/`, while many imports already target `satellite.*`. |
| Physics coupling | Medium | Satellite code still imports physics-facing components in the baseline graph. |
| Test coverage uncertainty | Medium | Rename needs import, CLI, and dashboard smoke validation. |
| Public spelling risk | High | The current spelling is not suitable for external-facing distribution. |

## Readiness Score

Rename readiness: **35/100**.

## Required Before Rename

1. Add a compatibility package or import alias so `satelite` and `satellite` both resolve during transition.
2. Replace physics dependencies with adapter/protocol interfaces or optional plugin loading.
3. Run satellite domain tests and dashboard import checks.
4. Use `git mv` on a migration branch and produce a path manifest.
5. Keep a rollback command and preserve old-path compatibility for one release.
