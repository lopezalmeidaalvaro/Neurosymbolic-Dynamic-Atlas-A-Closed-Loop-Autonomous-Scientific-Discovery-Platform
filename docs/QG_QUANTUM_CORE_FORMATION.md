# FASE 3 — Aparición de Efectos Cuánticos y Núcleo Planckiano

En esta tercera fase, analizamos la física detrás del surgimiento de la **presión cuántica repulsiva efectiva** y la formación de un núcleo regular denso de Planck (Planck star core) durante el colapso gravitatorio.

---

## Regularización de Densidad y Ecuación de Estado Cuántica

En la Relatividad General clásica, el colapso de polvo no tiene fuerzas internas que lo frenen, lo que lleva a un crecimiento ilimitado de la densidad de materia:
$$\rho(t) = \frac{\rho_0}{a(t)^3} \to \infty$$

Sin embargo, al incorporar los efectos semiclásicos de la gravedad cuántica, la densidad física real que experimenta la curvatura del espaciotiempo es la **densidad efectiva regularizada ($\rho_{eff}$)**, inspirada en las correcciones de Hayward:
$$\rho_{eff}(t) = \frac{\rho(t)}{1 + \rho(t) / \rho_{crit}}$$

Donde la densidad crítica Planckiana se fija a $\rho_{crit} = 8.0$ (Planck densities).

### Mecanismo de Repulsión Cuántica y Rebote:
1. **Fase Clásica ($\rho \ll \rho_{crit}$):**
   - El factor correctivo $\rho(t) / \rho_{crit} \approx 0$, lo que implica que $\rho_{eff}(t) \approx \rho(t)$. El colapso se comporta exactamente según la física clásica de Oppenheimer-Snyder.
2. **Fase Cuántica de Alta Densidad ($\rho \to \rho_{crit}$):**
   - Conforme $a(t)$ disminuye, la densidad clásica $\rho(t)$ se dispara. Sin embargo, la densidad efectiva $\rho_{eff}(t)$ se desvía de la clásica y comienza a saturarse.
   - En el punto de rebote exacto ($a_{min} \approx 0.2154$), la densidad clásica alcanza $\rho_{max} = 8.0$, lo que provoca que la densidad efectiva regularizada alcance su **límite superior absoluto**:
     $$\rho_{eff\_max} = \frac{8.0}{1 + 8.0/8.0} = 4.0 \text{ Planck}$$
   - Esta saturación de la densidad efectiva se traduce en una **presión exótica repulsiva cuántica** extremadamente intensa que detiene la contracción gravitatoria de la nube, forzando la velocidad de colapso a cero y provocando el **rebote cuántico (quantum bounce)**.

Este comportamiento de regularización y saturación de la densidad se detalla de forma transparente en la simulación:
![Núcleo Cuántico](/figures/quantum_core_growth.png)

Como se ilustra en `figures/quantum_core_growth.png` (escala logarítmica):
- La densidad clásica $\rho(t)$ (curva marrón discontinua) crece sin límites hacia el infinito a medida que el factor de escala decrece.
- La densidad efectiva regularizada $\rho_{eff}(t)$ (curva verde sólido) se desvía drásticamente del comportamiento clásico a altas energías. En lugar de divergir, la densidad efectiva se **satura suavemente**, chocando con el límite de Planck e interactuando con la densidad crítica $\rho_{crit}$ (línea roja punteada) para forzar el rebote y la dispersión.

---

## Estructura de la Estrella de Planck

Esta disolución de la singularidad central da origen a una **Estrella de Planck**: un objeto supercompacto de densidad Planckiana sostenido de forma temporal por las presiones de repulsión cuántica de la gravedad de bucles. El núcleo no colapsa a un punto singular, sino que forma una "esponja cuántica" que rebota y libera la energía acumulada, garantizando que el espaciotiempo permanezca suave y libre de patologías matemáticas en todo momento.
