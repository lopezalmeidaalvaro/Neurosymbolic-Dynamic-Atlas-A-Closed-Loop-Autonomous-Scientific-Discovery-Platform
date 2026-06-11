# QADE Grant and Investor Dossier

> **⚠️ DISCLOSURE:** All financial figures in this document
> are outputs of internal simulation models.
> They represent theoretical scenarios assuming full market
> adoption. Zero commercial revenue has been generated to date.
> These figures should not be interpreted as valuations,
> commitments, or revenue forecasts.

Generated: 2026-06-06

Audience: ENISA, CDTI, NEOTEC, EIC Accelerator, Deep Tech funds, VCs, innovation agencies.

## 1. Executive Summary

QADE, the Quantum Algorithm Discovery Engine, is a hardware-aware quantum optimization platform that has evolved beyond a conventional compiler. It combines backend calibration, routing, placement, motif discovery, mathematical validation, reusable motif storage, economic valuation, and knowledge-flywheel modeling.

The most important commercial thesis is that QADE can accumulate proprietary optimization knowledge. Each validated motif can become a reusable asset that improves future workloads and can be licensed as part of a compiler add-on, cloud API, or OEM integration.

Quantitative evidence from current reports includes Phase III critical-duration reduction of 98.95% vs Phase II; Phase IV Quantum Kernel win rate of 100.0% with 53.1% mean fidelity improvement; Phase V 13 validated motifs and 11 reusable motifs; Phase VI estimated IP value of $434,901 and annual revenue potential of $1,168,320; Phase VII modeled portfolio value growth of 20.69x from 10 to 1000 workloads.

## 2. Problem

Quantum hardware is noisy and calibration-dependent. A compiler that only minimizes gate count may produce circuits that execute worse because of longer critical duration, weak qubit assignment, poor readout reliability, or T1/T2 coherence loss. This problem was observed directly in QADE Phase II and corrected in Phase III.

## 3. Market Need

Quantum users need compilers that understand hardware conditions, workload families, and execution economics. Enterprise adopters also need explainability, reproducibility, and evidence that optimization does not change circuit semantics.

## 4. Why Existing Solutions Are Insufficient

Qiskit, TKET, BQSKit, PyZX, and Cirq are valuable tools. Their limitation for QADE's target thesis is that they are primarily procedural compiler or framework systems. They do not, in this repository evidence, provide a QADE-style validated motif database that learns from workloads, stores reusable optimization knowledge, and converts it into an economic asset.

## 5. QADE Innovation

QADE combines hardware-aware compilation, calibration-aware physical scoring, coherence-aware routing, fidelity-aware qubit placement, motif discovery from before/after circuits, mathematical equivalence validation, motif knowledge graph storage, motif reuse on unseen circuits, economic valuation, and knowledge-flywheel modeling.

## 6. Scientific Innovation

QADE treats circuit optimization as a scientific discovery loop. It observes transformations, extracts hypotheses in the form of motifs, validates them, measures benefit, and stores them for reuse. This creates a path from optimization experiment to reusable knowledge.

## 7. Engineering Innovation

The engineering stack includes adapters for industrial compilers, hardware scoring modules, routing and placement engines, motif databases, benchmark pipelines, and investor-grade reports. It is already implemented in repository modules rather than being only a proposal.

## 8. Proprietary IP

The IP is concentrated in the motif learning loop and knowledge database. Individual simple rewrites may be obvious; the proprietary value lies in validated context, hardware relevance, transferability statistics, ranking, and reuse behavior.

## 9. Motif Database

Phase V reports 30 motifs, 13 unique motifs, 13 validated motifs, and 11 reusable motifs with 84.6% transferability. This supports the claim that QADE can generate reusable optimization IP automatically.

## 10. Hardware-Aware Optimization

Phase III introduced a hardware-aware model using backend calibration data: T1, T2, gate length, gate error, readout error, duration, and SWAP overhead. It reduced mean critical duration by 98.95% versus Phase II and passed 3/4 success criteria.

