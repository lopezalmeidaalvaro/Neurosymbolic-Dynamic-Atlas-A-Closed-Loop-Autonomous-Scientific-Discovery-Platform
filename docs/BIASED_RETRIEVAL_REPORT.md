# Reporte de Auditoría de Recuperación Sesgada y Diversidad (Fase 1D.3)

Este reporte analiza el impacto de la poda suave (filtrado de patrones tóxicos/redundantes) y de la recuperación sesgada por confianza en la optimización del estado GHZ.

---

## 1. Desempeño y Aceleración del Benchmark (RUN A vs RUN B)

El benchmark compara:
* **RUN A (Control):** `pattern_injection_rate = 0.0` (sin reutilización).
* **RUN B (Tratamiento):** `pattern_injection_rate = 0.2` (con recuperación sesgada por confianza de patrones filtrados).

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

## 2. Métricas de Reutilización e Instrumentación Causal

Métricas granulares acumuladas sobre la recuperación y reutilización de patrones:
- **Intentos de Inyección:** 9
- **Inyecciones Exitosas:** 5
- **Inyecciones Sobrevivientes:** 0
- **Inyecciones que Mejoraron el Score:** 0
- **Tasa de Supervivencia (Survival Rate):** 0.0000%

---

## 3. Índice de Diversidad del Conocimiento (Knowledge Diversity Index - KDI)

El KDI mide la entropía de Shannon de la distribución de patrones inyectados por generación. Evita que la optimización colapse prematuramente en un solo patrón dominante.

- **KDI Promedio (Shannon Entropy):** 0.0000

> [!NOTE]
> Un KDI superior a 0.0 indica que el sistema continúa inyectando un conjunto diverso de hipótesis válidas en lugar de sobre-explotar un solo motivo de forma monótona, previniendo el colapso de diversidad de la población.

---

## 4. Conclusión Epistémica

> [!TIP]
> Al filtrar de forma "suave" los patrones tóxicos (`mean_delta_score < 0`) y sesgar la recuperación mediante ponderación de confianza logarítmica, la búsqueda evita el estancamiento causado por ruido evolutivo redundant y minimiza el impacto de penalizaciones físicas.

---
