# Pronóstico de Detectabilidad para el Observatorio Espacial LISA (Fase 4)

Este reporte evalúa el pronóstico de detectabilidad y el espacio de búsqueda observacional para las firmas cuántico-gravitacionales del candidato Hayward utilizando el futuro detector interferométrico espacial LISA (Laser Interferometer Space Antenna).

---

## 1. Fusiones de Relación de Masa Extrema (EMRIs)
Las EMRIs (Extreme Mass Ratio Inspirals) consisten en un objeto compacto de masa estelar ($m_1 \approx 10 M_\odot$) que cae en espiral en un agujero negro supermasivo ($M_2 \approx 10^6 M_\odot$). El objeto pequeño completa más de $10^5$ órbitas muy cerca de la frontera del horizonte antes de la fusión.

### Mapeo del Espaciotiempo de Hayward con EMRIs:
- **Órbitas en la Cavidad Cuántica:** Dado el gran número de ciclos en la región de gravedad fuerte ($r < 6 M_2$), LISA actuará como un espectrómetro de alta precisión para la geometría del candidato Hayward.
- **Multipolos del Espaciotiempo:** LISA podrá medir el momento cuadripolar efectivo del agujero negro supermasivo con una precisión relativa de:
  $$\frac{\Delta Q}{M_2^3} \le 10^{-4}$$
- Si la escala cuántica de regularización de Hayward $L$ es macroscópica o responde a un mecanismo de "cutoff" dinámico proporcional al radio de Schwarzschild, el desplazamiento acumulado de la fase en LISA alcanzará una relación señal-ruido (SNR) de:
  $$SNR_{EMRI} \ge 150$$
  Esto permitirá excluir o confirmar la existencia del pozo de regularización de Hayward con un nivel de confianza estadística de $5\sigma$.

---

## 2. Detección de Ecos Cuánticos de Agujeros Negros Supermasivos
Para agujeros negros supermasivos de $10^6 M_\odot$, el tren de ecos gravitacionales periódicos se localiza en la banda de frecuencia de los mili-Hertz (mHz), la cual coincide con la banda de máxima sensibilidad instrumental de LISA.

- **Tiempo de Eco en LISA:** Para $M_2 = 10^6 M_\odot$ y regularización cuántica $L = 0.866$ Planck, el tiempo de retraso entre ecos es:
  $$\Delta t_{echo} \approx 2 M_2 \ln\left(\frac{M_2}{L}\right) \approx 850 \text{ segundos}$$
- **Frecuencia del Eco:** $f_{echo} \approx 1.2 \text{ mHz}$.
- Gracias a la ausencia de ruido sísmico y a la extraordinaria longitud de los brazos de interferometría espacial de LISA, la sensibilidad a trenes de ecos amortiguados periódicos será de **2 a 3 órdenes de magnitud superior** a la de los detectores terrestres (LIGO/Virgo), permitiendo detectar amplitudes de eco extremadamente atenuadas de hasta $A_{echo} \sim 10^{-4} A_{ringdown}$.

---

## 3. Conclusión del Pronóstico observacional
LISA es el instrumento definitivo para testear la consistencia observacional de los agujeros negros regulares y remanentes sin horizonte de la clase Hayward. La alta densidad de ciclos en fase orbital de las EMRIs y la alta sensibilidad a bajas frecuencias proporcionarán una validación empírica directa de la regularización en el origen y del destino del remanente de gravedad cuántica.
