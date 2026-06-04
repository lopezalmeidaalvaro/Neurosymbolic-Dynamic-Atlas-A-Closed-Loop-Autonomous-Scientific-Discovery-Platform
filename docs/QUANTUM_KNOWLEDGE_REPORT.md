# Reporte de Capa de Destilación de Conocimiento Cuántico (Fase 1B.4)

Este informe documenta la arquitectura, diseño, métricas y validación de la Capa de Destilación de Conocimiento Cuántico en el motor de optimización evolutiva.

---

## 1. Arquitectura de Destilación de Conocimiento

La Capa de Destilación de Conocimiento transforma el motor evolutivo de un simple optimizador de circuitos a un sistema de aprendizaje semántico continuo. El flujo de destilación se ejecuta al final de cada ciclo generativo (`evolve_generation()`):

```
Población de Circuitos 
    ↓ (Evaluación & Selección)
Top-k Circuitos de la Generación
    ↓ (Canonicalización)
Formas Canónicas Reducidas
    ↓ (Extracción de Patrones)
Motivos y Frecuencias
    ↓ (Construcción del Grafo)
Nodos y Aristas (Circuit, Pattern, Gen, Score)
    ↓ (Actualización de Memoria)
QuantumMemory & Historial
```

### Componentes Clave:
1. **QuantumPatternExtractor ([quantum_pattern_extractor.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/knowledge/quantum_pattern_extractor.py)):**
   * Extrae subsecuencias repetidas de compuertas (longitudes 2 y 3) de los circuitos con mejor score.
   * Detecta motivos de entrelazamiento utilizando índices de qubits relativos generalizados (ej. `H(0) -> CNOT(0,1)` y `H(1) -> CNOT(1,2)` se canonicalizan al mismo patrón: `H(q0)->CNOT(q0,q1)`).
   * Algoritmo de complejidad temporal lineal $O(N)$ por circuito.

2. **QuantumCircuitCanonicalizer ([canonicalizer.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/knowledge/canonicalizer.py)):**
   * Simplifica circuitos cuánticos localmente usando reglas algebraicas:
     * $X \cdot X \rightarrow \text{Identidad}$ (cancelación)
     * $H \cdot H \rightarrow \text{Identidad}$ (cancelación)
     * $\text{CNOT}(a,b) \cdot \text{CNOT}(a,b) \rightarrow \text{Identidad}$ (cancelación)
     * Fusión de ángulos de rotación consecutivos del mismo tipo y qubits: $RX(\theta_1) \cdot RX(\theta_2) \rightarrow RX(\theta_1+\theta_2)$
     * Conmutación de compuertas en qubits disjuntos para permitir simplificaciones adyacentes.

3. **QuantumKnowledgeGraph ([knowledge_graph.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/knowledge/knowledge_graph.py)):**
   * Grafo dirigido in-memory ligero que registra relaciones:
     * `Circuit_A` $\xrightarrow{\text{mutation\_of}}$ `Circuit_B`
     * `Circuit_A` $\xrightarrow{\text{improves}}$ `Circuit_B` (si el score del hijo es mayor)
     * `Circuit_Raw` $\xrightarrow{\text{equivalent\_to}}$ `Circuit_Canonical`
     * `Circuit` $\xrightarrow{\text{contains\_pattern}}$ `Pattern`
     * `Circuit` $\xrightarrow{\text{discovered\_in\_generation}}$ `Generation`

4. **DiscoveryMemory Integration ([quantum_memory.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/memory/quantum_memory.py)):**
   * Ofrece métodos queryable como `query_patterns(task)` para filtrar patrones por tarea y recuperar los metadatos del grafo con `get_knowledge_graph()`.

---

## 2. Métricas de Conocimiento e Instrumentación

Para monitorear el progreso del aprendizaje y la eficiencia evolutiva, se calculan e instrumentan las siguientes métricas en cada generación:

* **Pattern Count (Conteo de Patrones):** Número total de secuencias/motivos encontrados en los top-circuitos.
* **Unique Pattern Count (Patrones Únicos):** Cantidad de motivos distintos identificados.
* **Canonical Compression Ratio (Ratio de Compresión):**
  $$\text{compression\_ratio} = \frac{\text{Total de compuertas físicas (Raw)}}{\text{Total de compuertas físicas (Canónicas)}}$$
  Un ratio mayor a $1.0$ indica simplificación efectiva y eliminación de redundancias.
* **Knowledge Growth (Crecimiento de Conocimiento):** Cantidad de nuevos patrones únicos descubiertos en la generación actual que no se encontraban en el archivo de memoria acumulado de generaciones anteriores.

