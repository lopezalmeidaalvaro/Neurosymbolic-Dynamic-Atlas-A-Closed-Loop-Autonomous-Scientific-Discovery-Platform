# Duplicate Consolidation Report

Generated: 2026-06-07

## Source Of Truth

Duplicate handling was executed from the existing governance classification and manifests, not from a new classification pass.

## Summary

| Category | Count |
| --- | ---: |
| Duplicate inventory rows reviewed | 1386 |
| Duplicate-classified files archived | 44 |
| Duplicate-classified files deleted | 540 |
| Duplicate-classified files retained as KEEP | 89 |
| Duplicate-classified files retained as REVIEW | 713 |

## Removed Duplicates

Deleted duplicate-classified files are recorded in [DELETE_MANIFEST.csv](DELETE_MANIFEST.csv). Most are rebuildable dashboard build artifacts, cache outputs, or generated duplicate files already classified as `DELETE_CANDIDATE`.

## Archived Duplicates

Archived duplicate-classified files are recorded in [ARCHIVE_MANIFEST.csv](ARCHIVE_MANIFEST.csv). These include older generated result files, backup CSVs, and historical satellite verification baseline documents.

## Retained Duplicates

Retained duplicate-classified files remain in place when their governance disposition was `KEEP` or `REVIEW`. This includes canonical benchmark reports/results and duplicate groups that still require owner review.

## Canonical Policy Applied

- Canonical benchmark reports remain under `benchmarks/reports/`.
- Canonical benchmark data remains under `benchmarks/results/`.
- Curated public QADE documentation remains under `docs/` and `docs/qade/`.
- Historical duplicates were archived instead of deleted when provenance mattered.

## Verdict

Duplicate consolidation was executed for files with existing `ARCHIVE` or `DELETE_CANDIDATE` disposition. Files marked `KEEP` or `REVIEW` were intentionally retained.
