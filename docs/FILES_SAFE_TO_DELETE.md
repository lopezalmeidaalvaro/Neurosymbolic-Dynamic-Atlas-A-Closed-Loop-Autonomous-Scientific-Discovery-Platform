# Files Safe To Delete

No files were deleted. This report lists candidates only.

| Path / Pattern | Reason | Risk Level | Replacement | Why It Appears Unnecessary |
| --- | --- | --- | --- | --- |
| dashboard/.next/ | Generated Next.js build output | Low | npm run build | Recreated by Next.js and already ignored |
| dashboard/node_modules/ | Installed dependencies | Low | npm install | Recreated from package.json / lockfile |
| .pytest_cache/ | Pytest cache | Low | Recreated by pytest | Not product source |
| .ruff_cache/ | Ruff cache | Low | Recreated by ruff | Not product source |
| **/__pycache__/ | Python bytecode cache | Low | Recreated by Python | Not source |
| *.log | Runtime logs | Low-Medium | Re-run scripts | Usually transient; inspect if used as evidence |
| README_AUDIT.md | Superseded report | Low | docs/REPOSITORY_AUDIT.md | Historical draft superseded |
| README_REWRITTEN.md | Superseded draft | Low | README.md | New README is canonical |
| benchmark/README.md | Legacy benchmark note | Medium | benchmarks/ or domain docs | Folder conflicts with benchmarks/ naming |
| benchmarks/results/COMPLETE_PHASE3_RESULTS.csv | Duplicate result CSV | Medium | PHASE3_HARDWARE_AWARE_RESULTS.csv | Hash duplicate detected |
| docs/PHASE5_MOTIF_DATABASE.csv/json | Mirrored generated data | Medium | benchmarks/results/PHASE5_MOTIF_DATABASE.* | Canonical generated data should live in results |
| satellite/VERIFICATION_BASELINE_v1-v3/ | Historical baselines | Medium | v4 plus archive | Keep archived if audit traceability matters |
| root *_report.json files | Generated research outputs in root | Medium | docs/archive/ or owner artifacts | They clutter root |
| outputs/*/checkpoint.pkl | Evolution checkpoints | Medium | Archive or re-run | Useful only for exact run continuation |
| .agent/ | Local agent tooling | Low for publication | Local tool config | Already ignored and not product source |

Deletion should be done only after a clean clone can rebuild, rerun, or intentionally exclude the artifact.
