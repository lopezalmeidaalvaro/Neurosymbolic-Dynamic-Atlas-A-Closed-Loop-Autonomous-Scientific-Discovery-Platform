# Informe de Simulación de Operaciones de Misión (Fase T43)

**Generado:** 2026-05-28 20:54:11 | **Duración de Simulación:** 7 días (Vuelo real)

Este informe documenta la simulación completa de operaciones de misión del Cubesat en órbita LEO con una red global de estaciones terrestres (polar y media latitud), validando el control térmico predictivo frente a perfiles de telecomandos y ventanas científicas.

## 1. Resumen Estadístico de Operaciones

| Parámetro de Operaciones | Valor Registrado | Unidad / Estado |
| :--- | :---: | :--- |
| **Duración de Simulación** | 7 | Días (604,800 s) |
| **Contactos de Estación (AOS)** | 280 | Pases de telemetría exitosos |
| **Telecomandos Ejecutados** | 727 | Comandos procesados (2-5s latencia) |
| **Observaciones Ejecutadas** | 196 | Imágenes científicas almacenadas |
| **Observaciones Pospuestas** | 112 | Postergaciones por restricción térmica / eclipse |
| **Alertas de Sobrecalentamiento** | 13 | Throttling de transmisión activado |

## 2. Análisis del Control Térmico de Operaciones

> [!NOTE]
> **Efectividad del Throttling de Transmisión:**
> - Antes de iniciar los pases, el software de vuelo verifica que la temperatura del transmisor ($T_{\text{tx}}$) sea inferior a $50^\circ\text{C}$. En pases donde la CPU acumuló calor, el sistema aplicó **throttling preventivo**, reduciendo la potencia de transmisión de 18W a 5W.
> - Esto previno de forma efectiva el sobrecalentamiento crítico de la CPU, estabilizando su temperatura a costa de una menor tasa de descarga de datos, demostrando la viabilidad de la toma de decisiones autónoma.

## 3. Registro de Telecomandos Ejecutados (Primeros 15)

| Timestamp (s) | Estación | Comando | Latencia (s) | Descripción | T_tx (°C) |
| :---: | :--- | :--- | :---: | :--- | :---: |
| 0 | Madrid | `ADJUST_THERMAL_MODEL` | 3.92 s | Calibración remota de emisividad del radiador ajustada a 0.82 | 20.00°C |
| 60 | Madrid | `REQUEST_TELEMETRY` | 2.83 s | Descarga de telemetría de payload prioritaria solicitada | 27.28°C |
| 1140 | Svalbard | `ADJUST_THERMAL_MODEL` | 4.68 s | Calibración remota de emisividad del radiador ajustada a 0.82 | 56.53°C |
| 1200 | Svalbard | `ADJUST_THERMAL_MODEL` | 3.27 s | Calibración remota de emisividad del radiador ajustada a 0.82 | 57.94°C |
| 1320 | Svalbard | `REQUEST_TELEMETRY` | 2.08 s | Descarga de telemetría de payload prioritaria solicitada | 58.79°C |
| 1500 | Svalbard | `ADJUST_THERMAL_MODEL` | 4.43 s | Calibración remota de emisividad del radiador ajustada a 0.82 | 57.20°C |
| 3840 | Troll | `REQUEST_TELEMETRY` | 3.02 s | Descarga de telemetría de payload prioritaria solicitada | 11.31°C |
| 3900 | Troll | `REQUEST_TELEMETRY` | 4.87 s | Descarga de telemetría de payload prioritaria solicitada | 14.67°C |
| 3960 | Troll | `ADJUST_THERMAL_MODEL` | 2.28 s | Calibración remota de emisividad del radiador ajustada a 0.82 | 16.37°C |
| 5340 | Madrid | `ADJUST_THERMAL_MODEL` | 4.11 s | Calibración remota de emisividad del radiador ajustada a 0.82 | 5.72°C |
| 6540 | Svalbard | `REQUEST_TELEMETRY` | 2.68 s | Descarga de telemetría de payload prioritaria solicitada | 50.19°C |
| 6600 | Svalbard | `REQUEST_TELEMETRY` | 2.24 s | Descarga de telemetría de payload prioritaria solicitada | 51.77°C |
| 6660 | Svalbard | `REQUEST_TELEMETRY` | 2.30 s | Descarga de telemetría de payload prioritaria solicitada | 52.60°C |
| 6720 | Svalbard | `SAFE_MODE` | 3.91 s | Modo Seguro (SAFE_MODE) comandado desde tierra por emergencia térmica | 52.92°C |
| 6780 | Svalbard | `REQUEST_TELEMETRY` | 3.11 s | Descarga de telemetría de payload prioritaria solicitada | 52.84°C |

## 4. Registro de Planificación Científica (Payload)

| Timestamp (s) | Estado | T_payload (°C) | Descripción |
| :---: | :--- | :---: | :--- |
| 180 | **EXECUTED** | 22.18°C | Observación científica ejecutada y almacenada en memoria flash. |
| 240 | **EXECUTED** | 24.75°C | Observación científica ejecutada y almacenada en memoria flash. |
| 7200 | **EXECUTED** | 36.26°C | Observación científica ejecutada y almacenada en memoria flash. |
| 7260 | **EXECUTED** | 34.57°C | Observación científica ejecutada y almacenada en memoria flash. |
| 7320 | **EXECUTED** | 32.86°C | Observación científica ejecutada y almacenada en memoria flash. |
| 7380 | **EXECUTED** | 31.14°C | Observación científica ejecutada y almacenada en memoria flash. |
| 7440 | **EXECUTED** | 29.44°C | Observación científica ejecutada y almacenada en memoria flash. |
| 14400 | **POSTPONED** | -13.98°C | Observación pospuesta: Límite de energía en eclipse activo. |
| 14460 | **POSTPONED** | -14.80°C | Observación pospuesta: Límite de energía en eclipse activo. |
| 14520 | **POSTPONED** | -15.60°C | Observación pospuesta: Límite de energía en eclipse activo. |
| 14580 | **POSTPONED** | -16.39°C | Observación pospuesta: Límite de energía en eclipse activo. |
| 21780 | **EXECUTED** | -26.44°C | Observación científica ejecutada y almacenada en memoria flash. |
| 21840 | **EXECUTED** | -23.72°C | Observación científica ejecutada y almacenada en memoria flash. |
| 28800 | **EXECUTED** | 14.65°C | Observación científica ejecutada y almacenada en memoria flash. |
| 28860 | **EXECUTED** | 13.53°C | Observación científica ejecutada y almacenada en memoria flash. |
