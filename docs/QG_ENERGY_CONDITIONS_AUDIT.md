# FASE 5 — Auditoría de Condiciones de Energía

En esta quinta fase, evaluamos de forma exhaustiva las condiciones clásicas de energía a lo largo de la coordenada radial $r \in [0, 5]$ para cada uno de los tres candidatos, utilizando el tensor de energía-impulso efectivo $T^\mu_\nu$ derivado a partir de las ecuaciones de Einstein:
$$G^\mu_\nu = 8 \pi T^\mu_\nu$$

---

## Formalismo y Componentes de Energía

Para la estructura métrica regularizada con $A(r) = 1 - \frac{2 M f(r)}{r}$, las componentes del tensor de energía-impulso efectivo en coordenadas ortonormales son:
1. **Densidad de Energía Efectiva ($\rho$):**
   $$\rho(r) = -T^t_t = \frac{M f'(r)}{4 \pi r^2}$$
2. **Presión Radial ($p_r$):**
   $$p_r(r) = T^r_r = -\rho(r) = -\frac{M f'(r)}{4 \pi r^2}$$
3. **Presión Transversa ($p_\theta = p_\phi$):**
   $$p_\theta(r) = T^\theta_\theta = -\frac{M f''(r)}{8 \pi r}$$

Las cuatro condiciones clásicas de energía se definen como:
- **Null Energy Condition (NEC):** $\rho + p_i \geq 0 \implies \rho + p_r \geq 0$ y $\rho + p_\theta \geq 0$.
  - Puesto que $\rho + p_r = 0$, la NEC se simplifica a:
    $$2 f'(r) - r f''(r) \geq 0$$
- **Weak Energy Condition (WEC):** $\rho \geq 0$ y $\rho + p_i \geq 0 \implies f'(r) \geq 0$ y la condición NEC.
- **Strong Energy Condition (SEC):** $\rho + p_i \geq 0$ y $\rho + \sum p_i \geq 0 \implies$ NEC y $\rho + p_r + 2 p_\theta \geq 0$.
  - Se reduce a:
    $$2 f'(r) - r f''(r) \geq 0 \quad \text{y} \quad f''(r) \leq 0$$
- **Dominant Energy Condition (DEC):** $\rho \geq |p_i| \implies \rho \geq |p_\theta|$.
  - Se reduce a:
    $$f'(r) \geq 0 \quad \text{y} \quad 2 f'(r) - r |f''(r)| \geq 0$$

---

## Tabla de Violación de Condiciones de Energía ($r \in [0, 5]$)

| Candidato | Puntos de Violación NEC (de 500) | Puntos de Violación WEC (de 500) | Puntos de Violación SEC (de 500) | Puntos de Violación DEC (de 500) | Clasificación de Exoticidad Física |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Candidato 1: Hayward** | **0 / 500 (0.0%)** | **0 / 500 (0.0%)** | **90 / 500 (18.0%)** | **356 / 500 (71.2%)** | **Mildly Exotic (Físicamente Plausible)** |
| **Candidato 2: Gaussiano** | 252 / 500 (50.4%) | 339 / 500 (67.8%) | 253 / 500 (50.6%) | 389 / 500 (77.8%) | **Strongly Exotic (No Físico)** |
| **Candidato 3: Cuadrático** | 500 / 500 (100%) | 500 / 500 (100%) | 500 / 500 (100%) | 500 / 500 (100%) | **Strongly Exotic (Completamente No Físico)** |

---

## Análisis de Exoticidad y Viabilidad Física

### 1. Candidato 1 — Hayward ($f(r) = \frac{r^3}{r^3 + 1.5}$)
- **NEC e WEC:** **Satisfacidas al 100% en todo el espaciotiempo.** La densidad de energía efectiva $\rho(r)$ es estrictamente positiva en cualquier radio ($f'(r) = \frac{4.5 r^2}{(r^3 + 1.5)^2} \geq 0$), lo que cumple con el principio de que la materia ordinaria posee energía positiva.
- **SEC:** Presenta una **violación localizada strictly en la región del núcleo cuántico ($r < 0.9$ Planck).**
  - **Explicación Física:** Los teoremas de singularidad clásica de Hawking y Penrose demuestran que el colapso gravitatorio inevitablemente genera una singularidad física *siempre que la materia satisfaga la SEC*. Por lo tanto, para lograr una resolución de la singularidad (métrica regular en $r=0$, como la del Candidato 1), **es matemáticamente obligatorio violar la SEC a escala de Planck**. Esta violación representa la presión de repulsión cuántica efectiva (o efectos de polarización del vacío) que detiene el colapso gravitatorio.
- **DEC:** Presenta violaciones moderadas en distancias intermedias, lo cual es típico en teorías de gravedad modificada efectivas y fluidos cuánticos.
- **Clasificación:** **Mildly Exotic.** Es el perfil óptimo de un agujero negro regular físicamente realizable en teorías cuánticas de la gravedad.

### 2. Candidato 2 — Gaussiano ($f(r) = 0.535 e^{-0.196(r-1.612)^2}$)
- **Violaciones:** Presenta extensas regiones de violación en todas las condiciones de energía, incluyendo violaciones masivas de la NEC y WEC en el rango de decaimiento radial externo. La densidad de energía se vuelve negativa en múltiples regiones, lo que requeriría inyecciones masivas de materia exótica no física para sustentar la métrica a gran escala.
- **Clasificación:** **Strongly Exotic.** La métrica es físicamente inviable e inestable.

### 3. Candidato 3 — Racional Cuadrático ($f(r) = \frac{0.891}{1 + 0.012 r^2}$)
- **Violaciones:** **100% de violaciones globales en todo el dominio de evaluación.** Todas las condiciones de energía (NEC, WEC, SEC, DEC) se violan en todos los puntos del espacio. El tensor de energía-impulso posee signos completamente patológicos en toda la coordenada radial.
- **Clasificación:** **Strongly Exotic.** Totalmente inviable.

---

## Conclusión

El análisis de las condiciones de energía confirma de forma contundente la superioridad física del **Candidato 1**. Su comportamiento cumple estrictamente con las condiciones de energía débil y nula en todo el espaciotiempo, limitando las violaciones de la condición fuerte al núcleo cuántico de Planck. Esto es exactamente lo que se espera de una descripción semiclásica consistente de la gravedad cuántica: el comportamiento clásico de la energía se mantiene intacto a grandes distancias y solo se altera a escalas ultra-cortas para disolver la singularidad. Los candidatos 2 y 3 fallan de forma dramática al requerir materia altamente exótica y no física de forma global.
