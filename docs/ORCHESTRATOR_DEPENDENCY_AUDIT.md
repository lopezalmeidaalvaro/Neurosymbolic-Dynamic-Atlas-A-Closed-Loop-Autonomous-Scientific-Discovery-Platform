# Auditoría de Dependencias del Orquestador (Fase 0D.1)

Este documento detalla la auditoría de dependencias acopladas en `autonomous_scientist.py`, identificando instanciaciones directas, imports concretos, dependencias ocultas, de configuración y datasets hardcodeados.

---

## 1. Mapeo de Dependencias Acopladas

### A. Instanciaciones Directas
- **`LLMReasoner` (Línea 32):** Instanciación directa en el constructor:
  ```python
  self.llm = LLMReasoner(provider=llm_provider)
  ```
- **`SandboxExecutor` (Línea 33):** Instanciación directa en el constructor:
  ```python
  self.sandbox = SandboxExecutor(use_docker=use_docker)
  ```
- **`ScientificKnowledgeGraph` (Líneas 49-51):** Instanciación condicional directa dentro del constructor si no se inyecta un grafo de conocimiento previo:
  ```python
  self.kg = ScientificKnowledgeGraph(uri="bolt://localhost:7687", ...)
  ```

### B. Imports Concretos y Locales
- **Imports en Cabecera (Líneas 12-13):**
  ```python
  from physics.core.autonomous.llm_reasoner import LLMReasoner
  from physics.core.autonomous.sandbox_executor import SandboxExecutor
  ```
- **Imports en Métodos (Líneas 46 y 317):**
  ```python
  from knowledge_graph import ScientificKnowledgeGraph  # En constructor
  from scientific_guard import sanitize_hypothesis      # En update_knowledge_graph
  ```

### C. Dependencias Ocultas
- **Base de Datos SQLite (`scientific_kb.db`, Líneas 65-101):** El orquestador interactúa directamente con SQLite y realiza consultas SQL directas en lugar de usar un DAO o componente de abstracción de almacenamiento (`BaseMemory`).
- **Cálculo de Ganancia Epistémica (Línea 10):** Requiere de la librería matemática `math` para operaciones de logaritmo base 2 en la entropía de Shannon.

### D. Dependencias de Configuración
- **Conexiones Hardcodeadas (Líneas 49-51):** Valores fijos para Neo4j:
  ```python
  uri="bolt://localhost:7687", user="neo4j", password="password"
  ```
- **Parámetros de Sandbox (Líneas 234-238):** Parámetros fijos pasados al experimento en el sandbox:
  ```python
  "noise_level": 0.05, "timesteps": 1000, "bifurcation_sweep": True
  ```

### E. Datasets y Métodos Hardcodeados (Líneas 143-156)
- **Datasets:** `"synthetic_lorenz"`, `"synthetic_rossler"`, `"ecg_data"`, `"ucr_datasets"`.
- **Métodos:** `"topological"`, `"geometric"`, `"koopman"`, `"symbolic"`.
- **Observaciones de Contexto (Línea 160):** `"Dynamic chaos and nonlinear behaviors under different noise regimes."`.

---

## 2. Impacto de la Auditoría
Este acoplamiento impide que `autonomous_scientist.py` sea utilizado en el dominio cuántico o en control térmico satelital, ya que asume de manera fija la existencia de variables clásicas y la inicialización de agentes específicos de física de relatividad general. La introducción de inversión de dependencias y de un cargador de configuraciones YAML desacoplará completamente este orquestador.
