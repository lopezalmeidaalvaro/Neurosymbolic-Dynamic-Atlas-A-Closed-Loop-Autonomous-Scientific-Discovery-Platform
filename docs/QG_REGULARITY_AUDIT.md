# FASE 2 — Auditoría de Regularidad de Curvatura

En esta fase realizamos una auditoría de regularidad geométrica rigurosa de los tres candidatos mediante el cálculo de sus límites analíticos exactos y la evaluación de sus invariantes de curvatura de Riemann.

---

## Ecuaciones de Métrica e Invariantes

Para un espaciotiempo estático con simetría esférica en coordenadas de Schwarzschild $(t, r, \theta, \phi)$, la métrica regularizada se define por:
$$ds^2 = -A(r) dt^2 + A(r)^{-1} dr^2 + r^2 d\Omega^2, \quad A(r) = 1 - \frac{2 M f(r)}{r}$$

Donde la masa ADM se fija a $M = 1.0$ para todas las auditorías numéricas.

Derivamos simbólicamente mediante `sympy` los dos invariantes más importantes en Relatividad General para caracterizar singularidades físicas:
1. **Ricci Escalar ($R$):**
   $$R(r) = \frac{2 M}{r^2} \left(r f''(r) + 2 f'(r)\right)$$
2. **Kretschmann Escalar ($K = R_{abcd} R^{abcd}$):**
   $$K(r) = A''(r)^2 + \frac{4 A'(r)^2}{r^2} + \frac{4 (1 - A(r))^2}{r^4}$$

---

## Tabla de Límites Analíticos en $r \to 0$ y $r \to \infty$

Evaluando simbólicamente los tres candidatos candidatos para la masa ADM $M = 1.0$:

| Candidato | Límite $r \to 0$ de $g_{tt}$ | Límite $r \to 0$ de $R$ | Límite $r \to 0$ de $K$ | Límite $r \to \infty$ de $g_{tt}$ | Límite $r \to \infty$ de $R$ | Límite $r \to \infty$ de $K$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Candidato 1: Hayward** | **$-1.0$** | **$+16.0$** | **$+42.67$ ($128/3$)** | **$-1.0$** | **$0.0$** | **$0.0$** |
| **Candidato 2: Gaussiano** | $+\infty$ | $+\infty$ | $+\infty$ | $-1.0$ | $0.0$ | $0.0$ |
| **Candidato 3: Cuadrático** | $+\infty$ | $-\infty$ | $+\infty$ | $-1.0$ | $0.0$ | $0.0$ |

---

## Análisis de Singularidades y Regularización

### 1. Candidato 1 — Hayward ($f(r) = \frac{r^3}{r^3 + 1.5}$)
- **¿Existe singularidad física?** **NO.** Todos los invariantes físicos de curvatura ($R$ y $K$) convergen a valores constantes completamente finitos en el origen radial ($r = 0$).
  - Ricci Escalar en el centro: $R(0) = 16.0$ (Unidades de Planck).
  - Kretschmann en el centro: $K(0) = \frac{128}{3} \approx 42.67$ (Unidades de Planck).
- **¿Existe singularidad de coordenadas?** **NO.** La métrica $g_{tt}(0) = -1.0$ es completamente regular e idéntica a la métrica plana de Minkowski en el origen.
- **¿Existe regularización efectiva?** **SÍ.** El Candidato 1 logra una regularización completa de la curvatura del espaciotiempo clásica (donde $R$ y $K$ divergirían a infinito como $1/r^3$ y $1/r^6$). A distancias infinitas, el espaciotiempo tiende asintóticamente a la planitud plana ($g_{tt} \to -1.0, R \to 0, K \to 0$), recuperando perfectamente la física clásica en el infinito.

### 2. Candidato 2 — Gaussiano ($f(r) = 0.535 e^{-0.196(r-1.612)^2}$)
- **¿Existe singularidad física?** **SÍ.** A pesar del alto score numérico debido a su buen ajuste en distancias medias, los invariantes $R(r)$ y $K(r)$ de este candidato divergen a $+\infty$ cuando $r \to 0$.
- **¿Existe singularidad de coordenadas?** **SÍ.** El factor métrico $g_{tt}(r) \to +\infty$ a corta distancia, lo que invalida la consistencia causal del espaciotiempo.
- **¿Existe regularización efectiva?** **NO.** Este ansatz no regulariza la singularidad central. Esto ocurre porque en el límite $r \to 0$, la función gaussiana tiende a un valor constante no nulo ($f(0) \approx 0.3215$), lo que provoca que el factor métrico de Schwarzschild modificado contenga un término singular del tipo $\sim 1/r$, causando la divergencia de todas las curvaturas en el origen.

### 3. Candidato 3 — Racional Cuadrático ($f(r) = \frac{0.891}{1 + 0.012 r^2}$)
- **¿Existe singularidad física?** **SÍ.** Tanto el Ricci escalar ($R \to -\infty$) como el Kretschmann ($K \to +\infty$) presentan divergencias físicas en $r \to 0$.
- **¿Existe singularidad de coordenadas?** **SÍ.** $g_{tt}(r) \to +\infty$ en el origen.
- **¿Existe regularización efectiva?** **NO.** La función en $r \to 0$ tiende a $f(0) = 0.891 \neq 0$. Por lo tanto, el factor correctivo $\frac{2M f(r)}{r}$ sigue comportándose como $1/r$ en el origen, fallando en suavizar la métrica de Schwarzschild clásica.

---

## Conclusión

El análisis de regularidad analítica mediante SymPy demuestra inequívocamente que **únicamente el Candidato 1 posee interés genuino en Gravedad Cuántica**, ya que es el único capaz de amortiguar y disolver las divergencias del espaciotiempo de Schwarzschild clásico. La caída cúbica en el origen de $f(r) \sim r^3$ contrarresta exactamente la divergencia $1/r$ del término gravitacional, logrando una regularidad de curvatura matemáticamente impecable.
