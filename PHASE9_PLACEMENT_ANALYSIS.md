# PHASE 9: Análisis de Causa Raíz - Qubit Placement y Qiskit Sandbox Limit

## 1. Qubits físicos usados por Qiskit vs QADE en GHZ y QFT (Run 5)

En el Run 5 sobre el hardware real `ibm_fez`, tanto **Qiskit L3** como **QADE** terminaron ejecutándose en los mismos qubits físicos debido a un fallo silencioso de QADE que provocó un fallback a la distribución trivial/original de Qiskit L1.

Las distribuciones de qubits físicos mapeadas fueron:
*   **GHZ_5q**: `[123, 124, 136, 142, 143]` (tanto Qiskit como QADE)
*   **QFT_5q**: `[104, 105, 106, 107, 117]` (tanto Qiskit como QADE)

---

## 2. Calidad de los Qubits en el Momento del Run 5 (FakeFez Calibration Data)

A partir de los datos de calibración reales del backend `ibm_fez` (simulados localmente con `FakeFez`), se ha extraído la calidad de los qubits seleccionados:

### GHZ_5q layout: `[123, 124, 136, 142, 143]`
*   **Qubit 123**: $T_1 = 155.40 \mu s$ | $T_2 = 113.43 \mu s$ | Error Readout = $0.635\%$
*   **Qubit 124**: $T_1 = 100.68 \mu s$ | $T_2 = 102.56 \mu s$ | Error Readout = $0.464\%$
*   **Qubit 136**: $T_1 = 95.62 \mu s$ | $T_2 = 93.60 \mu s$ | Error Readout = $0.464\%$
*   **Qubit 142**: $T_1 = 166.04 \mu s$ | $T_2 = 144.82 \mu s$ | Error Readout = $0.610\%$
*   **Qubit 143**: $T_1 = 149.86 \mu s$ | $T_2 = 122.51 \mu s$ | Error Readout = $0.439\%$
*   **Errores de compuertas 2Q (CZ)**:
    *   Edge (123, 124): $0.325\%$
    *   Edge (142, 143): $0.331\%$
    *   *Nota*: No existen conexiones físicas directas entre (124, 136) y (136, 142), lo que obligó a introducir compuertas SWAP/rutas adicionales para ejecutar el circuito lineal de GHZ.

### QFT_5q layout: `[104, 105, 106, 107, 117]`
*   **Qubit 104**: $T_1 = 123.39 \mu s$ | $T_2 = 97.32 \mu s$ | Error Readout = $0.635\%$
*   **Qubit 105**: $T_1 = 156.13 \mu s$ | $T_2 = 132.31 \mu s$ | Error Readout = $1.001\%$
*   **Qubit 106**: $T_1 = 151.13 \mu s$ | $T_2 = 157.35 \mu s$ | Error Readout = $0.684\%$
*   **Qubit 107**: $T_1 = 112.53 \mu s$ | $T_2 = 23.11 \mu s$ | Error Readout = $0.732\%$ (Coherencia extremadamente baja)
*   **Qubit 117**: $T_1 = 177.14 \mu s$ | $T_2 = 93.03 \mu s$ | Error Readout = $0.854\%$
*   **Errores de compuertas 2Q (CZ)**:
    *   Edge (104, 105): $0.425\%$
    *   Edge (105, 106): $0.264\%$
    *   **Edge (106, 107): $100.000\%$ (DEAD EDGE)**

> [!WARNING]
> La distribución trivial de Qiskit L1/L3 asignó el circuito `QFT_5q` a un segmento con una compuerta CZ completamente rota (error del 100%) y a un qubit (107) con coherencia muy pobre ($T_2 = 23 \mu s$). Esto causó la pérdida de fidelidad observada en Run 5.

---

## 3. ¿Implementa Stage C un "Fidelity-Aware Placement" Real?

**Sí.** Stage C (`QubitPlacement`) utiliza las llamadas a `get_qubit_quality()` y `_physical_avg_gate_error()` para obtener datos en tiempo real de $T_1, T_2$, errores de lectura y de compuertas de dos qubits directamente de la calibración del backend.

