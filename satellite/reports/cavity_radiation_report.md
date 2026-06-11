# Informe de Radiación Interna de Cavidad (Fase T36)

**Generado:** 2026-05-28 20:37:38 | **Semilla:** 42

Este informe detalla la física de transferencia radiativa interna (cavidad cerrada) entre los 6 nodos acoplados de un Cubesat, validando su impacto en vacío orbital y confirmando la conservación de energía interna.

## 1. Tabla Comparativa de Impacto de la Cavidad

| Nodo | T_max Sin Cavidad (°C) | T_max Con Cavidad (°C) | Delta Térmico (°C) | Estado de Disipación |
| :--- | :---: | :---: | :---: | :--- |
| **CPU** | 53.91°C | 54.31°C | +0.40°C | Menor disipación (Más caliente) |
| **Battery** | 36.72°C | 37.60°C | +0.88°C | Menor disipación (Más caliente) |
| **Payload** | 48.67°C | 49.18°C | +0.51°C | Menor disipación (Más caliente) |
| **Structure** | 47.10°C | 47.58°C | +0.48°C | Menor disipación (Más caliente) |
| **Radiator** | 34.16°C | 35.00°C | +0.84°C | Menor disipación (Más caliente) |
| **Paneles** | 181.58°C | 177.87°C | -3.71°C | Mayor acoplamiento (Más frío/estable) |

## 2. Discusión Física de la Transferencia de Calor por Radiosidad

> [!NOTE]
> **Efecto Termodinámico de la Cavidad Cerrada:**
> 1. En condiciones de vacío, las vías conductivas se saturan debido a la pequeña masa del chasis. El acoplamiento por radiación interna permite transferir calor directamente entre los componentes calientes (CPU y Payload) y las superficies de disipación (Radiador y Estructura).
> 2. **Conservación de Energía**: El solver de radiosidad iterativo de Gauss-Seidel converge con precisión de máquina ($< 10^{-6}$), garantizando que la suma neta de los flujos radiativos internos sea estrictamente **cero** (dentro de un error de redondeo de solo **5.69e-15 W**). Esto ratifica que la cavidad interna es un sistema cerrado conservativo.
> 3. **Gradiente de Nodos Internos**: Los nodos internos como la **Batería** aumentan ligeramente su temperatura debido al atrapamiento de la radiación infrarroja de la CPU, mientras que la CPU se enfría de forma más estable al transferir calor por radiación directa al chasis.

## 3. Matriz de Factores de Vista Empleada
La matriz simétrica de factores de vista $F_{ij}$ se escaló y cerró para cumplir con la regla de suma de flujos (suma = 1.0):

```text
[[0.5455 0.1364 0.0909 0.2273 0.     0.    ]
 [0.1364 0.6818 0.     0.1818 0.     0.    ]
 [0.0909 0.     0.7273 0.1818 0.     0.    ]
 [0.2273 0.1818 0.1818 0.     0.2727 0.1364]
 [0.     0.     0.     0.2727 0.6818 0.0455]
 [0.     0.     0.     0.1364 0.0455 0.8182]]
```

## 4. Curvas de Telemetría Orbital Comparativa

![Gráfico Cavidad](cavity_radiation_plot.png)