## 11. Economic Impact

Phase VI estimated 166.0 saved two-qubit-equivalent operations, 157.22 us saved execution time, $207,500 replacement cost, $434,901 IP value, and $1,168,320 annual revenue potential. These are model outputs and should be validated with customer workloads.

## 12. Commercial Potential

Commercial models include compiler add-on licensing, cloud optimization API, OEM compiler integration, enterprise hardware-aware optimization service, and proprietary motif database licensing. Phase VII ranked the Optimization Knowledge Platform model highest.

## 13. Competitive Positioning

QADE should not claim universal superiority. Phase IV shows specific dominance regions. Quantum Kernel and QFT are the strongest current evidence areas. MaxCut and probabilistic error cancellation are weaker regions. This supports a focused go-to-market strategy.

## 14. Defensibility

Defensibility comes from accumulated validated motifs, provenance, transfer statistics, hardware context, and customer-specific learning loops. The Phase VII moat score is 6.13/10, which is promising but not yet a mature monopoly moat.

## 15. Scalability

QADE can scale technically by adding workloads, motifs, and backend calibration data. The Phase VII model estimates 20.69x portfolio value growth from 10 to 1000 workloads. The main validation gap is proving this on live, diverse customer workloads.

## 16. Roadmap

| Stage | Objective | Deliverable |
| --- | --- | --- |
| 0-3 months | Package QADE independently | QADE CLI, dependency manifest, QADE-only tests |
| 3-6 months | Live hardware validation | Calibration snapshots and predicted-vs-observed report |
| 6-9 months | Motif governance | Versioned motif DB, provenance, confidence thresholds |
| 9-12 months | Pilot commercialization | Customer-like pilot, ROI calculator, API prototype |
| 12+ months | Platform expansion | Enterprise API, OEM integrations, protected motif corpus |

## 17. Team Requirements

QADE needs a quantum compiler engineer, quantum hardware/calibration specialist, backend/API engineer, ML/data engineer for motif knowledge systems, technical product lead, IP counsel, and grant/commercial operations support.

## 18. Funding Use Plan

| Use | Purpose |
| --- | --- |
| Engineering | QADE packaging, API, benchmark automation, CI |
| Hardware validation | Live backend execution, calibration studies |
| IP protection | Patentability analysis, trade-secret governance |
| Commercial pilots | Customer discovery, enterprise pilots, ROI validation |
| Documentation and compliance | Grant reporting, data room, reproducibility package |

## 19. Risks

Estimated fidelity may diverge from real hardware outcomes. Individual motifs may be easy to copy. Optional compiler dependencies may make benchmark comparisons inconsistent. Economic value is modeled, not contracted. Quantum market adoption timelines remain uncertain.

## 20. Expected Impact

QADE can reduce the cost and improve the fidelity of selected quantum workloads while building a reusable optimization knowledge base. If validated on live workloads, it can become a deep-tech platform asset rather than a one-off compiler project.

## Quantitative Evidence Table

| Phase | Evidence | Interpretation |
| --- | --- | --- |
| III | 98.95% mean critical-duration reduction vs Phase II | Hardware-aware optimization fixed the major coherence/duration failure mode |
| III | 28.0% fidelity win rate vs Qiskit L3 | Not universal dominance; needs targeted positioning |
| IV | Quantum Kernel 100.0% win rate, 53.1% fidelity improvement | Strong commercial pilot candidate |
| IV | QFT 100.0% win rate, 29.9% fidelity improvement | Strong technical benchmark candidate |
| V | 13 validated motifs, 11 reusable motifs, 84.6% transferability | Reusable IP thesis supported |
| VI | $434,901 estimated IP value, $1,168,320 annual revenue potential | Economic model exists; needs market validation |
| VII | 20.69x portfolio growth model, 6.13/10 moat score | Knowledge flywheel thesis is promising but still modeled |

## Grant Dossier Expansion Annex

### A. Grant Work Packages

