# FASE 2 — Auditoría de Perturbaciones Escalares

En esta fase de la auditoría de estabilidad dinámica, introducimos un campo escalar de prueba real y sin masa $\Phi(u, v)$ que satisface la ecuación de Klein-Gordon generalizada en el espaciotiempo curvo de Hayward:
$$\Box \Phi = 0$$

Evaluamos la propagación de perturbaciones en la **Región II** (la región interior comprendida entre el horizonte externo de eventos $r_+$ y el horizonte de Cauchy $r_-$), donde $A(r) < 0$.

---

## Formulación del Solucionador de Doble-Null

Aprovechando la simetría esférica, la ecuación de Klein-Gordon para el modo fundamental s-wave ($l=0$) se simplifica al redefinir el campo escalar como $\psi(u, v) = r \Phi(u, v)$:
$$\frac{\partial^2 \psi}{\partial u \partial v} = -\frac{1}{4} V(r) \psi$$

Donde la barrera de potencial efectivo $V(r)$ depende de las componentes métricas y su derivada radial:
$$V(r) = \frac{A(r) A'(r)}{r}$$

Puesto que los horizontes de eventos y Cauchy corresponden a $A(r_h) = 0$, el potencial efectivo $V(r)$ se anula de forma exacta en ambas fronteras del dominio ($V(r_-) = 0, V(r_+) = 0$).

### Esquema Numérico de Salto de Rana (Leapfrog)
Evolucionamos la perturbación en una malla bidimensional $(u, v)$ con espaciado uniforme $du$ y $dv$. Para integrar la ecuación hiperbólica en cada celda elemental, empleamos un esquema de diferencias finitas de segundo orden en coordenadas null:
$$\psi(i+1, j+1) = \psi(i+1, j) + \psi(i, j+1) - \psi(i, j) - \frac{1}{4} du dv V(r_{mid}) \psi_{mid}$$

Donde los valores intermedios se evalúan en el centro de la celda de evolución:
$$r_{star\_mid} = \frac{v_{j+1/2} - u_{i+1/2}}{2}, \quad r_{mid} = \text{get\_r}(r_{star\_mid})$$
$$\psi_{mid} = \frac{1}{2} \left(\psi(i+1, j) + \psi(i, j+1)\right)$$

---

## Configuración y Propagación de Pulsos

Para la simulación, inyectamos un **pulso gaussiano ingoing** en la frontera null $u = 0$:
$$\psi(0, v) = \exp\left(-\frac{(v - v_c)^2}{2 \sigma^2}\right)$$
Con centro en $v_c = 6.0$ y ancho $\sigma = 1.2$ (unidades de Planck). En la frontera $v = 0$, fijamos $\psi(u, 0) = 0$ (condición reflexiva en el origen).

### Resultados de la Simulación Temporal:
El análisis de la evolución temporal revela que:
- El pulso gaussiano inicial se propaga de manera estable hacia el interior del agujero negro.
- Al atravesar la barrera de potencial de curvatura efectiva, la perturbación se dispersa parcialmente, dejando una cola de radiación atenuada de largo plazo.
- A medida que el campo se aproxima al horizonte de Cauchy $r_- = 1.0$ (lo cual corresponde al límite $v \to \infty$ en la región interior), la amplitud del campo se acumula debido al fenómeno de compresión null.

Esta evolución dinámica se ilustra de manera clara en los perfiles de amplitud del campo escalar guardados durante la simulación:
![Evolución Escalar](/figures/scalar_evolution.png)

Como se observa gráficamente en `figures/scalar_evolution.png`:
- En la etapa inicial ($u = 0$, curva azul), el pulso tiene una forma gaussiana pura y simétrica.
- En etapas intermedias ($u = 2.0$, curva naranja), la dispersión por curvatura genera una cola en la parte trasera del pulso.
- En la fase tardía ($u = 5.0$, curva verde), el pulso principal ha cruzado la región central y su energía comienza a acumularse y colapsar en las proximidades del horizonte de Cauchy, sentando las bases para el test de inflación de masa de la Fase 4.
