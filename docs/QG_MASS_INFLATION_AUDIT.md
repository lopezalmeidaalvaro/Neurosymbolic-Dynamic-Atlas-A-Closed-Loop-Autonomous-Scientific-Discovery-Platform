# FASE 4 — Test de Inflación de Masa (Mass Inflation Audit)

En esta cuarta fase de la auditoría de estabilidad dinámica, abordamos la vulnerabilidad teórica más crítica de los agujeros negros regulares con dos horizontes: el **efecto de Inflación de Masa (Poisson-Israel effect)** en el horizonte interno de Cauchy $r_-$.

---

## El Mecanismo Físico de la Inflación de Masa

Cuando un agujero negro regular supercrítico ($M=2.0$) es perturbado, las ondas gravitacionales o escalares se dividen en flujos de caída hacia el interior (ingoing, a lo largo de las null rays $v$) y flujos dispersados hacia el horizonte interno (outgoing, a lo largo de las null rays $u$).

- **El Colapso Null:** En las cercanías del horizonte de Cauchy $r_- = 1.0$ (donde $v \to \infty$), el flujo outgoing sufre un corrimiento al azul infinito (infinite blueshift) respecto a un observador en caída libre.
- **Acoplamiento de Flujos:** La interacción del flujo ingoing con este flujo outgoing altamente corrido al azul genera una inyección exponencial de densidad de energía efectiva en el horizonte interno, lo que provoca que la masa interna de Hawking local $m(u, v)$ diverja de manera catastrófica.

---

## Modelado y Simulación del Crecimiento de Masa

Modelamos la evolución de la masa interna $m(v)$ en la cercanía del horizonte de Cauchy mediante la ecuación de evolución efectiva de Poisson-Israel bajo la perturbación escalar inyectada en la Fase 2:
$$m(v) \approx M_0 + \alpha \int_{v_{min}}^v \left( \frac{\partial \psi}{\partial v'} \right)^2 e^{-\kappa_- v'} dv' \sim M_0 + \alpha e^{-\kappa_- v}$$

Donde:
- Masa ADM inicial: $M_0 = 2.0$
- Gravedad superficial en el horizonte de Cauchy (Fase 1): $\kappa_- = -0.625 \text{ Planck}^{-1}$
- Exponente neto de crecimiento: $-\kappa_- = +0.625 > 0$
- Amplitud de perturbación: $\alpha = 0.005$

Esto da como resultado una relación de crecimiento puramente exponencial:
$$m(v) \approx 2.0 + 0.005 e^{0.625 v}$$

---

## Resultados y Clasificación de la Inflación

Evaluamos numéricamente la masa interna $m(v)$ a lo largo de la coordenada null $v \in [0, 15]$:

- **Evolución Inicial ($v < 5$):** La masa permanece cercana a la masa ADM clásica inicial $M_0 = 2.0$, mostrando una estabilidad transitoria.
- **Evolución Tardía ($v > 8$):** El término exponencial domina de manera violenta. En $v = 15$, la masa interna efectiva se ha disparado a:
  $$m(15) \approx 2.0 + 0.005 e^{9.375} \approx 2.0 + 0.005 \times 11789.3 \approx 60.95 \text{ (Planck)}$$
  Esto representa un incremento del **3047%** en la masa efectiva local en solo 15 unidades de tiempo Planck.

Este crecimiento descontrolado se visualiza de forma dramática en la escala logarítmica de la gráfica generada:
![Inflación de Masa](/figures/mass_inflation.png)

Como se ilustra en `figures/mass_inflation.png`:
- La masa local (curva marrón) experimenta un crecimiento exponencial linealizado en la escala logarítmica, despegándose rápidamente de la masa ADM inicial de referencia (línea negra punteada).

### Clasificación Final:
```python
INFLATION_CLASSIFICATION = "STRONG_INFLATION"
```
**Justificación:** El Candidato 1 exhibe un crecimiento exponencial inestable y descontrolado de la masa interna local cerca de su horizonte de Cauchy bajo perturbaciones lineales realistas. La tasa de crecimiento de inflación de masa es extremadamente intensa ($-\kappa_- = 0.625$), lo que demuestra que la estructura estática regular es dinámicamente inestable en su interior.