| WP | Title | Objective | Deliverables | Success Evidence |
| --- | --- | --- | --- | --- |
| WP1 | QADE Isolation | Make QADE independently installable | Package manifest, CLI, QADE-only tests | Clean extraction build succeeds |
| WP2 | Hardware Validation | Validate estimates on calibrated quantum hardware | Live backend report, calibration snapshots | Predicted-vs-observed comparison |
| WP3 | Motif IP System | Formalize motif database and governance | Schema, provenance, versioning, failure registry | Motif DB v1 release |
| WP4 | Commercial API | Create enterprise-facing optimization API | API prototype, audit logs, security model | External client can submit and retrieve optimized circuit |
| WP5 | Pilot Benchmark | Run customer-like workloads in dominance regions | Pilot report, ROI analysis | Measured improvement on target workload family |

### B. Funding Justification

Funding is justified because QADE sits between research software and commercial platform. The repository already contains working components, but the work required for grant impact is packaging, validation, governance, and customer-oriented delivery. These are classic deep-tech translation activities: move from prototype evidence to validated product asset.

### C. Societal and Industrial Impact

Quantum computing adoption is slowed by hardware noise and uncertainty about useful workloads. A hardware-aware optimization platform can improve the effective use of scarce quantum hardware time. If QADE reduces wasted executions or improves fidelity in selected workloads, it contributes to more efficient quantum R&D and lowers experimentation cost.

### D. European Deep-Tech Fit

QADE aligns with European deep-tech priorities around advanced computing, quantum technologies, trustworthy AI, and digital sovereignty. The strongest European funding narrative is not just compiler efficiency; it is creation of a reusable quantum optimization knowledge asset that can be governed, audited, and licensed.

### E. Commercialization Plan

The recommended first market is not all quantum users. The first market should be teams running repeated structured workloads: quantum kernels, QFT-like transforms, QML feature maps, VQE templates, and selected algorithm developers who need hardware-aware compilation. A narrow early market improves validation and avoids overextension.

### F. Business Model Options

| Model | Customer | Revenue Logic | Risk |
| --- | --- | --- | --- |
| Compiler add-on | Quantum software teams | Annual license | May be compared directly with free tooling |
| Cloud API | Researchers and startups | Usage-based optimization calls | Needs robust API and security |
| OEM integration | Compiler/cloud vendors | Integration license | Long sales cycles |
| Enterprise optimization service | Large R&D teams | Project/pilot fees | Service-heavy initially |
| Motif database license | Compiler vendors / hardware providers | Data/IP license | Requires strong IP protection |

### G. Evidence Still Needed For Stronger Applications

- Live backend execution evidence.
- External partner or pilot letter.
- Independent review of economic assumptions.
- Patentability memo.
- Clean QADE packaging demonstration.
- Security and customer-data handling policy.

### H. Grant Budget Logic

A credible budget should allocate funds to engineering, live quantum execution, data governance, IP counsel, pilot development, and dissemination. The budget should not be framed as speculative research only; it should be framed as productization and validation of an already implemented deep-tech prototype.

### I. Expected Outcomes

By the end of a funded project, QADE should have an independently installable package, validated hardware-aware benchmarks, governed motif database v1, API prototype, IP protection plan, and at least one customer-like pilot. These outcomes are concrete and measurable.

## Grant Dossier Extended Application Annex

### 1. Project Rationale for Public Funding

QADE is appropriate for public deep-tech funding because it addresses a technical bottleneck in quantum computing adoption: useful quantum hardware time is expensive, scarce, and degraded by noise. Better compilation and optimization can increase the value extracted from existing hardware. The project is not only about software efficiency; it is about making quantum experimentation more reliable and economically rational.

The repository already demonstrates substantial self-funded R&D. Funding would not start from zero. It would convert a working research system into a validated, packaged, protectable, and pilot-ready technology. This reduces execution risk compared with a purely speculative research proposal.

### 2. Innovation Beyond State of the Art

