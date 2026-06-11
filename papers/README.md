# Papers

## Purpose

The papers folder stores manuscripts, PDFs, LaTeX sources, and publication assets for IA-MATEMATICA research lines.

## Architecture

```text
papers/
|-- system/
|-- qg/
|-- thermal/
```

## Folder Structure

Source code and durable documentation should remain separate from generated artifacts, caches, and transient experiment outputs. Domain-specific generated evidence should be placed in domain-local artifacts, results, or reports folders.

## Usage

```bash
# QADE
python run_all_benchmarks.py

# Dashboard
cd dashboard && npm run dev

# Satellite
cd satellite && pytest tests/ -q
```

## Dependencies

Dependencies are inherited from the owning domain manifest where available. Cross-domain imports are documented in docs/DOMAIN_DEPENDENCY_REPORT.md and should be reduced during migration.

## Status

Documented during the repository consolidation audit on 2026-06-06.

## Roadmap

- Make the domain independently installable and removable.
- Move generated outputs into domain-local artifact folders.
- Replace hidden cross-domain imports with explicit adapters or exported data contracts.
- Keep README, usage, dependencies, status, roadmap, and related documents current.

## Related Documents

- docs/REPOSITORY_AUDIT.md
- docs/DOMAIN_DEPENDENCY_REPORT.md
- docs/DOCUMENT_CONSOLIDATION_REPORT.md
