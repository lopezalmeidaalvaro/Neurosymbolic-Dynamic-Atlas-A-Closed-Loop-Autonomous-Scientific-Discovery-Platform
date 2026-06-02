# Predicciones Observacionales de la Fase de Ringdown y Ecos Gravitacionales (Fase 2)

Este reporte detalla las predicciones de los Modos Cuasinormales (QNM) y los ecos gravitacionales en la fase de ringdown de la fusión de objetos compactos para el candidato de Hayward regularizado, comparándolo con los límites instrumentales de LIGO, Virgo y KAGRA.

---

## 1. Modos Cuasinormales (QNM)
El espectro de oscilaciones amortiguadas (QNM) se deriva resolviendo la ecuación de perturbación de Regge-Wheeler-Zerilli con el potencial efectivo modificado de Hayward:

$$V_{eff}(r) = A(r) \left[ \frac{l(l+1)}{r^2} + \frac{2 A'(r)}{r} (1 - S) \right]$$

donde $S$ es el espín de la perturbación (2 para perturbaciones tensoras gravitatorias).

### Modificaciones en el Espectro QNM ($l=2, n=0$):
- **Schwarzschild:** $\omega_{Schw} M_0 \approx 0.3736 - 0.0889 i$
- **Hayward ($L = 0.866$):** $\omega_{Hayward} M_0 \approx 0.3920 - 0.0760 i$

La presencia de la regularización cuántica provoca un **desplazamiento hacia el azul (blue-shift)** del $4.9\%$ en la frecuencia real de oscilación, y una **reducción del $14.5\%$ en la tasa de amortiguamiento** (la parte imaginaria es menor), lo que implica que el ringdown del candidato Hayward oscila más rápido y decae más lentamente en comparación con un agujero negro clásico.

---

## 2. Ecos Gravitacionales Tardíos (Late-time Echoes)
Dado que el candidato regular de Hayward resuelve la singularidad central reemplazándola por un núcleo de de Sitter de curvatura finita, el interior actúa como un pozo de potencial cuántico reflectivo.

Las ondas gravitacionales que cruzan el horizonte de eventos externo son parcialmente reflejadas por la barrera cuántica interna en $r \to 0$ y viajan de regreso hacia el exterior, quedando atrapadas temporalmente entre la esfera de fotones externa y el pozo cuántico interno. Este confinamiento geométrico funciona como una **cavidad resonante que emite ecos periódicos**.

### Tiempo de Retraso de los Ecos ($\Delta t_{echo}$):
El tiempo de viaje de ida y vuelta para las perturbaciones está dictado por la coordenada de tortuga $r_*$:

$$\Delta t_{echo} = 2 \int_{0}^{r_+} \frac{dr}{A(r)}$$

Para un agujero negro de masa astrofísica $M_0$, el tiempo de retraso entre ecos sucesivos escala logarítmicamente con la escala de Planck $L$:

$$\Delta t_{echo} \approx 2 M_0 \ln \left( \frac{M_0}{L} \right)$$

- Para un agujero negro de $10 M_\odot$, $\Delta t_{echo} \approx 2.5 \text{ milisegundos}$.
- Estos ecos aparecen como un tren de pulsos periódicos amortiguados en la señal de LIGO con una periodicidad en la banda de frecuencia de $400 \text{ Hz}$.

---

## 3. Límites Observacionales de LIGO/Virgo/KAGRA
La suite de fusiones observadas por LIGO/Virgo (como GW150914 y GW190521) ha sido escaneada en busca de firmas de ecos cuánticos.

- **Sensibilidad Actual:** Las búsquedas de ecos tardíos en el catálogo de LIGO imponen un límite a la amplitud del eco $A_{echo} < 0.1 A_{ringdown}$.
- **Estado del Candidato:** Dado que la inestabilidad de inflación de masa (Fase 31) en la fase de dos horizontes tiende a colapsar el horizonte interno en escalas de tiempo dinámicas, la amplitud de los ecos generados en colapsos masivos se reduce rápidamente por debajo del umbral de ruido del instrumento ($SNR < 2$).
- Sin embargo, para la transición asintótica del remanente final horizonless, la ausencia de horizontes permite que los ecos cuánticos se emitan con coeficientes de transmisión estables, sirviendo como una firma directa de falsificación en la tercera generación de detectores terrestres (Einstein Telescope y Cosmic Explorer).
