# QADE Phase IX - Hardware Cost Model Audit

> **⚠️ DISCLOSURE:** All economic metrics, hardware costs, and licensing models discussed in this project context represent speculative simulation projections and do not reflect active revenues or contracted values. (modelo especulativo — sin revenue real)

This document contains a detailed technical audit of the original `hardware_cost_model.py` implementation, explaining the scale discrepancy between predicted fidelity ($\approx 0.004$) and observed Hellinger fidelity ($\approx 0.97$) on `ibm_marrakesh`.

---

## 1. Line-by-Line Annotated Code Audit

Below is the annotated implementation of the original `estimate_physical_cost` function:

```python
def estimate_physical_cost(
    circuit: CircuitLike,
    backend: Any,
    lambda_duration: float = 0.0,
    lambda_swaps: float = 0.01,
) -> Dict[str, Any]:
    # 1. Convierte el circuito de entrada a QuantumCircuit si viene en JSON
    qc = _as_quantum_circuit(circuit)
    
    # 2. Transpila el circuito al backend con nivel 0 para simular la estructura física
    native = _native_circuit(qc, backend)
    
    # 3. Determina el número total de qubits del procesador
    num_qubits = int(getattr(backend, "num_qubits", native.num_qubits))

    active_qubits = set()
    qubit_end_times = {q: 0.0 for q in range(num_qubits)}
    log_gate_fidelity = 0.0
    swap_count = 0
    two_qubit_count = 0
    gate_details: List[Dict[str, Any]] = []

    # 4. Bucle principal sobre todas las instrucciones en el circuito transpiled
    for instruction in native.data:
        op_name = instruction.operation.name
        # Encuentra el índice físico del qubit
        qargs = tuple(native.find_bit(qubit).index for qubit in instruction.qubits)
        
        # BUG #1: Añade todos los qubits a active_qubits, incluso los qubits inactivos
        # que solo aparecen en instrucciones globales (barriers, delays) o layouts físicos
        active_qubits.update(qargs)
        
        if op_name.lower() == "swap":
            swap_count += 1
        if len(qargs) == 2:
            two_qubit_count += 1

        # 5. Obtiene error y duración de la puerta
        props = get_gate_properties(backend, op_name, qargs)
        duration = props["duration"]
        error = max(0.0, min(1.0, props["error"]))
        
        # BUG #2: Suma log-fidelidades de TODAS las puertas del circuito, 
        # incluyendo las puertas de un qubit, que tienen errores irrelevantes (~10x menores)
        log_gate_fidelity += math.log(max(1e-15, 1.0 - error))

        if qargs:
            start = max(qubit_end_times.get(q, 0.0) for q in qargs)
            finish = start + duration
            for q in qargs:
                qubit_end_times[q] = finish

        gate_details.append({
            "gate": op_name,
            "qubits": qargs,
            "error": error,
            "duration_sec": duration,
        })

    if not active_qubits:
        active_qubits = set(range(native.num_qubits))

    log_readout_fidelity = 0.0
    log_coherence_fidelity = 0.0
    qubit_quality = {}
    
    # 6. Bucle sobre active_qubits para readout y coherencia
    for q in active_qubits:
        quality = get_qubit_quality(backend, q)
        qubit_quality[q] = quality
        
        # BUG #3: Calcula readout_error sobre active_qubits (que contiene los 156 qubits
        # debido a la transpilación y layouts). Multiplica (1 - readout_error) para qubits 
        # que NUNCA son medidos, resultando en una fidelidad de readout artificialmente baja (~0.007).
        readout_error = max(0.0, min(1.0, quality["readout_error"]))
        log_readout_fidelity += math.log(max(1e-15, 1.0 - readout_error))

        # BUG #4: Calcula decoherencia temporal sobre todos los 156 qubits.
        # Al tener residence_time mayor que cero por barreras globales, sumamos
        # decoherencia de todo el chip en vez de solo los 5 qubits activos.
        residence_time = qubit_end_times.get(q, 0.0)
        t1 = max(quality["t1"], 1e-15)
        t2 = max(quality["t2"], 1e-15)
        log_coherence_fidelity += -(residence_time / t1) - (residence_time / t2)

    critical_duration_sec = max(qubit_end_times.values()) if qubit_end_times else 0.0
    log_total = log_gate_fidelity + log_readout_fidelity + log_coherence_fidelity
    total_estimated_fidelity = math.exp(max(-745.0, min(0.0, log_total)))
    score = log_total - lambda_duration * critical_duration_sec - lambda_swaps * swap_count

    return {
        "score": score,
        "log_total_fidelity": log_total,
        "total_estimated_fidelity": total_estimated_fidelity,
        "estimated_fidelity": total_estimated_fidelity,
        "gate_fidelity": math.exp(max(-745.0, min(0.0, log_gate_fidelity))),
        "readout_fidelity": math.exp(max(-745.0, min(0.0, log_readout_fidelity))),
        "coherence_fidelity": math.exp(max(-745.0, min(0.0, log_coherence_fidelity))),
        "critical_path_duration_sec": critical_duration_sec,
        ...
    }
```