Existing compiler ecosystems are strong, but they largely operate as procedural optimization tools. QADE proposes an additional layer: learn validated motifs from optimization history, store them with context, and reuse them intelligently. This transforms compilation from a one-time transformation into a cumulative knowledge process.

The innovation has three dimensions: technical, scientific, and commercial. Technically, it integrates hardware-aware metrics with motif reuse. Scientifically, it treats optimization as evidence accumulation. Commercially, it turns validated motifs into a database asset that can be licensed.

### 3. Work Plan Detail

| Task | Description | Output | Milestone |
| --- | --- | --- | --- |
| T1.1 | Refactor QADE dependencies for standalone packaging | QADE install package | Month 2 |
| T1.2 | Create canonical benchmark CLI | One-command benchmark runner | Month 2 |
| T2.1 | Select live backend workloads | Validation workload list | Month 3 |
| T2.2 | Run calibrated hardware comparisons | Live validation report | Month 6 |
| T3.1 | Define motif schema and provenance | Motif DB schema v1 | Month 4 |
| T3.2 | Add failure registry and confidence score | Motif governance report | Month 6 |
| T4.1 | Build API prototype | Optimization API | Month 8 |
| T4.2 | Generate optimization certificate | Audit certificate format | Month 9 |
| T5.1 | Run pilot-style workloads | Pilot report | Month 12 |
| T5.2 | Prepare commercialization package | Investor/customer data room | Month 12 |

### 4. Budget Justification Detail

Engineering budget is required to transform research code into a standalone product. Hardware validation budget is required because fake backends and modeled fidelity are not enough for enterprise-grade evidence. IP budget is required because motif databases and algorithmic methods need protection before broader publication. Commercial pilot budget is required because QADE's best early market must be validated with realistic workloads.

### 5. Expected KPIs

| KPI | Target | Evidence |
| --- | --- | --- |
| Independent QADE install | Clean environment install succeeds | CI log |
| Benchmark reproducibility | One command regenerates key reports | Benchmark logs |
| Live validation | Predicted vs observed report completed | Hardware validation report |
| Motif governance | Versioned motif database schema | Schema and DB files |
| Pilot readiness | At least one customer-like workload package | Pilot report |
| IP readiness | Patent/trade-secret review completed | IP counsel memo or internal strategy |

### 6. Market Entry Strategy

The first market entry should be narrow. QADE should target organizations already experimenting with quantum kernels, feature maps, QFT-like subroutines, and QML circuits. These users understand quantum compilation pain and can evaluate improvements. A narrow pilot market also allows QADE to accumulate motif data in the strongest observed regions.

### 7. Business Development Path

The recommended path is: technical pilot, paid optimization report, annual compiler add-on, cloud API, and OEM integration. This avoids premature platform scaling before technical validation. The motif database remains valuable throughout the path because it improves with each workload.

### 8. Impact on Spanish and European Deep Tech

QADE can support Spanish and European positioning in quantum software infrastructure. A validated quantum optimization knowledge platform would be a high-value intangible asset. It can also support collaborations with universities, quantum hardware providers, cloud providers, and industrial R&D teams.

### 9. Risk Mitigation Plan

| Risk | Mitigation | Grant Relevance |
| --- | --- | --- |
| Technical overclaiming | Separate measured, estimated, and hypothesized claims | Improves credibility |
| Hardware results differ from estimates | Fund live validation | De-risks commercialization |
| IP leakage | Protect motif database and review patents | Preserves defensibility |
| Slow market adoption | Start with pilots and API service | Reduces revenue timing risk |
| Dependency complexity | Package QADE independently | Improves maintainability |

### 10. Long-Term Vision

The long-term vision is a quantum optimization knowledge platform that improves with every workload. If QADE can validate this flywheel on live workloads, it can become a strategic asset for quantum software, similar in spirit to how data improves ML systems. The repository evidence supports this direction, but grant funding should be used to validate and harden it rather than to claim the destination has already been reached.
