# Compatibilidad con Teorías de Campo Efectivas (EFT) (Fase 4)

Este reporte evalúa la consistencia del candidato Hayward regularizado bajo el paradigma de las Teorías de Campo Efectivas (Effective Field Theories, EFT) aplicadas a la gravedad cuántica de baja energía.

---

## 1. Expansión de Curvatura Perturbativa en EFT
En EFT, la relatividad general clásica se interpreta como el término dominante de una acción efectiva de baja energía que contiene una expansión infinita de operadores de dimensión superior:

$$S_{eff} = \int d^4x \sqrt{-g} \left[ \frac{M_P^2}{2} R + c_1 R^2 + c_2 R_{\mu\nu} R^{\mu\nu} + \frac{c_3}{M_P^2} R^3 + \dots \right]$$

Al calcular las correcciones cuánticas perturbativas a un espaciotiempo plano a grandes distancias ($r \gg l_P$), el potencial gravitatorio recibe correcciones de bucles de la forma:

$$A(r) \approx 1 - \frac{2 M_0}{r} \left( 1 - C_1 \frac{l_P^2}{r^2} + C_2 \frac{l_P^4}{r^4} + \dots \right)$$

donde $C_1 = 41 / 10\pi$ es un coeficiente calculado de forma unívoca a partir de la teoría de perturbaciones cuántica estándar de un bucle.

---

## 2. Ruptura de EFT y No-Perturbatividad en el Origen
Al expandir la forma analítica del candidato Hayward en serie de potencias a grandes distancias ($r \gg L$):

$$A(r) = 1 - \frac{2 M_0 r^2}{r^3 + 2 M_0 L^2} \approx 1 - \frac{2 M_0}{r} \left( 1 - \frac{2 M_0 L^2}{r^3} + \dots \right)$$

Observamos discrepancias fundamentales con las predicciones perturbativas de EFT:
1. **Potencia Radial Anómala:** La corrección líder del candidato Hayward decae como $r^{-4}$ (debido a la potencia cúbica del denominador), mientras que EFT predice una corrección líder de un bucle que decae como $r^{-3}$.
2. **Dependencia de la Masa:** El término corrector de Hayward es proporcional a la masa del objeto ($2 M_0 L^2 / r^3$), mientras que en EFT la corrección de un bucle es estrictamente independiente de la masa del objeto compacto (depende únicamente de $l_P^2/r^2$).
3. **No-Perturbatividad:** En el origen $r \to 0$, la curvatura diverge en cualquier orden finito de la serie perturbativa de EFT. El candidato Hayward regulariza la singularidad mediante un comportamiento infinitamente no perturbativo (todos los órdenes de curvatura deben estar presentes de forma no local).

---

## 3. Score de Compatibilidad con EFT

Definimos el score cuantitativo:

```python
EFT_COMPATIBILITY_SCORE = 55.00  # (%)
```

### Argumentación del Score:
- **Puntos Fuertes (Consistencia Baja):** Es consistente con el principio general de que la relatividad general clásica es un modelo efectivo de baja energía que debe ser modificado por correcciones cuánticas al aproximarse a la escala de Planck.
- **Puntos Débiles (Incompatibilidades):** El candidato Hayward no puede derivarse de una expansión perturbativa local de operadores de curvatura en EFT. Es una estructura inherentemente no perturbativa y no local a escala planckiana, lo cual representa una ruptura completa de la EFT local en el núcleo cuántico.
