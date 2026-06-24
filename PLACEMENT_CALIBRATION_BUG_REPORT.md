# QADE Stage C Placement Calibration Bug Report

This report analyzes the root cause of the qubit placement regression observed in Run 8 on the real IBM Quantum QPU `ibm_fez` and documents the implemented fix.

---

## 1. Analysis of Real Calibration Data vs. Mock (FakeFez)

Using the IBM API token, we queried the real-time calibration parameters of `ibm_fez` and compared them to the static parameters stored in `FakeFez` for the trivial layout qubits (`0-4`) and the selected layout qubits (`131-135`).

### Comparative Calibration Table

| Parameter / Qubit | Trivial Qubit 0 | Trivial Qubit 2 | Selected Qubit 131 | Selected Qubit 132 | Selected Qubit 134 | Selected Qubit 135 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Real T1 ($\mu s$)** | 54.4 | 178.4 | **255.7** | **174.2** | 183.4 | 184.1 |
| **FakeFez T1 ($\mu s$)**| 48.8 | 274.4 | 141.2 | 137.0 | 151.3 | 179.6 |
| **Real T2 ($\mu s$)** | 58.4 | 136.4 | **264.3** | **307.4** | 32.2 | 188.7 |
| **FakeFez T2 ($\mu s$)**| 42.4 | 100.0 | 201.5 | 161.6 | 22.7 | 92.5 |
| **Real Readout Error**| 1.31% | 0.32% | **7.996% (High)**| 0.45% | 0.35% | **3.418% (High)**|
| **FakeFez Readout Err**| 1.15% | 0.49% | 5.54% | 1.34% | 0.54% | 6.01% |
| **Real Avg Gate Error**| 0.22% | 0.02% | 0.01% | 0.02% | **4.400% (High)**| 0.02% |
| **FakeFez Gate Err** | 0.08% | 0.02% | 0.01% | 0.02% | 0.04% | 0.01% |

---

## 2. Diagnosing the Selection Bug (Root Cause)

1. **Fresh Calibration Retrieval Verified**: The diagnostics script confirmed that `get_qubit_quality()` and `get_gate_properties()` correctly query the passed backend object's dynamic properties (i.e. no internal caching issues exist). 
2. **Imbalance in Scoring Weights**:
   The QADE path placement scoring formula is defined as:
   $$Score = w_1 \cdot \frac{T_1}{T_{1, max}} + w_2 \cdot \frac{T_2}{T_{2, max}} - w_3 \cdot E_{readout} - w_4 \cdot E_{gate}$$
   with weights set to:
   $$w_1 = 0.35, \quad w_2 = 0.35, \quad w_3 = 0.15, \quad w_4 = 0.15$$
   
   - **Coherence Domination**: Qubits `131` and `132` have exceptionally high real coherence times ($T_1 \approx 255\mu s, T_2 \approx 307\mu s$), which are near the maximum available on the chip. This grants them a massive score boost ($\approx +0.70$).
   - **Error Under-Penalization**: In contrast, the readout error of `131` ($7.996\%$) and the gate error of `134` ($4.4\%$) are extremely high but are only penalized by $-0.15 \times 0.08 \approx -0.012$ and $-0.15 \times 0.044 \approx -0.0066$ respectively.
   - **Result**: The layout `131-135` received a total score of **1.9867**, while the trivial layout `0-4` received **1.4192**. The scoring model chose the high-noise qubits because of their long coherence, completely ignoring that an 8% readout error and a 4.4% gate error heavily degrade state fidelity for short-depth circuits (where coherence decay is negligible).

---

## 3. Description of the Fix

We modified `quantum/optimization/qubit_placement.py` to implement a robust **dual fallback mechanism**:

1. **Standard QADE Score Fallback**: If the standard QADE score of the selected path is worse than the trivial path score, fallback to the trivial layout.
2. **Physical State Fidelity Fallback**:
   We estimate the physical state fidelity ($F_{est}$) of a layout as:
   $$F_{est} = \prod_{p \in \text{path}} (1 - E_{readout, p}) \cdot \prod_{(u, v) \in \text{edges}} (1 - E_{gate, u, v})$$
   - If the estimated fidelity of the selected layout is worse than that of the trivial layout, the trivial layout is selected as a fallback.
   - **High-Noise Threshold Protection**: If any qubit in the selected layout exceeds a readout error of $5\%$ or a gate error of $3\%$, and the trivial layout is comparable or better, it falls back to the trivial layout to prevent sending jobs to bad hardware components.

This directly fixes the selection of high-noise qubits like `131` and `134` on real backends while preserving optimal placement on cleaner subgraphs.
