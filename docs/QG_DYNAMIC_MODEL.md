# FASE 1 — Construcción del Modelo Dinámico de Hayward

En esta fase de la auditoría de estabilidad dinámica, construimos la estructura espaciotemporal de fondo para el Candidato 1 (Métrica de Hayward). Para evaluar la física del interior y de los horizontes de manera rigurosa, debemos trabajar con una masa **supercrítica** que admita horizontes físicos.

---

## Estructura Geométrica de la Métrica

La métrica regular de Hayward en coordenadas de Schwarzschild $(t, r, \theta, \phi)$ está dada por:
$$ds^2 = -A(r) dt^2 + A(r)^{-1} dr^2 + r^2 d\Omega^2, \quad A(r) = 1 - \frac{2 M r^2}{r^3 + 2 M L^2}$$

Fijamos los parámetros físicos del fondo dinámico a:
- Masa ADM: $M = 2.0$
- Parámetro de escala de Planck: $L^2 = 0.75 \implies L \approx 0.866$
- Término correctivo: $2 M L^2 = 3.0$

Sustituyendo estos valores, el factor métrico se reduce a:
$$A(r) = 1 - \frac{4 r^2}{r^3 + 3.0} = \frac{r^3 - 4 r^2 + 3.0}{r^3 + 3.0}$$

---

## Determinación Exacta de Horizontes

La ecuación de horizontes se obtiene resolviendo $A(r) = 0$:
$$r^3 - 4 r^2 + 3.0 = 0$$

Dado que $r = 1.0$ es una raíz exacta de este polinomio de tercer grado ($1 - 4 + 3 = 0$), podemos factorizarlo como:
$$(r - 1)(r^2 - 3r - 3) = 0$$

Las soluciones físicas positivas ($r > 0$) corresponden a:
1. **Horizonte Interno de Cauchy ($r_-$):**
   $$r_- = 1.0 \text{ (Unidad Planck)}$$
2. **Horizonte Externo de Eventos ($r_+$):**
   $$r_+ = \frac{3 + \sqrt{21}}{2} \approx 3.7913 \text{ (Unidades Planck)}$$

Puesto que $M = 2.0 > M_{crit} \approx 1.082$, la métrica posee efectivamente la topología de un agujero negro regular con dos horizontes bien definidos.

---

## Gravedad Superficial en los Horizontes

La gravedad superficial $\kappa$ se evalúa mediante:
$$\kappa = \frac{1}{2} A'(r_h)$$

Derivando simbólicamente el factor métrico $A(r)$:
$$A'(r) = \frac{4 r (r^3 - 6.0)}{(r^3 + 3.0)^2}$$

Evaluamos en cada horizonte:
- **En el Horizonte Interno de Cauchy ($r_- = 1.0$):**
   $$\kappa_- = \frac{1}{2} A'(1.0) = \frac{1}{2} \left[ \frac{4(1)(1 - 6)}{(1 + 3)^2} \right] = \frac{1}{2} \left( -\frac{20}{16} \right) = -0.625 \text{ Planck}^{-1}$$
- **En el Horizonte Externo de Eventos ($r_+ \approx 3.7913$):**
   $$\kappa_+ = \frac{1}{2} A'(r_+) = \frac{r_+^3 - 6.0}{4 r_+^3} \approx 0.1112 \text{ Planck}^{-1}$$

La gravedad superficial del horizonte de Cauchy $\kappa_-$ es estrictamente **negativa**, lo cual es un indicativo del carácter repulsivo cuántico central y de la inestabilidad de corrimiento al azul en esta superficie.

---

## Transformación a Coordenadas Doble-Null

Para realizar simulaciones de evolución dinámica estables en el interior, pasamos de las coordenadas singulares de Schwarzschild a coordenadas **doble-null** $(u, v)$ libres de singularidades en los horizontes.

Definimos la coordenada tortuga $r^*$ como:
$$r^* = \int \frac{dr}{A(r)}$$

Las coordenadas null ingoing y outgoing se definen como:
$$u = t - r^*, \quad v = t + r^*$$

Bajo estas coordenadas, la métrica adopta la forma doble-null:
$$ds^2 = -A(r) du dv + r^2 d\Omega^2$$
Donde la coordenada radial $r(u, v)$ queda definida implícitamente por la relación:
$$r^*(r) = \frac{v - u}{2}$$

Los resultados analíticos y numéricos del fondo dinámico calculados en esta fase se han guardado con precisión en `physics/benchmark/dynamic_background.json`.
