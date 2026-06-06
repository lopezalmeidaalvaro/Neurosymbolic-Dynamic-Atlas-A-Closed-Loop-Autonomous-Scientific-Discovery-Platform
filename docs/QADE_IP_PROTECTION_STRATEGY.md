# QADE IP Protection Strategy

Generated: 2026-06-06

## Objective

Protect QADE's proprietary value while preserving a credible path for open-source/public presentation.

## IP Categories

| Category | Assets | Protection Route | Recommendation |
| --- | --- | --- | --- |
| Algorithms | Hardware cost model, coherence-aware routing, fidelity-aware placement, motif ranking | Copyright + selective patents | Keep source proprietary until patent review or publish controlled subset |
| Motifs | Validated motif database and transfer statistics | Trade secret + database rights where applicable | Keep motif corpus proprietary; publish aggregate metrics only |
| Knowledge base | Motif-to-family/topology/hardware graph | Trade secret | Protect schema, confidence scores, and customer-specific data |
| Data assets | Benchmark CSVs, motif economics, workload analysis | Copyright + trade secret for non-public customer data | Open public benchmark subset, keep customer data private |
| Software code | QADE modules and benchmark runner | Copyright/license | Use proprietary or dual-license strategy |
| Reports | Dossiers, investor summaries, technical reports | Copyright | Share under NDA in data room where needed |
| Commercial models | Licensing, valuation, moat models | Trade secret | Publish high-level narrative only |

## Potential Patent Themes

- Automatic extraction of hardware-aware circuit optimization motifs from before/after circuit pairs.
- Validation and ranking of motifs conditioned on hardware calibration and topology.
- Knowledge graph linking quantum circuit motifs to workload families, hardware regimes, and economic gains.
- Pre-optimization motif rewrite engine that applies learned motifs before compiler passes.
- Economic valuation pipeline for validated quantum optimization motifs.

## Trade Secrets

The strongest trade-secret candidates are motif database contents, motif confidence scores, transferability statistics by workload family, hardware relevance weights, customer-specific optimization history, and ranking/reuse heuristics.

## Copyright Assets

QADE source modules, benchmark generation scripts, generated reports, dossiers, motif database files, documentation, and investor materials.

## Licensable Assets

QADE compiler add-on, motif database access, cloud optimization API, OEM compiler integration, and enterprise hardware-aware optimization reports.

## Open-Source Boundaries

Recommended public/open material: high-level architecture, public benchmark methodology, selected non-sensitive benchmark results, and documentation explaining methodology.

Recommended proprietary material: full motif database, ranking weights and confidence scores, customer-derived motifs, economic models tied to customer workloads, production API, and enterprise integration logic.

## Immediate Actions

1. Run patentability review before broad publication of motif-learning details.
2. Add provenance/version metadata to motif database files.
3. Separate public benchmark artifacts from proprietary motif corpus.
4. Draft contributor/IP assignment policy before adding employees or contractors.
5. Define customer-data policy: private motifs, shared motifs, or opt-in pooled learning.
