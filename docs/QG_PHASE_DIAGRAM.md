# FASE 6 — Diagrama de Fases y Robustez Paramétrica

En esta sexta fase de la auditoría de colapso, exploramos la robustez física y la naturalidad del modelo mediante la realización de un barrido paramétrico masivo en el espacio bidimensional de parámetros:
- **Masa ADM Inicial ($M_0 \in [0.2, 5.0]$):** Controla la cantidad total de materia colapsante.
- **Densidad de Regularización LQC ($\rho_{crit} \in [1.0, 15.0]$):** Representa la escala cuántica a la que se activa la repulsión de Planck (inversamente proporcional a $L^2$).

Construimos el **Diagrama de Fases Dinámico del Colapso Gravitatorio** para mapear los límites exactos de los estados finales.

---

## El Diagrama de Fases Bidimensional

El análisis numérico del espacio de parámetros revela dos fases principales de gravedad cuántica completamente estables y libres de singularidades:

1. **Fase de Remanente sin Horizonte / Rebote Minkowski (Región Verde, `HORIZONLESS_REMNANT`):**
   - **Condiciones:** Masa inicial baja $M_0$ o escala de regularización crítica baja $\rho_{crit}$ (núcleo repulsivo muy grande).
   - **Física:** La densidad de la nube alcanza la escala cuántica crítica $\rho_{crit}$ y rebota *antes* de que su radio exterior cruce el radio de Schwarzschild ($R(t) > R_s(t)$ en todo momento). **No se forma ningún horizonte**. El colapso rebota limpiamente y se dispersa, o se estabiliza en un núcleo regular Planckiano frío y visible.
2. **Fase de Estrella de Planck (Región Marrón, `PLANCK_STAR`):**
   - **Condiciones:** Masa inicial alta $M_0$ (típico de colapsos astrofísicos reales) o escala cuántica crítica alta $\rho_{crit}$ (Planck a distancias extremadamente cortas).
   - **Física:** La nube se contrae por debajo de su radio de Schwarzschild, **creando un horizonte aparente temporal**. Posteriormente, el colapso se detiene debido a la repulsión de LQC, el núcleo rebota y se expande, disolviendo el horizonte aparente a tiempos tardíos y liberando la radiación atrapada.

Este diagrama de fases dinámico se detalla de forma explícita en el plano paramétrico generado:
![Diagrama de Fases](/figures/phase_space.png)

Como se ilustra en `figures/phase_space.png`:
- La **Fase de Remanente sin Horizonte** (verde) domina la parte inferior del plano para masas bajas ($M_0 < 0.35$ para la escala estándar de Planck), extendiéndose a masas superiores si la regularización cuántica es más suave (valores pequeños de $\rho_{crit}$).
- La **Fase de Estrella de Planck** (marrón) domina la región de masas superiores y colapsos astrofísicos masivos, demostrando que la formación de horizontes temporales es la firma astrofísica genérica de los colapsos masivos reales en gravedad cuántica.

---

## Análisis de Robustez y Ausencia de Ajuste Fino

Una de las críticas más severas a los modelos de remanentes estáticos de la Fase 30 era la necesidad de un ajuste fino de sus parámetros de regularización para evitar singularidades y conservar horizontes.

Nuestra auditoría dinámica demuestra lo contrario:
- **Formación Genérica:** Las dos fases regulares de colapso cubren el **100% del espacio paramétrico evaluado**. No existe ninguna combinación de parámetros físicos realistas que conduzca a un colapso singular clásico Divergente.
- **La Singularidad es Imposible:** Puesto que la corrección cuántica de LQC $\rho (1 - \rho/\rho_{crit})$ es un principio fundamental que restringe el crecimiento de la densidad de energía, **la disolución de la singularidad clásica de curvatura es una propiedad universal y genérica** del modelo que no depende de ningún ajuste fino de parámetros. El rebote cuántico y la formación de un estado final regular (estrella de Planck o remanente sin horizonte) son inevitables bajo cualquier configuración de colapso homogéneo.
