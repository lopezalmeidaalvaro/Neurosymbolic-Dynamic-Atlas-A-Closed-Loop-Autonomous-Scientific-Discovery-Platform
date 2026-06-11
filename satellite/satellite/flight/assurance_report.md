# Informe de Aseguramiento de Calidad de Software de Vuelo (ECSS + MISRA) (Fase T45)

**Generado:** 2026-05-28 20:53:46 | **Archivo Evaluado:** `surrogate_mlp_inference.c`

Este informe detalla el análisis estático automatizado de la arquitectura del software de vuelo (FSW) del Cubesat, validando su cumplimiento estricto con los estándares de seguridad espacial **ECSS-E-ST-40C** y **MISRA-C:2012**.

## 1. Tabla de Cumplimiento y Mapeo de Requisitos (Trazabilidad)

| Módulo / Función C | Líneas de Código | Complejidad Ciclomática | Requisito ECSS Vinculado | Pre / Post Documentado | Estado de Conformidad |
| :--- | :---: | :---: | :--- | :---: | :--- |
| **relu** | 3 | 1 | ECSS-E-ST-40C-REQ-003 (Mathematical Safe ReLU Boundary Check) | No | **NO_CONFORME** |
| **thermal_mlp_predict** | 31 | 7 | ECSS-E-ST-40C-REQ-TBD (General FSW Module) | No | **NO_CONFORME** |
| **main** | 12 | 2 | ECSS-E-ST-40C-REQ-TBD (General FSW Module) | No | **NO_CONFORME** |

## 2. Infracciones Críticas Detectadas y Mitigación

> [!WARNING]
> **Alertas y Desviaciones de Estándar Registradas:**
> - ECSS Traceability Violation: Function 'relu' is missing structured headers. Preconditions (@pre), postconditions (@post), and requirements (@req) must be documented in header comments.
> - ECSS Traceability Violation: Function 'thermal_mlp_predict' is missing structured headers. Preconditions (@pre), postconditions (@post), and requirements (@req) must be documented in header comments.
> - ECSS Traceability Violation: Function 'main' is missing structured headers. Preconditions (@pre), postconditions (@post), and requirements (@req) must be documented in header comments.

## 3. Matriz de Recomendaciones de FSW
> 1. **Prevención de Punteros Nulos (MISRA Rule 8.1)**: Asegurar que las precondiciones de entrada verifiquen que todos los punteros pasados como argumento son distintos de `NULL` mediante sentencias `assert` controladas.
> 2. **Protección de División por Cero**: Todo cálculo matemático involucrando división debe ejecutarse dentro del método `safe_division(a, b)` para evitar fallos de desbordamiento aritmético en la FPU.
