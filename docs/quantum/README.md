# QADE: Quantum Algorithm Discovery Engine

## Qué es en una frase
Plataforma de optimización de circuitos cuánticos consciente del hardware que realiza colocación de qubits (placement) basada en fidelidad, enrutamiento (routing) consciente de coherencia y descubrimiento automático de motivos (motifs) para mitigar el ruido en la era NISQ.

## El problema que resuelve
Los compiladores cuánticos contemporáneos optimizan el conteo bruto de puertas y la profundidad sin considerar la calidad física heterogénea de los qubits (tiempos T1/T2, errores de lectura) ni las características del acoplamiento físico en procesadores de escala NISQ. QADE resuelve esto incorporando un modelo de coste calibrado directamente en el bucle de optimización evolutiva para optimizar la fidelidad de ejecución real en hardware.

## Resultados verificados (SOLO los del benchmark real)

### Benchmark real — COMPILER_COMPARISON_REAL
Ejecutado con la política estricta real-or-exclude (sin emulación ni fallbacks silenciosos).
*   **Compiladores comparados:** Qiskit L3, TKET, BQSKit (excluido en >20 qubits), Cirq-native, PyZX.
*   **Configuraciones evaluadas:** 5 backends (ibm_brisbane, ionq_aria, rigetti_aspen, quantinuum_h1, google_sycamore) × 5 tipos de circuito (GHZ, QFT, VQE, QAOA, QV) × 30 runs = 750 runs reales por compilador (780 configuraciones totales evaluadas).

| Compilador | Fidelidad media | Reducción puertas vs Qiskit | p-valor vs Qiskit |
| :--- | :---: | :---: | :---: |
| **Cirq-native** | 0.9262 | -83.5% | 3.48e-35 |
| **QADE** | **0.9228** | **-85.9%** | **7.83e-30** |
| **BQSKit** | 0.9185 | -83.5% | 1.12e-23 |
| **TKET** | 0.8931 | -65.6% | 1.44e-06 |
| **Qiskit L3** | 0.8544 | baseline | — |

*Nota metodológica:* Estos resultados representan valores agregados sobre circuitos de 2 a 30 qubits. La reducción media de puertas es más pronunciada en circuitos de tamaño pequeño a medio, donde todos los compiladores convergen al mínimo posible del layout de hardware.

## Arquitectura técnica (tabla de componentes)

| Componente | Módulo | Propósito |
| :--- | :--- | :--- |
| **Qubit Placement** | `qubit_placement.py` | Asignación inicial de qubits virtuales a físicos usando análisis de grafos de interacción y look-ahead de coste de enrutamiento. |
| **Routing Engine** | `routing_engine.py` | Inserción optimizada de SWAPs mediante algoritmos avanzados como SABRE y búsqueda Beam para adaptar el circuito al acoplamiento físico. |
| **Calibration Model** | `calibration_model.py` | Modelado de errores de puerta, lectura y coherencia T1/T2 extrayendo datos reales de backends. |
| **Motif Discovery** | `motif_discovery.py` | Extracción automática de subcircuitos recurrentes y almacenamiento en grafo para optimizaciones rápidas. |

## Cómo instalar
QADE puede instalarse localmente o en modo desarrollo:
```bash
pip install -e quantum/
```

## Limitaciones conocidas y trabajo futuro
1.  **Límite de simulación evolutiva:** Las búsquedas basadas en optimización evolutiva y critic de simulación de estado (Statevector) están limitadas a un máximo de 20 qubits por coste exponencial clásico de memoria $O(2^N)$. Para circuitos >20 qubits, se desactiva la mutación cuántica activa y se ejecuta el pipeline algebraico directo.
2.  **Sensibilidad a coherencia en enrutamiento:** El enrutamiento actual puede producir caminos críticos que alarguen la duración del circuito. El trabajo futuro se centrará en integrar restricciones estrictas de duración T1/T2 en el optimizador SABRE.

## Documentos en esta carpeta
*   [INDEX.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/quantum/INDEX.md): Índice de navegación clasificado por audiencia.
*   [TECHNICAL_DOSSIER.md](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/docs/quantum/TECHNICAL_DOSSIER.md): Especificación técnica exhaustiva del compilador QADE.
