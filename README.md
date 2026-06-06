# IA-MATEMATICA

IA-MATEMATICA is a multi-domain AI-for-science and deep-tech research portfolio. The repository combines quantum optimization, neurosymbolic physics, spacecraft thermal digital twins, mathematical formalization, scientific dashboards, and publication assets into one evolving technology ecosystem.

The current repository is not a single-purpose QADE repository. QADE is one major product line inside the broader IA-MATEMATICA ecosystem.

## Project Overview

The ecosystem develops software systems that discover, validate, optimize, and document scientific structure. Its main domains are:

- **Quantum:** Quantum Algorithm Discovery Engine (QADE), a hardware-aware quantum optimization platform that can discover, validate, rank, store, reuse, and economically value optimization motifs.
- **Physics:** Neurosymbolic scientific discovery pipelines for chaotic dynamics, ECG transfer analysis, quantum-gravity-inspired audits, autonomous research loops, and empirical validation.
- **Satellite:** AST-OS, a spacecraft thermal digital twin and software-in-the-loop simulation stack for orbital thermal modeling, CAD thermal networks, HIL calibration, FDIR, and space protocol workflows. The current folder is named satelite/; the migration target is satellite/.
- **Mathematics:** A lightweight domain for symbolic discovery, theorem proving, and future formal verification.
- **Dashboard:** A Next.js observatory for scientific artifacts, telemetry, multilingual educational views, and experiment visualization.
- **Papers:** Manuscripts, PDFs, LaTeX sources, and publication-supporting documentation.

## Ecosystem Architecture

```text
ia-matematica-github/
|-- dashboard/        # Next.js scientific observatory and UI
|-- physics/          # Neurosymbolic physics and autonomous scientific discovery
|-- quantum/          # QADE quantum optimization, motif IP, and benchmark platform
|-- satelite/         # AST-OS spacecraft thermal digital twin; planned rename: satellite/
|-- mathematics/      # Symbolic mathematics and formal verification roadmap
|-- papers/           # Manuscripts and publication assets
|-- docs/             # Cross-domain audits, phase reports, dossiers, and grant materials
|-- benchmarks/       # QADE reproducible competitive benchmark suite
|-- core/             # Shared abstractions, domain registry, orchestration, observability
|-- tests/            # Root-level tests for shared infrastructure
```

## Current Status

| Domain | Status | Evidence |
| --- | --- | --- |
| Quantum / QADE | Active product-grade research platform | Hardware-aware optimization, competitive benchmarks, motif IP, economic valuation, platform moat reports |
| Physics | Active research system | Neurosymbolic discovery, ECG/chaos validation, QG audit reports, autonomous scientist modules |
| Satellite / AST-OS | Active engineering research system | Thermal solver, CAD voxelization, HIL, FDIR, verification baselines |
| Dashboard | Active frontend | Next.js app, telemetry hooks, artifact visualization, Playwright tests |
| Mathematics | Early roadmap | README and symbolic verification direction |
| Papers | Supporting documentation | System, thermal, and QG manuscript folders |

## Repository Structure

The target professional structure is:

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

The current repository still contains shared core/, root-level generated artifacts, and the misspelled satelite/ folder. These are documented in the migration plan rather than moved destructively.

## Core Technologies

Python, Qiskit, PyZX, optional TKET/BQSKit/Cirq integrations, NumPy, SciPy, pandas, scikit-learn, PyTorch, NetworkX, Next.js, React, TypeScript, Playwright, SQLite, CSV/JSON reproducibility artifacts, and LaTeX.

## Research Areas

Quantum compilation and circuit optimization; calibration-aware and coherence-aware routing; motif discovery and knowledge reuse; autonomous scientific discovery; chaotic dynamical systems; clinical ECG feature transfer; spacecraft thermal simulation; CAD-derived thermal networks; formal symbolic mathematics; scientific observability and reproducibility.

## Commercial Vision

IA-MATEMATICA is being organized as a deep-tech portfolio with multiple commercialization paths:

- QADE as a quantum optimization knowledge platform and licensable motif database.
- AST-OS as a spacecraft thermal digital-twin and software-in-the-loop validation stack.
- Physics discovery modules as AI4Science research tooling and validation infrastructure.
- Dashboard and documentation systems as enterprise-facing evidence and observability layers.

## Long-Term Roadmap

1. Isolate each domain as an independently installable project.
2. Rename satelite/ to satellite/ through a controlled migration.
3. Move generated artifacts into domain-local artifacts/, results/, and reports/ folders.
4. Convert QADE benchmarks into a one-command reproducibility package.
5. Add package metadata and dependency manifests per domain.
6. Prepare grant, investor, and enterprise technical dossiers from the consolidated documentation.

## Documentation Links

- [Repository Audit](docs/REPOSITORY_AUDIT.md)
- [Domain Dependency Report](docs/DOMAIN_DEPENDENCY_REPORT.md)
- [Repository Migration Plan](docs/REPOSITORY_MIGRATION_PLAN.md)
- [QADE Master Walkthrough](docs/QADE_MASTER_WALKTHROUGH.md)
- [QADE Technical Dossier](docs/QADE_TECHNICAL_DOSSIER.md)
- [QADE IP Asset Register](docs/QADE_IP_ASSET_REGISTER.md)
- [Deep Tech Grant Readiness](docs/DEEPTECH_GRANT_READINESS.md)
- [Document Consolidation Report](docs/DOCUMENT_CONSOLIDATION_REPORT.md)
- [Files Safe To Delete](docs/FILES_SAFE_TO_DELETE.md)

## Usage

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
python run_all_benchmarks.py
pytest quantum/tests/test_hardware_aware_optimization.py quantum/tests/test_qiskit_plugin.py -q
cd dashboard && npm install && npm run dev
```

## License

See [LICENSE](LICENSE). The current repository declares proprietary and confidential rights for Alvaro Lopez Almeida unless a separate written permission or license applies.

## Contributing

Treat each domain as an independent subsystem. Avoid cross-domain imports unless they pass through an explicit interface. Generated artifacts should be reproducible, documented, and placed in domain-local reports/results folders.
