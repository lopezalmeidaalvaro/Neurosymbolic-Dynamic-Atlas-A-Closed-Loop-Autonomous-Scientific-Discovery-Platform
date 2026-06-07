# Artifact Governance Report

Generated: 2026-06-06

## Scope

This report classifies generated, stale, and duplicate artifacts using the existing machine-readable inventories. No files were deleted, moved, or renamed during this step.

## Inventory Inputs

| Inventory | Rows |
| --- | ---: |
| GENERATED_ARTIFACT_INVENTORY.csv | 2058 |
| STALE_FILE_INVENTORY.csv | 1307 |
| DUPLICATE_FILE_INVENTORY.csv | 1386 |
| Unique candidate paths | 2571 |

## Disposition Summary

| Disposition | Count | Meaning |
| --- | ---: | --- |
| KEEP | 101 | Active evidence, benchmark result, report, or verification baseline |
| ARCHIVE | 74 | Historical generated evidence that may be moved later with a manifest |
| DELETE_CANDIDATE | 1266 | Cache/build/transient output; deletion still requires owner review |
| REVIEW | 1130 | Requires manual owner decision before any physical change |

## Governance Rules

- Keep benchmark CSVs, benchmark reports, phase reports, data-room documents, and active verification baselines.
- Archive historical root-level generated reports only after a manifest records original path, new path, checksum, and downstream references.
- Treat caches, build outputs, and bytecode as delete candidates, but do not delete them as part of this execution.
- Preserve compatibility copies or shims for one release when scripts may rely on old paths.

## Machine-Readable Output

The full classification is stored in [ARTIFACT_GOVERNANCE_CLASSIFICATION.csv](ARTIFACT_GOVERNANCE_CLASSIFICATION.csv).

## Recommendation

Proceed with archive moves only after a branch, checksums, and path-reference validation are prepared. No delete operation is recommended in the current working tree.
