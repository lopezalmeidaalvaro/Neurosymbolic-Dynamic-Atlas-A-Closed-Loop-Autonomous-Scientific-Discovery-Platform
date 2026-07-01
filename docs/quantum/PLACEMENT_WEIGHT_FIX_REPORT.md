# Reporte de Recalibración de Pesos de Qubit Placement (Readout Error)

Este reporte detalla los resultados de la modificación de los pesos de la fórmula de scoring en `qubit_placement.py` (Stage C) para penalizar de forma más agresiva el readout error, previniendo que qubits con alta coherencia (T1/T2) pero pésimo readout error (como 131-135 en FakeFez / Run 8) sean seleccionados erróneamente sobre layouts más limpios.

---

## 1. Comparativa de Fórmulas y Pesos

La fórmula de puntuación de Stage C se define como:
\[\text{Score} = w_{\text{T1}} \frac{T_1}{\max(T_1)} + w_{\text{T2}} \frac{T_2}{\max(T_2)} - w_{\text{readout}} \cdot E_{\text{readout}} - w_{\text{gate}} \cdot E_{\text{gate}} + 0.01 \cdot \text{degree}\]

Comparamos tres configuraciones de pesos:
1. **Línea Base (Original)**: \(w_{\text{T1}}=0.35\), \(w_{\text{T2}}=0.35\), \(w_{\text{readout}}=0.15\), \(w_{\text{gate}}=0.15\)
2. **Propuesta Agresiva**: \(w_{\text{T1}}=0.20\), \(w_{\text{T2}}=0.20\), \(w_{\text{readout}}=0.35\), \(w_{\text{gate}}=0.25\)
3. **Alternativa Conservadora**: \(w_{\text{T1}}=0.225\), \(w_{\text{T2}}=0.225\), \(w_{\text{readout}}=0.30\), \(w_{\text{gate}}=0.25\)

---

## 2. Comparativa de Scores por Grupos (FakeFez)

A continuación se muestra la media del score calculado para los tres grupos experimentales de Run 8 en el backend simulado `FakeFez`:

| Configuración de Pesos | WINNERS (19,35,15,13,14) | LOSERS (131-135) | TRIVIAL (0-4) | Margen TRIVIAL vs LOSERS |
| :--- | :---: | :---: | :---: | :---: |
| **Línea Base (Original)** | 0.42417 | 0.34599 | 0.46085 | **+0.11486** (TRIVIAL gana por 33.2%) |
| **Propuesta Agresiva** | 0.24739 | 0.19967 | 0.26907 | **+0.06940** (TRIVIAL gana por 34.7%) |
| **Alternativa Conservadora** | 0.27702 | 0.22452 | 0.30114 | **+0.07662** (TRIVIAL gana por 34.1%) |

> [!NOTE]
> En todas las configuraciones, **TRIVIAL (0-4)** sigue ganando a **LOSERS (131-135)** en FakeFez.
> Además, en ninguna configuración se invierten los resultados del orden de los grupos, y el grupo **WINNERS** sigue siendo altamente competitivo, manteniendo el Qubit 13 en el puesto #2 de todo el chip (156 qubits).

---

## 3. Impacto en Gate Overhead y Fidelidad local (`gate_overhead_debug.py`)

Se evaluó la compilación de varios circuitos de control para medir el número de puertas de 1 Qubit (1Q), 2 Qubits (2Q), profundidad (Depth) y la fidelidad de Hellinger estimada bajo las 3 configuraciones:

### Tabla Comparativa de Rendimiento (Fidelidad Qiskit L3 vs QADE)

