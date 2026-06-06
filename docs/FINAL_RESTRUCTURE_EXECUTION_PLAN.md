# Final Restructure Execution Plan

Generated: 2026-06-06

## Operating Rule

This is an execution plan only. No destructive changes are authorized by this document. File deletion, physical moves, and folder renames must be performed in a separate branch after tests and rollback points are confirmed.

## Preconditions

- Preserve current functionality of `run_all_benchmarks.py`, `benchmarks/run_all_benchmarks.py`, domain tests, and dashboard startup.
- Keep `docs/REPOSITORY_AUDIT.md`, `docs/DOMAIN_DEPENDENCY_REPORT.md`, and machine-readable inventories as the baseline.
- Create a migration branch before any physical move or rename.

## Phase 1: Safe Moves

| Action | Rationale | Risks | Dependencies | Estimated Effort | Rollback Strategy |
| --- | --- | --- | --- | --- | --- |
| Move QADE benchmark orchestration behind a quantum-owned CLI wrapper while keeping root shim | Makes QADE extractable without breaking existing command | Duplicate entrypoints may drift | Current run_all_benchmarks.py and benchmarks/run_all_benchmarks.py | 1-2 days | Keep root shim that imports old runner; revert CLI wrapper only |
| Move root generated JSON/CSV reports into owner-domain archive folders | Reduces root clutter and improves due diligence readability | Some scripts may expect root output paths | GENERATED_ARTIFACT_INVENTORY.csv, DOCUMENT_INVENTORY.csv | 1 day inventory + 1 day path checks | Keep copies until path usage is verified |
| Move QADE public report mirrors into docs/qade/ or keep docs/ with index | Improves navigation and investor data-room clarity | Existing links may break | DOCUMENTATION_CONSOLIDATION_REPORT.md | 0.5-1 day | Use redirect/index links; revert by moving back |
| Move physics generated outputs into physics/artifacts/archive when uncited | Separates research source from evidence artifacts | May obscure historical context | DOCUMENT_INVENTORY.csv and generated artifact inventory | 1-2 days | Retain archive manifest and restore paths from manifest |

## Phase 2: Safe Renames

| Action | Rationale | Risks | Dependencies | Estimated Effort | Rollback Strategy |
| --- | --- | --- | --- | --- | --- |
| Rename satelite/ to satellite/ | Corrects public-facing spelling and aligns with target architecture | Internal imports use satellite.* while folder is satelite; path/package confusion likely | SATELLITE_RENAME_PLAN.md, satellite tests | 2-4 days | Git mv back to satelite/ and restore import map |
| Rename benchmark/ or merge it into benchmarks/ | Eliminates singular/plural ambiguity | Links may reference benchmark/README.md | DOCUMENTATION_CONSOLIDATION_REPORT.md | 0.5 day | Restore legacy README path |
| Rename root generated reports only through archive manifest | Improves organization | Scripts may write/read fixed names | Generated artifact inventory | 1 day | Keep compatibility copies for one release |

## Phase 3: Dependency Decoupling

| Action | Rationale | Risks | Dependencies | Estimated Effort | Rollback Strategy |
| --- | --- | --- | --- | --- | --- |
| Remove core -> physics reverse import in core/orchestration/scientist_factory.py | Shared core must not depend on a domain | Factory behavior may change | CORE_SPLIT_STRATEGY.md; domain registry tests | 1 day | Restore direct import and mark core non-extractable |
| Replace quantum -> core imports with ia_core package or quantum-local interfaces | QADE must become independently installable | Many test/import paths need updates | QADE_ISOLATION_REPORT.md | 2-5 days | Keep compatibility imports from core during transition |
| Replace satelite -> physics neurosymbolic imports with adapter/protocol | Satellite should be independently removable | PINN/Neural ODE training may need wrappers | SATELLITE_RENAME_PLAN.md and satellite tests | 3-5 days | Keep optional physics plugin fallback |
| Move tests that import physics from quantum into integration tests | QADE extraction should not require physics | Coverage may split across packages | IMPORT_GRAPH.csv | 0.5 day | Keep root integration test suite separate |

## Phase 4: Documentation Consolidation

| Action | Rationale | Risks | Dependencies | Estimated Effort | Rollback Strategy |
| --- | --- | --- | --- | --- | --- |
| Adopt docs/ as public canonical documentation root | Investor/grant navigation becomes predictable | Benchmark generated reports still need raw location | QADE_DATA_ROOM_INDEX.md | 0.5 day | Keep links to benchmarks/reports raw outputs |
| Keep benchmarks/reports as generated raw report store | Preserves reproducibility | Duplicate-looking docs remain | Benchmark runner behavior | No code if documented | N/A |
| Archive superseded README_AUDIT.md and README_REWRITTEN.md | Avoids outdated positioning | Historical context loss | DOCUMENTATION_CONSOLIDATION_REPORT.md | 0.25 day | Move back from archive |
| Add docs/qade/ index or investor-data-room landing page | Simplifies due diligence | Extra maintenance | QADE_DATA_ROOM_INDEX.md | 0.5 day | Remove index only |

## Phase 5: Artifact Consolidation

| Action | Rationale | Risks | Dependencies | Estimated Effort | Rollback Strategy |
| --- | --- | --- | --- | --- | --- |
| Classify generated artifacts as keep/archive/delete-candidate | Prevents accidental loss of evidence | Large inventory requires review | GENERATED_ARTIFACT_INVENTORY.csv, SAFE_DELETE_CANDIDATES.md | 1-2 days | No delete until reviewed |
| Keep latest satellite baseline active and archive older baselines | Reduces confusion about current status | Older baselines may matter for traceability | Satellite verification owner review | 1 day | Restore archive path |
| Separate dashboard build outputs from source | Professional repository hygiene | None if regenerated | package-lock.json, package.json | 0.5 day | npm install / npm run build |
| Create artifact manifest for any moved result | Reproducibility protection | Manifest maintenance | All inventories | 1 day | Use manifest to restore paths |

## Phase 6: Final Cleanup

| Action | Rationale | Risks | Dependencies | Estimated Effort | Rollback Strategy |
| --- | --- | --- | --- | --- | --- |
| Run full test suite by domain | Proves functionality preservation | Some legacy tests may be slow or environment-specific | Dependency manifests | 0.5-1 day | Fix regressions or revert last migration phase |
| Run QADE benchmark command after migration | Proves benchmark reproducibility | Optional compilers may be unavailable | QADE package and benchmark runner | 0.5 day | Fallback to current root runner |
| Run dashboard build and Playwright smoke tests | Proves frontend integrity | Node dependency/version issues | dashboard package files | 0.5-1 day | Revert dashboard path changes |
| Produce final migration report with changed paths | Audit trail for investors and future employees | None | All migration manifests | 0.5 day | N/A |

## Execution Recommendation

Do not start with folder renames. Start with dependency decoupling and compatibility wrappers, then move artifacts, then rename `satelite/` after the test surface is known.
