# Documentation Consolidation Report

Generated: 2026-06-06

## Scope

Reviewed documentation from `docs/`, `benchmarks/reports/`, root reports, phase reports, investor summaries, audit documents, technical reports, research reports, IP reports, walkthroughs, and grant readiness documents using `DOCUMENT_INVENTORY.csv`.

Documents inventoried: **667**.

## Canonical Strategy

| Document Type | Canonical Location | Rule |
| --- | --- | --- |
| Investor / grant dossiers | docs/ | Public-facing, curated, stable |
| Technical dossiers | docs/ | Definitive reference documents |
| Generated benchmark reports | benchmarks/reports/ | Raw reproducibility outputs |
| Generated benchmark data | benchmarks/results/ | CSV/JSON canonical data |
| Domain READMEs | Domain root | Usage and architecture for that domain |
| Historical baselines | Domain archive/baseline folder | Keep for traceability, not as landing-page docs |
| Superseded drafts | docs/archive/ or root archive | Do not delete until reviewed |

## Duplicate / Near-Duplicate Documents

| Title | Canonical Document | Duplicate Locations | Merge Strategy |
| --- | --- | --- | --- |
| Radiator Geometry and Topology Optimization Report | geometry_optimization_report.md | geometry_optimization_report.md; satelite/reports/geometry_optimization_report.md | Keep canonical; archive or mark others generated/raw |
| Hardware-in-the-Loop (HIL) Real-Time Validation Report | hil_report.md | hil_report.md; satelite/hil_report.md; satelite/reports/hil_report.md; satelite/satellite/thermal/hil_report.md | Keep canonical; archive or mark others generated/raw |
| Reporte del Dominio Cuántico MVP (Fase 1A) | docs/QUANTUM_DOMAIN_REPORT.md | QUANTUM_DOMAIN_REPORT.md; docs/QUANTUM_DOMAIN_REPORT.md | Keep canonical; archive or mark others generated/raw |
| Reporte de Quantum Fitness y Fidelidad Física (Fase 1B.2) | docs/QUANTUM_FITNESS_REPORT.md | QUANTUM_FITNESS_REPORT.md; docs/QUANTUM_FITNESS_REPORT.md | Keep canonical; archive or mark others generated/raw |
| Reporte de Capa de Destilación de Conocimiento Cuántico (Fase 1B.4) | docs/QUANTUM_KNOWLEDGE_REPORT.md | QUANTUM_KNOWLEDGE_REPORT.md; docs/QUANTUM_KNOWLEDGE_REPORT.md | Keep canonical; archive or mark others generated/raw |
| Reporte de Quantum Sandbox con Simulación Real (Fase 1B.1) | docs/QUANTUM_SANDBOX_REPORT.md | QUANTUM_SANDBOX_REPORT.md; docs/QUANTUM_SANDBOX_REPORT.md | Keep canonical; archive or mark others generated/raw |
| Scientific Discovery Loop Report | artifacts/discovery_report.md | artifacts/discovery_report.md; physics/artifacts/discovery_report.md | Keep canonical; archive or mark others generated/raw |
| Autonomous Quantum Gravity Discovery Report | artifacts/qg_discovery_report.md | artifacts/qg_discovery_report.md; physics/artifacts/qg_discovery_report.md | Keep canonical; archive or mark others generated/raw |
| Phase 8E — Robustness Stress Test Report | artifacts/robustness_report.md | artifacts/robustness_report.md; physics/artifacts/robustness_report.md | Keep canonical; archive or mark others generated/raw |
| Phase 8C — SOTA Benchmark Report | artifacts/sota_report.md | artifacts/sota_report.md; physics/artifacts/sota_report.md | Keep canonical; archive or mark others generated/raw |
| This is NOT the Next.js you know | dashboard/AGENTS.md | dashboard/AGENTS.md; satelite/dashboard/AGENTS.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase III Hardware-Aware Validation Report | docs/PHASE3_HARDWARE_AWARE_REPORT.md | docs/PHASE3_HARDWARE_AWARE_REPORT.md; benchmarks/reports/PHASE3_HARDWARE_AWARE_REPORT.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase III Investor Summary | docs/PHASE3_INVESTOR_SUMMARY.md | docs/PHASE3_INVESTOR_SUMMARY.md; benchmarks/reports/investor_executive_summary.md; benchmarks/reports/PHASE3_INVESTOR_SUMMARY.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase IV Commercial Positioning | docs/PHASE4_COMMERCIAL_POSITIONING.md | docs/PHASE4_COMMERCIAL_POSITIONING.md; benchmarks/reports/PHASE4_COMMERCIAL_POSITIONING.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase IV Competitive Advantage Report | docs/PHASE4_COMPETITIVE_ADVANTAGE_REPORT.md | docs/PHASE4_COMPETITIVE_ADVANTAGE_REPORT.md; benchmarks/reports/PHASE4_COMPETITIVE_ADVANTAGE_REPORT.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase IV Investor Summary | docs/PHASE4_INVESTOR_SUMMARY.md | docs/PHASE4_INVESTOR_SUMMARY.md; benchmarks/reports/PHASE4_INVESTOR_SUMMARY.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase V Investor Summary | docs/PHASE5_INVESTOR_SUMMARY.md | docs/PHASE5_INVESTOR_SUMMARY.md; benchmarks/reports/PHASE5_INVESTOR_SUMMARY.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase V IP Report | docs/PHASE5_IP_REPORT.md | docs/PHASE5_IP_REPORT.md; benchmarks/reports/PHASE5_IP_REPORT.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase VI Competitive Moat Report | docs/PHASE6_COMPETITIVE_MOAT_REPORT.md | docs/PHASE6_COMPETITIVE_MOAT_REPORT.md; benchmarks/reports/PHASE6_COMPETITIVE_MOAT_REPORT.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase VI Economic Impact Report | docs/PHASE6_ECONOMIC_IMPACT_REPORT.md | docs/PHASE6_ECONOMIC_IMPACT_REPORT.md; benchmarks/reports/PHASE6_ECONOMIC_IMPACT_REPORT.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase VI Investor Summary | docs/PHASE6_INVESTOR_SUMMARY.md | docs/PHASE6_INVESTOR_SUMMARY.md; benchmarks/reports/PHASE6_INVESTOR_SUMMARY.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase VI IP Valuation Report | docs/PHASE6_IP_VALUATION_REPORT.md | docs/PHASE6_IP_VALUATION_REPORT.md; benchmarks/reports/PHASE6_IP_VALUATION_REPORT.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase VI Licensing Model | docs/PHASE6_LICENSING_MODEL.md | docs/PHASE6_LICENSING_MODEL.md; benchmarks/reports/PHASE6_LICENSING_MODEL.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase VI Risk Analysis | docs/PHASE6_RISK_ANALYSIS.md | docs/PHASE6_RISK_ANALYSIS.md; benchmarks/reports/PHASE6_RISK_ANALYSIS.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase VII Competitive Gap Report | docs/PHASE7_COMPETITIVE_GAP_REPORT.md | docs/PHASE7_COMPETITIVE_GAP_REPORT.md; benchmarks/reports/PHASE7_COMPETITIVE_GAP_REPORT.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase VII Economic Moat Report | docs/PHASE7_ECONOMIC_MOAT_REPORT.md | docs/PHASE7_ECONOMIC_MOAT_REPORT.md; benchmarks/reports/PHASE7_ECONOMIC_MOAT_REPORT.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase VII Executive Summary | docs/PHASE7_EXECUTIVE_SUMMARY.md | docs/PHASE7_EXECUTIVE_SUMMARY.md; benchmarks/reports/PHASE7_EXECUTIVE_SUMMARY.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase VII Investor Positioning | docs/PHASE7_INVESTOR_POSITIONING.md | docs/PHASE7_INVESTOR_POSITIONING.md; benchmarks/reports/PHASE7_INVESTOR_POSITIONING.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase VII Knowledge Flywheel Report | docs/PHASE7_KNOWLEDGE_FLYWHEEL_REPORT.md | docs/PHASE7_KNOWLEDGE_FLYWHEEL_REPORT.md; benchmarks/reports/PHASE7_KNOWLEDGE_FLYWHEEL_REPORT.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase VII Network Effect Report | docs/PHASE7_NETWORK_EFFECT_REPORT.md | docs/PHASE7_NETWORK_EFFECT_REPORT.md; benchmarks/reports/PHASE7_NETWORK_EFFECT_REPORT.md | Keep canonical; archive or mark others generated/raw |
| QADE Phase VII Platform Analysis | docs/PHASE7_PLATFORM_ANALYSIS.md | docs/PHASE7_PLATFORM_ANALYSIS.md; benchmarks/reports/PHASE7_PLATFORM_ANALYSIS.md | Keep canonical; archive or mark others generated/raw |
| Statistical Validation: Reproducibility 30-Seed Final Report | docs/REPRODUCIBILITY_30_SEED_FINAL_REPORT.md | docs/REPRODUCIBILITY_30_SEED_FINAL_REPORT.md; docs/REPRODUCIBILITY_IMPROVED_30_SEED_FINAL_REPORT.md | Keep canonical; archive or mark others generated/raw |
| Black Compliance Report | satelite/black_compliance_report.md | satelite/black_compliance_report.md; satelite/VERIFICATION_BASELINE_v4/black_compliance_report.md | Keep canonical; archive or mark others generated/raw |
| CDR Final Review Board Report | satelite/cdr_final_review_board_report.md | satelite/cdr_final_review_board_report.md; satelite/VERIFICATION_BASELINE_v4/cdr_final_review_board_report.md | Keep canonical; archive or mark others generated/raw |
| Spacecraft Thermal OS (AST-OS) — Critical Design Review (CDR) Readiness Report | satelite/CDR_READINESS_REVIEW.md | satelite/CDR_READINESS_REVIEW.md; satelite/VERIFICATION_BASELINE_v3/CDR_READINESS_REVIEW.md | Keep canonical; archive or mark others generated/raw |
| Spacecraft Thermal OS (AST-OS) — Nominal EKF Verification & Validation Report | satelite/ekf_validation_report.md | satelite/ekf_validation_report.md; satelite/VERIFICATION_BASELINE_v2/ekf_validation_report.md; satelite/VERIFICATION_BASELINE_v3/ekf_validation_report.md; satelite/VERIFICATION_BASELINE_v4/ekf_validation_report.md | Keep canonical; archive or mark others generated/raw |
| Flight Heritage Calibration Report | satelite/flight_heritage_calibration_report.md | satelite/flight_heritage_calibration_report.md; satelite/VERIFICATION_BASELINE_v4/flight_heritage_calibration_report.md | Keep canonical; archive or mark others generated/raw |
| Pydantic Migration Report | satelite/pydantic_migration_report.md | satelite/pydantic_migration_report.md; satelite/VERIFICATION_BASELINE_v4/pydantic_migration_report.md | Keep canonical; archive or mark others generated/raw |
| BiasDetector | physics/artifacts/bias_report.md | physics/artifacts/bias_report.md; physics/artifacts/bias_report.tagged.md | Keep canonical; archive or mark others generated/raw |
| Epistemological Knowledge Graph Report (Neo4j) | physics/artifacts/knowledge_report.md | physics/artifacts/knowledge_report.md; physics/artifacts/test_knowledge_report.md | Keep canonical; archive or mark others generated/raw |
| PhysicsSanityEngine | physics/artifacts/sanity_report.md | physics/artifacts/sanity_report.md; physics/artifacts/sanity_report.tagged.md | Keep canonical; archive or mark others generated/raw |
| Spacecraft Material Degradation & Thermal Drift Report | satelite/reports/aging_report.md | satelite/reports/aging_report.md; satelite/satellite/thermal/aging_report.md | Keep canonical; archive or mark others generated/raw |
| CAD-Aware 3D Geometry Voxelization & Thermal Optimization Report | satelite/reports/cad_optimization_report.md | satelite/reports/cad_optimization_report.md; satelite/satellite/thermal/cad_optimization_report.md | Keep canonical; archive or mark others generated/raw |
| Informe de Radiación Interna de Cavidad (Fase T36) | satelite/reports/cavity_radiation_report.md | satelite/reports/cavity_radiation_report.md; satelite/satellite/thermal/cavity_radiation_report.md | Keep canonical; archive or mark others generated/raw |
| Closed-Loop Thermo-Avionics Active Predictive Control Report | satelite/reports/closed_loop_report.md | satelite/reports/closed_loop_report.md; satelite/satellite/thermal/closed_loop_report.md | Keep canonical; archive or mark others generated/raw |
| Multi-Spacecraft Constellation Modeler Report (Phase T24) | satelite/reports/constellation_report.md | satelite/reports/constellation_report.md; satelite/satellite/thermal/constellation_report.md | Keep canonical; archive or mark others generated/raw |
| Autonomous Thermal Discovery Report | satelite/reports/discovery_report.md | satelite/reports/discovery_report.md; satelite/satellite/thermal/discovery_report.md | Keep canonical; archive or mark others generated/raw |
| ESA ECSS Spacecraft Thermal Margins Verification Summary | satelite/reports/ecss_margins_summary.md | satelite/reports/ecss_margins_summary.md; satelite/satellite/thermal/ecss_margins_summary.md | Keep canonical; archive or mark others generated/raw |
| Experimental Calibration and Hardware Validation Report | satelite/reports/experiment_report.md | satelite/reports/experiment_report.md; satelite/satellite/thermal/experiment_report.md | Keep canonical; archive or mark others generated/raw |
| Informe de Diagnóstico y Mitigación Térmica FDIR (Fase T33) | satelite/reports/fdir_report.md | satelite/reports/fdir_report.md; satelite/satellite/thermal/fdir_report.md | Keep canonical; archive or mark others generated/raw |
| FEA/FEM Professional Correlation Report | satelite/reports/fem_correlation_report.md | satelite/reports/fem_correlation_report.md; satelite/satellite/thermal/fem_correlation_report.md | Keep canonical; archive or mark others generated/raw |
| Informe de Validación de Bucle Hardware-in-the-Loop Real (Fase T34) | satelite/reports/hil_real_report.md | satelite/reports/hil_real_report.md; satelite/satellite/thermal/hil_real_report.md | Keep canonical; archive or mark others generated/raw |
| Spacecraft Thermal Twin HPC & GPU Acceleration Report | satelite/reports/hpc_report.md | satelite/reports/hpc_report.md; satelite/satellite/thermal/hpc_report.md | Keep canonical; archive or mark others generated/raw |
| Biblioteca de Materiales COTS Aeroespaciales y Envejecimiento (Fase T32) | satelite/reports/material_comparison_report.md | satelite/reports/material_comparison_report.md; satelite/satellite/thermal/material_comparison_report.md | Keep canonical; archive or mark others generated/raw |
| Informe de Observabilidad Formal y Sensibilidad del EKF (Fase T30) | satelite/reports/observability_report.md | satelite/reports/observability_report.md; satelite/satellite/thermal/observability_report.md | Keep canonical; archive or mark others generated/raw |
| Operational Flight Validation Report (Phases T22) | satelite/reports/operational_validation_report.md | satelite/reports/operational_validation_report.md; satelite/satellite/thermal/operational_validation_report.md | Keep canonical; archive or mark others generated/raw |
| Spacecraft Telemetry Ingestion & Real-Data Calibration Report | satelite/reports/real_data_report.md | satelite/reports/real_data_report.md; satelite/satellite/thermal/real_data_report.md | Keep canonical; archive or mark others generated/raw |
| Spacecraft Thermo-Avionics Numerical Stiffness Report | satelite/reports/stiffness_report.md | satelite/reports/stiffness_report.md; satelite/satellite/thermal/stiffness_report.md | Keep canonical; archive or mark others generated/raw |
| Informe de Estabilidad Numérica y Solvers Stiff (Fase T29) | satelite/reports/stiff_benchmark_report.md | satelite/reports/stiff_benchmark_report.md; satelite/satellite/thermal/stiff_benchmark_report.md | Keep canonical; archive or mark others generated/raw |
| Informe de Calificación Final de Misión de 30 días (Thermal OS) (Fase T50) | satelite/reports/thermal_os_final_report.md | satelite/reports/thermal_os_final_report.md; satelite/satellite/platform/thermal_os_final_report.md | Keep canonical; archive or mark others generated/raw |

