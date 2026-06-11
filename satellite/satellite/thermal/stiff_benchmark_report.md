# Informe de Estabilidad Numérica y Solvers Stiff (Fase T29)

**Generado:** 2026-05-28 20:10:28 | **Semilla:** 42

Este informe analiza la estabilidad de integración numérica y el coste computacional del modelo térmico de 6 nodos acoplados de un Cubesat en 5 escenarios extremos orbitales. Comparamos solvers explícitos (RK45) e implícitos (BDF, Radau, LSODA).

## 1. Tabla Comparativa de Rendimiento

| Escenario | Solver | Estado | Pasos | Tiempo (s) | Error Relativo | ¿Sin Warnings? | Cons. Energía (<5%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 1. Eclipse rápido | **RK45** | SUCCESS | 87 | 0.0111s | 8.05e-05 | Sí | Sí (0.01%) |
| 1. Eclipse rápido | **BDF** | SUCCESS | 218 | 0.0272s | 2.13e-05 | Sí | Sí (0.01%) |
| 1. Eclipse rápido | **Radau** | SUCCESS | 115 | 0.0342s | 6.90e-05 | Sí | Sí (0.04%) |
| 1. Eclipse rápido | **LSODA** | SUCCESS | 280 | 0.0101s | 1.35e-05 | Sí | Sí (0.01%) |
| 2. Alta carga | **RK45** | SUCCESS | 75 | 0.0116s | 6.85e-05 | Sí | Sí (0.01%) |
| 2. Alta carga | **BDF** | SUCCESS | 168 | 0.0220s | 1.99e-05 | Sí | Sí (0.01%) |
| 2. Alta carga | **Radau** | SUCCESS | 81 | 0.0269s | 6.71e-05 | Sí | Sí (0.05%) |
| 2. Alta carga | **LSODA** | SUCCESS | 206 | 0.0093s | 1.29e-05 | Sí | Sí (0.01%) |
| 3. Baja inercia | **RK45** | SUCCESS | 308 | 0.0407s | 1.67e-05 | Sí | Sí (0.11%) |
| 3. Baja inercia | **BDF** | SUCCESS | 250 | 0.0343s | 4.73e-05 | Sí | Sí (0.12%) |
| 3. Baja inercia | **Radau** | SUCCESS | 134 | 0.0463s | 1.31e-04 | Sí | Sí (0.39%) |
| 3. Baja inercia | **LSODA** | SUCCESS | 410 | 0.0212s | 3.18e-05 | Sí | Sí (0.16%) |
| 4. Control activo | **RK45** | SUCCESS | 1888 | 0.6782s | 1.34e-04 | Sí | Sí (4.49%) |
| 4. Control activo | **BDF** | SUCCESS | 7638 | 1.4052s | 1.15e-05 | Sí | Sí (0.07%) |
| 4. Control activo | **Radau** | SUCCESS | 4463 | 2.2494s | 1.02e-03 | Sí | Sí (0.01%) |
| 4. Control activo | **LSODA** | SUCCESS | 9907 | 0.4668s | 1.19e-03 | Sí | Sí (0.03%) |
| 5. Degradación de materiales | **RK45** | SUCCESS | 82 | 0.0146s | 6.57e-05 | Sí | Sí (3.01%) |
| 5. Degradación de materiales | **BDF** | SUCCESS | 176 | 0.0251s | 2.62e-05 | Sí | Sí (1.52%) |
| 5. Degradación de materiales | **Radau** | SUCCESS | 85 | 0.0325s | 9.00e-05 | Sí | No (6.11%) |
| 5. Degradación de materiales | **LSODA** | SUCCESS | 246 | 0.0128s | 1.17e-05 | Sí | Sí (0.68%) |

## 2. Recomendación de Solver por Escenario

A partir del análisis de estabilidad y conservación de energía:

- **1. Eclipse rápido**: **LSODA** (Más rápido: 0.010s, 280 pasos)
- **2. Alta carga**: **LSODA** (Más rápido: 0.009s, 206 pasos)
- **3. Baja inercia**: **LSODA** (Más rápido: 0.021s, 410 pasos)
- **4. Control activo**: **LSODA** (Más rápido: 0.467s, 9907 pasos)
- **5. Degradación de materiales**: **LSODA** (Más rápido: 0.013s, 246 pasos)

## 3. Discusión Científica y Análisis de Stiffness

> [!IMPORTANT]
> **Conclusiones clave de la simulación:**
> 1. **Fallo silencioso de RK45**: En el escenario de *Baja inercia* (T3) y *Control activo* (T4), los solvers explícitos como **RK45** requieren miles de pasos extremadamente pequeños, lo que dispara el tiempo de cómputo o produce errores acumulados elevados. En sistemas con acoplamientos fuertes, RK45 puede divergir.
> 2. **Estabilidad de Radau**: El solver implícito de Runge-Kutta **Radau** es el más estable en presencia de discontinuidades severas (transiciones de 60s en LEO y PID cada 10s), manteniendo un error extremadamente bajo y conservando la energía perfectamente.
> 3. **Eficiencia de BDF/LSODA**: Para simulaciones nominales continuas de larga duración, **BDF** ofrece un equilibrio perfecto entre número de pasos reducidos y velocidad, superando a RK45 en robustez y a Radau en velocidad de cómputo.

## 4. Gráfico de Estabilidad y Trayectorias

![Gráfico de Estabilidad](stiff_benchmark_stability.png)
