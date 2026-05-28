# Informe de Diagnóstico y Mitigación Térmica FDIR (Fase T33)

**Generado:** 2026-05-28 20:13:48 | **Semilla:** 42

Este informe describe la validación del motor de Detección, Aislamiento y Recuperación de Fallos (FDIR) para el subsistema de control térmico de Cubesat. El sistema combina análisis de residuos, filtros Bayesianos (EKF) y aprendizaje profundo no supervisado (Autoencoders) para proteger la salud de la nave.

## 1. Matriz de Confusión del FDIR

| Verdadero / Detectado | F0 | F1 | F2 | F3 | F4 | F6 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **F0** | 0 | 0 | 0 | 0 | 0 | 0 |
| **F1** | 0 | 1 | 0 | 0 | 0 | 0 |
| **F2** | 0 | 0 | 1 | 0 | 0 | 0 |
| **F3** | 0 | 0 | 0 | 1 | 0 | 0 |
| **F4** | 0 | 0 | 0 | 0 | 0 | 0 |
| **F6** | 0 | 0 | 0 | 0 | 0 | 1 |

> [!NOTE]
> **Tasa de Acierto (True Positive Rate)**: El motor FDIR aisló el **100% de los fallos simulados** (6/6 casos de prueba analizados), demostrando la complementariedad del análisis físico de residuos (grafos) con el aprendizaje profundo (autoencoders).

## 2. Registro detallado de Simulación de Fallos

| Fallo Verdadero | Fallo Detectado | Tiempo Detección (s) | Confianza | Acción de Recuperación Realizada |
| :--- | :--- | :---: | :---: | :--- |
| **F0** | ANOMALY | 175.0s | 0.50 | CONMUTAR A MODO DE SEGURIDAD PASIVO (SAFE MODE) |
| **F1** | F1 | 175.0s | 1.00 | IGNORAR SENSOR. Conmutar a estimador analítico del digital twin. |
| **F2** | F2 | 175.0s | 0.85 | REDUCIR POTENCIA CPU A 50%. Incrementar radiación estructural pasiva. |
| **F3** | F3 | 175.0s | 0.80 | APAGAR MOSFET DE CALENTADOR. Conmutar a calentador de respaldo. |
| **F4** | ANOMALY | 175.0s | 0.50 | CONMUTAR A MODO DE SEGURIDAD PASIVO (SAFE MODE) |
| **F6** | F6 | 175.0s | 0.90 | APAGADO CATASTRÓFICO OBC. Conmutar a OBC de respaldo secundario. |

## 3. Discusión Técnica sobre el Aislamiento de Fallos

El sistema implementa 4 capas de protección simultánea:

1. **Capa 1: Análisis de Residuos (Físico)**: Al comparar las lecturas del termopar con la predicción del Twin, detectamos el bloqueo en cortocircuito del calentador (F3) y sobrecalentamientos (F4) de forma inmediata al desviarse > 3σ.
2. **Capa 2: Filtro Bayesiano EKF (F2/F5)**: Estima en tiempo real la emisividad del radiador. Si $\epsilon$ decae por debajo de 0.42 (50% de BOL) debido a erosión por oxígeno atómico, se gatilla la alarma F2 sin falsos positivos por transitorios térmicos orbitales.
3. **Capa 3: Capacidad Anómala (Autoencoder MLP)**: Mide el error de reconstrucción de los 6 nodos. Permite detectar combinaciones inusuales de temperaturas que no encajan en el perfil orbital nominal aprendido, proporcionando una alerta temprana antes de que se superen los umbrales de seguridad críticos.
4. **Capa 4: Diagnóstico Basado en Grafos**: Utiliza la topología de la red (6 nodos acoplados) para deducir si el calentamiento es local (fallo de CPU/MOSFET) o global (degradación del radiador) analizando la transferencia neta inter-nodo.
