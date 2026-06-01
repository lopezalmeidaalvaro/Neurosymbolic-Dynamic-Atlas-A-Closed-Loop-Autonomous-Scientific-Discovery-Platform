# Landing Page Claims Audit

**Scope**: `backend/landing.html` and `satellite/landing/index.html`  
**Audit objective**: remove or flag non-verifiable user, growth, customer, mission, operator, and production claims.  
**Date**: 2026-05-31

| claim | evidence_available | publicly_verifiable | keep_or_remove |
|---|---|---|---|
| Active Satellite Operators | No real external-user evidence supplied. | No | REMOVE |
| Active Space Node Keys | Only local seeded/API keys were present; not evidence of external operators. | No | REMOVE |
| Simulations & EKF Diagnoses as live usage metric | Local usage counters are not real production events. | No | REMOVE |
| Acquired & verified flight V&V engineers | No evidence supplied. | No | REMOVE |
| Real NASA ISS telemetry pipelines | No public evidence supplied for an active real telemetry pipeline in the landing context. | No | REMOVE |
| Flexible Developer Subscription Plans with monthly paid tiers | No evidence of commercial traction or launched billing plan supplied. | No | REMOVE |
| Production customer / operator acquisition implication | No external customer evidence supplied. | No | REMOVE |
| Autonomous Spacecraft Thermal Digital Twin | Describes project scope; retained as product/research name, not flight autonomy claim. | Partially, via repo/demo artifacts | KEEP |
| Physics-informed spacecraft thermal simulation platform for CubeSat and SmallSat mission analysis. | Supported by local thermal model/API implementation. | Partially, via source code | KEEP |
| Interactive thermal modelling, transient orbital simulations, and anomaly analysis through a web interface and REST API. | Supported by landing UI and FastAPI endpoints. | Partially, via source code and running demo | KEEP |
| 6 Thermal Nodes | Supported by implemented thermal network and landing capability description. | Partially, via source code | KEEP |
| Physics-based spacecraft thermal network | Supported by thermal model source code. | Partially, via source code | KEEP |
| FastAPI REST API | Supported by `backend/thermal_api.py`. | Yes, if deployed or run locally | KEEP |
| Interactive simulation endpoints | Supported by `/v1/simulate` and UI controls. | Yes, if deployed or run locally | KEEP |
| Real-Time Digital Twin | Describes interactive transient simulation behavior; no flight/prod claim attached. | Partially, via demo | KEEP |
| Dynamic transient thermal simulations | Supported by simulation endpoint output. | Partially, via source code/API | KEEP |
| Academic Preview: Free | Access-positioning text, not a traction metric. | No external verification needed | KEEP |
| Research Collaboration: Contact Us | Access-positioning text, not a traction metric. | No external verification needed | KEEP |
| Enterprise: Coming Soon | Future availability clearly marked as not launched. | No external verification needed | KEEP |

## Audit Result

All landing page claims that imply external users, production traction, verified operators, real customer acquisition, real mission deployments, or unsupported NASA telemetry integration were removed from the landing pages. Remaining claims are limited to implemented technical capabilities, demo workflow, and clearly labelled access options.

