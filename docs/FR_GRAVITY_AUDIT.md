# Auditoría de Gravedad $f(R)$ para el Candidato Hayward (Fase 2)

Este reporte evalúa de manera matemática la viabilidad de reconstruir una teoría de gravedad modificada de la clase $f(R)$ en el vacío capaz de admitir al candidato regular de Hayward como solución clásica.

---

## 1. Escalar de Ricci y No-Invertibilidad de $R(r)$

En gravedad $f(R)$, la curvatura del espaciotiempo está descrita por el escalar de Ricci $R$. Para la métrica de Hayward, el cálculo simbólico arroja:

$$R(r) = \frac{24 M_0^2 L^2 (4 M_0 L^2 - r^3)}{(r^3 + 2 M_0 L^2)^3}$$

### Análisis del Perfil de Curvatura:
1. **Límite Central ($r \to 0$):**
   $$R(0) = \frac{12}{L^2}$$
2. **Mínimo Global (Criticalidad):**
   El punto crítico donde la derivada del escalar de Ricci se desvanece ($R'(r) = 0$) se localiza en:
   $$r_{crit} = (7 M_0 L^2)^{1/3}$$
   Para $M_0 = 1.0, L = 0.866$ ($M_0 L^2 = 0.75$), el punto crítico es:
   $$r_{crit} \approx 1.738 \text{ unidades Planck}$$
   donde el escalar de Ricci alcanza su valor mínimo global:
   $$R_{min} = R(r_{crit}) \approx -0.1316 \text{ Planck}^{-2}$$
3. **Límite Asintótico ($r \to \infty$):**
   $$R(r) \approx - \frac{24 M_0^2 L^2}{r^6} \to 0^-$$

### Consecuencia de No-Invertibilidad:
Debido a que el escalar de Ricci $R(r)$ disminuye desde $+16.0$ hasta $-0.1316$ y luego aumenta asintóticamente hacia $0$, la función $R(r)$ **no es monótona**. 

Por lo tanto, la función **$r(R)$ no es invertible globalmente**. Para cualquier valor de curvatura en el rango $R \in (-0.1316, 0)$, existen múltiples radios $r$ que producen el mismo valor de $R$. Esto impide definir una función analítica $f(R)$ única y de un solo valor en todo el dominio del espaciotiempo.

---

## 2. Reconstrucción de la Serie $f(R)$ en Campo Débil ($R \to 0^-$)

A grandes distancias (campo débil, $r \gg L$), el escalar de Ricci $R \to 0$ desde valores negativos. En este régimen, podemos intentar aproximar $f(R)$ mediante un desarrollo perturbativo en potencias del escalar de curvatura:

$$f(R) = R + \alpha R^2 + \beta R^3 + \mathcal{O}(R^4)$$

En una gravedad $f(R)$ pura en vacío, la ecuación de traza es:

$$3 \Box f_R(R) + f_R(R) R - 2 f(R) = 0$$

donde $f_R(R) \equiv \frac{df}{dR}$. Sustituyendo la expansión:

$$3 \Box (1 + 2 \alpha R + 3 \beta R^2) + (1 + 2 \alpha R + 3 \beta R^2) R - 2(R + \alpha R^2 + \beta R^3) = 0$$

Simplificando a primer orden en $\alpha$ y despreciando términos no lineales de curvatura:

$$-R + 6 \alpha \Box R \approx 0$$

Para la métrica de Hayward a grandes distancias, la curvatura decae como $R \approx -C / r^6$ (con $C = 24 M_0^2 L^2$). El operador de d'Alembertian en el límite plano actúa como:

$$\Box R \approx \frac{d^2 R}{dr^2} + \frac{2}{r} \frac{dR}{dr} \approx - \frac{30 C}{r^8}$$

Sustituyendo en la ecuación de traza:

$$\frac{C}{r^6} - \frac{180 \alpha C}{r^8} \approx 0 \implies \alpha \approx \frac{r^2}{180}$$

### Inconsistencia Física de la Serie:
Dado que el coeficiente $\alpha$ depende del radio de manera cuadrática ($\alpha \propto r^2$), **no existe una constante local $\alpha$** que satisfaga la ecuación en vacío a grandes distancias. Esto demuestra que la geometría de Hayward no puede ser reproducida por ninguna teoría local de gravedad $f(R)$ pura en el vacío.

---

## 3. Análisis de Estabilidad y Modos Fantasma/Taquiónicos

Si forzamos la construcción de una teoría $f(R)$ efectiva aceptando la no-localidad o fuentes adicionales, la estabilidad cuántica de la teoría requiere cumplir dos condiciones estrictas:

1. **Evitación de Fantasmas (Ghost Freedom):**
   $$f_R(R) > 0 \quad (\forall R)$$
   Si $f_R < 0$, la constante de acoplamiento efectiva de Newton se vuelve negativa ($G_{eff} < 0$), lo que implica que el gravitón linealizado transporta energía negativa (estados fantasma con Hamiltoniano no acotado inferiormente).
   
2. **Evitación de Taquiones (Tachyon Freedom):**
   $$f_{RR}(R) > 0 \quad (\forall R)$$
   Si $f_{RR} < 0$, el modo escalar de la teoría (el escalaron) adquiere una masa al cuadrado negativa ($M^2_{scalaron} \approx \frac{1}{3} (f_R/f_{RR} - R) < 0$), desencadenando una inestabilidad taquiónica que hace crecer exponencialmente las perturbaciones del espaciotiempo.

### Evaluación para Hayward:
Como el modelo requiere una transición de un núcleo de tipo de Sitter ($R > 0$) a una métrica plana ($R \to 0^-$) con un punto de inflexión y no-invertibilidad, cualquier mapeo numérico de la traza de las ecuaciones de campo forzado a simular Hayward exhibe singularidades en $f_{RR}$ (donde $R'(r) = 0 \implies f_{RR} \to \infty$) y regiones con $f_{RR} < 0$ en el interior del horizonte de Cauchy. Esto implica que una formulación $f(R)$ efectiva para Hayward estaría plagada de taquiones e inestabilidades de cizalladura.

---

## 4. Conclusión de la Auditoría

El candidato Hayward **no puede ser interpretado como una solución de gravedad $f(R)$ en el vacío**. La no-invertibilidad del escalar de Ricci en el rango de radios astrofísicos y la imposibilidad de balancear la ecuación de traza local con constantes de acoplamiento estáticas descartan por completo esta hipótesis. Cualquier intento de forzar esta correspondencia introduce inestabilidades taquiónicas no físicas en el régimen cuántico central.
