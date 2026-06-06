# Repository Migration Plan

## Rule

No move, rename, merge, or delete operation should occur until this plan is reviewed. This document is a non-destructive migration plan.

## Target Structure

```text
README.md
.gitignore
.github/
.agent/
dashboard/
physics/
mathematics/
quantum/
satellite/
papers/
docs/
```

## Phase A: Documentation Freeze

- Keep the new root README as the ecosystem landing page.
- Use docs/REPOSITORY_AUDIT.md as the audit baseline.
- Use docs/DOMAIN_DEPENDENCY_REPORT.md as the dependency baseline.

## Phase B: Domain Isolation

- Refactor core/orchestration/scientist_factory.py so it does not import physics directly.
- Replace direct physics -> satellite and satelite -> physics imports with adapter protocols.
- Create domain-local dependency manifests.

## Phase C: Satellite Rename

- Rename satelite/ to satellite/ in a branch.
- Rewrite imports and test package resolution.
- Preserve verification baselines with a manifest.

## Phase D: Benchmark Relocation

- Move QADE benchmark runner into quantum/benchmarks or expose a CLI.
- Keep generated CSV/Markdown under benchmarks/results only if benchmarks/ remains a QADE-owned output folder.

## Phase E: Artifact Cleanup

- Remove caches/build outputs after approval.
- Archive stale root reports into docs/archive/ or owning domain folders.
- Keep only reproducible, cited artifacts in the public tree.
