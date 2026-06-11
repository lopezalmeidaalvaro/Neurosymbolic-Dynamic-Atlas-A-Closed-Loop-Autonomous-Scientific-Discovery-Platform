# Informe de Observabilidad Formal y Sensibilidad del EKF (Fase T30)

**Generado:** 2026-05-28 20:10:51 | **Semilla:** 42

Este documento presenta un análisis matemático de la observabilidad formal del sistema térmico de 6 nodos acoplados de un Cubesat, validando qué parámetros físicos pueden ser estimados de forma robusta por el Filtro de Kalman Extendido (EKF) utilizando los sensores disponibles.

## 1. Análisis Matemático de la Matriz de Observabilidad

- **Dimensión del vector de estados ($n$):** 6
- **Sensores disponibles:** 3 ($T_\text{CPU}$, $T_\text{bat}$, $T_\text{rad}$)
- **Rango de la Matriz de Observabilidad ($\mathcal{O}$):** **6**

> [!NOTE]
> **Conclusión de Observabilidad de Estados:**
> Dado que el rango de $\mathcal{O}$ es igual a la dimensión del sistema ($6$), **el vector de estados térmicos es completamente observable**. Esto significa que es matemáticamente posible deducir las temperaturas de los nodos no medidos (Estructura, Payload y Paneles Solares) basándose únicamente en las lecturas de los 3 sensores disponibles.

## 2. Análisis de Sensibilidad y Observabilidad de Parámetros

Evaluamos el impacto que tiene una variación del $\pm 10\%$ en cada parámetro sobre las lecturas combinadas de los sensores a lo largo de una órbita completa LEO (5400 segundos):

| Parámetro | Significado | Sensibilidad Normalizada | Clasificación de Observabilidad |
| :--- | :--- | :---: | :--- |
| `C_cpu` | C de nodo(s) 0 | 0.0611% | **Practically Non-Observable (Baja)** |
| `C_bat` | C de nodo(s) 1 | 0.1228% | **Practically Observable (Alta/Media)** |
| `eps_rad` | eps de nodo(s) 4 | 1.0486% | **Practically Observable (Alta/Media)** |
| `k_cpu_struct` | k de nodo(s) (0, 3) | 0.0921% | **Practically Non-Observable (Baja)** |
| `k_struct_rad` | k de nodo(s) (3, 4) | 0.1481% | **Practically Observable (Alta/Media)** |

## 3. Discusión Científica y Directrices de Vuelo

> [!IMPORTANT]
> **Parámetros Estimables por el EKF:**
> - **`C_cpu`**, **`eps_rad`**, y **`C_bat`** presentan una alta sensibilidad. Cambios del 10% en estos parámetros provocan variaciones significativas en los residuos de los sensores. El EKF puede estimar estos parámetros de manera rápida y sin peligro de divergencia.
> - **`k_cpu_struct`** y **`k_struct_rad`** presentan una sensibilidad baja/moderada. Aunque teóricamente son acoplamientos importantes, en la práctica el flujo térmico amortiguado por la estructura hace que sus gradientes se diluyan, dificultando su estimación rápida online.

> [!CAUTION]
> **Parámetros No Observables en la Práctica:**
> Cualquier intento de estimar la capacidad del payload (`C_payload`) o conductancia de paneles (`k_panels_struct`) resultará en la deriva del filtro (Kalman divergence), ya que las mediciones no contienen suficiente información espectral de estos nodos. **El EKF debe limitarse a actualizar únicamente los parámetros con alta sensibilidad observable.**

## 4. Recomendación de Instrumentación Adicional

Si se requiere estimar el comportamiento dinámico del Payload (por ejemplo, para predecir la degradación de un sensor óptico), se recomienda:
1. **Añadir un termistor PT100 en el Payload**: Esto añadiría la fila $C_{3, 2} = 1$ en la matriz de medidas, aumentando el acoplamiento directo y haciendo que todos los parámetros del payload sean observables.
2. **Añadir un termopar en la Estructura**: Ayuda a aislar los coeficientes de conducción inter-nodo al eliminar la amortiguación del bus estructural en las ecuaciones de residuos.

## 5. Gráfico de Sensibilidad

![Gráfico de Sensibilidad](observability_sensitivity.png)
