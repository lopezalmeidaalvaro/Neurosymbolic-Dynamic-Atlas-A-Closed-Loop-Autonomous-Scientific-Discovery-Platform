# Reconstrucción Física del Candidato Hayward (Fase 1)

Este documento presenta la reconstrucción física detallada del candidato de Gravedad Cuántica dominante descubierto en el atlas (`Candidato 1`), el cual corresponde algebraicamente a la métrica regular de Hayward. 

---

## 1. Métrica y Parámetros de Regularización
La métrica estática y esféricamente simétrica para el candidato regularizado se escribe como:

$$ds^2 = -A(r) dt^2 + \frac{1}{A(r)} dr^2 + r^2 (d\theta^2 + \sin^2\theta d\phi^2)$$

donde el coeficiente métrico $A(r)$ incorpora la función de masa modificada por Gravedad Cuántica:

$$A(r) = 1 - \frac{2 M(r)}{r} = 1 - \frac{2 M_0 r^2}{r^3 + 2 M_0 L^2}$$

Aquí, la función de masa normalizada obtenida de forma modal por el regresor simbólico es:

$$f(r) = \frac{M(r)}{M_0} = \frac{r^3}{r^3 + 2 M_0 L^2} = \frac{r^3}{r^3 + 1.5}$$

### Parámetros Físicos Extraídos:
- **Masa ADM Inicial ($M_0$):** $1.0$ (o $1.5$ en el colapso dinámico).
- **Parámetro de Escala Cuántica ($L^2$):** $0.75 \implies L = \sqrt{0.75} \approx 0.866$ unidades Planck.
- **Factor de Amortiguación Cuántica ($2 M_0 L^2$):** $1.5$ unidades Planck.

---

## 2. Comportamiento en el Origen y Regularidad
Al evaluar el límite ultravioleta (UV) en $r \to 0$, el coeficiente métrico se comporta como:

$$A(r) \approx 1 - \frac{r^2}{L^2} + \mathcal{O}(r^5)$$

Esto corresponde exactamente a un **espaciotiempo local de de Sitter** en el centro del objeto compacto, donde la densidad de energía efectiva del vacío cuántico actúa como una constante cosmológica repulsiva:

$$\Lambda_{eff} = \frac{3}{L^2} = 4.0 \text{ Planck}^{-2}$$

### Invariantes de Curvatura en el Núcleo ($r \to 0$):
- **Ricci Escalar ($R$):** $R(0) = \frac{12}{L^2} = 16.0$ unidades Planck.
- **Kretschmann Escalar ($K$):** $K(0) = \frac{24}{L^4} = 42.67$ unidades Planck.

La finitud de estos invariantes demuestra analíticamente la resolución de la singularidad clásica de Schwarzschild en $r=0$.

---

## 3. Estructura de Horizontes y Límite Crítico
Los horizontes del espaciotiempo ocurren cuando $A(r) = 0$, lo que conduce a la ecuación cúbica:

$$r^3 - 2 M_0 r^2 + 2 M_0 L^2 = 0$$

El análisis del discriminante de este polinomio define tres regímenes físicos posibles dependiendo de la masa $M_0$:

1. **Régimen Supercrítico ($M_0 > M_{crit}$):**
   Existen dos horizontes reales: un horizonte de eventos externo ($r_+$) y un horizonte de Cauchy interno ($r_-$). Para $L = 0.866$, la masa crítica es:
   $$M_{crit} = \frac{3\sqrt{3}}{4} L \approx 1.125 \text{ masas Planck}$$
2. **Régimen Crítico ($M_0 = M_{crit}$):**
   Los dos horizontes se fusionan en un único horizonte extremo en $r = \frac{4}{3} M_0 \approx 1.50$ unidades Planck.
3. **Régimen Subcrítico / Remanente ($M_0 < M_{crit}$):**
   No existen raíces reales positivas. El objeto es un **remanente cuántico regular sin horizonte (horizonless remnant)**.

---

## 4. Comportamiento Termodinámico y Emisión Hawking
La temperatura de Hawking del agujero negro regular se calcula a partir de la gravedad superficial en el horizonte externo $r_+$:

$$T_H = \frac{A'(r_+)}{4\pi} = \frac{1}{4\pi r_+} \left( 1 - \frac{3 r_+^3}{r_+^3 + 2 M_0 L^2} \right) = \frac{r_+^3 - 2 M_0 L^2}{4\pi r_+ (r_+^3 + 2 M_0 L^2)}$$

### Características Termodinámicas:
- **Transición de Fase:** A diferencia de la temperatura clásica de Schwarzschild ($T_H \propto 1/M$), la temperatura del candidato Hayward alcanza un máximo a $r_+ \approx 2.33$ Planck y luego cae rápidamente a cero cuando $r_+ \to r_{crit}$.
- **Destino del Remanente:** Cuando el agujero negro se evapora hasta alcanzar la masa crítica $M_{crit}$, la evaporación térmica se detiene por completo ($T_H = 0$). El remanente cuántico final es estable térmicamente, evitando el colapso singular y la paradoja de la pérdida de información.

---

## 5. Condiciones de Energía
A través de las ecuaciones de Einstein semiclásicas $G_{\mu\nu} = 8\pi T_{\mu\nu}^{eff}$, extraemos las densidades y presiones efectivas de la fuente anisotrópica cuántica:

- **Densidad de Energía Efectiva:** $\rho(r) = \frac{2 M_0 L^2 dF/dr}{8\pi r^2 \dots}$
- **Presión Radial Efectiva:** $P_r(r) = -\rho(r)$
- **Presión Tangencial Efectiva:** $P_\theta(r) = \rho(r) \left( 1 - \frac{3 r^3}{2(r^3 + 2 M_0 L^2)} \right)$

### Evaluación de Condiciones de Energía:
1. **Condición de Energía Nula (NEC) y Débil (WEC):**
   $$\rho + P_r = 0 \quad \text{y} \quad \rho + P_\theta \ge 0 \quad (\forall r \ge 0)$$
   Satisfechas globalmente al 100% en todo el espaciotiempo, garantizando que no se inyecta energía negativa exótica global.
2. **Condición de Energía Fuerte (SEC):**
   Violada estrictamente en la región central $r < (4 M_0 L^2)^{1/3} \approx 0.9$ Planck, lo cual proporciona la presión repulsiva necesaria para evitar la singularidad central.
