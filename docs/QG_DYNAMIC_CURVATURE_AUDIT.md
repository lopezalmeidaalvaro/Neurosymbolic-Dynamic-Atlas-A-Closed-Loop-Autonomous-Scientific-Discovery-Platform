# FASE 5 — Estabilidad de Curvatura Dinámica

En esta quinta fase de la auditoría, analizamos la evolución temporal de los invariantes de curvatura del espaciotiempo de Hayward bajo perturbaciones dinámicas para verificar si la regularidad central sobrevive a la inestabilidad interior.

---

## Evolución de los Invariantes de Curvatura

En la Relatividad General semiclásica, los invariantes de curvatura como el **Kretschmann escalar ($K = R_{abcd}R^{abcd}$)** caracterizan la presencia de singularidades físicas de forma covariante e independiente de las coordenadas.

En el régimen estático de la Fase 30, demostramos que el invariante de Kretschmann central del Candidato 1 era completamente finito:
$$K(0) = \frac{128}{3} \approx 42.67$$

Sin embargo, en el régimen dinámico actual, la acumulación y compresión de energía debido al corrimiento al azul en el horizonte de Cauchy $r_-$ acopla la masa interna efectiva $m(v)$ de la Fase 4 con la curvatura de Riemann:
$$K(v) \approx \frac{48 m(v)^2}{r_-^6}$$

Sustituyendo los valores del fondo y la masa dinámica ($r_- = 1.0$, $m(v) \approx 2.0 + 0.005 e^{0.625 v}$):
$$K(v) \approx 48 \left(2.0 + 0.005 e^{0.625 v}\right)^2$$

---

## Resultados del Análisis Dinámico

Evaluamos numéricamente el Kretschmann escalar a lo largo de la coordenada null $v \in [0, 15]$:
- **En la Fase Inicial ($v < 5$):** $K(v)$ permanece estable en $\approx 192$ ( Planck), consistente con la métrica Schwarzschild clásica en distancias intermedias.
- **En la Fase Tardía ($v = 15$):** Debido al acoplamiento cuadrático con la masa inflada, el invariante de Kretschmann se dispara de forma masiva a:
  $$K(15) \approx 48 \times (60.95)^2 \approx 48 \times 3714.9 \approx 1.78 \times 10^5 \text{ (Planck)}$$
  Esto representa una desviación de más de **900 veces** respecto a su valor estático regular original en solo $15$ unidades de Planck.
- **Límite cuando $v \to \infty$:**
  $$K(v) \to \infty$$

Esta divergencia catastrófica se visualiza de forma explícita en la gráfica generada durante nuestra simulación:
![Curvatura Dinámica](/figures/dynamic_curvature.png)

Como se ilustra en `figures/dynamic_curvature.png`:
- El invariante de Kretschmann (curva roja) crece de manera descontrolada, rompiendo los límites físicos regulares y divergencia a infinito.

---

## Clasificación de Estabilidad de Curvatura

A partir de los resultados analíticos y numéricos, clasificamos al Candidato 1 como:

```python
CURVATURE_CLASSIFICATION = "CURVATURE_DIVERGENT"
```

### Justificación Física:
La hipótesis nula $H_0$ queda **completamente refutada**. Aunque la métrica estática de Hayward es geométricamente regular en $r=0$, esta regularidad es una característica sumamente **frágil** que solo existe en ausencia de perturbaciones. Ante cualquier fluctuación dinámica realista (como un campo escalar sin masa), el horizonte de Cauchy colapsa debido al efecto de inflación de masa, **recreando dinámicamente la singularidad de curvatura física** en el origen. El interior del agujero negro regular colapsa en una singularidad de tipo curvatura de luz, destruyendo la regularización cuántica estática.
