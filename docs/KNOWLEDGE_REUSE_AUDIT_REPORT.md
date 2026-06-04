# Reporte de Auditoría Causal de Reutilización de Conocimiento (Fase 1D.1)

Este reporte presenta los resultados cuantitativos del benchmark causal diseñado para aislar el impacto del reuso de motivos de conocimiento y evaluar su contribución física al fitness.

---

## 1. Carrera Causal por Semilla (RUN A vs RUN B)

El benchmark compara:
* **RUN A (Control):** `pattern_injection_rate = 0.0` (sin reutilización de patrones en GHZ).
* **RUN B (Tratamiento):** `pattern_injection_rate = 0.2` (con reutilización de patrones transferidos desde Bell).

| Semilla | Generaciones (RUN A - Control) | Generaciones (RUN B - Tratamiento) | Speedup (Control / Tratamiento) |
| :--- | :---: | :---: | :---: |
| 1 | 2 | 2 | 1.0000x |
| 42 | 2 | 2 | 1.0000x |
| 123 | 2 | 2 | 1.0000x |
| 999 | 2 | 2 | 1.0000x |
| 2025 | 3 | 3 | 1.0000x |

### Estadísticas Globales
- **Promedio Speedup:** 1.0000x
- **Mediana Speedup:** 1.0000x
- **Desviación Estándar:** 0.0000

---

## 2. Métricas de Instrumentación Causal

Granulares sobre las mutaciones guiadas por conocimiento inyectadas en las ejecuciones de tratamiento (RUN B):

- **Intentos de Inyección (Attempts):** 9
- **Inyecciones Exitosas en Circuitos Válidos:** 5
- **Inyecciones que Sobrevivieron a Selección (Survived):** 0
- **Inyecciones que Mejoraron el Score (Improved):** 0

- **Tasa de Éxito de Inyección (Injected / Attempts):** 55.5556%
- **Tasa de Supervivencia (Survived / Injected):** 0.0000%
- **Tasa de Mejora de Score (Improved / Injected):** 0.0000%

---

## 3. Clasificación de Evidencia

- **TRANSFER_LEARNING_EVIDENCE:** `FAILED_OR_BUGGED`

---

## 4. Clasificación y Ranking de Valor de Motivos

El ranking a continuación ordena los motivos descubiertos y reusados por su `mean_delta_score` (contribución física al fitness):

| Motivo (Motif) | Ejecuciones | Mean Delta Score | Median Delta Score |
| :--- | :---: | :---: | :---: |
| `H(q0)->CNOT(q0,q1)` | 3 | -0.2720 | -0.2720 |
| `H->CNOT` | 2 | -0.2720 | -0.2720 |

---
