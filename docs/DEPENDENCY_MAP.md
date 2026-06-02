# Mapa de Dependencias y Acoplamiento del Sistema (Fase 0.2 — 0.5)

Este documento detalla el análisis de acoplamiento de los módulos clave, define abstracciones reutilizables, mapea dependencias externas y analiza el grado de acoplamiento físico en el orquestador principal.

---

## 1. Tabla de Acoplamiento de Módulos Clave

Analizamos los tres archivos centrales del sistema para clasificar su acoplamiento con la física clásica y la Gravedad General (RG):

| Archivo | Tipo / Ubicación | Dependencias Principales | Nivel de Acoplamiento | Evidencia de Código |
| :--- | :--- | :--- | :---: | :--- |
| **`physics/agents/hypothesis_generator.py`** | Módulo de Agente | `random`, `re`, `pathlib`, `knowledge_graph.json` | **SEMI_COUPLED** | **Líneas 55-109:** Define las reglas de la CFG. Aunque la estructura de la gramática es genérica, las producciones específicas contienen plantillas explícitas para wormholes (`pow(r,-1.5)`), warp drives (`tanh(5.0*(r-0.5))`) y regularizaciones de QG (`pow(r,3)/(pow(r,3)+Const)`). |
| **`physics/agents/theory_critic.py`** | Módulo de Agente | `numpy`, `sympy`, `parse_expr` | **HARD_COUPLED** | **Líneas 70-166:** Implementa validaciones analíticas acopladas a la RG clásica. Evalúa condiciones de garganta de wormhole (`b(r0) == r0`), condiciones de flaring-out (`b'(r0) < 1.0`), la densidad efectiva de la WEC (`b'/(8*pi*r^2)`) y el escalar de Ricci de agujeros negros regulares. |
| **`physics/core/autonomous/autonomous_scientist.py`** | Orquestador | `sqlite3`, `json`, `llm_reasoner`, `sandbox_executor` | **SEMI_COUPLED** | **Líneas 143-156 (`build_context`):** Aunque el ciclo de descubrimiento es lógicamente abstracto, contiene nombres hardcodeados de datasets físicos ("synthetic_lorenz", "ecg_data") y métodos ("topological", "koopman", "symbolic"). |

---

## 2. Análisis de Abstracciones Reutilizables

Identificamos los candidatos principales para convertirse en interfaces abstractas compartidas:

### A. `BaseHypothesisGenerator`
- **Componentes Reutilizables:** Algoritmos de mutación genética, cálculo de distancia de Levenshtein para similitud (`levenshtein_distance`, líneas 22-38) y el resolvedor recursivo de CFG (`_generate_raw`, líneas 111-129).
- **Métodos Reutilizables:** `_mutate()`, `_clean_expression()`, `similarity_score()`.
- **Métodos Dependientes del Dominio:** `propose()` (especialmente la sección de plantillas de agujeros negros `metric_type == "black_hole"` en líneas 191-214).

### B. `BaseCritic`
- **Componentes Reutilizables:** Clase base para verdicts de hipótesis, validaciones numéricas en grids coordenados.
- **Métodos Reutilizables:** `validate()` a nivel de firma de interfaz y capturador de excepciones aritméticas.
- **Métodos Dependientes del Dominio:** Toda la lógica de cálculo de tensores y derivadas analíticas de SymPy (`validate()`, líneas 58-166).

### C. `BaseSandbox`
- **Componentes Reutilizables:** La clase `SafetyVisitor` basada en AST para inspección estática del código (líneas 50-131) y la lógica de creación de directorios temporales (`create_sandbox_environment`, líneas 25-47).
- **Métodos Reutilizables:** `validate_code_safety()`, `execute()`.
- **Métodos Dependientes del Dominio:** La lista de librerías instalables en Docker (`Dockerfile` en línea 314) y el PYTHONPATH del subprocess.

### D. `BaseMemory`
- **Componentes Reutilizables:** Manejo de embeddings de texto, persistencia local en SQLite y conexiones a base de datos de grafos Neo4j.
- **Métodos Reutilizables:** `_init_local_db()`, `update_knowledge_graph()`.
- **Métodos Dependientes del Dominio:** Nombres de las tablas y campos relacionales físicos (`prediction`, `confidence_prior`).

---

## 3. Auditoría de Dependencias Externas

### Dependencias Clásicas Comunes:
- **`numpy` / `scipy`:** Utilizados globalmente en simuladores de colapso, resolvedores ODE, y análisis topológicos.
- **`sympy`:** El motor matemático algebraico para derivadas analíticas, cálculo de curvaturas y asintóticas.
- **`pytorch` (`torch`):** Empleado en `pinn.py` y `neural_ode.py` para aproximar potenciales continuos.

### Preguntas Clave:

1. **¿Puede el sistema funcionar sin SymPy?**
   **Sí.** El orquestador principal (`autonomous_scientist.py`), la base de datos de conocimiento y las herramientas de análisis de series temporales (homología persistente, Koopman) no importan ni dependen de SymPy. En un dominio cuántico, los circuitos y Hamiltonianos pueden formularse de manera matricial numérica pura sin requerir álgebra simbólica continua.
   
2. **¿Qué porcentaje del código depende directamente de SymPy?**
   Aproximadamente el **`10%`** de los archivos Python del dominio `physics/` importan `sympy` (15 de ~150 archivos). Está confinado a validadores analíticos, calculadores de curvatura y equivalencias del scorer.
   
3. **¿Qué porcentaje depende de física clásica?**
   Cerca del **`50%`** del código total (40% de `physics/` enfocado en wormholes/warp drives y 100% de `satelite/` enfocado en termodinámica clásica de naves).

---

## 4. Análisis del Orquestador (`autonomous_scientist.py`)

- **¿Conoce detalles internos de física?**
  **Solo de forma superficial.** Hardcodea los métodos y datasets ("synthetic_lorenz", "koopman", etc.) en `build_context()` (líneas 143-156) para enriquecer el prompt del LLM, pero no resuelve ecuaciones ni realiza integraciones físicas dentro de la clase.
- **¿Instancia directamente `TheoryCritic`?**
  **No.** `TheoryCritic` no es importado ni instanciado en el archivo. La validación física clásica ocurre de forma externa durante las llamadas del sandbox o en los scripts de benchmark de revalidación.
- **¿Instancia directamente `HypothesisGenerator`?**
  **No.** La hipótesis es generada consultando al razonador LLM (`llm.generate_hypothesis()`, línea 436).
- **¿Existe inversión de dependencias?**
  **No.** Instancia directamente `LLMReasoner` y `SandboxExecutor` en su constructor (líneas 32-33) en lugar de recibirlos como interfaces inyectadas.
- **¿Puede recibir implementaciones alternativas?**
  **No.** No está diseñado con interfaces de inyección de dependencias. Para soportar dominios cuánticos o satelitales directamente, se requiere parametrizar o inyectar las clases críticas y los prompt builders.
