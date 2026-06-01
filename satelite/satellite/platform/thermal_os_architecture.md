# Arquitectura del Sistema Operativo Térmico Autónomo (Thermal OS)

**Generado:** 2026-05-28 20:55:52 | **Versión:** 1.0.0-Flight

Este documento detalla la arquitectura de FSW en capas que integra todas las capacidades de detección, estimación, diagnóstico de fallos, control térmico lazo cerrado y self-healing del Cubesat.

## 1. Diagrama de la Arquitectura en Capas

```mermaid
graph TD
  subgraph Perception_Layer["Capa de Percepción (Sensing)"]
    A["Sensores Analógicos PT1000"] --> B["Robust EKF Gating (T38)"]
    B --> C["FDIR Autoencoder Diagnostic (T33)"]
  end
  subgraph Prediction_Layer["Capa de Predicción (AI Core)"]
    D["MLP Surrogate Engine (T31)"] --> E["ECC Weight Check (T39)"]
    E --> F["Priority Scheduler Ticks (T40)"]
  end
  subgraph Decision_Layer["Capa de Decisión (Autonomy)"]
    G["Bang-Bang Heater Hysteresis (T37)"] --> H["Constellation Load Sharing (T47)"]
    H --> I["Operational Mode Controller (T50)"]
  end
  subgraph Safety_Layer["Capa de Seguridad (Safety)"]
    J["Watchdog Timer 50ms (T40)"] --> K["Nelder-Mead Self-Healing (T46)"]
  end
  B --> D
  F --> I
  I --> J
  K --> B
```

## 2. Definición de Capas y Controladores

> [!IMPORTANT]
> **Especificación de Operaciones:**
> 1. **Capa de Percepción**: Encargada de leer la telemetría, descartar ruido parásito EMC/EMI y acoplar el estimador EKF adaptativo para eliminar el TID sensor drift.
> 2. **Capa de Predicción**: Ejecuta de forma determinista el surrogate C99 de la CPU, securizado mediante firmas SHA256 contra Single Event Upsets (SEU).
> 3. **Capa de Decisión**: Controla la calefacción de la batería y la carga de procesamiento del satélite, redistribuyéndola cooperativamente entre satélites de la constelación.
> 4. **Capa de Seguridad**: El watchdog externo monitoriza que el ciclo de inferencia no exceda 50ms, forzando un reinicio físico si la CPU sufre sobrecarga temporal.

