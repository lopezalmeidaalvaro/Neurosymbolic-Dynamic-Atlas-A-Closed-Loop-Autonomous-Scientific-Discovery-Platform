# Reconstrucción Einsteiniana del Candidato Hayward (Fase 1)

Este documento detalla la reconstrucción de la física del candidato Hayward ($f(r) = r^3 / (r^3 + 2 M_0 L^2)$) interpretado dentro del marco de la Relatividad General de Einstein ($G_{\mu\nu} = 8\pi T_{\mu\nu}^{eff}$). Derivamos el tensor de energía-momento efectivo necesario y analizamos la violación y cumplimiento de las condiciones de energía.

---

## 1. Derivación del Tensor de Energía-Momento Efectivo ($T_{\mu\nu}^{eff}$)

Para una métrica estática y esféricamente simétrica con $g_{tt} = -A(r)$ y $g_{rr} = A(r)^{-1}$:

$$ds^2 = -A(r) dt^2 + \frac{1}{A(r)} dr^2 + r^2 (d\theta^2 + \sin^2\theta d\phi^2)$$

donde:

$$A(r) = 1 - \frac{2 M_0 r^2}{r^3 + 2 M_0 L^2}$$

El tensor de Einstein $G^\mu_\nu$ en coordenadas estándar es diagonal:

$$G^t_t = - \frac{2 M'(r)}{r^2}$$

$$G^r_r = - \frac{2 M'(r)}{r^2}$$

$$G^\theta_\theta = G^\phi_\phi = - \frac{M''(r)}{r}$$

donde la función de masa efectiva es $M(r) = \frac{M_0 r^3}{r^3 + 2 M_0 L^2}$.

### Densidad de Energía y Presiones
Usando las ecuaciones semiclásicas de Einstein, el tensor de energía-momento efectivo se define como $T^\mu_\nu = \text{diag}(-\rho, P_r, P_t, P_t)$, donde:

1. **Densidad de Energía ($\rho$):**
   $$\rho(r) = \frac{M'(r)}{4\pi r^2} = \frac{3 M_0^2 L^2}{2\pi (r^3 + 2 M_0 L^2)^2}$$

2. **Presión Radial ($P_r$):**
   $$P_r(r) = - \rho(r) = - \frac{3 M_0^2 L^2}{2\pi (r^3 + 2 M_0 L^2)^2}$$

3. **Presión Tangencial / Transversal ($P_t$):**
   $$P_t(r) = \rho(r) \left( \frac{2 r^3 - 2 M_0 L^2}{r^3 + 2 M_0 L^2} \right) = \frac{3 M_0^2 L^2 (r^3 - M_0 L^2)}{\pi (r^3 + 2 M_0 L^2)^3}$$

### Límites Físicos Extremos

- **En el origen ($r \to 0$):**
  $$\rho(0) = \frac{3}{8\pi L^2}, \quad P_r(0) = -\frac{3}{8\pi L^2}, \quad P_t(0) = -\frac{3}{8\pi L^2}$$
  Esto reproduce exactamente la ecuación de estado de un vacío de de Sitter:
  $$P_r(0) = P_t(0) = - \rho(0)$$
  con una constante cosmológica efectiva $\Lambda_{eff} = 8\pi \rho(0) = \frac{3}{L^2}$.

- **A grandes distancias ($r \to \infty$):**
  $$\rho(r) \approx \frac{3 M_0^2 L^2}{2\pi r^6}, \quad P_r(r) \approx - \frac{3 M_0^2 L^2}{2\pi r^6}, \quad P_t(r) \approx \frac{3 M_0^2 L^2}{\pi r^6}$$
  La densidad y las presiones decaen rápidamente como $r^{-6}$, lo que explica por qué el espaciotiempo recupera la geometría clásica de Schwarzschild de forma extremadamente rápida en el campo lejano.

---

## 2. Evaluación de las Condiciones de Energía

Analizamos analíticamente las cuatro condiciones clásicas de energía para todo $r \ge 0$:

1. **Condición de Energía Nula (NEC):**
   - Radial: $\rho + P_r = 0$ (satisfecha de forma idéntica).
   - Transversal: $\rho + P_t = \rho \left( \frac{3 r^3}{r^3 + 2 M_0 L^2} \right) \ge 0$ (satisfecha para todo $r \ge 0$).
   - **Resultado:** **SATISFECHA GLOBALMENTE**.

2. **Condición de Energía Débil (WEC):**
   - Requiere NEC y $\rho \ge 0$. Dado que la densidad de energía es estrictamente positiva para toda masa física:
     $$\rho(r) > 0 \quad (\forall r \ge 0)$$
   - **Resultado:** **SATISFECHA GLOBALMENTE**.

3. **Condición de Energía Dominante (DEC):**
   - Requiere $\rho \ge |P_i|$.
   - Radial: $\rho \ge |P_r| = \rho$ (satisfecha).
   - Transversal: $\rho \ge |P_t| \iff \left| \frac{2 r^3 - 2 M_0 L^2}{r^3 + 2 M_0 L^2} \right| \le 1$.
   - Esto se cumple si y solo si:
     $$r^3 \le 4 M_0 L^2$$
   - Para $r > (4 M_0 L^2)^{1/3}$, la presión tangencial supera la densidad de energía ($P_t > \rho$), lo cual viola la DEC.
   - **Resultado:** **VIOLADA LOCALMENTE** para $r > (4 M_0 L^2)^{1/3}$.

4. **Condición de Energía Fuerte (SEC):**
   - Requiere WEC y $\rho + P_r + 2 P_t \ge 0 \implies 2 P_t \ge 0$.
   - Esto requiere:
     $$r^3 \ge M_0 L^2$$
   - En la región central $r < (M_0 L^2)^{1/3}$, la presión tangencial es negativa ($P_t < 0$), lo que provoca la violación de la SEC.
   - **Resultado:** **VIOLADA LOCALMENTE** en el núcleo central $r < (M_0 L^2)^{1/3}$.

---

## 3. Conclusión: ¿Hayward como GR + Fluido Anisótropo?

**Sí.** A nivel puramente fenomenológico y clásico, la métrica de Hayward puede interpretarse de manera exacta como una solución de la Relatividad General acoplada a un **fluido anisótropo exótico** de materia cuántica efectiva. 

### Características de esta interpretación:
- El núcleo central de de Sitter es producido por una ecuación de estado tipo energía oscura ($p = -\rho$).
- La violación local de la SEC en el núcleo es el mecanismo clásico que evita la formación de la singularidad, proporcionando una fuerza repulsiva que contrarresta el colapso gravitacional.
- Sin embargo, este fluido anisotrópico no corresponde a ningún campo fundamental del Modelo Estándar (como campos escalares o fermiónicos locales estándar), por lo que debe entenderse como la representación clásica media de fluctuaciones cuánticas del espaciotiempo.