---

## 2. Identificación del Bug y Discrepancias

1.  **Over-counting del Error de Readout (BUG #3)**:
    En Qiskit, el circuito transpiled sobre el hardware real mapea los 5 qubits virtuales a 5 físicos de `ibm_marrakesh` (156 qubits). Debido a que `active_qubits` incluye a todos los qubits implicados en barreras o layouts iniciales (156 qubits), el bucle calcula el producto de readout fidelity para **los 156 qubits**. Con un error medio de readout de $1.5\%$, esto da:
    $$F_{\text{readout}} \approx (1 - 0.015)^{156} \approx 0.093$$
    Si además algunos qubits tienen errores altos ($>10\%$), el valor se reduce a **$0.0076$** (tres órdenes de magnitud por debajo del valor real).
2.  **Over-counting de Decoherencia (BUG #4)**:
    El cálculo de decaimiento por $T_1$ y $T_2$ se realiza para todos los 156 qubits en lugar de limitarse a los qubits utilizados. Debido a las barreras globales del transpiler, todos los qubits adquieren un tiempo de residencia no-nulo, sumando el decaimiento de todo el procesador. Esto reduce la fidelidad de coherencia a **$0.637$** en lugar de $\approx 0.98$.
3.  **Inclusión de Puertas Single-Qubit (BUG #2)**:
    Suma errores de todas las puertas. Las puertas single-qubit tienen tasas de error despreciables ($\approx 10^{-4}$) comparadas con las CNOTs ($\approx 5 \times 10^{-3}$). Sumar 33 puertas de un solo qubit reduce artificialmente el presupuesto de fidelidad.

---

## 3. Valores de Entrada y Ejecución Real (`ibm_marrakesh`)

Los datos reales obtenidos del archivo de ejecución `hardware_results_20260614_210334.json` y `compilation_metrics_20260614_210334.json` para **GHZ_5q (QADE)** son:

*   **Active Qubits**: 156 qubits (debido a barreras e instrucciones de layout).
*   **Gate Fidelity**: $0.81102$ (37 puertas transpuestas en total).
*   **Readout Fidelity**: $0.00762$ (multiplicando $156$ qubits con errores de readout).
*   **Coherence Fidelity**: $0.63710$ (decoherencia integrada de 156 qubits durante la duración del circuito).
*   **Total Estimated Fidelity**:
    $$F_{\text{est}} = 0.81102 \times 0.00762 \times 0.63710 \approx 0.0039387$$

---

## 4. Cálculo Manual Esperado

Para el circuito **GHZ_5q** en `ibm_marrakesh` con 5 qubits activos y 4 CNOTs:

1.  **Fidelidad de Puertas (Two-Qubit Solo)**:
    Con 4 CNOTs físicas con una tasa de error media de $e_{\text{CNOT}} \approx 0.0055$ ($0.55\%$):
    $$F_{\text{gate, manual}} = (1 - 0.0055)^4 = 0.9945^4 \approx 0.9782$$
2.  **Fidelidad de Readout (Medidos Solo)**:
    Con 5 qubits medidos, cada uno con un error de lectura de $e_{\text{readout}} \approx 0.012$ ($1.2\%$):
    $$F_{\text{readout, manual}} = (1 - 0.012)^5 = 0.988^5 \approx 0.9413$$
3.  **Fidelidad de Coherencia (Critical Path de Qubits Activos)**:
    Con una duración del critical path de $t_{\text{crit}} = 500\text{ ns} = 0.5 \times 10^{-6}\text{ s}$ y tiempos medios de coherencia de $T_1 \approx 180\ \mu\text{s}$ y $T_2 \approx 90\ \mu\text{s}$:
    $$-\frac{t_{\text{crit}}}{T_1} - \frac{t_{\text{crit}}}{T_2} = -\frac{0.5 \times 10^{-6}}{180 \times 10^{-6}} - \frac{0.5 \times 10^{-6}}{90 \times 10^{-6}} = -0.00278 - 0.00556 = -0.00834$$
    Para 5 qubits activos:
    $$F_{\text{coherence, manual}} = e^{5 \times (-0.00834)} = e^{-0.0417} \approx 0.9592$$
4.  **Fidelidad Total Esperada**:
    $$F_{\text{total, manual}} = F_{\text{gate, manual}} \times F_{\text{readout, manual}} \times F_{\text{coherence, manual}} \approx 0.9782 \times 0.9413 \times 0.9592 \approx 0.8832$$

Este valor de **$0.8832$** ($88.32\%$) es físicamente correcto y comparable con las fidelidades reales de Hellinger observadas en hardware real ($\approx 0.93 - 0.95$).
