# Auditoría de Gravedad No Local para el Candidato Hayward (Fase 4)

Este reporte investiga si la métrica regularizada de Hayward puede surgir de manera natural como la solución clásica efectiva de una teoría covariante de **Gravedad No Local**, caracterizada por acciones que incorporan infinitas derivadas o funciones del operador de Green de d'Alembert $\Box$.

---

## 1. Motivación y Estructura de la Acción No Local

Las teorías de Gravedad No Local (como la Gravedad de Derivadas Infinitas, *Infinite Derivative Gravity* - IDG) proponen acciones que modifican el propagador del gravitón para resolver el problema de las singularidades y renormalizabilidad sin introducir fantasmas. La acción típica de esta clase de teorías se escribe como:

$$S = \int d^4x \sqrt{-g} \left[ \frac{R}{16\pi G} + R F(\Box) R + R_{\mu\nu} H(\Box) R_{\mu\nu} \right]$$

donde $F(\Box)$ y $H(\Box)$ son operadores no locales que involucran infinitos términos de derivadas, comúnmente modelados mediante funciones trascendentales enteras para preservar la unitariedad:

$$F(\Box) \propto \frac{e^{-\Box / M_{uv}^2} - 1}{\Box}$$

donde $M_{uv}$ es la escala de corte ultravioleta (de escala Planckiana).

---

## 2. Firmas Características de la Gravedad No Local en Hayward

Analizamos si las propiedades físicas del candidato Hayward coinciden con las firmas analíticas predichas por la gravedad no local:

### A. Suavizado UV y Ausencia de Singularidad
- **Predicción de Gravedad No Local:** El factor de regularización $e^{-\Box/M_{uv}^2}$ en el propagador del gravitón actúa como una función de transferencia no local que distribuye la masa puntual de una partícula de forma difusa a lo largo de un volumen de Planck $\sim L^3$. Esto "suaviza" el potencial newtoniano en el origen.
- **Correspondencia en Hayward:** El candidato Hayward exhibe exactamente esta atenuación de la singularidad, eliminando la divergencia en $r \to 0$ mediante el parámetro cuántico $L$. Los invariantes de curvatura son estrictamente finitos ($R(0) = 12/L^2$).

### B. Formación del Núcleo de de Sitter
- **Predicción de Gravedad No Local:** El suavizado de la fuente puntual concentrada en $r=0$ produce una distribución efectiva de materia regularizada con densidad constante en el origen ($\rho(r) \to \rho_0$). En Relatividad General, esto se traduce en una ecuación de estado $P = -\rho$ en el centro, es decir, un núcleo de de Sitter local.
- **Correspondencia en Hayward:** Hayward exhibe de manera natural este comportamiento:
  $$A(r) \approx 1 - \frac{r^2}{L^2} + \mathcal{O}(r^5)$$
  El núcleo central de Hayward es algebraicamente un espacio de de Sitter con una constante cosmológica efectiva $\Lambda_{eff} = 3/L^2$.

### C. Caída del Perfil de Masa Cúbico y Regularización Exponencial
- **Análisis Comparativo:** Las teorías de derivadas infinitas con regularización exponencial simple (p. ej., $e^{-\Box/M_{uv}^2}$) predicen típicamente perfiles de potencial regularizados mediante la función de error:
  $$\Phi(r) \sim - \frac{M_0}{r} \text{erf}\left( \frac{r}{2L} \right)$$
  lo que da origen a la métrica regular de **Bardeen** en lugar de la métrica de **Hayward**.
- **La Alternativa No Local para Hayward:** Para recuperar el decaimiento de tipo ley de potencias cúbica de la métrica de Hayward ($M(r) \propto \frac{r^3}{r^3+2M_0 L^2}$), el operador no local $F(\Box)$ no debe ser puramente exponencial básico, sino que debe incorporar una función de distribución racional o de Bessel no local. Esto sugiere que Hayward corresponde a una clase específica de teoría no local donde los efectos de auto-interacción de curvatura se saturan de forma cúbica debido a la retroalimentación no lineal del campo fuerte.

---

## 3. Conclusión de la Auditoría

La Gravedad No Local es **el marco covariante más plausible** para explicar el origen dinámico de la métrica de Hayward sin la inyección manual de fluidos exóticos anisótropos. 

El núcleo regular de de Sitter y el suavizado UV son firmas naturales del propagador regularizado por infinitas derivadas a escala de Planck. Para reproducir analíticamente la potencia cúbica en el denominador del candidato de Hayward, la acción no local subyacente debe incorporar operadores $R F(\Box) R$ con funciones de transferencia racionales específicas que representen la interacción colectiva no perturbativa de los modos gravitacionales en el régimen de campo fuerte.
