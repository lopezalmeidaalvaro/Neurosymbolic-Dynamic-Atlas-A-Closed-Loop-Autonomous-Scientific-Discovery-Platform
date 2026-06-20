# Monorepo Overview

This document provides a high-level guide to the multi-domain research repository.

## Directory Structure

The repository is organized under strict domain boundaries to maximize isolation and prevent cross-pollution:

- **`core/`**: Shared domain-agnostic abstractions, dynamic loading utilities, orchestration containers, and helper scripts.
- **`physics/`**: Neurosymbolic physical discovery, chaotic trajectory regression, and scientific validation engine.
- **`quantum/`**: QADE compilation, fidelity-aware placement, and physical QPU execution pipelines.
- **`satellite/`**: AST-OS digital twin and HIL/SIL thermal simulator.
- **`mathematics/`**: Prover tactic engines, auto-formalization orchestrator, and theorem verification.
- **`dashboard/`**: Next.js UI observatory.
- **`docs/`**: Global cross-domain documentation and policies.
- **`papers/`**: Publications and LaTeX assets.
- **`tests/`**: Integration test suites.

## Root Governance

The repository root is kept strictly clean. Only explicitly approved root folders and files are permitted. CI actions automatically reject any unlisted files or directories. Refer to [ROOT_GOVERNANCE.md](ROOT_GOVERNANCE.md) for details.
