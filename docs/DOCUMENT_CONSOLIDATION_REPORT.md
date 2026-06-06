# Document Consolidation Report

Generated: 2026-06-06

## Summary

The repository contains **657 Markdown documents** after excluding dependency/cache folders. Documentation is valuable but fragmented. The main issues are duplicated QADE reports in both docs/ and benchmarks/reports/, root-level report files mixed with source folders, and historical satellite baselines that should be archived rather than presented as current state.

## Canonical Documentation Policy

| Document Class | Canonical Location | Notes |
| --- | --- | --- |
| Public cross-domain reports | docs/ | Audits, dossiers, investor summaries, grant readiness |
| Generated QADE raw reports | benchmarks/reports/ | Keep as generator output; mirror only summaries to docs/ |
| Generated QADE data | benchmarks/results/ | Canonical CSV/JSON result store |
| Domain README files | Domain root | Must be current and independently useful |
| Satellite verification baselines | satelite/VERIFICATION_BASELINE_v4/ plus archive | Keep newest active baseline; archive older baselines |
| Physics experiment outputs | physics/artifacts/ or docs/physics/ | Move root generated files in migration phase |

## Consolidation Decisions

| Document / Group | Decision | Justification |
| --- | --- | --- |
| README.md | keep | New ecosystem landing page |
| README_AUDIT.md | archive | Historical README audit superseded by current audit |
| README_REWRITTEN.md | archive | Historical draft superseded by root README |
| docs/PHASE3-7 reports | keep | Public QADE summaries |
| benchmarks/reports/PHASE3-7 reports | keep generated | Raw generated benchmark outputs |
| benchmarks/results/*.csv/json | keep generated | Canonical result store |
| satelite/VERIFICATION_BASELINE_v1-v3 | archive | Historical baselines |
| satelite/VERIFICATION_BASELINE_v4 | keep | Most recent active satellite verification baseline |
| root *_report.json | merge/archive | Generated research outputs should move under owner domain artifacts |
| dashboard/.next/* | delete after approval | Generated build output |
| dashboard/node_modules/* | delete after approval | Installable dependency folder |

## Duplicated Report Groups

| Duplicate Group | Recommendation |
| --- | --- |
| docs/PHASE3_HARDWARE_AWARE_RESULTS.csv; benchmarks/results/PHASE3_HARDWARE_AWARE_RESULTS.csv; benchmarks/results/COMPLETE_PHASE3_RESULTS.csv | Merge or keep one generated plus one public summary |
| docs/PHASE3_INVESTOR_SUMMARY.md; benchmarks/reports/PHASE3_INVESTOR_SUMMARY.md; benchmarks/reports/investor_executive_summary.md | Merge or keep one generated plus one public summary |
| docs/PHASE5_MOTIF_DATABASE.csv; benchmarks/results/PHASE5_MOTIF_DATABASE.csv; benchmarks/results/QADE_MOTIF_DATABASE.csv | Merge or keep one generated plus one public summary |
| docs/PHASE5_MOTIF_DATABASE.json; benchmarks/results/PHASE5_MOTIF_DATABASE.json; benchmarks/results/QADE_MOTIF_DATABASE.json | Merge or keep one generated plus one public summary |
| satelite/VERIFICATION_BASELINE_v1-v4 repeated baseline reports | Merge or keep one generated plus one public summary |
| dashboard/.next generated route manifests and RSC files | Merge or keep one generated plus one public summary |
| dashboard/public/artifacts and satelite/dashboard/public/artifacts mirrored history files | Merge or keep one generated plus one public summary |

## Outdated or Overlapping Documents

- Old root README language described quantum and mathematics as future placeholders. This is no longer true for QADE.
- Several PHASE documents overlap between docs/ and benchmarks/reports/.
- Satellite baselines v1-v3 are valuable traceability assets but should not be presented as current state.
- Root-level generated JSON reports make repository purpose harder to read and should be archived by domain.
