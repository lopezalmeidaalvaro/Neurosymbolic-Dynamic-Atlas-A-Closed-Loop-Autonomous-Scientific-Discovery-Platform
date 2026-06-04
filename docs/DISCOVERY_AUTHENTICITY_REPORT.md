# Discovery Authenticity Report — Phase 1H.1

## Final Authenticity Verdict: **PARTIAL_DISCOVERY**

> [!WARNING]
> **Verdict Summary:** Evolved scaffolds show partial authenticity. They represent structural variants or recombinations with significant but compiler-dependent optimization gains.

### 1. Key Success Criteria Verification

| Criterion | Target Value | Actual Evaluated Value | Status |
| :--- | :---: | :---: | :---: |
| **Criterio A: Novelty Score** | > 0.60 | 0.4200 (STRUCTURAL_VARIANT) | FAILED |
| **Criterio B: Law Guided Significance** | p < 0.05 | p = 3.142140e-01 (d = +0.0648) | FAILED |
| **Criterio C: Cross-Domain Utility** | Positive | POSITIVE | PASSED |
| **Criterio D: Optimization Loss** | < 50% | 5.26% | PASSED |
| **Criterio E: Final Verdict** | AUTHENTIC_DISCOVERY | PARTIAL_DISCOVERY | FAILED |


### 2. Detailed Audit Outcomes

#### Novel Structure Audit
- **Discovered Scaffold:** `CNOT`
- **Best Matching Baseline:** `RY->CNOT->RY->CNOT`
- **Novelty Score:** `0.4200`


#### Optimization Removal Audit
- **Fidelity Drop without PyZX:** `5.26%`
- **Status:** `FUNCTIONAL_STRUCTURE_VERIFIED`


#### Random Search vs Law-Guided Search
- **Law-Guided Mean Utility:** `0.9982`
- **Random Search Mean Utility:** `0.9982`
- **Effect Size (Cohen's d):** `+0.0648`


#### Cross-Domain Out-of-Distribution Discovery
| Target Holdout Domain | Utility | Synergy | Novelty | Transferability |
| :--- | :---: | :---: | :---: | :---: |
| `vqe` | 0.9992 | 0.4992 | 0.1867 | 0.9000 |
| `qaoa` | 0.5000 | 0.0000 | 0.1867 | 0.9000 |
| `qft` | 0.9977 | 0.4977 | 0.5367 | 0.7000 |
| `grover` | 0.9985 | 0.4985 | 0.3617 | 0.9000 |


#### Discovery Compression Audit
- **Decoupled Classification:** `TRUE_DISCOVERY`


#### Evolutionary Lineage Reconstruction
- **Lineage Depth:** `3`
- **Cumulative Novelty Growth:** `+0.4833`

