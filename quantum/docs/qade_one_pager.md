# QADE — Quantum Algorithm Discovery Engine
**Hardware-aware quantum compiler. Fidelity-aware qubit placement.**

## Verified Results (ibm_fez, June 2026)
QADE compiled circuits outperform standard Qiskit Level 3 transpilation in Hellinger fidelity on real quantum hardware:

| Circuit | Qiskit L3 | QADE | Delta | Winner |
|---|---|---|---|---|
| **GHZ_5q** | 0.9438 | 0.9490 | **+0.52%** | QADE |
| **Kernel_5q** | 0.9955 | 0.9975 | **+0.20%** | QADE |
| **Kernel_8q** | 0.9821 | 0.9826 | **+0.05%** | QADE |

*   **Win rate:** 3/5 (60%) on real hardware.
*   **Verifiable:** Publicly auditable Job IDs on IBM Quantum platform.

## What it does differently
Standard compilers (like Qiskit) route qubits based solely on topology/connectivity. QADE dynamically analyzes QPU calibration data ($T_1, T_2$, single-qubit errors, and two-qubit gate errors) for each individual qubit and edge.
*   **Example:** For `GHZ_5q` on `ibm_fez` (156 qubits), QADE avoids physical Qubit 0 (calibrated at a very low $T_1 = 48.8\text{ }\mu\text{s}$, $T_2 = 42.4\text{ }\mu\text{s}$) and maps the active path to `[1, 2, 3, 4, 5]`.
*   **Outcome:** Over +1.36% theoretical fidelity improvement before any evolutionary gate reduction or ZX-calculus simplification.

## Operational ROI (estimated — speculative financial model)
When compiling with QADE, the improved gate fidelity decreases the number of shots required to extract expectations above the noise floor. 
*   **Formula:** $\text{shots\_needed} = \frac{\text{shots\_base}}{1 + \text{fidelity\_improvement}}$
*   **Fintech Scenario:** 500 jobs/month, average 8192 shots:
    *   **Short test jobs (0.3s QPU runtime):** Saves ~37 shots/job, translating to ~$1.08/month saved (based on IBM public PAYG pricing of ~$1.60/s).
    *   **Production workloads (60s average runtime):** Saves ~$216.80/month (over $2,600/year in QPU costs) for the same job throughput.
*   *(Note: Financial calculations represent a speculative model based on IBM public pricing. QADE has no active commercial contracts or revenues).*

## Status
*   **Class D — Pilot-Ready:** 7 successive real hardware runs completed and documented.
*   **Corporate Entity:** Incorporating *QADE Technologies SL*.
*   **NEOTEC:** Grant application dossier in preparation.
*   **Funding target:** Seeking pre-seed conversations and technical pilot partners.

## Known gaps
*   **QFT Routing Overhead:** -0.82% fidelity vs Qiskit L3 due to SWAP overhead on heavy-hex architecture.
*   **Cost Model:** Prediction error exceeding 20% on dense circuits (under active correction).

**Alvaro Lopez Almeida — lopezalmeidaalvaro (GitHub)**
---
