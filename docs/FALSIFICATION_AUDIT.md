# Auditoría de Falsabilidad Cuantitativa del Candidato Hayward (Fase 6)

Este reporte presenta la evaluación de falsabilidad del modelo regularizado de Hayward ($f(r) = r^3 / (r^3 + 1.5)$) a través de canales teóricos, astrofísicos, gravitacionales y cosmológicos. El objetivo es determinar si las consecuencias físicas del candidato pueden ser refutadas empíricamente mediante observaciones de precisión.

---

## 1. Rúbrica de Falsabilidad Cuantitativa

Para evaluar la falsabilidad de manera objetiva, definimos cuatro canales independientes de contrastación experimental, asignando una puntuación basada en la viabilidad técnica y precisión de los límites observacionales actuales y proyectados:

### A. Canal de Sombras e Interferometría VLBI (EHT)
- **Criterio:** Capacidad de excluir el parámetro de regularización $L$ mediante el radio de la sombra del agujero negro.
- **Sensibilidad:** Las observaciones de M87* y Sgr A* limitan $L \lesssim 0.1 M_0$. Si el parámetro escala con la masa (p. ej., $L \propto M_0^{1/3}$), el modelo está en la frontera de detección. Para cutoffs estrictamente Planckianos, la desviación de $10^{-88}$ en la sombra es indetectable.
- **Puntuación:** $18/25$ (Falsabilidad moderada debido al límite técnico clásico).

### B. Canal de Modos Cuasinormales y Ecos (LIGO/Virgo/LISA)
- **Criterio:** Medición del desplazamiento hacia el azul del ringdown y detección del tren de ecos gravitacionales periódicos.
- **Sensibilidad:** LISA y los detectores de tercera generación (Einstein Telescope, Cosmic Explorer) podrán medir desfases del ringdown con precisión sub-porcentual e identificar ecos amortiguados con amplitudes relativas tan bajas como $A_{echo}/A_{ringdown} \approx 10^{-4}$.
- **Puntuación:** $22/25$ (Alta falsabilidad dinámica en campo fuerte).

### C. Canal de Coalescencia (Inspiral 3PN)
- **Criterio:** Derivación de desviaciones en la fase de ondas gravitacionales causadas por efectos de regularización y momento cuadripolar modificado.
- **Sensibilidad:** El desfase post-Newtoniano dominante a orden 3PN ($\delta \psi_{3PN} \propto -L^2/M^2$) limita severamente modelos de escala macroscópica. Las EMRIs medidas por LISA permitirán mapear el espaciotiempo y acotar el momento cuadripolar $Q$ con error $\Delta Q/M_3^3 \le 10^{-4}$.
- **Puntuación:** $21/25$ (Muy testeable para binarias asimétricas).

### D. Canal Cosmológico y de Materia Oscura
- **Criterio:** Detección indirecta o límites de abundancia de remanentes cuánticos subcríticos estables de masa Planckiana ($M_{rem} \approx 1.125 M_P$) a temperatura cero.
- **Sensibilidad:** La hipótesis de remanentes como el 100% de la materia oscura fría (CDM) impone una fracción de colapso de agujeros negros primordiales (PBHs) de $\beta \approx 10^{-20}$ para masas iniciales $M_i \approx 10^5\text{ g}$. Esta hipótesis es sensible a las restricciones de la nucleosíntesis primordial (BBN), distorsiones del fondo cósmico de microondas (CMB) y búsquedas directas de WIMPs ultra-pesadas.
- **Puntuación:** $24/25$ (Altamente falsificable debido a la rigidez del límite termodinámico $T_H = 0$).

---

## 2. Cálculo del Score de Falsabilidad (`FALSIFICATION_SCORE`)

El score global de falsabilidad se obtiene como el promedio ponderado de los cuatro canales evaluados:

$$\text{FALSIFICATION\_SCORE} = \frac{S_{VLBI} + S_{QNM} + S_{PN} + S_{Cosmo}}{100} \times 100\%$$

Sustituyendo los valores cuantitativos:

$$\text{FALSIFICATION\_SCORE} = \frac{18 + 22 + 21 + 24}{100} \times 100\% = 85.00\%$$

```python
FALSIFICATION_SCORE = 0.85  # 85.00%
```

---

## 3. Clasificación del Candidato

Bajo la taxonomía formal de falsación física, el candidato se clasifica como:

```python
FALSIFICATION_STATUS = "STRONGLY_FALSIFIABLE"
```

### Justificación de la Clasificación:
El candidato Hayward es clasificado como **STRONGLY_FALSIFIABLE** (Altamente Falsificable) por las siguientes razones fundamentales:
1. **Predicciones numéricas rígidas:** La temperatura de Hawking nula en el remanente crítico $M_{rem} \approx 1.125 M_P$ es un límite ineludible. Si la evaporación de un agujero negro primordial no se detiene y continúa hasta desaparecer por completo, o si el remanente posee una temperatura distinta de cero, el modelo de Hayward queda inmediatamente refutado.
2. **Múltiples canales experimentales independientes:** La regularización cuántica altera simultáneamente la métrica estática (VLBI), la estabilidad dinámica (ecos de perturbaciones) y la cosmología de partículas (abundancia de remanentes), permitiendo que la refutación en un canal invalide de inmediato las asunciones de los otros.
3. **Escala del parámetro $L$:** Si la regularización es macroscópica ($L \propto M^{1/3}$), el tamaño de la sombra angular y las desviaciones de fase en la fase de inspiral ya se encuentran en los límites instrumentales del EHT y LIGO/Virgo. Si la escala es estrictamente Planckiana, el modelo sigue siendo falsificable a través de las firmas cosmológicas de materia oscura de remanentes y la fase del ringdown en detectores de tercera generación (LISA/Einstein Telescope).
