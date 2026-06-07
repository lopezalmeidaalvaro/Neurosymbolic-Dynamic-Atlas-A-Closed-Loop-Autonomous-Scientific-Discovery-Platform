# QADE Documentation Index

Generated: 2026-06-06

This folder is the curated public entry point for Quantum Algorithm Discovery Engine (QADE) due diligence. Raw benchmark outputs remain in `benchmarks/results/` and `benchmarks/reports/`; this index links to the canonical evidence without moving historical files.

## Start Here

| Document | Purpose |
| --- | --- |
| [QADE Data Room Index](../QADE_DATA_ROOM_INDEX.md) | Investor and grant reading order |
| [QADE Technical Dossier](../QADE_TECHNICAL_DOSSIER.md) | Technical architecture and evidence |
| [QADE Grant Dossier](../QADE_GRANT_DOSSIER.md) | Funding narrative and commercialization case |
| [QADE IP Asset Register](../QADE_IP_ASSET_REGISTER.md) | Proprietary motif and platform assets |
| [QADE IP Protection Strategy](../QADE_IP_PROTECTION_STRATEGY.md) | Patent, trade-secret, and licensing boundaries |

## Phase Evidence

| Phase | Evidence |
| --- | --- |
| Phase III | [Hardware-Aware Report](../PHASE3_HARDWARE_AWARE_REPORT.md) |
| Phase IV | [Competitive Advantage Report](../PHASE4_COMPETITIVE_ADVANTAGE_REPORT.md) |
| Phase V | [IP Report](../PHASE5_IP_REPORT.md) |
| Phase VI | [Investor Summary](../PHASE6_INVESTOR_SUMMARY.md) |
| Phase VII | [Executive Summary](../PHASE7_EXECUTIVE_SUMMARY.md) |

## Restructure Evidence

| Report | Purpose |
| --- | --- |
| [QADE Extraction Progress](../QADE_EXTRACTION_PROGRESS_REPORT.md) | Decoupling progress and remaining extraction blockers |
| [QADE Standalone Readiness](../QADE_STANDALONE_READINESS_REPORT.md) | Install/test/benchmark readiness |
| [Benchmark Restructure](../BENCHMARK_RESTRUCTURE_REPORT.md) | QADE-owned benchmark CLI and compatibility shims |
| [Data Room Validation](../DATA_ROOM_VALIDATION_REPORT.md) | Data-room path and evidence validation |
| [Restructure Completion](../PHASE_RESTRUCTURE_COMPLETION_REPORT.md) | Final execution summary |

## One-Command Benchmark

```bash
python -m quantum.benchmarks.run_all
```

Compatibility entrypoints remain available at `run_all_benchmarks.py` and `benchmarks/run_all_benchmarks.py`.
