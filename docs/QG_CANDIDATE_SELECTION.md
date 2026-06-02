# FASE 1 — Identificación y Perfilamiento del Candidato Dominante

En esta primera fase de la auditoría física dirigida, analizamos de forma exhaustiva las ecuaciones para el **Problema C (Gravedad Cuántica)** descubiertas a lo largo de las 30 semillas de la campaña de reproducibilidad (`physics/benchmark/reproducibility_improved_30.json`).

El benchmark de Gravedad Cuántica requiere descubrir una función regularizadora $f(r)$ que corrija la singularidad clásica de Schwarzschild a corta distancia, satisfaciendo estrictos criterios físicos analíticos supervisados por `TheoryCritic`.

---

## Tabla Comparativa de Candidatos

A partir de las 30 ejecuciones independientes, hemos clasificado las soluciones descubiertas en tres candidatos representativos:

| Propiedad | Candidato 1: Ecuación Modal & Estable | Candidato 2: Mejor Score Exponencial | Candidato 3: Ecuación Cuadrática |
| :--- | :--- | :--- | :--- |
| **Fórmula Analítica (LaTeX)** | $$f(r) = \frac{r^3}{r^3 + 1.5}$$ | $$f(r) = 0.535 e^{-0.196(r-1.612)^2}$$ | $$f(r) = \frac{0.891}{1 + 0.012 r^2}$$ |
| **Familia Funcional** | Racional (Tipo Hayward de grado 3) | Exponencial (Tipo Gaussiano) | Racional de Grado 2 |
| **Frecuencia (Semillas)** | 10 / 30 (33.33%) | 19 / 30 (63.33%) | 1 / 30 (3.33%) |
| **Score Medio** | **100.00%** | 88.75% (Familia) | 81.47% |
| **Score Máximo** | **100.00%** | 95.33% (Semilla 26) | 81.47% |
| **Estabilidad Paramétrica** | **Excelente (Desviación = 0.00)** | Moderada ($\sigma_A \approx 0.15$, $\sigma_B \approx 0.08$, $\sigma_C \approx 0.41$) | N/A (Semilla única) |
| **Vedicto del Benchmark** | **Aceptado (100% Score)** | Aceptado (Seed 26: 95.33%) | Aceptado (Seed 3: 81.47%) |

---

## Perfil Detallado de los Candidatos

### 1. Candidato 1 — Rational Ansatz (Tipo Hayward)
Esta es la solución **modal** de mayor puntuación física del sistema. Surge con parámetros idénticos ($A = 1.0$, $B = 1.5$, exponente del numerador y denominador = 3) en 10 semillas diferentes. Su score perfecto del 100% se debe a que coincide de forma exacta con la forma matemática de la métrica regularizada de Hayward para la resolución de singularidades, logrando regularidad total de los invariantes físicos. Su desviación paramétrica es de 0.00, lo que demuestra un atractor funcional extremadamente fuerte en el espacio de búsqueda simbólica cuando se aplican restricciones físicas estrictas.

### 2. Candidato 2 — Gaussian Ansatz (Exponencial)
Esta familia representa el **63.33%** de los descubrimientos totales del sistema, lo que indica que el PINN y el motor PySR tienen una alta afinidad por la suavidad analítica de las funciones gaussianas. Aunque la familia presenta variaciones menores en sus coeficientes entre semillas, el candidato de semilla 26 ($f(r) = 0.535 e^{-0.196(r-1.612)^2}$) obtuvo el score más alto de esta familia (95.33%). Analizaremos si esta suavidad exponencial se traduce en una resolución real de singularidades físicas.

### 3. Candidato 3 — Quadratic Rational Ansatz
Este candidato racional de segundo grado se descubrió únicamente en la semilla 3. Obtuvo un score de 81.47%. Aunque es una solución simple, su baja frecuencia (3.33%) y su menor puntuación sugieren que es un óptimo local del espacio de búsqueda con limitaciones físicas considerables, las cuales serán reveladas en las siguientes fases de la auditoría.
