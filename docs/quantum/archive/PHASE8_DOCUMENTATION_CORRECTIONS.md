# QADE Documentation Corrections

This document provides exact replacement text and rewritten sections for the [`README.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/README.md) and [`quantum/README.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/README.md) files, removing overstated claims and establishing high technical credibility.

---

## Claims que requieren corrección

| Claim Original | Claim Corregido | Justificación Técnica |
| :--- | :--- | :--- |
| "QADE supera a Qiskit L3 en compilación de circuitos cuánticos" | "QADE muestra ventajas selectivas frente a Qiskit L3 en familias específicas de circuitos (Quantum Kernel y QFT), aunque Qiskit L3 es superior en promedio." | El win rate físico real en la Phase III fue de solo el 28.0% (7/25 casos). QADE tiene pérdidas en el 72% de los casos evaluados en promedio. |
| "QADE logra 53.1% de mejora en fidelidad en Quantum Kernel" | "QADE estima una mejora del 53.1% en la fidelidad física de Quantum Kernel bajo simulaciones internas con un modelo de ruido de hardware." | La fidelidad no se midió en hardware cuántico real, sino que fue calculada mediante simulación de ruido estimada. |
| "100% win rate en Quantum Kernel y QFT" | "Win rate preliminar del 100% en Quantum Kernel y QFT con un tamaño de muestra limitado de 3 casos por familia (n=3)." | Un tamaño de muestra tan pequeño (n=3 casos por backend) es preliminar y estadísticamente no concluyente. |
| "98.95% de reducción en duración crítica vs Phase II" | "Reducción del 98.95% en la duración crítica del circuito en comparación con la versión no optimizada de la Phase II de QADE." | Se trata de una mejora interna sobre el propio código ineficiente de la Phase II, no de una comparación contra compiladores de mercado. |
| "Fidelidad media de QADE es 0.9057" | "Fidelidad lógica/matemática media de QADE de 0.9057 calculada bajo condiciones ideales sin ruido." | Mezclar fidelidad lógica sin ruido con fidelidad física calibrada es engañoso. En el modelo con ruido calibrado, la fidelidad de QADE cae a 0.0000 debido a la degradación por coherencia T2. |
| "QADE benchmarkeado contra TKET, BQSKit y Cirq reales" | "QADE benchmarkeado contra TKET y BQSKit cuando están instalados, utilizando Qiskit L3 como emulación para BQSKit si el circuito supera los 5 qubits o si TKET no está disponible. Cirq se utiliza únicamente para conversión de formatos." | BQSKit tiene una limitación por la cual circuitos con más de 5 qubits se desvían de forma silenciosa a Qiskit L3, y Cirq no aplica pases de optimización nativos en el benchmark. |
| "Valor de IP estimado en $434,901" | "Coste teórico de desarrollo y reemplazo de la base de datos de motifs modelado internamente en $434,901." | Es un modelo financiero teórico basado en costes de desarrollo estimados, no una valoración de mercado ni ingresos reales. |
| "Enterprise value de $62,882,402 y potencial de ingresos de $1,168,320" | "Proyecciones teóricas a largo plazo que sugieren un enterprise value potencial de $62.8M y un mercado de licencias de hasta $1.16M en escenarios de adopción masiva." | Cifras especulativas obtenidas mediante simulación interna sin contratos, facturación ni clientes reales. |
| "QADE reduce gate count vs Qiskit L3" | "QADE incrementa la cantidad de puertas en la mayoría de los casos, pero optimiza la asignación (placement) de qubits físicos de alta calidad." | QADE tiene gate improvements negativos en Phase IV ya que su ventaja radica en la selección inteligente de qubits físicos (fidelity-aware placement), no en la reducción de operaciones. |

---

## [`README.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/README.md) — Sección Results reescrita

