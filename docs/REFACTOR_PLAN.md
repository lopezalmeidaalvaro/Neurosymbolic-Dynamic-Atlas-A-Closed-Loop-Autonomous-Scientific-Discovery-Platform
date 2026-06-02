# Plan de Refactorización Multi-Dominio (Fase 0.6 — 0.7)

Este documento detalla la estructura de directorios propuesta para independizar el motor de descubrimiento científico autónomo de los dominios físicos específicos (gravedad clásica, térmica satelital y circuitos cuánticos), y define un plan de tareas prioritarias (P0, P1, P2) con evaluación de riesgos y complejidad.

---

## 1. Estructura de Directorios Objetivo (Multi-Dominio)

Para soportar múltiples dominios de forma simultánea, proponemos reorganizar el repositorio de la siguiente forma:

```
├── core/                         # Motor de descubrimiento agnóstico
│   ├── abstractions/             # Contratos e interfaces abstractas
│   │   ├── base_module.py        # Interfaz BaseScientificModule
│   │   ├── base_generator.py     # Interfaz BaseHypothesisGenerator
│   │   └── base_critic.py        # Interfaz BaseCritic
│   ├── orchestration/            # Ciclo científico autónomo y APIs
│   │   ├── autonomous_scientist.py
│   │   ├── llm_reasoner.py
│   │   ├── sandbox_executor.py
│   │   ├── config_manager.py
│   │   └── artifact_manager.py
│   ├── memory/                   # Gestión de bases de datos y grafos
│   │   ├── knowledge_graph.py
│   │   └── scientific_memory.py
│   └── metrics/                  # Cálculo de ganancia epistémica y reportes
│       └── report_manager.py
│
├── physics/                      # Dominio de Gravedad Cuántica y RG clásica
│   ├── agents/                   # Implementaciones de HypoGen y TheoryCritic
│   │   ├── hypothesis_generator.py
│   │   └── theory_critic.py
│   ├── benchmark/                # Simuladores LTB-LQC y revalidación
│   └── tests/
│
├── satelite/                     # Dominio de Control Térmico Espacial (AST-OS)
│   ├── satellite/                # EKF, simuladores orbitales y térmicos
│   └── tests/
│
└── quantum/                      # Dominio de Circuitos y Algoritmos Cuánticos
    ├── circuits/                 # Simuladores cuánticos y generadores de puertas
    └── tests/
```

---

## 2. Mapa de Destino de los Módulos Actuales

| Módulo Actual | Acción Propuesta | Justificación Arquitectónica |
| :--- | :--- | :--- |
| `physics/core/base_module.py` | **Mover a `core/abstractions/`** | Debe convertirse en la interfaz base `BaseScientificModule` común para todos los dominios. |
| `physics/core/autonomous/autonomous_scientist.py` | **Mover a `core/orchestration/`** | Convertir en orquestador agnóstico, desacoplando los nombres de los datasets físicos y métodos. |
| `physics/core/autonomous/llm_reasoner.py` | **Mover a `core/orchestration/`** | Generalizar el constructor de prompts, inyectando las plantillas de prompts desde el dominio activo. |
| `physics/core/autonomous/sandbox_executor.py` | **Mover a `core/orchestration/`** | Permitir que cada dominio defina su conjunto de dependencias de Docker/Subprocess (`requirements.txt`). |
| `physics/agents/hypothesis_generator.py` | **Mantener en `physics/`** | Modificar para heredar de la nueva interfaz `BaseHypothesisGenerator`. Contiene reglas y plantillas exclusivas de la RG. |
| `physics/agents/theory_critic.py` | **Mantener en `physics/`** | Modificar para heredar de `BaseCritic`. Su lógica de validación de condiciones de energía depende totalmente de SymPy. |
| `physics/knowledge_graph.py` | **Mover a `core/memory/`** | El almacenamiento relacional en Neo4j es totalmente reutilizable para cualquier rama científica. |
| `physics/scientific_memory_advanced.py` | **Mover a `core/memory/`** | La gestión de embeddings vectoriales es genérica y agnóstica del dominio. |
| `physics/physics_sanity_engine.py` | **Mantener en `physics/`** | Conservar en el dominio físico clásico, ya que requiere SymPy y constantes físicas. |

