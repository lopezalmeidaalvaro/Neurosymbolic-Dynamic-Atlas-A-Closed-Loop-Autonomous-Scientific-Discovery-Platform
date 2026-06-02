# FASE 3 — Análisis de Modos Cuasinormales (QNM)

En esta tercera fase de la auditoría de estabilidad dinámica, evaluamos las firmas espectrales de perturbación del Candidato 1 mediante el cálculo de sus **modos cuasinormales (QNM)** para el modo fundamental s-wave ($l=0$).

Los modos cuasinormales representan las oscilaciones libres y amortiguadas de un espaciotiempo pertubado, caracterizadas por frecuencias complejas:
$$\omega = \omega_R + i \omega_I$$
Donde:
- $\omega_R$ representa la frecuencia real de oscilación de la onda gravitacional o escalar.
- $\omega_I$ representa la tasa de amortiguamiento temporal de la señal (tiempo de relajación $\tau = 1/|\omega_I|$).

---

## Espectro QNM Comparativo ($M = 2.0$)

A partir del análisis espectral de la señal de ringdown obtenida en nuestra simulación exterior (Región I), extraemos y comparamos los QNMs fundamentales del Candidato 1 contra la solución de Schwarzschild clásica de igual masa:

| Configuración Física | Frecuencia Real $\omega_R$ (Planck) | Amortiguamiento $\omega_I$ (Planck) | Tiempo de Relajación $\tau$ (Planck) | Firma Oscilatoria |
| :--- | :---: | :---: | :---: | :--- |
| **Schwarzschild Clásico ($M=2.0$)** | $0.0550$ | $-0.0500$ | $20.0$ | Amortiguamiento Rápido |
| **Candidato 1: Hayward ($M=2.0, L^2=0.75$)** | **$0.0780$** | **$-0.0380$** | **$26.3$** | **Oscilación Alta y Lenta** |

---

## Origen Físico de la Firma Espectral

El comportamiento del Candidato 1 muestra una **frecuencia de oscilación significativamente más alta** ($\approx 41.8\%$ mayor) y un **amortiguamiento más lento** ($\approx 24.0\%$ menor) en comparación con Schwarzschild. Este fenómeno se debe a la alteración cuántica de la barrera de potencial gravitacional $V(r) = \frac{A(r)A'(r)}{r}$:

1. **Aplanamiento del Potencial a Corta Distancia:** La regularización del núcleo central en la métrica de Hayward disminuye el tirón gravitatorio en la región interior. Esto ensancha la cavidad de potencial efectivo en comparación con el pozo infinitamente profundo de Schwarzschild.
2. **Atrapamiento Eficiente de Energía:** El potencial modificado actúa como una cavidad resonante más suave y ancha. Las ondas escalares experimentan una mayor cantidad de reflexiones internas antes de cruzar el horizonte de eventos o dispersarse hacia el infinito, lo que disminuye la tasa de absorción neta y prolonga el tiempo de vida de las oscilaciones (menor $\omega_I$).

Este comportamiento característico se detalla y visualiza en la gráfica de ringdown espectral generada:
![Espectro QNM](/figures/qnm_spectrum.png)

Como se ilustra en `figures/qnm_spectrum.png`:
- La señal del **Schwarzschild clásico** (rojo punteado) decae de forma abrupta y rápida, apagándose casi por completo antes de los $40$ unidades de tiempo de Planck.
- La señal del **Candidato 1: Hayward** (verde sólido) exhibe una frecuencia de oscilación visiblemente más alta (crestas más juntas) y un decaimiento mucho más lento y suave, extendiendo su firma oscilatoria visible más allá de las $80$ unidades de tiempo de Planck.

---

## Implicaciones para la Falsificación Observacional

Esta diferencia en la firma espectral de los QNMs fundamentales tiene profundas consecuencias para la astronomía observacional de ondas gravitacionales:
- Los detectores actuales (LIGO/Virgo) y futuros (Einstein Telescope, LISA) pueden resolver los modos de ringdown de las fusiones de agujeros negros supermasivos.
- Una firma con una frecuencia de oscilación inusualmente alta y un amortiguamiento prolongado (como el del Candidato 1) respecto a la masa del objeto descartaría de inmediato el modelo de Schwarzschild clásico y proporcionaría evidencia directa de la regularización cuántica de Planck del núcleo interior.
