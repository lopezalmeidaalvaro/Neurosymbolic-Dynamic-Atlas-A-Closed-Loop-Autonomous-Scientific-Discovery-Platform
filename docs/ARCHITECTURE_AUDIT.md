# Auditoría Arquitectónica del Sistema Científico Autónomo (Fase 0.1)

Este documento presenta una auditoría detallada de la arquitectura actual del repositorio `Neurosymbolic-Dynamic-Atlas` y `satelite` (AST-OS), identificando módulos, componentes reutilizables, dependencias físicas clásicas y áreas de acoplamiento crítico para preparar la transición hacia un marco multi-dominio (clásico, satelital y cuántico).

---

## 1. Estructura Completa del Repositorio

La disposición actual de directorios y subdirectorios de primer nivel en el proyecto se organiza como sigue:

- **`physics/`**: El núcleo de investigación en gravedad cuántica y sistemas dinámicos clásicos.
  - `agents/`: Contiene los agentes decisores simbólicos y físicos (`hypothesis_generator.py`, `theory_critic.py`, `metric_analyst.py`, `experiment_planner.py`).
  - `core/`: Utilidades principales del ciclo científico y neurosimbólico.
    - `autonomous/`: Orquestador y razonador central de la plataforma (`autonomous_scientist.py`, `llm_reasoner.py`, `sandbox_executor.py`).
    - `neurosymbolic/`: Redes neuronales informadas por la física (`pinn.py`, `neural_ode.py`).
    - `schemas/` y `io/`: Serialización y bases de conocimiento.
  - `benchmark/`: Suites de revalidación estadística y colapso gravitatorio.
  - `tests/`: Pruebas de regresión e integración.
- **`satelite/`**: Subsistema para control térmico espacial (AST-OS), acoplado a simulaciones de órbita y telemetry de naves.
  - `satellite/`: Lógica de estimación de órbita, simulaciones térmicas, UQ y validación.
- **`quantum/`**: Directorio preparado para el futuro dominio cuántico, actualmente conteniendo plantillas básicas de circuitos.
- **`docs/`**: Documentación técnica, física y observacional.

---

## 2. Inventario de Componentes Principales

Identificamos los módulos encargados de realizar tareas clave en la plataforma científica:

### A. Generadores de Hipótesis (Hypothesis Generators)
- **`physics/agents/hypothesis_generator.py` (Clase `HypothesisGenerator`):**
  - **Líneas 45-241:** Implementa un motor simbólico basado en Gramáticas Libres de Contexto (CFG) para proponer ansatzes matemáticos. Posee un fuerte acoplamiento a métricas de la RG (wormholes, warp drives y agujeros negros).
- **`physics/core/autonomous/llm_reasoner.py` (Clase `LLMReasoner`):**
  - **Líneas 337-395 (`generate_hypothesis`):** Consulta a LLMs para proponer hipótesis científicas estructuradas en JSON.

### B. Críticos y Evaluadores (Critics / Evaluators)
- **`physics/agents/theory_critic.py` (Clase `TheoryCritic`):**
  - **Líneas 24-178:** Evalúa la consistencia física analítica de las hipótesis simbólicas (condiciones de energía, horizontes, divergencia de curvatura central).
- **`physics/physics_sanity_engine.py` (Clase `PhysicsSanityEngine`):**
  - **Líneas 29-170:** Realiza validaciones de consistencia dimensional, límites físicos y leyes de conservación de energía.

### C. Motores de Simulación (Simulation Engines)
- **`physics/benchmark/run_inhomogeneous_collapse.py`:**
  - **Líneas 1-320:** Resolvedor de diferencias finitas en tiempo y espacio comóvil para el colapso gravitatorio modificado LTB-LQC.
- **`satelite/satellite/run_thermal_pipeline.py` y `run_warp_simulation.py`:**
  - **Líneas 1-180:** Simulaciones de redes térmicas de satélites en órbita y órbitas en eclipse.

### D. Memoria Científica (Memory)
- **`physics/scientific_memory_advanced.py` (Clase `ScientificMemoryAdvanced`):**
  - **Líneas 10-150:** Almacena, incrusta (embeddings) y recupera conocimiento científico previo.
- **`physics/knowledge_graph.py` (Clase `ScientificKnowledgeGraph`):**
  - **Líneas 20-300:** Integración con base de datos de grafos Neo4j para estructurar hipótesis, experimentos y veredictos.

### E. Benchmark y Reproducibilidad
- **`physics/benchmark/reproducibility_challenge.py`:**
  - **Líneas 20-830:** Orquesta la revalidación estadística completa sobre 30 semillas de colapso para problemas clásicos.
- **`physics/reproducibility_verification.py`:**
  - **Líneas 15-500:** Verifica que los resultados de la búsqueda de ecuaciones satisfagan las métricas de estabilidad y reproducibilidad.

### F. APIs y Configuración
- **`physics/core/config_manager.py` (Clase `ConfigManager`):**
  - **Líneas 5-80:** Carga y valida configuraciones YAML.
- **`physics/core/artifact_manager.py` (Clase `ArtifactManager`):**
  - **Líneas 5-110:** Centraliza el guardado de datos y reportes científicos en formato JSON/Markdown.
