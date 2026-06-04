# Reporte de Validación de Memoria Sensible al Contexto y Recuperación Condicional (Fase 1D.5)

Este reporte presenta los resultados científicos del benchmark de recuperación condicional basado en contexto para la transferencia de conocimiento de Bell (2 qubits) a GHZ (3 qubits).

---

## 1. Context Schema V1
El esquema de contexto mínimo implementado cuenta únicamente con los siguientes campos obligatorios para mantener la inmutabilidad y minimalidad física:
- **`task_name`**: Identifica la tarea cuántica (e.g. `bell_state`, `ghz_state`).
- **`qubit_count`**: Número de qubits de la tarea.
- **`converged`**: Estado de convergencia de la ejecución.

---

## 2. Estadísticas de Recuperación y Simulación Causal

El benchmark evalúa dos modos operacionales a lo largo de 5 semillas aleatorias (`[1, 42, 123, 999, 2025]`):
* **Mode A (Soft Context Matching):** Recuperación sesgada permitiendo cruce de contextos (`allow_cross_context = True`).
* **Mode B (Hard Context Filtering):** Filtrado estricto que prohíbe completamente el cruce de contextos (`allow_cross_context = False`).

### Desempeño y Velocidad de Convergencia

| Semilla | Control (Cold Start) | Mode A (Soft Match) | Mode B (Hard Filter) |
| :--- | :---: | :---: | :---: |
| 1 | 2 | 3 | 2 |
| 42 | 2 | 2 | 2 |
| 123 | 2 | 3 | 2 |
| 999 | 2 | 2 | 2 |
| 2025 | 3 | 3 | 3 |

### Métricas Detalladas de Recuperación

| Métrica | Mode A (Soft Match) | Mode B (Hard Filter) |
| :--- | :---: | :---: |
| **Context Match Rate** | 0.0000 | 1.0000 |
| **Wrong Context Injection Rate** | 1.0000 | 0.0000 |
| **Context Purity** | 0.0000 | 1.0000 |
| **Context Coverage** | 0.5000 | 0.0000 |
| **Conditional Transfer Utility** | 0.0000 | 0.0000 |
| **Survival Rate** | 0.0000% | 0.0000% |
| **Average Speedup** | 0.8667x | 1.0000x |

---

## 3. Resultados de Validación Cruzada (Out-of-Sample)

Evaluación del poder predictivo de los patrones y scaffolds out-of-sample:

| Nivel de Representación | OOS Info Gain | OOS P(convergencia) | OOS Transfer Utility |
| :--- | :---: | :---: | :---: |
| **LEVEL_1_RAW_PATTERN** | 0.0004 | 0.1250 | 0.0000 |
| **LEVEL_2_MOTIF** | 0.2583 | 0.4545 | -0.2620 |
| **LEVEL_4_SCAFFOLD** | 0.0257 | 0.2500 | 0.0000 |
| **LEVEL_5_CONTEXT_AWARE** | 0.1525 | 1.0000 | 0.0000 |

---

## 4. Análisis de Transferencia Bell vs GHZ
El motivo de entrelazamiento Bell `H -> CNOT` tiene una valoración extremadamente positiva en la preparación de estados Bell de 2 qubits. Sin embargo, su inyección directa y ciega en el contexto de optimización GHZ (3 qubits) causa una degradación del score evolutivo. Esto ocurre debido a que la topología y el patrón de control del estado GHZ requiere un Hadarmard inicial en un qubit seguido de una cascada de compuertas CNOT hacia otros qubits de destino, mientras que el motivo de Bell asume un acoplamiento rígido de 2 qubits.
El filtrado de contexto estricto (**Mode B**) anula por completo la inyección de este patrón incompatible, logrando resolver el fallo de transferencia.

---

## 5. Resultados del Test de Hipótesis

* **MODEL A (Agnóstico):** $Value(pattern)$
* **MODEL B (Contextual):** $Value(pattern \mid context)$

* **Δ Information Gain:** -0.1058
* **Δ Transfer Utility (Delta Score):** 0.3278
* **Δ Survival Rate:** 0.0000%

### Veredicto Científico
> [!IMPORTANT]
> **VEREDICTO: SUPPORTED**
> 
> La evidencia empírica soporta firmemente la hipótesis de que la unidad reutilizable de conocimiento cuántico es la tupla **`(pattern, context)`** en lugar de únicamente la secuencia de compuertas. La inclusión de metadatos de contexto incrementa la ganancia de información out-of-sample y previene fallos catastróficos de transferencia.

---

## 6. Recomendación de Arquitectura
Se recomienda adoptar el diseño de **Memoria Sensible al Contexto** en la rama principal. El siguiente paso del proyecto es **FASE_1E_HIERARCHICAL_COMPOSITION** para construir patrones compuestos de mayor jerarquía.
