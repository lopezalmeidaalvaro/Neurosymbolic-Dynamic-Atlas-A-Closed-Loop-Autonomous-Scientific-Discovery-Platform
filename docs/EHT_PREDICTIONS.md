# Predicciones Observacionales de Sombras de Agujeros Negros — EHT (Fase 1)

Este reporte deriva cuantitativamente el radio de la esfera de fotones, el tamaño de la sombra y las desviaciones observacionales del candidato Hayward en comparación con la métrica clásica de Schwarzschild, contrastándolo con las mediciones empíricas de Sgr A* y M87* por el EHT (Event Horizon Telescope).

---

## 1. Derivación de la Esfera de Fotones ($r_{ph}$)
En una métrica estática y esférica, las geodésicas nulas circulares (órbita de fotones) se localizan en los puntos críticos que satisfacen:

$$2 A(r) - r A'(r) = 0$$

Para la métrica de Hayward con masa normalizada $M_0 = 1.0$ y parámetro de Planck $L = 0.866$ ($2 M_0 L^2 = 1.5$):

$$A(r) = 1 - \frac{2 r^2}{r^3 + 1.5}$$

$$A'(r) = \frac{2 r (r^3 - 3.0)}{(r^3 + 1.5)^2}$$

Sustituyendo y simplificando, obtenemos la ecuación polinomial de sexto grado:

$$r^6 - 3 r^5 + 3 r^3 + 2.25 = 0$$

- **Schwarzschild ($L = 0$):** $r_{ph} = 3.0 M_0 = 3.0$ Planck.
- **Hayward ($L = 0.866$):** $r_{ph} \approx 2.50$ Planck.

Esto representa una **reducción del $16.7\%$** en el radio de la esfera de fotones debido a la concentración de masa suavizada en el núcleo repulsivo.

---

## 2. Tamaño Crítico de la Sombra ($r_{sh}$)
El radio de la sombra de impacto óptico vista por un observador asintótico lejano está dado por la relación de la esfera de fotones:

$$r_{sh} = \frac{r_{ph}}{\sqrt{A(r_{ph})}}$$

Evaluando el coeficiente métrico en $r_{ph} = 2.50$:

$$A(2.50) = 1 - \frac{12.50}{17.125} \approx 0.270$$

$$r_{sh} = \frac{2.50}{\sqrt{0.270}} \approx 4.81 \text{ unidades Planck}$$

- **Schwarzschild ($L = 0$):** $r_{sh} = 3\sqrt{3} M_0 \approx 5.196 M_0$.
- **Hayward ($L = 0.866$):** $r_{sh} \approx 4.81 M_0$.

El candidato Hayward predice una **sombra un $7.43\%$ más pequeña** que la clásica de Schwarzschild.

---

## 3. Comparación con M87* y Sgr A* (EHT)
El EHT ha medido con alta precisión el tamaño de la sombra angular de los agujeros negros supermasivos M87* y Sagitario A* (Sgr A*).

### Datos Empíricos del EHT:
1. **Sagitario A*:** $\theta_{Sgr} = 48.7 \pm 5.9 \ \mu\text{as}$ (consistente con Schwarzschild dentro de un margen del $10\%$).
2. **M87*:** $\theta_{M87} = 42 \pm 3 \ \mu\text{as}$ (consistente con Schwarzschild dentro del $10\%$).

### Análisis de Desviación:
- **Cutoff Planckiano ($L \approx l_P$):**
  Para masas astrofísicas ($M_{Sgr} \approx 4 \times 10^6 M_\odot$), la relación adimensional de regularización es infinitamente pequeña:
  $$\frac{L^2}{M_{Sgr}^2} \approx 10^{-88}$$
  La desviación en el tamaño de la sombra respecto a Schwarzschild es del orden de $10^{-88}$, lo cual es completamente indetectable para cualquier tecnología observacional actual o futura.
- **Modelo de Escala Macroscópica ($L \propto M_0^{1/3}$):**
  Si el parámetro de regularización escala macroscópicamente debido a efectos cuánticos colectivos, la reducción del $7.43\%$ cae justamente dentro del margen de error del $10\%$ del EHT. Esto sitúa al candidato en el límite de la exclusión observacional, haciéndolo una teoría altamente testeable.
