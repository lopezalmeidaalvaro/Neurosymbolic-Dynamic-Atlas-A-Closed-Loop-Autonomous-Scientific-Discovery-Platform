# Auditoría de Gravedad Cuadrática del Candidato Hayward (Fase 3)

Este reporte analiza la compatibilidad del candidato regular de Hayward con las teorías de gravedad cuadrática de curvatura, descritas por la acción covariante efectiva:

$$S = \int d^4x \sqrt{-g} \left( R + \alpha R^2 + \beta R_{\mu\nu} R^{\mu\nu} \right)$$

donde $\alpha$ y $\beta$ son constantes de acoplamiento de orden superior que parametrizan correcciones cuánticas de un bucle a la Relatividad General.

---

## 1. Correcciones de Curvatura Dominantes

Evaluamos los términos cuadráticos de curvatura que aparecen en la acción para comprender el comportamiento del candidato Hayward en los regímenes ultravioleta (UV) e infrarrojo (IR).

### A. Límite Ultravioleta ($r \to 0$)
En el núcleo cuántico, el candidato Hayward exhibe una regularidad completa comportándose localmente como un espaciotiempo de de Sitter con $\Lambda_{eff} = 3/L^2$. Las métricas de tipo de Sitter son altamente simétricas y sus tensores de curvatura satisfacen:

$$R_{\mu\nu\rho\sigma} = \frac{1}{L^2} \left( g_{\mu\rho} g_{\nu\sigma} - g_{\mu\sigma} g_{\nu\rho} \right)$$

$$R_{\mu\nu} = \frac{3}{L^2} g_{\mu\nu}, \quad R = \frac{12}{L^2}$$

Calculamos los escalares cuadráticos de curvatura dominantes en este límite:
- **Término $R^2$:**
  $$R^2 \to \left( \frac{12}{L^2} \right)^2 = \frac{144}{L^4}$$
- **Término $R_{\mu\nu} R^{\mu\nu}$:**
  $$R_{\mu\nu} R^{\mu\nu} \to g^{\mu\alpha} g^{\nu\beta} \left( \frac{3}{L^2} g_{\mu\nu} \right) \left( \frac{3}{L^2} g_{\alpha\beta} \right) = \frac{9}{L^4} \delta^\mu_\mu = \frac{36}{L^4}$$

Ambos términos de curvatura son estrictamente finitos y constantes en el centro, lo que confirma que el candidato está libre de singularidades cuadráticas de curvatura en el régimen cuántico profundo.

### B. Límite Infrarrojo / Campo Débil ($r \to \infty$)
A grandes distancias, el espaciotiempo decae hacia la planitud. Usando las derivaciones analíticas del script `derive_actions.py`:
- **Escalar de Ricci ($R$):**
  $$R(r) \approx - \frac{24 M_0^2 L^2}{r^6}$$
  Por lo tanto, la corrección $R^2$ decae como:
  $$R^2 \approx \frac{576 M_0^4 L^4}{r^{12}}$$
- **Ricci Cuadrático ($R_{\mu\nu} R^{\mu\nu}$):**
  Dado que los componentes individuales del tensor de Ricci $R^\mu_\nu$ decaen como $r^{-6}$ debido al perfil cúbico de Hayward:
  $$R_{\mu\nu} R^{\mu\nu} \propto \frac{M_0^4 L^4}{r^{12}}$$

Las correcciones de curvatura cuadrática decaen de forma extremadamente veloz en el infinito (escala $r^{-12}$).

---

## 2. Compatibilidad con las Ecuaciones de Movimiento de Gravedad Cuadrática

Las ecuaciones de campo en vacío para la gravedad cuadrática son de cuarto orden y están dadas por:

$$G_{\mu\nu} + 2\alpha H_{\mu\nu}^{(1)} + \beta H_{\mu\nu}^{(2)} = 0$$

donde $H_{\mu\nu}^{(1)}$ y $H_{\mu\nu}^{(2)}$ provienen de las variaciones de $R^2$ y $R_{\mu\nu} R^{\mu\nu}$ respectivamente. 

### Análisis de Consistencia:
1. **Órdenes de Decaimiento:** 
   El tensor de Einstein clásico $G_{\mu\nu}$ para la métrica de Hayward decae asintóticamente como $r^{-6}$ (ya que $\rho \sim r^{-6}$ y $P_i \sim r^{-6}$).
   Sin embargo, las contribuciones de curvatura cuadrática $H_{\mu\nu}^{(1)}$ y $H_{\mu\nu}^{(2)}$ involucran derivadas segundas de los términos cuadráticos de curvatura, por lo que decaen a grandes distancias como:
   $$H_{\mu\nu} \propto \nabla\nabla(R^2) \sim \frac{M_0^4 L^4}{r^{14}}$$
2. **Incompatibilidad de Escala:**
   Para satisfacer las ecuaciones en vacío a grandes distancias, los términos $G_{\mu\nu}$ ($r^{-6}$) y $H_{\mu\nu}$ ($r^{-14}$) deben balancearse. Dado que decaen con potencias radiales completamente distintas y no existe un término de materia en la ecuación cuadrática pura en vacío, la igualdad es matemáticamente imposible a menos que la masa $M_0$ sea cero o que la constante de acoplamiento cuadrática dependa del radio, lo cual viola la covariancia local.

---

## 3. Conclusión de la Auditoría

El candidato Hayward **no es una solución de vacío de la Gravedad Cuadrática local estándar**. 

Aunque los términos cuadráticos de curvatura en el origen ($R^2 = 144/L^4$, $R_{\mu\nu} R^{\mu\nu} = 36/L^4$) demuestran que la geometría de Hayward es compatible con un control ultravioleta completo de las divergencias cuadráticas, las ecuaciones de movimiento dinámicas a grandes distancias revelan que no existe una constante local $\alpha$ o $\beta$ capaz de generar la caída radial de Hayward en vacío. Nuevamente, la métrica de Hayward debe entenderse como un modelo efectivo sustentado por presiones cuánticas no locales o fluidos efectivos de materia cuántica colectiva.
