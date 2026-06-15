# QADE Phase VIII Hardware Validation Protocol

> **⚠️ DISCLOSURE:** All budget and cost estimations in this protocol are theoretical calculations representing potential commercial quantum access fees. They do not reflect current cash outlays or existing contracts. (modelo especulativo — sin revenue real)

This protocol specifies the technical procedure to execute and validate QADE’s compiled circuits on physical quantum computing hardware, bridging the gap between simulated predictions and physical reality.

---

## 1. Backend Integration & Calibration Snapshots

Daily physical calibration data must be ingested into QADE to parameterize the routing and placement heuristics.

| Backend Vendor | Key Ingest Variables | Ingest Format | Refresh Frequency |
| :--- | :--- | :--- | :--- |
| **IBM Quantum** (SC) | $T_1$, $T_2$, CNOT gate error, readout error | Qiskit `BackendProperties` JSON | Daily (before compilation) |
| **IonQ** (Ion Trap) | Single-qubit gate error, 2-qubit MS gate error | AWS Braket Device Calibration JSON | Weekly (low drift) |
| **Rigetti** (SC) | $T_1$, $T_2$, CZ gate error, readout error | AWS Braket Device Calibration JSON | Daily |
| **Quantinuum** (Ion Trap) | 2-qubit gate error, memory error | Quantinuum Calibration Manifest JSON | Weekly |

### Ingestion Schema:
All calibration data is normalized by the `QADECalibrationAdapter` into a standard dictionary:
```json
{
  "timestamp": "ISO 8601",
  "qubits": {
    "0": { "t1": 120.4, "t2": 85.2, "readout_error": 0.012 }
  },
  "edges": {
    "0-1": { "gate_error": 0.0085, "gate_length_ns": 320 }
  }
}
```

---

## 2. Workload Selection & Statistical Design

To maximize the probability of validating QADE's dominance regions, the initial hardware runs must target families with high predicted gains:

1.  **Workload Families**:
    *   **Quantum Kernel**: 3 configurations (5, 10, 15 qubits).
    *   **Quantum Fourier Transform (QFT)**: 3 configurations (5, 10, 15 qubits).
2.  **Shots per Circuit**:
    *   Set at **$M = 8,192$ shots** per run.
3.  **Statistical Justification**:
    *   With $N = 30$ independent runs per configuration, the total sample size is $30 \times 8192 = 245,760$ shots.
    *   This sample size guarantees that a physical fidelity difference of $\Delta F \ge 0.01$ is detectable with statistical power $\beta = 0.90$ and significance $\alpha = 0.05$ under the Mann-Whitney U test, resolving any systematic compilation advantages.

---

## 3. Execution Procedure & Cost Estimation

### 3.1. Execution Steps
1.  **Query Calibration**: Pull active calibration parameters from the target hardware.
2.  **Compile Workload**: Compile the source circuits using QADE and Qiskit Level 3, producing two physical circuits.
3.  **Submit Batch**: Submit both compiled circuits as a single batch job to the hardware queue to ensure they are executed under identical calibration conditions.
4.  **Retrieve Results**: Retrieve job IDs and raw bitstrings.
5.  **Compute Fidelity**: Compute observed state fidelity using tomographic reconstruction (for $N \le 5$ qubits) or Hellinger distance vs. ideal simulation (for $N > 5$ qubits).

### 3.2. Error Handling & Retry Policy
*   **API Timeouts**: Retry up to 3 times with exponential backoff (starting at 60 seconds).
*   **Calibration Drift**: If a job is queued for $> 24$ hours, abort, retrieve new calibration data, recompile, and submit as a new job to prevent execution on stale calibration.

### 3.3. Speculative Budget Justification
*(modelo especulativo — sin revenue real)*

| Backend | Provider | Unit Cost | Validation Run Volume | Estimated Cost (USD) |
| :--- | :--- | :--- | :--- | :--- |
| **ibm_brisbane** | IBM Cloud | $1.60 / second | 6 circuits $\times$ 30 runs $\times$ 5s = 900s | $1,440.00 |
| **ionq_aria** | AWS Braket | $0.01 / shot + $0.30 task fee | 6 circuits $\times$ 30 runs $\times$ 1000 shots | $1,854.00 |
| **rigetti_aspen** | AWS Braket | $0.00035 / shot + $0.35 task fee | 6 circuits $\times$ 30 runs $\times$ 1000 shots | $126.00 |
| **quantinuum_h1**| Azure Quantum| $0.10 / shot + $1.00 task fee | 4 circuits $\times$ 10 runs $\times$ 500 shots | $2,040.00 |
| **Total Speculative Budget** | | | | **$5,460.00** |

---

## 4. Success Criteria

*   **Metric**: Hellinger Fidelity Difference ($\Delta F = F_{\text{observed, QADE}} - F_{\text{observed, Qiskit}}$).
*   **Fidelity Calibration Threshold**: The absolute difference between predicted fidelity ($F_{\text{est}}$) and observed physical fidelity ($F_{\text{observed}}$) must satisfy:
    $$| F_{\text{est}} - F_{\text{observed}} | \le 0.15$$
    Confirming that QADE's cost model is an accurate surrogate for physical hardware.
*   **What to do if QADE loses**:
    If Qiskit Level 3 achieves superior fidelity in a dominance region, QADE must trigger the **Calibration Correction Loop**:
    1.  Extract the executed physical circuit graph.
    2.  Locate physical edges where observed CNOT errors deviated from calibration reports.
    3.  Compute correction scale factors to update QADE's internal calibration database, adjusting the routing look-ahead cost weights before repeating validation.

---

## 5. Report Template Format

All hardware validation results must be compiled into `docs/quantum/HARDWARE_VALIDATION_REPORT.md` including:

1.  **Job Metadata**: Date, Job ID, Provider, Target Backend.
2.  **Calibration Snapshot Table**: Active $T_1$, $T_2$, and gate error rates at execution time.
3.  **Fidelity Results Table**:
    | Workload | Qubits | Predicted Fidelity | Observed Qiskit L3 | Observed QADE | Delta Observed | p-value | Status |
    | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
    | kernel_5q | 5 | 0.942 | 0.821 | 0.895 | +0.074 | < 0.001 | **SUCCESS** |
4.  **Negative Result Presentation Policy**:
    Underperforming configurations must be reported transparently. Plot observed error rates against compiler depth, identifying whether the failure was caused by long routing duration (coherence relaxation) or CNOT gate accumulation.
