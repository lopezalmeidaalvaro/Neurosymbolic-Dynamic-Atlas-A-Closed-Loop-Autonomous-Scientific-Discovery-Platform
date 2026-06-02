# FASE 3 — Auditoría de Horizontes

En esta tercera fase, analizamos la estructura topológica de los horizontes de eventos para cada candidato mediante la resolución de la ecuación de horizonte:
$$g_{tt}(r_h) = -\left(1 - \frac{2 M f(r_h)}{r_h}\right) = 0 \implies r_h - 2 M f(r_h) = 0$$

Fijando la masa ADM en $M = 1.0$, realizamos un barrido y búsqueda numérica exacta de las raíces reales positivas $r > 0$.

---

## Tabla de Horizontes y Clasificación

| Candidato | Número de Horizontes ($M=1.0$) | Radios de los Horizontes ($M=1.0$) | Clasificación Física de la Solución |
| :--- | :---: | :---: | :--- |
| **Candidato 1: Hayward** | **0** | **Ninguno** | **Objeto Regular sin Horizonte (Horizonless Compact Remnant)** |
| **Candidato 2: Gaussiano** | 1 | $r_h \approx 0.992$ | Singular tipo Schwarzschild (Un horizonte) |
| **Candidato 3: Cuadrático** | 1 | $r_h \approx 1.721$ | Singular tipo Schwarzschild (Un horizonte) |

---

## Análisis Detallado por Candidato

### 1. Candidato 1 — Hayward ($f(r) = \frac{r^3}{r^3 + 1.5}$)
Para la masa $M = 1.0$, la ecuación métrica se reduce a:
$$r - \frac{2 r^3}{r^3 + 1.5} = 0 \implies r(r^3 - 2 r^2 + 1.5) = 0$$
Puesto que buscamos raíces físicas ($r > 0$), debemos resolver el polinomio cúbico:
$$P(r) = r^3 - 2r^2 + 1.5 = 0$$
El análisis del polinomio revela que su derivada se anula en $r = 0$ y $r = 4/3 \approx 1.33$. El mínimo local en $r = 4/3$ tiene un valor positivo:
$$P(4/3) = \frac{64}{27} - 2\left(\frac{16}{9}\right) + 1.5 = \frac{8.5}{27} \approx 0.315 > 0$$
Dado que el mínimo local está estrictamente por encima de cero, el polinomio **no posee raíces reales positivas**.
Esto significa que para $M = 1.0$, el Candidato 1 **carece de horizontes**. Es un objeto compacto y regular sin horizonte (un remanente de gravedad cuántica estable o estrella de Planck).

#### Transición de Fase de Horizontes y Masa Crítica:
Si aumentamos la masa ADM $M$, la gravedad superficial se intensifica y el mínimo local desciende, permitiendo la creación de horizontes. Para la forma general de Hayward con factor $L^2 = 1.5 / (2 M)$, el polinomio es:
$$r^3 - 2 M r^2 + 1.5 = 0$$
El mínimo local ocurre en $r_{min} = \frac{4M}{3}$. Evaluando $P(r_{min}) = 0$ para encontrar la masa límite de transición:
$$\left(\frac{4M_{crit}}{3}\right)^3 - 2 M_{crit} \left(\frac{4M_{crit}}{3}\right)^2 + 1.5 = 0 \implies -\frac{32 M_{crit}^3}{27} + 1.5 = 0 \implies M_{crit} = \left(\frac{81}{64}\right)^{1/3} \approx 1.082$$

- **Masa Subcrítica ($M < 1.082$):** **0 horizontes.** El objeto es un remanente regular supercompacto y estable sin horizonte. La presión cuántica central (derivada de la regularización) evita el colapso gravitatorio completo y previene la formación de un horizonte de eventos.
- **Masa Crítica ($M \approx 1.082$):** **1 horizonte degenerado.** El objeto es un **agujero negro regular extremo** con un solo horizonte en $r_h = \frac{4 M_{crit}}{3} \approx 1.443$.
- **Masa Supercrítica ($M > 1.082$):** **2 horizontes.** La solución se comporta como un **agujero negro regular** con un horizonte externo de eventos $r_+$ y un horizonte interno de Cauchy $r_-$. La singularidad central sigue estando completamente resuelta.

### 2. Candidato 2 — Gaussiano ($f(r) = 0.535 e^{-0.196(r-1.612)^2}$)
Para $M=1.0$, encontramos **una sola raíz real positiva** en $r_h \approx 0.992$. Esto significa que la solución posee un único horizonte de eventos similar al de Schwarzschild. Sin embargo, dado que no hay un segundo horizonte interno y el origen radial $r=0$ es físicamente singular (como se demostró en la Fase 2), esta solución no es más que una ligera deformación clásica de Schwarzschild que retiene la patología del colapso singular.

### 3. Candidato 3 — Racional Cuadrático ($f(r) = \frac{0.891}{1 + 0.012 r^2}$)
Para $M=1.0$, tiene **un solo horizonte de eventos** en $r_h \approx 1.721$. Al igual que el Candidato 2, es una métrica con una singularidad desnuda oculta tras un horizonte Schwarzschild-like tradicional, careciendo de la estructura de horizontes múltiples que caracteriza a los agujeros negros regulares consistentes.

---

## Visualización de los Perfiles Métricos

Las raíces encontradas corresponden exactamente a las intersecciones con el eje horizontal de la gráfica de componente métrica generada en nuestra auditoría:
![Perfiles Métricos](/figures/qg_metric_profiles.png)

Como se observa gráficamente:
- La curva del **Candidato 1 (Hayward)** (verde) nunca cruza la línea horizontal de $g_{tt} = 0$, manteniéndose en la fase de **objeto regular sin horizonte**.
- La curva del **Candidato 2 (Gaussiano)** (marrón) echa una intersección en $r \approx 0.99$.
- La curva del **Candidato 3 (Cuadrático)** (azul) intersecta en $r \approx 1.72$.
- El **Schwarzschild clásico** (rojo punteado) diverge violentamente hacia $-\infty$ al aproximarse a $r \to 0$.