```markdown
## QADE Compilation Performance & Validation Summary

The Quantum Algorithm Discovery Engine (QADE) focuses on hardware-aware qubit placement and routing under physical noise. Below is the audited performance summary across development phases:

*   **Phase III (Hardware-Aware Routing):** Passed 3 out of 4 success criteria. Replaced the unoptimized Phase II compiler routing to achieve a **98.95% reduction in critical path duration** (average path duration reduced from 15.6 ms to 352 us). Achieved a **28.0% physical execution win rate (7/25 cases)** against the Qiskit Level 3 baseline under simulated backend noise profiles, showing targeted rather than universal dominance.
*   **Phase IV (Dominance Regions):** Rather than competing on average compiler rank, QADE identifies specific workload families where qubit quality selection is critical. In preliminary tests (n=3 cases per backend/family), QADE achieved a **100% win rate on Quantum Kernel** (with an estimated 53.1% mean physical fidelity improvement) and **100% win rate on QFT** (with an estimated 29.9% mean physical fidelity improvement) compared to the best available industrial baseline. Gate counts are typically higher than baselines to satisfy hardware constraints.
*   **Phase V (Motif IP):** Discovered and mathematically validated 13 unique circuit optimization patterns (motifs), showing an **84.6% transferability rate (11/13 reused)** on a selected set of unseen circuit workloads.
*   **Phase VI & VII (Commercial Modeling):** Implemented theoretical pricing, licensing, and knowledge-flywheel models evaluating potential commercialization pathways (Optimization Knowledge Platform model ranked highest). Moat index (6.13/10) and long-term valuations represent speculative simulation projections and do not reflect current revenue or market traction.
*   **Benchmark Configuration Disclosure:** TKET and BQSKit benchmarks utilize Qiskit L3 emulations under the hood if packages are unavailable or if circuit sizes exceed BQSKit's 5-qubit size threshold. Cirq benchmarks are format-translation checks and do not run native Cirq optimization passes.
```

---

## [`quantum/README.md`](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/README.md) — Sección Results reescrita

```markdown
## Audited Performance & Development Phase Snapshot

QADE’s value proposition is centered around hardware-aware qubits placement (fidelity-aware placement) and custom motif reuse, rather than simple gate reduction.

| Phase | Audited Objective | Core Results & Disclosures | Status |
| :--- | :--- | :--- | :--- |
| **Phase III** | Hardware-Aware Optimization | Achieved a **98.95% reduction in critical path duration** vs QADE's unoptimized Phase II compiler. Achieved a **28.0% physical fidelity win rate** (7/25 cases) against Qiskit L3 under simulated noise. | **Completed (3/4 success criteria met)** |
| **Phase IV** | Dominance Regions | Identified family-specific advantages under small-sample runs (n=3 per backend): **Quantum Kernel** (100% win rate, +53.1% simulated fidelity gain, -102.8% gate overhead) and **QFT** (100% win rate, +29.9% simulated fidelity gain, -282.6% gate overhead). | **Completed (Targeted advantage established)** |
| **Phase V** | Motif IP Database | Discovered 30 motifs, mathematically validated 13 unique motifs, and demonstrated **84.6% motif transferability** (11/13 reused) on 4 unseen circuit families. | **Completed (Database populated)** |
| **Phase VI** | Economic Valuation | Modeled a theoretical database replacement cost of **$434,901** and a speculative SaaS annual revenue potential of **$1,168,320**. *Note: These are financial models with zero commercial revenue.* | **Completed (Financial model only)** |
| **Phase VII** | Moat & Flywheel Analysis | Moat score modeled at **6.13/10**, and theoretical long-term mid-case enterprise value calculated at **$62,882,402**. *Note: Speclative simulation output; no market valuation established.* | **Completed (Flywheel hypothesis modeled)** |

### Critical Benchmark Disclosures

1.  **Fidelity Types:** Leaderboards reporting an average QADE fidelity of **0.9057** represent ideal, noiseless mathematical statevector equivalence. Under physical noise profiles (incorporating T1, T2, and readout calibration), QADE's physical fidelity drops to **0.0000** on FakeSherbrooke and FakeKyoto due to coherence decay caused by long critical path durations (47–54 us).
2.  **Gate Counts:** QADE does not outperform industrial baselines on gate count minimization. The competitive advantage is driven by placement on higher-fidelity physical qubits, despite using more gates.
3.  **Compiler Fallbacks:** Cirq benchmarks do not execute native Cirq optimization passes. BQSKit benchmarks silently fall back to Qiskit Level 3 transpilation for any circuit $>5$ qubits. TKET falls back to Qiskit L3 transpilation if the `pytket` library is missing.
```
