# Reporte de Inyección de Dependencias (Fase 0D.7)

Este informe documenta la refactorización arquitectónica para la inversión de dependencias en el orquestador principal (`autonomous_scientist.py`), lo que permite que sea completamente agnóstico al dominio científico.

---

## 1. Componentes Desacoplados

Se han desacoplado los cinco componentes fundamentales del ciclo de descubrimiento científico autónomo:
- **Hypothesis Generator (`BaseHypothesisGenerator`):** Abstraído para que el orquestador no dependa del generador simbólico o LLM concreto de física general.
- **Theory Critic (`BaseCritic`):** Abstraído para eliminar la dependencia directa de la verificación analítica y el cálculo del tensor de curvatura de SymPy.
- **Sandbox Executor (`BaseSandbox`):** Abstraído para admitir diferentes entornos de ejecución (locales, Docker, o en la nube para circuitos cuánticos/telemetría).
- **Scientific Memory (`BaseMemory`):** Abstraído para independizar el almacenamiento y detección de contradicciones científicas (que pueden residir en Neo4j, SQLite, bases de datos vectoriales, etc.).
- **LLM Reasoner:** Desacoplado de instanciaciones directas mediante parámetros de inyección opcionales en el constructor.

---

## 2. Imports Eliminados y Desplazamiento

Se han eliminado todos los imports acoplados al dominio de física clásica en la cabecera de [autonomous_scientist.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/physics/core/autonomous/autonomous_scientist.py):
- Se removieron los imports estáticos de `LLMReasoner` y `SandboxExecutor`.
- Los imports de la base de datos `knowledge_graph` y del sanitizador `scientific_guard` se trasladaron del nivel de módulo a cargas perezosas (lazy loading) dinámicas y protegidas con cláusulas `try-except` de fallback. Esto permite que el orquestador se importe y ejecute en otros dominios (e.g., `quantum/` o `satellite/`) sin que fallen las dependencias por archivos ausentes de `physics/`.

---

## 3. Compatibilidad Retroactiva Preservada

Para garantizar el funcionamiento legacy inalterado (`LEGACY_CODE_MODIFIED = FALSE`):
- El constructor `__init__` de [autonomous_scientist.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/physics/core/autonomous/autonomous_scientist.py) acepta parámetros de inyección opcionales.
- Si no se inyecta ningún componente (como en las llamadas legacy), el orquestador detecta el parámetro nulo y carga de forma perezosa las implementaciones concretas originales (`SandboxExecutor` y `LLMReasoner`), comportándose de forma idéntica a las versiones anteriores del sistema.
- Se verificó que toda la suite de pruebas del proyecto (57 tests en total) continúa pasando sin fallos.

---

## 4. Riesgos Residuales

- **Orden de Carga de Módulos (sys.path):** Debido a que tanto el orquestador de física clásico como la raíz contienen directorios llamados `core`, se resolvió el conflicto de nombres mediante la auto-extensión del `__path__` en [core/__init__.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/core/__init__.py). Esto reduce el riesgo de colisión de módulos a cero, pero cualquier cambio en la estructura física del repositorio debe mantener el contrato de rutas de importación.
