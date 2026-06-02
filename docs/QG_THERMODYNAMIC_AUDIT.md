# FASE 4 — Auditoría Termodinámica

En esta cuarta fase, realizamos un análisis termodinámico riguroso de los candidatos a agujero negro regular, evaluando su comportamiento térmico de Hawking, entropía efectiva y capacidad calorífica local.

---

## Ecuaciones Termodinámicas Fundamentales

Para una métrica esféricamente simétrica dada por $g_{tt} = -A(r)$, los parámetros termodinámicos se evalúan en el horizonte externo $r_h$ (raíz de $A(r_h) = 0$):
1. **Gravedad Superficial ($\kappa$):**
   $$\kappa = \frac{1}{2} A'(r_h)$$
2. **Temperatura de Hawking ($T_H$):**
   $$T_H = \frac{\kappa}{2\pi} = \frac{A'(r_h)}{4\pi}$$
3. **Entropía de Bekenstein-Hawking ($S$):**
   $$S = \frac{\text{Área}}{4} = \pi r_h^2$$
4. **Capacidad Calorífica Local ($C$):**
   $$C = \frac{dM}{dT_H} = \left(\frac{dT_H}{dM}\right)^{-1}$$

---

## Resultados Termodinámicos ($M=1.0$)

Evaluamos los parámetros termodinámicos en el estado actual de masa $M = 1.0$:

| Candidato | Radio Horizonte $r_h$ | Gravedad Superficial $\kappa$ | Temperatura Hawking $T_H$ (Plck) | Entropía $S$ | ¿Evaporación Consistente? |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Candidato 1: Hayward** | **Ninguno ($M < M_{crit}$)** | **N/A** | **N/A** | **N/A** | **SÍ (Fase Remanente Estable)** |
| **Candidato 2: Gaussiano** | $0.992$ | $0.382$ | $0.061$ | $3.094$ | **NO (Colapso Singular a $T \to \infty$)** |
| **Candidato 3: Cuadrático** | $1.721$ | $0.310$ | $0.049$ | $9.303$ | **NO (Colapso Singular a $T \to \infty$)** |

---

## Auditoría Detallada del Candidato 1 (Hayward)

Aunque para $M = 1.0$ el **Candidato 1** se encuentra en su fase de remanente subcrítico sin horizonte (y por lo tanto no tiene temperatura de Hawking ni entropía de área asociadas en ese estado), podemos analizar la **familia termodinámica general** de Hayward para masas superiores a la crítica ($M > 1.082$).

### 1. Relación Analítica Masa-Horizonte:
Evaluando $A(r_h) = 0$ para $f(r) = \frac{r^3}{r^3 + 2 M L^2}$, obtenemos la masa del agujero negro como función del radio de horizonte $r_h$ y de la constante de regularización $L = \sqrt{0.75} \approx 0.866$:
$$M(r_h) = \frac{r_h^3}{2 (r_h^2 - L^2)}$$

### 2. Temperatura de Hawking Analítica:
Derivando $A(r)$ y evaluando en el horizonte, obtenemos la temperatura de Hawking exacta para Hayward:
$$T_H(r_h) = \frac{1}{4\pi r_h} \left( \frac{r_h^2 - 3 L^2}{r_h^2 - L^2} \right)$$

- **Límite Clásico ($L \to 0$):**
  $$T_H \to \frac{1}{4\pi r_h} = \frac{1}{8\pi M}$$
  Se recupera de forma exacta el comportamiento clásico de Schwarzschild, donde la temperatura diverge a infinito cuando el radio tiende a cero.
- **Límite de Remanente Cuántico ($r_h \to \sqrt{3} L$):**
  $$T_H \to 0$$
  La temperatura de Hawking desciende a **cero absoluto** en un radio de horizonte finito $r_{rem} = \sqrt{3} L \approx 1.5$ (Planck). La masa correspondiente a este remanente es:
  $$M_{rem} = \frac{3\sqrt{3}}{4} L \approx 1.125$$
  
Esto demuestra que el agujero negro de Hayward **no se evapora por completo**. Al perder masa debido a la radiación de Hawking, su horizonte se contrae hasta alcanzar $r_{rem}$, donde la evaporación térmica cesa por completo debido a que la temperatura cae a cero. El resultado es un **remanente cuántico estable** y regular, el cual almacena la información inicial y resuelve el dilema de la pérdida de información de Hawking.

---

## Transiciones de Fase y Capacidad Calorífica

La capacidad calorífica local se deriva analíticamente a partir de:
$$C = \frac{dM}{dr_h} \left( \frac{dT_H}{dr_h} \right)^{-1}$$
Donde:
$$\frac{dM}{dr_h} = \frac{r_h^2 (r_h^2 - 3 L^2)}{2 (r_h^2 - L^2)^2}$$

### Comportamiento de Fases:
1. **Fase Agujero Negro Grande ($r_h > \sqrt{3(1 + \sqrt{2})} L \approx 2.69 L$):**
   - $C < 0$ (Capacidad calorífica negativa). El agujero negro clásico es inestable; al perder masa por radiación, su temperatura aumenta.
2. **Punto Crítico de Transición de Fase ($r_h \approx 2.69 L \approx 2.33$ Planck):**
   - La derivada $dT_H/dr_h = 0$, lo que provoca que la capacidad calorífica $C$ diverja a $\pm\infty$. Se produce una **transición de fase de segundo orden** termodinámica.
3. **Fase de Agujero Negro Pequeño y Estable ($\sqrt{3} L < r_h < 2.69 L$):**
   - $C > 0$ (Capacidad calorífica positiva). En esta fase de enfriamiento cuántico, el agujero negro se vuelve termodinámicamente estable; al emitir radiación, se enfría de forma controlada hasta alcanzar $T_H = 0$ en $r_{rem} = \sqrt{3} L$.

Este comportamiento de transición de fase y remanencia estable es termodinámicamente impecable y es una de las razones por las cuales la métrica de Hayward es de un interés físico excepcional en Gravedad Cuántica.

---

## Comparación con Candidatos 2 y 3

Por el contrario, los candidatos **2 (Gaussiano)** y **3 (Cuadrático)** no poseen esta estructura regulada de fases. Al evaporarse, sus horizontes se contraen continuamente sin una fase de transición estable, provocando que la temperatura y la curvatura diverjan catastróficamente en el origen al final de la evaporación. Esto demuestra que estas aproximaciones exponenciales y cuadráticas son físicamente inviables bajo el escrutinio termodinámico.
