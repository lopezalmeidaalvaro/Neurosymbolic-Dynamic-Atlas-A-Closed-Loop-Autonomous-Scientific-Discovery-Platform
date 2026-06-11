# QADE Phase VI Risk Analysis

## Technical Risks

* Motifs are currently exact local rewrites; broader graph matching may be needed for noisier real workloads.
* Hardware benefit estimates depend on calibration and provider cost assumptions.
* Some motif+optimizer combinations can lose gate-count gains after downstream compilation.

## Market Risks

* Buyers may prefer established compiler stacks unless QADE shows repeatable savings on their workloads.
* Quantum hardware pricing is immature, so per-shot savings may change materially.

## Adoption Risks

* Integration into enterprise toolchains requires compatibility with Qiskit, TKET, BQSKit, and cloud workflows.
* Customers will require explainability and safety guarantees for learned rewrites.

## Competitive Risks

* Industrial compilers could add persistent motif databases.
* Open-source rule systems could absorb common cancellation motifs.

## Overvaluation Risks

* Replacement-cost valuation is conservative but still assumes motifs remain reusable across future backends.
* Revenue potential is scenario-based, not contracted revenue.