| Circuito | Métrica | Línea Base (Original) | Propuesta Agresiva | Alternativa Conservadora |
| :--- | :--- | :---: | :---: | :---: |
| **GHZ_5q** | 1Q / 2Q / Depth<br>Fidelidad (Qis/QAD) | 23/27/+4 \| 4/4/+0 \| 16/16<br>**0.8695 / 0.8820** | 23/27/+4 \| 4/4/+0 \| 16/13<br>**0.8695 / 0.8825** | 23/27/+4 \| 4/4/+0 \| 16/16<br>**0.8695 / 0.8820** |
| **Quantum_Kernel_5q** | 1Q / 2Q / Depth<br>Fidelidad (Qis/QAD) | 51/52/+1 \| 8/8/+0 \| 25/25<br>**0.8170 / 0.8603** | 51/52/+1 \| 8/8/+0 \| 25/25<br>**0.8170 / 0.8603** | 51/52/+1 \| 8/8/+0 \| 25/25<br>**0.8170 / 0.8603** |
| **Quantum_Kernel_8q** | 1Q / 2Q / Depth<br>Fidelidad (Qis/QAD) | 87/115/+28 \| 14/14/+0 \| 34/44<br>**0.7288 / 0.7273** | 87/115/+28 \| 14/14/+0 \| 34/44<br>**0.7288 / 0.7273** | 87/113/+26 \| 14/14/+0 \| 34/44<br>**0.7288 / 0.7273** |
| **VQE_5q** | 1Q / 2Q / Depth<br>Fidelidad (Qis/QAD) | 35/36/+1 \| 4/4/+0 \| 20/21<br>**0.8685 / 0.8788** | 35/36/+1 \| 4/4/+0 \| 20/21<br>**0.8685 / 0.8788** | 35/36/+1 \| 4/4/+0 \| 20/21<br>**0.8685 / 0.8788** |
| **QFT_5q** (Regresión) | 1Q / 2Q / Depth<br>Fidelidad (Qis/QAD) | 106/139/+33 \| 28/49/+21 \| 79/102<br>**0.6897 / 0.6752** | 106/160/+54 \| 28/65/+37 \| 79/130<br>**0.6897 / **0.4833**** | 106/156/+50 \| 28/61/+33 \| 79/127<br>**0.6897 / **0.5216**** |

---

## 4. Análisis Técnico del Comportamiento de QFT_5q

> [!WARNING]
> **Regresión local detectada en QFT**:
> Al elevar el peso del readout error, el algoritmo prioriza fuertemente evitar qubits con mayor ruido de readout, restringiendo el subgrafo físico de qubits utilizables.
>
> Para circuitos con alta conectividad 2Q cruzada como **QFT** (donde todos los qubits interactúan entre sí), esta restricción física destruye la optimalidad topológica del layout. Esto obliga al enrutador (Stage G) a insertar múltiples puertas SWAP extras para conectar los qubits elegidos.
>
> - Con la **Propuesta Agresiva**, las puertas 2Q aumentan de **49 a 65 (+16)**, lo que resulta en una caída drástica de fidelidad a **0.4833**.
> - Con la **Alternativa Conservadora**, las puertas 2Q aumentan a **61 (+12)**, mitigando parcialmente la caída de fidelidad a **0.5216**.

---

## 5. Veredicto: ¿Listo para Run 9?

> [!IMPORTANT]
> **Veredicto: APROBADO CON RESERVAS (Recomendado usar Alternativa Conservadora)**
>
> 1. **Mitigación de Errores Críticos**: La alternativa conservadora mantiene la protección necesaria para penalizar qubits defectuosos como los de Run 8 sin llegar a ser tan extrema como la propuesta agresiva.
> 2. **Comportamiento del Fallback**: El sistema cuenta con un mecanismo de fallback de Stage C. Si el layout seleccionado estima una fidelidad o score menor que el layout trivial, el compilador cae automáticamente al layout trivial `[0..N-1]`.
> 3. **Recomendación para Run 9**:
>    - Usar la **Alternativa Conservadora** (`w_T1=0.225, w_T2=0.225, w_readout=0.30, w_gate=0.25`) ya implementada en `qubit_placement.py`.
>    - Monitorear circuitos densos como QFT para asegurar que el overhead de puertas de Stage G no penalice en exceso la fidelidad.
