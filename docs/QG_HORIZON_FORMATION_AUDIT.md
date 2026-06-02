# FASE 4 — Formación y Disolución de Horizontes Aparentes

En esta cuarta fase de la auditoría de colapso, investigamos de forma cuantitativa la estructura topológica y temporal de los horizontes mediante el registro continuo de la componente métrica de Schwarzschild efectiva y el radio del horizonte aparente $r_{ah}(t)$:
$$r_{ah}(t) = 2 m(t)$$

Donde $m(t)$ es la masa efectiva de Hawking encerrada en la nube en cada instante.

---

## Seguimiento del Horizonte Aparente vs. Radio de la Nube

Para las condiciones iniciales bajo auditoría ($M_0 = 1.5$, $\rho_{crit} = 8.0$), comparamos la evolución temporal del radio físico de la superficie de la nube $R(t) = r_b a(t)$ contra el radio del horizonte aparente $R_s(t) = 2 m(t)$:

1. **Etapa Pre-Horizonte ($t \in [0, 6.70]$ Planck):**
   - El radio de la nube $R(t)$ se contrae desde $2.5$ Planck.
   - El radio del horizonte aparente $R_s(t)$ es menor que el radio de la nube ($R(t) > R_s(t)$), lo que significa que **no hay horizontes**. La nube es visible para observadores asintóticos externos.
2. **Formación del Horizonte Aparente ($t \approx 6.70$ Planck):**
   - El radio físico de la nube se contrae por debajo de su radio de Schwarzschild efectivo ($R(t) \le R_s(t)$).
   - En este instante, se crea un **horizonte aparente** que encapsula a la nube.
3. **El Rebote Cuántico en el Interior ($t_{bounce} \approx 9.38$ Planck):**
   - El colapso se detiene en $a_{min} \approx 0.215$, lo que corresponde a un radio de nube mínimo de $R_{min} \approx 0.538$ Planck.
   - El horizonte aparente en este punto tiene su radio máximo de $R_s = 2 M_0 = 3.0$ Planck. Puesto que el radio de la nube ($0.538$) es muy inferior al del horizonte ($3.0$), el rebote cuántico ocurre **completamente dentro del horizonte aparente**, de forma oculta a los observadores externos en esta etapa.
4. **Disolución del Horizonte Aparente ($t \approx 12.06$ Planck):**
   - Tras el rebote, la nube se expande rápidamente.
   - En $t \approx 12.06$ Planck, el radio físico de la nube en expansión cruza nuevamente el radio de Schwarzschild efectivo desde adentro hacia afuera ($R(t) > R_s(t)$).
   - En este instante, **el horizonte aparente se disuelve por completo**, liberando la materia en expansión y permitiendo que la información cuántica del núcleo escape hacia el infinito asintótico.

Esta evolución topológica de horizontes se detalla de forma impecable en la simulación:
![Evolución de Horizontes](/figures/horizon_evolution.png)

Como se ilustra en `figures/horizon_evolution.png`:
- El radio físico de la nube (curva verde sólido) disminuye continuamente, cruzando por debajo de la línea del horizonte aparente (curva roja discontinua) en $t \approx 6.7$.
- El rebote ocurre en el punto más bajo de la curva verde ($R \approx 0.538$).
- La curva verde sube de nuevo, cruzando por encima del horizonte aparente en $t \approx 12.0$, lo que demuestra la liberación de la nube y la disolución del horizonte.

---

## Clasificación de la Formación de Horizontes

A partir de los resultados de la evolución dinámica, clasificamos el horizonte del Candidato 1 como:

```python
HORIZON_CLASSIFICATION = "TEMPORARY_HORIZON"
```

### Justificación Física:
La hipótesis del horizonte eterno queda **refutada**. El colapso gravitatorio cuántico del Candidato 1 no genera un agujero negro eterno y estático. En su lugar, produce un **agujero negro temporal (Planck Star)**: un objeto donde el horizonte de eventos se forma únicamente de manera transitoria durante la etapa de máxima compresión y se disuelve completamente tras el rebote cuántico del núcleo, permitiendo la evacuación de la energía y resolviendo de raíz el problema de la singularidad y de la censura cósmica de forma dinámica.
