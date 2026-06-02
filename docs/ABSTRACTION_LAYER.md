# Capa de Abstracciones del Sistema (Fase 0B.2)

Este documento detalla el diseño de los contratos de interfaz abstracta introducidos en `core/abstractions/` para desacoplar el motor de descubrimiento científico autónomo de los dominios específicos.

---

## 1. Contratos y Responsabilidades

### A. `BaseHypothesisGenerator`
- **Propósito:** Definir el contrato de firmas común para los generadores de hipótesis, ansatzes o ideas científicas (ya sean motores CFG genéticos, LLMs o razonadores lógicos).
- **Responsabilidades:**
  - `propose()`: Proponer una nueva hipótesis basada en un contexto de exploración.
  - `mutate()`: Modificar ligeramente una hipótesis exitosa previa para explotar el espacio de búsqueda.

### B. `BaseCritic`
- **Propósito:** Definir el contrato común para la evaluación de hipótesis.
- **Responsabilidades:**
  - `validate()`: Analizar y computar la consistencia analítica, matemática o de límites de la hipótesis, devolviendo un veredicto de consistencia y una estimación de energía/relevancia.

### C. `BaseSandbox`
- **Propósito:** Definir el contrato común para la ejecución de experimentos.
- **Responsabilidades:**
  - `execute()`: Correr código generado de manera aislada (subprocess o contenedor Docker) y recolectar logs de stdout/stderr y resultados estructurados.

### D. `BaseMemory`
- **Propósito:** Definir el contrato común para la persistencia del conocimiento científico.
- **Responsabilidades:**
  - `store()`: Registrar hipótesis, experimentos y relaciones en una base de datos local o remota.
  - `retrieve()`: Recuperar el historial de exploración científica.

---

## 2. Dependencias Permitidas y Prohibidas

Para garantizar que la capa de abstracción permanezca neutral al dominio y agnóstica de las librerías matemáticas específicas, se imponen las siguientes reglas de acoplamiento:

### Dependencias Permitidas:
- Librerías estándar de Python (`abc`, `typing`, `json`, `pathlib`).
- Tipos de datos primitivos de Python (`dict`, `list`, `str`, `float`, `int`, `tuple`).

### Dependencias Prohibidas (No Importar en la capa core):
Las interfaces **NO** pueden importar bajo ninguna circunstancia:
- **`sympy`** (específico del dominio de relatividad general clásica en `physics/`).
- **`qiskit` / `pennylane`** (específicos del dominio de computación y circuitos cuánticos en `quantum/`).
- **`torch` / `tensorflow`** (específicos de las implementaciones continuas neuronales locales).

---

## 3. Conclusión de Diseño
La separación estricta de las dependencias asegura que la lógica del orquestador pueda interactuar con el motor cuántico, clásico o satelital utilizando las mismas clases base abstractas sin requerir la presencia de librerías exóticas fuera de su dominio activo.
