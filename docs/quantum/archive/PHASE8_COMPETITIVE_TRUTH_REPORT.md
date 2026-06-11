# QADE Competitive Truth Report

This report answers 10 key due-diligence questions concerning the QADE (Quantum Algorithm Discovery Engine) repository, referencing direct codebase and report evidence.

---

### 1. ¿QADE está benchmarkeado contra Qiskit real? ¿Cuál versión?

**Sí.** QADE benchmarks execute real Qiskit transpilation passes. The benchmarking pipeline in [`benchmark_all_compilers.py`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/benchmarks/benchmark_all_compilers.py#L167-L169) imports and invokes `transpile()` with `optimization_level=3` on a dynamically generated `GenericBackendV2` instance.
* **Versión:** The version active in the environment is **`2.4.1`** (specifically, Qiskit 2.4.1 or compatible, as verified by system telemetry).

---

### 2. ¿QADE está benchmarkeado contra TKET real o contra un adapter de fallback? Si es fallback, ¿qué hace ese fallback exactamente?

**Parcial.** QADE executes real TKET passes when the library is installed (`pytket` version `2.18.0` is present in the current environment). However, the compiler integration contains a fallback mechanism to handle environments where TKET is missing.
* **Comportamiento del Fallback:** According to [`tket_adapter.py`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/integration/tket_adapter.py#L130-L160), if `PYTKET_AVAILABLE` is `False`, the adapter catches the import error, prints a warning, and emulates TKET by executing **Qiskit Level 3 transpilation** under the hood. It then returns the transpiled circuit in QADE JSON format and simulates an initial layout.

---

### 3. ¿QADE está benchmarkeado contra BQSKit real o fallback?

**Parcial (con limitaciones críticas de escalabilidad).** The adapter in [`bqskit_adapter.py`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/integration/bqskit_adapter.py#L110-L142) compiles with BQSKit synthesis/partitioning search optimization only if:
1. `BQSKIT_AVAILABLE` is `True` (it is version `1.2.1` in the current environment).
2. **`num_qubits <= 5`** (hardcoded check at line 111).

* **Comportamiento del Fallback:** If BQSKit is missing OR the circuit size exceeds 5 qubits, the adapter **falls back to Qiskit Level 3 transpilation** on `GenericBackendV2` to emulate BQSKit. Since all benchmarks evaluated in the Phase IV reports (e.g., Quantum Kernel 8q, QFT 8q, QAOA 10q) have $>5$ qubits, BQSKit results in those reports were actually **Qiskit L3 emulations** rather than native BQSKit execution.

---

### 4. ¿QADE está benchmarkeado contra Cirq real o fallback?

**No.** The Cirq integration in [`cirq_adapter.py`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/integration/cirq_adapter.py) only provides format translation functions (`qade_json_to_cirq` and `cirq_to_qade_json`). 
* **Comportamiento del Fallback:** If `CIRQ_AVAILABLE` is `False`, it returns the input circuit untouched.
* **Falta de compilador nativo:** Even when Cirq is installed (version `1.6.1`), the benchmark execution pipeline in [`benchmark_all_compilers.py`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/benchmarks/benchmark_all_compilers.py#L181-L187) only converts the circuit formats and then routes the circuit using **QADE's own routing engine**. No native Cirq compilation passes or optimizers are ever run. Thus, the comparison in the reports does not benchmark Cirq's compilation capabilities.

---

### 5. ¿Cuál es el resultado QADE más fuerte que sobrevive si eliminamos todos los comparadores no reales y nos quedamos solo con Qiskit?

Si nos limitamos estrictamente a comparaciones reales frente a Qiskit L3:
1. **Iteración interna de ruteo:** The Phase III hardware-aware routing achieved a **98.95% reduction in critical path duration** compared to QADE's unoptimized Phase II compiler baseline, resolving a critical coherence decay issue.
2. **Ventaja regional por calidad de qubits (placement):** QADE achieves an estimated physical execution fidelity improvement over Qiskit L3 in specific, small-sample workload dominance regions: **Quantum Kernel** (+53.1% simulated fidelity improvement) and **QFT** (+29.9% simulated fidelity improvement). This advantage is achieved solely by selecting higher-quality physical qubits (fidelity-aware placement), as QADE actually increases total gate counts ("Gate Improvement vs Best Industrial" is negative, e.g., $-102.8\%$ for Quantum Kernel and $-282.6\%$ for QFT).

---

### 6. ¿La fidelidad de 0.9057 del Compiler Comparison y los 0.0000 del Calibration Report miden lo mismo? Si no, ¿qué mide cada uno?

**No. Miden propiedades físicas y matemáticas totalmente distintas:**
* **Fidelidad lógica/matemática (0.9057):** Calculated in [`COMPILER_COMPARISON_REPORT.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/reports/COMPILER_COMPARISON_REPORT.md) under ideal noiseless conditions. It represents statevector equivalence and is derived from a simple gate count error model. It does not account for physical hardware constraints.
* **Fidelidad física/calibrada (0.0000):** Calculated in [`CALIBRATION_AWARE_REPORT.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/reports/CALIBRATION_AWARE_REPORT.md) using live/fake backend calibration parameters ($T_1$, $T_2$ coherence times, gate durations, readout errors, and idle qubit decoherence). In this model, QADE's routed circuits on FakeSherbrooke and FakeKyoto have extremely long critical path durations (47–54 µs vs 5–6 µs for Qiskit), causing complete coherence decay and an underflow to $0.0000$ execution success probability.

---

### 7. ¿En qué circuitos y backends específicos QADE obtiene 0.0000 de fidelidad física? ¿Son estos los mismos circuitos de las dominance regions de Phase IV?

* **Circuitos y Backends con 0.0000:** In [`CALIBRATION_AWARE_REPORT.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/reports/CALIBRATION_AWARE_REPORT.md), QADE obtains **0.0000** total estimated fidelity on the **FakeSherbrooke** backend (critical path duration `47.06 us`) and **FakeKyoto** backend (critical path duration `52.14 us`).
* **Relación con dominance regions:** These are **not** the same circuits as the dominance regions. The dominance regions in Phase IV (Quantum Kernel, QFT, QAOA, VQE) are based on small 3-case runs per family where QADE was evaluated against the best available industrial baseline, and where fidelity-aware placement could win. The 0.0000 cases typically occur on large, deep circuits (e.g. 10q, 12q) where QADE's routing engine fails to control critical path duration, leading to complete coherence decoherence.

---

### 8. ¿Cuál es el claim más débil actualmente en la documentación orientada a inversores?

El claim más débil es doble:
1. **Financial Valuation and Speculative Projections:** Presenting a long-term enterprise value of **`$62,882,402`** ([`PHASE7_EXECUTIVE_SUMMARY.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/reports/PHASE7_EXECUTIVE_SUMMARY.md)), a motif database IP value of **`$434,901`** and annual revenue projections of **`$1,168,320`** ([`PHASE6_INVESTOR_SUMMARY.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/benchmarks/reports/PHASE6_INVESTOR_SUMMARY.md)) as current commercial facts. These are purely simulated financial model outputs based on zero current revenue.
2. **Untruthful Benchmarking representation:** Claiming that QADE was benchmarked against "TKET, BQSKit, and Cirq" without disclosing that BQSKit runs Qiskit L3 under the hood for $>5$ qubits, Cirq does no optimization, and TKET falls back to Qiskit L3 when missing.

---

### 9. ¿Cuál es el claim más fuerte y más defendible que tiene QADE hoy?

The strongest and most defendible claim is its **hardware-aware qubit placement loop**. By identifying high-quality physical qubits (using live or simulated $T_1$, $T_2$, and gate error calibration data) and matching them to the most active logical qubits, QADE can compile selected workload families (e.g., Quantum Kernel and QFT) to achieve higher estimated physical execution fidelity than standard compilers in noise-heavy regimes, even when using more gates. This is supported by the Phase III/IV reports showing targeted advantage in specific dominance regions.

---

### 10. ¿Qué afirmaciones deben eliminarse completamente antes de que un inversor o revisor de grants vea el material?

Deben eliminarse por completo las siguientes afirmaciones:
1. **Valuation Numbers:** The speculative $62.8M enterprise value and $434k IP valuation.
2. **Universal Dominance Claims:** Wording that suggests QADE universally beats Qiskit, TKET, and BQSKit. The actual win rate vs Qiskit L3 is only 28.0% in Phase III.
3. **Misleading Competitor Benchmarking:** Claims of direct performance comparison with BQSKit and Cirq, unless the fallback size limit and format-only conversion are explicitly and prominently disclosed.
4. **Physical Equivalence Gaps:** Any statement presenting simulated physical fidelity on fake backends as equivalent to real-world quantum hardware execution.