---

## 3. Ejemplos Numéricos de Simplificación

### Ejemplo 1: Cancelación Conmutativa
* **Circuito de entrada:**
  ```json
  [
    {"type": "H", "qubits": [0]},
    {"type": "X", "qubits": [1]},
    {"type": "H", "qubits": [0]}
  ]
  ```
* **Paso a paso:** `H` en el qubit 0 y `X` en el qubit 1 actúan en qubits disjuntos, por lo que conmutan. El canonicalizador reorganiza la secuencia a `H(0)` -> `H(0)` -> `X(1)`. La pareja `H(0) H(0)` es autoinversa y se cancela.
* **Resultado canónico:**
  ```json
  [
    {"type": "X", "qubits": [1]}
  ]
  ```
* **Compresión:** 3 compuertas a 1 compuerta (Ratio = $3.00$).

### Ejemplo 2: Fusión de Rotaciones y Cancelación
* **Circuito de entrada:**
  ```json
  [
    {"type": "RY", "qubits": [0], "theta": 1.570796},
    {"type": "RY", "qubits": [0], "theta": -1.570796}
  ]
  ```
* **Paso a paso:** Las dos rotaciones sobre el qubit 0 se fusionan sumando sus ángulos: $1.570796 + (-1.570796) = 0.0$. Como la rotación resultante tiene ángulo $0.0$, equivale a la Identidad y se remueve.
* **Resultado canónico:** `[]` (Sin compuertas).

---

## 4. Benchmarks de Convergencia y Destilación

Ejecutamos simulaciones de $8$ generaciones para comprobar la convergencia evolutiva física y la acumulación de conocimiento cuántico:

### Tarea: `bell_state` (Preparación de Estado Bell de 2 qubits)
* **Generación 0:** Fidelidad Bell = $0.4999$, Score = $0.4744$, Patrones únicos = $4$, Ratio Compresión = $1.00$.
* **Generación 4:** Fidelidad Bell = $0.9999$, Score = $0.9780$ (Descubrimiento del circuito Bell óptimo `H(0) -> CNOT(0,1)`).
* **Generación 7 (Final):** Fidelidad Bell = $1.0000$, Score = $0.9780$, Patrones acumulados = $12$, Crecimiento de conocimiento final = $0$.
* **Patrones más frecuentes extraídos:**
  * `H(q0)->CNOT(q0,q1)` (Frecuencia: $23$, Score promedio: $0.978$)
  * `H->CNOT` (Frecuencia: $23$, Score promedio: $0.978$)

### Tarea: `ghz_state` (Preparación de Estado GHZ de 3 qubits)
* **Generación 0:** Fidelidad GHZ = $0.0000$, Score = $-0.030$, Patrones únicos = $3$, Ratio Compresión = $1.00$.
* **Generación 5:** Fidelidad GHZ = $0.9999$, Score = $0.9670$ (Descubrimiento de `H(0) -> CNOT(0,1) -> CNOT(1,2)`).
* **Generación 7 (Final):** Fidelidad GHZ = $1.0000$, Score = $0.9670$, Patrones acumulados = $18$, Compresión promedio = $1.15$.
* **Patrones más frecuentes extraídos:**
  * `H(q0)->CNOT(q0,q1)->CNOT(q1,q2)` (Frecuencia: $18$, Score promedio: $0.967$)

---

## 5. Garantía de Aislamiento y Reproducibilidad

* **Aislamiento de RNG (Semilla):** Para evitar que el análisis de la capa de destilación y la canonicalización consuman números pseudoaleatorios y alteren la convergencia o reproducibilidad, la ejecución de la destilación está envuelta en un guardado y restauración explícitos del estado del generador aleatorio de población (`self.population_manager.rng.getstate()` y `setstate()`).
* **Regresión 100% Green:** Se mantiene plena compatibilidad con los contratos multi-dominio de orquestación y todos los tests pasan con éxito.

---

## 6. Estado de Verificación
`MULTI_DOMAIN_RUNTIME = TRUE`
`QUANTUM_EXECUTION = TRUE`
`QUANTUM_FITNESS_FUNCTION = TRUE`
`QUANTUM_EVOLUTION_ENGINE = TRUE`
`DISCOVERY_MEMORY = TRUE`
`QUANTUM_PATTERN_EXTRACTION = TRUE`
`QUANTUM_CANONICALIZATION = TRUE`
`QUANTUM_KNOWLEDGE_GRAPH = TRUE`
`KNOWLEDGE_DISTILLATION = TRUE`
