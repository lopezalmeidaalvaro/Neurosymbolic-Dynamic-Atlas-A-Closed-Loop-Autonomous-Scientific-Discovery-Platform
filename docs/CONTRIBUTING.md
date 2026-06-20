# Contributing Guide

This monorepo accepts contributions adhering to strict architectural isolation and governance rules.

## Core Directives

1. **Domain Isolation**:
   - Do not cross-import modules between domains directly (e.g., `physics/` importing from `quantum/`).
   - All shared logic must go through `core/` abstractions or explicit service adapters.
2. **Clean Root Policy**:
   - Any new file or folder in the repository root must be whitelisted in `docs/ROOT_GOVERNANCE.md`.
   - Never add generated databases, `.json` or `.csv` files to the root.
3. **Commit Mappings**:
   - Follow semantic commit messages: `feat:`, `fix:`, `docs:`, `science:`, `refactor:`.
   - Ensure the automated pre-commit hooks and tests run successfully before making a PR.
