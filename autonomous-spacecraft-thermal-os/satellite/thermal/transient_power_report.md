# Informe de Perfiles de Potencia Transitorios y Eventos de Shock (Fase T37)

**Generado:** 2026-05-28 20:44:36 | **Semilla Principal:** 42

Este informe detalla la simulación térmica avanzada bajo perfiles de potencia dinámicos de misión (comunicaciones, calefacción termostática con histéresis, ráfagas de imagen y maniobras de actitud), evaluando la seguridad térmica global a través de un estudio estadístico de 500 escenarios.

## 1. Resumen Estadístico del Dataset (500 Configuraciones)

| Métrica | Valor Promedio | Desviación Estándar | Máximo Histórico | Límite Crítico |
| :--- | :---: | :---: | :---: | :---: |
| **T_max CPU** | 56.74°C | 3.09°C | 64.28°C | 85.00°C |
| **T_max Batería** | 37.32°C | 0.42°C | 38.64°C | 50.00°C |
| **T_max Payload** | 49.26°C | 0.27°C | 50.52°C | 60.00°C |
| **Consumo Energía (Wh)** | 103.83 Wh | 0.64 Wh | 105.46 Wh | - |
| **Sobrecalentamiento CPU (s)** | 0.0 s | 0.0 s | 0.0 s | - |
| **Sobrecalentamiento Batería (s)** | 0.0 s | 0.0 s | 0.0 s | - |

## 2. Análisis del Control Bang-Bang de la Batería

> [!TIP]
> **Comportamiento del Calefactor con Histéresis:**
> - El calefactor se activa a $0^\circ\text{C}$ y se apaga a $5^\circ\text{C}$, manteniendo la batería en su ventana operativa de almacenamiento y descarga segura.
> - Debido al acoplamiento por radiación interna de la cavidad (Fase T36), la batería recibe calor indirecto de la CPU cuando el transmisor está activo (18W), lo que reduce la necesidad de activación del calefactor eléctrico autónomo de 5W, optimizando el balance de potencia orbital.

## 3. Gráfico de Telemetría Dinámica
El siguiente gráfico muestra el comportamiento dinámico de los perfiles de potencia y la respuesta de temperatura acoplada durante 3 órbitas completas:

![Perfiles de Potencia](transient_power_plot.png)
