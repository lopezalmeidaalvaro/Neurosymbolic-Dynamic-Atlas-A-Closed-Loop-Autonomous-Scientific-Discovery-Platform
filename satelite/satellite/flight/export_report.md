# Informe de Exportación de Modelos de Vuelo (ONNX/C) (Fase T31)

Este documento detalla el proceso de compilación, verificación y optimización de los modelos neuronales subrogados (MLP) y físicos (PINN) para su ejecución segura en sistemas embebidos de satélites (CPU de vuelo ARM/microcontroladores).

---

## 1. Métrica de Modelos Exportados

| Modelo | Formato | Tamaño en Disco | Latencia Promedio (CPU) | RAM Requerida | Estado de Inferencia vs PyTorch |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Surrogate MLP** | ONNX | 3.50 KB | 0.0154 ms | 12.0 KB | **VERIFICADO** (Max Diff: 0.00e+00) |
| **PINN Thermal** | ONNX | 51.61 KB | 0.0171 ms | 80.0 KB | **VERIFICADO** (Max Diff: 5.96e-07) |

---

## 2. Optimización y Cuantización ONNX Runtime
- **Graph Optimizations**: Se han aplicado fusiones de nodos redundantes (fusionando multiplicaciones y adiciones lineales en operaciones MAC) mediante la configuración interna de `onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL`.
- **Cuantización de Vuelo**: Para sistemas con restricciones extremas de almacenamiento, se incluye una exportación a código C puro que reduce la sobrecarga del runtime de ONNX a **cero bytes de dependencias**.

---

## 3. Demostración en Código C Puro para CPU Embebida (microTVM)
Hemos extraído los pesos y sesgos de la red neuronal `ThermalMLP` y generado la función forward completa en código **C99 puro**.

El archivo compilable e independiente de dependencias se almacena en:
- [surrogate_mlp_inference.c](file:///C:\Users\Alvaro\Desktop\ia-matematica-github\satellite\flight\surrogate_mlp_inference.c)

### Características del código C:
> [!TIP]
> - **Sin dependencias**: No requiere `libonnxruntime.so`, `libtorch.so` ni librerías externas de álgebra lineal. Solo la librería estándar `math.h`.
> - **Ideal para microcontroladores**: Consumo de memoria estática despreciable (< 5 KB de flash de solo lectura).
> - **Precisión nativa**: Utiliza coma flotante de precisión simple (`float`) nativo de la FPU de procesadores ARM Cortex-M4/M7 de grado espacial.

---

## 4. Archivos Generados en `/satellite/flight/`
1. `surrogate.onnx`: Modelo MLP subrogado en formato ONNX.
2. `pinn_thermal.onnx`: Red Neuronal PINN en formato ONNX.
3. `flight_benchmark.csv`: Resultados comparativos de rendimiento de hardware.
4. `surrogate_mlp_inference.c`: Código en C puro para integración directa en el software de vuelo (OBC).