## Obsolete or Superseded Documents

| Document | Recommendation | Reason |
| --- | --- | --- |
| README_AUDIT.md | Archive | Superseded by REPOSITORY_AUDIT.md |
| README_REWRITTEN.md | Archive | Superseded by updated README.md |
| benchmarks/reports/investor_executive_summary.md | Mark generated duplicate | Same title/content class as PHASE3_INVESTOR_SUMMARY.md |
| docs/PHASE5_MOTIF_DATABASE.csv/json | Move or mark mirror | Generated data canonical location should be benchmarks/results |
| satelite/VERIFICATION_BASELINE_v1-v3 | Archive | Older baselines; v4 appears current |
| root *_report.json | Archive by owner domain | Generated reports should not live at root |

## Recommended Final Locations

- QADE curated docs: `docs/qade/` or current `docs/` with `QADE_DATA_ROOM_INDEX.md` as index.
- QADE generated reports: `benchmarks/reports/`.
- QADE generated data: `benchmarks/results/`.
- Physics generated research reports: `physics/artifacts/` or `docs/physics/`.
- Satellite verification: `satellite/verification/` after rename, with frozen baselines archived by version.
- Organization-level docs: root `README.md`, `docs/REPOSITORY_AUDIT.md`, `docs/REPOSITORY_EXECUTIVE_STATUS.md`.

## Merge Strategy

1. Keep the public canonical document in `docs/`.
2. Keep generated raw outputs in their generator-owned folder.
3. Add links from public summaries to raw reports/data.
4. Archive superseded drafts rather than deleting.
5. Keep a manifest for moved documents.