---

## 3. Plan de Refactorización por Prioridades

### P0 — Imprescindible (Critical Refactoring)

#### Tarea 1: Creación de la capa de Abstracciones e Interfaces
- **Descripción:** Definir `BaseScientificModule`, `BaseHypothesisGenerator`, `BaseCritic` y `BaseSandbox` en `core/abstractions/` utilizando la librería estándar `abc`.
- **Archivos Afectados:** `physics/core/base_module.py` (migración), nuevos archivos en `core/abstractions/`.
- **Riesgo:** **Bajo**. No modifica lógica, solo define contratos.
- **Impacto Esperado:** Desacoplamiento inmediato de firmas y contratos.
- **Complejidad Estimada:** Baja (1-2 días).

#### Tarea 2: Generalización de `autonomous_scientist.py` y Migración
- **Descripción:** Mover el orquestador a `core/orchestration/`. Desacoplar las listas de datasets y métodos hardcodeados (líneas 143-156) pasándolas a través de archivos de configuración YAML específicos de dominio.
- **Archivos Afectados:** `physics/core/autonomous/autonomous_scientist.py` $\to$ `core/orchestration/autonomous_scientist.py`.
- **Riesgo:** **Medio**. Requiere asegurar que los imports de las suites de test no se rompan (usando redirección de módulos temporales).
- **Impacto Esperado:** El orquestador puede instanciar cualquier ciclo científico sin importar su dominio.
- **Complejidad Estimada:** Media (3-4 días).

---

### P1 — Recomendable (Domain Decoupling)

#### Tarea 3: Inyección de Prompts en `LLMReasoner`
- **Descripción:** Extraer las plantillas de prompts de hipótesis en `llm_reasoner.py` (líneas 337-385) y moverlas a archivos JSON/YAML bajo el dominio `physics/` y `quantum/`. `LLMReasoner` cargará estas plantillas de forma dinámica según el dominio activo.
- **Archivos Afectados:** `physics/core/autonomous/llm_reasoner.py`.
- **Riesgo:** **Bajo**. Requiere verificar que la estructuración JSON esperada por la API se mantenga intacta.
- **Impacto Esperado:** Flexibilidad absoluta para cambiar las directrices y reglas del LLM por dominio.
- **Complejidad Estimada:** Baja (2 días).

#### Tarea 4: Configuración de Dependencias de Sandbox
- **Descripción:** Permitir que `SandboxExecutor` reciba una lista de librerías requeridas por el experimento. En `physics` instalará `sympy`, mientras que en `quantum` instalará `qiskit` o `pennylane`.
- **Archivos Afectados:** `physics/core/autonomous/sandbox_executor.py`.
- **Riesgo:** **Bajo**. Afecta a la construcción del contenedor Docker o virtualenv temporal.
- **Impacto Esperado:** Evita instalar librerías pesadas e innecesarias en contenedores de prueba cruzados.
- **Complejidad Estimada:** Baja (2 días).

---

### P2 — Futura Mejora (Multi-domain Integration)

#### Tarea 5: Implementación del Piloto Cuántico (`quantum`)
- **Descripción:** Crear un agente crítico cuántico (`QuantumCritic`) y un generador cuántico (`QuantumHypoGen`) en `quantum/` que hereden de las interfaces base. Diseñar un experimento sandbox para optimizar un circuito de preparación de estado cuántico simple.
- **Archivos Afectados:** `quantum/circuits/` (nuevos archivos).
- **Riesgo:** **Bajo**. Es un desarrollo nuevo y aislado.
- **Impacto Esperado:** Validación empírica completa de la arquitectura multi-dominio.
- **Complejidad Estimada:** Media-Alta (1-2 semanas).