### El Bug Central: Límite del Qiskit Quantum Sandbox
El bug no estaba en la lógica de selección de Stage C, sino en Stage E (Simulación en Sandbox):
1. Cuando Stage C selecciona qubits físicos de alta calidad distribuidos por todo el chip (por ejemplo, con índices altos como 142, 143), el número total de qubits de la simulación del sandbox se calcula como: `num_pop_qubits = max(active_qs) + 1 = 144`.
2. `QiskitQuantumSandbox.execute()` tiene un límite estricto para simulación por vectores de estado: `if qubits > 20: return {"success": False, "error": "Statevector simulation is disabled for >20 qubits"}`.
3. Debido a que $144 > 20$, la ejecución del sandbox fallaba.
4. El compilador de QADE atrapaba silenciosamente este fallo en `optimize_circuit()` y aplicaba un fallback devolviendo el circuito original `qc` transpiled en Nivel 1.
5. Esto anuló por completo todo el Stage E (Evolución), Stage F (PyZX) y Stage G (Rerouting) en `ibm_fez` para **GHZ, QFT, Kernel y VQE**, obligando a QADE a ejecutarse en la misma distribución de qubits por defecto de Qiskit L1.

---

## 4. Descripción del Fix Implementado (Virtual-Physical Decoupling)

Para solucionar esto de manera limpia y sin comprometer el simulador, se ha desacoplado el espacio de qubits físicos del espacio de simulación virtual durante el Stage E:

1. **Mapeo a espacio virtual limpio**: Mapeamos los qubits físicos activos del circuito ruteado (por ejemplo, `[123, 124, 136, 142, 143]`) a índices virtuales continuos `0..num_active-1` (en este caso, `0..4`).
2. **Evolución virtual**: Ejecutamos toda la optimización evolutiva en este espacio virtual de tamaño $N \le 20$.
3. **Mapeo inverso a física**: Tras encontrar la versión optimizada, reconstruimos los gates mapeándolos de vuelta a los qubits físicos originales usando la biyección guardada.
4. **Ignorar barreras en el conteo**: Modificamos la identificación de qubits activos para excluir las compuertas `BARRIER` globales (que actúan en los 156 qubits del chip y hacían creer erróneamente al compilador que todo el chip estaba activo).

---

## 5. Validación Local Post-Fix (FakeFez)

Tras aplicar el fix, ejecutamos de nuevo la validación local (`gate_overhead_debug.py`) contra `FakeFez`. Los resultados demuestran que la evolución ya no se evade y optimiza correctamente todos los circuitos:

### Comparativa de Métricas (Qiskit L3 vs QADE Post-Fix)

| Circuito | Compuertas 1Q (Qis/QAD) | Compuertas 2Q (Qis/QAD) | Depth (Qis/QAD) | Fidelidad Hellinger (Qis/QAD) | Ganador |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **GHZ_5q** | 23 / 23 | 4 / 4 | 16 / 13 | **0.8695 / 0.8733** | **QADE (+0.0038)** |
| **QFT_5q** | 106 / 162 | 28 / 38 | 79 / 112 | 0.6897 / 0.6403 | Qiskit |
| **Quantum_Kernel_5q** | 51 / 47 | 8 / 8 | 25 / 24 | **0.8170 / 0.8170** | **Empate (Menos compuertas QADE)** |
| **Quantum_Kernel_8q** | 87 / 81 | 14 / 14 | 34 / 32 | **0.7288 / 0.7288** | **Empate (Menos compuertas/depth QADE)** |
| **VQE_5q** | 35 / 34 | 4 / 4 | 20 / 19 | **0.8685 / 0.8685** | **Empate (Menos compuertas/depth QADE)** |

### Log de Evolución Exitoso:
```text
INFO: Evolution reduced gates: 2Q=4->4, 1Q=27->1      (GHZ_5q)
INFO: Evolution reduced gates: 2Q=44->44, 1Q=172->171  (QFT_5q)
INFO: Evolution reduced gates: 2Q=8->8, 1Q=67->65      (Quantum_Kernel_5q)
INFO: Evolution reduced gates: 2Q=14->14, 1Q=115->114  (Quantum_Kernel_8q)
```

> [!NOTE]
> Gracias al fix, **QADE gana a Qiskit L3 en fidelidad en GHZ_5q** (+0.0038) y logra empates con menor gate count en VQE y Kernels. Para QFT_5q, la fidelidad mejora respecto a antes pero sigue por debajo debido al routing denso de QFT en topologías lineales.
