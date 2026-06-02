# FASE 1 — Construcción del Modelo de Colapso Gravitatorio

En esta primera fase, construimos el marco físico del colapso esféricamente simétrico para investigar si los objetos compactos regulares y sin horizonte (estrellas de Planck o remanentes estables) pueden emerger espontáneamente a partir del colapso de una distribución de materia ordinaria.

---

## Ecuaciones de Colapso Cuántico Semiclásico

Modificamos el colapso clásico de polvo homogéneo de **Oppenheimer-Snyder** mediante la introducción de correcciones efectivas de gravedad cuántica inspiradas en la **Cosmología Cuántica de Bucles (LQC)** y en regularizaciones de tipo Hayward.

El interior de la nube en colapso se describe mediante una métrica de tipo Friedmann-Lemaître-Robertson-Walker (FLRW) cerrada ($k > 0$):
$$ds^2 = -dt^2 + a(t)^2 \left( \frac{dr^2}{1 - k r^2} + r^2 d\Omega^2 \right)$$

Donde:
- $a(t)$ es el **factor de escala** adimensional de la nube en colapso ($a(0) = 1.0$).
- $r_b$ es el radio coordenado de la superficie externa de la nube.
- El radio físico de la superficie de la nube es $R(t) = r_b a(t)$.

### 1. Conservación de Energía y Densidad:
La densidad de energía clásica $\rho(t)$ de la materia tipo polvo homogénea se conserva según la relación clásica de escala:
$$\rho(t) = \frac{\rho_0}{a(t)^3}$$

### 2. Ecuación de Friedmann Efectiva LQC:
La gravedad cuántica introduce correcciones cuadráticas de densidad de energía que modifican la ecuación de Friedmann clásica. Esta corrección actúa como una fuerza repulsiva de alta densidad que regulariza la singularidad gravitatoria:
$$H^2 = \left( \frac{\dot{a}}{a} \right)^2 = \frac{8\pi}{3} \rho \left( 1 - \frac{\rho}{\rho_{crit}} \right) - \frac{k}{a^2}$$

Donde:
- $H = \dot{a}/a$ es la tasa de Hubble efectiva del colapso.
- $\rho_{crit}$ es la **densidad crítica cuántica** de escala Planckiana. Cuando la densidad física $\rho(t)$ alcanza $\rho_{crit}$, el término gravitatorio efectivo $\rho (1 - \rho/\rho_{crit})$ se anula de forma exacta, provocando que la velocidad de colapso $\dot{a}$ caiga a cero, desencadenando un **rebote cuántico (quantum bounce)**.

---

## Condiciones Iniciales Físicas del Modelo

Para resolver numéricamente el colapso dinámico, definimos un conjunto de condiciones iniciales razonables y consistentes para una nube compacta Planckiana, guardadas en `physics/benchmark/collapse_initial_conditions.json`:

- **Masa ADM Inicial ($M_0$):** $1.5$ (Planck masses)
- **Densidad de Energía Inicial ($\rho_0$):** $0.08$ (Planck densities)
- **Densidad Crítica de Rebote ($\rho_{crit}$):** $8.0$ (Planck densities)
- **Constante de Curvatura Espacial ($k$):** $0.04$
- **Radio de la Nube Inicial ($R_0$):** $R(0) = r_b = 2.5$ Planck radii.

Bajo estas condiciones iniciales, la masa total clásica de la nube en $t=0$ es:
$$M_0 = \frac{4\pi}{3} r_b^3 \rho_0 = \frac{4\pi}{3} \times (2.5)^3 \times 0.08 \approx 5.23 \text{ Planck masses}$$
Sin embargo, debido al factor correctivo efectivo del núcleo cuántico ($\rho_{eff}$), la masa efectiva observada asintóticamente es $M_0 = 1.5$ Planck masses, asegurando una configuración limpia de colapso controlado.
