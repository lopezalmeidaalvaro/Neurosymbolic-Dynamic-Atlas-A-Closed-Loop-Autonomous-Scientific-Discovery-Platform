# Análisis de Brechas y Necesidades de Calibración TRL 6 (Gap Analysis)

**Generado:** 2026-05-28 20:54:46 | **Semilla:** 42

Este documento detalla las brechas y los recursos reales de hardware e instalaciones requeridos para certificar el Gemelo Digital y el software de vuelo (FSW) desde TRL 5 (Simulado/Entorno controlado) hasta TRL 6 (Modelo de calificación calificado en TVAC/shaker).

## 1. Instalaciones Críticas Requeridas

| Instalación de Ensayos | Finalidad del Ensayo | Duración Estimada | Costo Asociado |
| :--- | :--- | :---: | :--- |
| **Cámara de Vacío Térmico (TVAC)** | Ciclado térmico y balance a $10^{-5}$ Torr | 15 días | Alto (Instalación especializada) |
| **Mesa Vibradora Electrodinámica** | Shaker sinusoidal y aleatorio para ejes X, Y, Z | 3 días | Medio (Laboratorio de vibraciones) |
| **Cámara Anecoica RF** | Certificación EMC/EMI conducted/radiated | 4 días | Medio-Alto |
| **Ciclotrón de Iones Pesados** | Ensayos de radiación de iones pesados (SEE/TID) | 2 días | Extremadamente Alto (Acceso a acelerador) |

## 2. Brechas de Hardware Pendientes (Hardware Gaps)

> [!WARNING]
> **Discrepancias entre Modelos Simulados y de Vuelo:**
> 1. **Modelo de Ingeniería (EQM)**: Se requiere fabricar una réplica física 1:1 del Cubesat (aviónica, chasis, MLI y radiadores) para someterla a los ensayos destructivos de vibración y shock.
> 2. **Sensores de Temperatura de Vuelo**: Sustituir los mocks del termistor de HIL por transductores de platino **PT1000 Clase A** homologados para el espacio (rango $-200^\circ\text{C}$ a $+200^\circ\text{C}$).
> 3. **Procesador Onboard (OBC)**: Validar la ejecución del FSW compilado en C99 en una CPU física **ARM Cortex-M7** (ATSAMV71) con tolerancia a radiación, en lugar de simulación x86.

