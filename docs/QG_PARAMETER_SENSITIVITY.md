# FASE 6 — Robustez y Sensibilidad Paramétrica

En esta sexta fase de la auditoría de estabilidad dinámica, realizamos un barrido paramétrico sobre el parámetro de regularización cuántica $L \in [0.5, 2.0]$ para evaluar cómo influye en la estructura de horizontes, la naturalidad física y la susceptibilidad del espaciotiempo a la inestabilidad dinámica de inflación de masa.

---

## Estructura de Horizontes vs. Parámetro L

Para una masa ADM fija $M = 2.0$, la posición de los horizontes de eventos $r_+$ y Cauchy $r_-$ se determina resolviendo la ecuación:
$$r^3 - 4 r^2 + 4 L^2 = 0$$

Analizamos tres regímenes bien diferenciados según el valor de $L$:

1. **Régimen de Agujero Negro Regular de Dos Horizontes ($L < 1.54$):**
   - El espaciotiempo posee un horizonte externo $r_+$ y un horizonte interno de Cauchy $r_-$.
   - **Vulnerabilidad Dinámica:** La presencia del horizonte de Cauchy expone inevitablemente al espaciotiempo a la **inflación de masa** y a la **divergencia de curvatura dinámica** demostrada en las Fases 4 y 5.
2. **Caso Extremo Límite ($L \approx 1.549$):**
   - Los horizontes interno y externo se fusionan en un único horizonte degenerado (agujero negro extremo) en $r_+ = r_- \approx 2.67$.
3. **Régimen de Objeto Compacto Regular sin Horizonte ($L > 1.55$):**
   - La ecuación no posee raíces reales positivas. La presión cuántica de regularización es tan intensa que evita por completo la formación de horizontes.
   - **Inmunidad Dinámica:** Puesto que **no existe horizonte de Cauchy**, este espaciotiempo es **completamente inmune a la inflación de masa** y a la divergencia de curvatura dinámica. La regularización cuántica de curvatura estática de la Fase 30 sobrevive dinámicamente.

Este barrido y transición crítica de horizontes se ilustra de manera clara en la gráfica generada:
![Scan Paramétrico](/figures/parameter_scan.png)

Como se visualiza en `figures/parameter_scan.png`:
- Para valores pequeños de $L$, el horizonte de Cauchy $r_-$ (línea azul) y el horizonte externo $r_+$ (línea verde) están muy separados.
- Conforme $L$ aumenta, el horizonte interno se expande y el externo se contrae.
- En el punto de masa extrema $L \approx 1.55$, ambas curvas colisionan y se detienen abruptamente.
- Para $L > 1.55$, no existen horizontes (el espacio queda en blanco), indicando la transición de fase hacia un **objeto regular supercompacto y dinámicamente estable**.

---

## Sensibilidad de la Inflación de Masa respecto a L

Para el régimen de dos horizontes ($L < 1.55$), evaluamos cómo influye $L$ en la tasa de crecimiento de la inflación de masa, la cual es gobernada por la gravedad superficial $\kappa_-$ del horizonte de Cauchy:
$$\text{Tasa de Crecimiento} = -\kappa_- = -\frac{1}{2} A'(r_-)$$

Sustituyendo la derivada del factor métrico:
$$-\kappa_- = -\frac{2 r_- (r_-^3 - 8 L^2)}{(r_-^3 + 4 L^2)^2}$$

- **Valores Pequeños de $L$ ($L \approx 0.5$):**
  - El horizonte de Cauchy está muy adentro ($r_- \approx 0.53$).
  - La gravedad superficial es sumamente intensa y negativa, lo que provoca una tasa de crecimiento de inflación de masa extremadamente rápida y violenta.
- **Conforme $L$ se aproxima al Límite Extremo ($L \to 1.55$):**
  - Los horizontes se aproximan. En el límite extremo exacto, la gravedad superficial se anula ($\kappa_- \to 0$).
  - Esto disminuye la tasa de crecimiento de la inflación de masa a cero, mitigando temporalmente la inestabilidad en la vecindad inmediata del punto extremo. Sin embargo, esta configuración extrema es altamente inestable ante cualquier perturbación dinámica de la masa que aleje al sistema de la extremidad.

---

## Conclusión de la Robustez Paramétrica

El barrido paramétrico revela un resultado teórico de gran envergadura: **la inestabilidad dinámica del horizonte de Cauchy es genérica para toda la familia de agujeros negros regulares de dos horizontes**. La única vía para preservar la regularidad cuántica central ante perturbaciones dinámicas es entrar en la fase de **Objeto Compacto sin Horizonte ($L > 1.55$, o a masas bajas subcríticas)**. En esta fase, la regularidad cuántica es robusta, dinámicamente estable e inmune a las patologías internas de la Relatividad General relativista clásica.
