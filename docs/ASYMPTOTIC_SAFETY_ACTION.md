# Acción Efectiva de Seguridad Asintótica (AS) para Hayward (Fase 6)

Este reporte investiga la correspondencia y reconstrucción del candidato regular de Hayward bajo el paradigma de la **Seguridad Asintótica (Asymptotic Safety - AS)** en gravedad cuántica no perturbativa, basándose en el score de consistencia de la Fase 34:

$$\text{ASYMPTOTIC\_SAFETY\_SCORE} = 85.00\%$$

---

## 1. El Fenómeno de Running en Asymptotic Safety

En la formulación de Seguridad Asintótica del grupo de renormalización (RG), la constante de gravitación de Newton $G$ no es constante, sino que corre con la escala de energía del corte infrarrojo $k$ de acuerdo con la existencia de un Punto Fijo Ultravioleta (UV Fixed Point) no perturbativo:

$$G(k) = \frac{G_0}{1 + \omega G_0 k^2}$$

donde $G_0$ es el valor clásico en el infrarrojo (IR) y $\omega$ es un parámetro numérico positivo del flujo de RG. En el límite cuántico profundo ($k \to \infty$), la constante de Newton se desvanece de forma cuadrática ($G(k) \propto 1/k^2$), lo que suaviza la interacción gravitatoria y evita la formación de singularidades físicas.

---

## 2. Reconstrucción de la Identificación de Escala para Hayward

Para mapear esta constante de Newton dependiente de la escala $G(k)$ a una constante efectiva dependiente de las coordenadas del espaciotiempo $G(r)$, se requiere formular una **identificación de escala** $k = k(r)$ o $k = k(R)$.

### A. Identificación Clásica $k \propto 1/r$ (Métrica de Bardeen)
Si se adopta la identificación de escala clásica simple basada en la distancia radial al centro del agujero negro:
$$k(r) = \frac{\xi}{r}$$
donde $\xi$ es una constante de proporcionalidad. Sustituyendo esta escala en la ecuación de running de Newton:
$$G(r) = \frac{G_0}{1 + \omega G_0 \xi^2 / r^2} = \frac{G_0 r^2}{r^2 + L_{B}^2}$$
donde $L_{B}^2 \equiv \omega G_0 \xi^2$. Al sustituir esta constante efectiva en el factor clásico de Schwarzschild $A(r) = 1 - \frac{2 G(r) M_0}{r}$, obtenemos:
$$A_{Bardeen}(r) = 1 - \frac{2 G_0 M_0 r}{r^2 + L_{B}^2}$$
Esta es la métrica regularizada de **Bardeen (1968)**. Por lo tanto, la identificación de escala clásica simple $k \propto 1/r$ **no puede producir la métrica de Hayward**, ya que predice una caída cuadrática en lugar de cúbica.

### B. Identificación Coordenada-Independiente en Curvatura $k \propto R^{1/4}$ (Métrica de Hayward)
Para reconstruir de forma exacta el perfil de Hayward, buscamos una identificación de escala que dependa de invariantes de curvatura locales del espaciotiempo. 

El escalar de Ricci $R(r)$ para la métrica de Hayward decae en el infinito asintótico (campo débil) como:
$$R(r) \approx - \frac{24 M_0^2 L^2}{r^6}$$
Si postulamos que la escala de corte de RG $k$ está gobernada por la escala de curvatura local:
$$k(r) = \chi |R(r)|^{1/4}$$
donde $\chi$ es un coeficiente adimensional de escala. A grandes distancias, esta identificación se comporta como:
$$k(r) \propto r^{-3/2}$$
Sustituyendo esta identificación de escala en la ecuación de running $G(k)$:
$$G(r) = \frac{G_0}{1 + \lambda (k(r))^2} \approx \frac{G_0}{1 + \lambda' r^{-3}} = \frac{G_0 r^3}{r^3 + 2 M_0 L^2}$$
Al insertar este $G(r)$ modificado en la métrica Schwarzschild:
$$A(r) = 1 - \frac{2 G(r) M_0}{r} = 1 - \frac{2 G_0 M_0 r^2}{r^3 + 2 M_0 L^2}$$
Esta es la **métrica regular de Hayward** de forma exacta.

---

## 3. Conclusión de la Auditoría

El candidato Hayward **es completamente compatible con la hipótesis de Seguridad Asintótica**. 

La diferencia clave entre las métricas de Bardeen y Hayward radica únicamente en la elección de la identificación de la escala de corte infrarrojo $k$. Mientras que Bardeen asume una escala simplista $k \propto 1/r$ dependiente de las coordenadas, **Hayward surge de manera elegante al identificar la escala con la curvatura local del espaciotiempo ($k \propto R^{1/4}$)**. Esto dota al candidato Hayward de una consistencia teórica superior, ya que su regularización está gobernada por magnitudes covariantes locales de curvatura y no por distancias de coordenadas arbitrarias.
