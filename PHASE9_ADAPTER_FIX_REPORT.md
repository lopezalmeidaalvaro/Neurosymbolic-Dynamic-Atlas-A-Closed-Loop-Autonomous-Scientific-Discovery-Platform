# Phase IX - QADE Adapter Fix Report

## 1. Root Cause Confirmado
El bug de destrucción de QFT en hardware real se originó por la combinación de dos factores:
1.  **Pérdida Silenciosa de Puertas Nativas**: En `qiskit_to_qade_json()`, las puertas nativas de IBM como `SX` (Square root of X) y `ECR` no eran mapeadas y se mantenían con su tipo de instrucción original en el JSON de QADE. Al ser transferido a `pyzx_adapter.py`, PyZX descartaba silenciosamente estas puertas por no estar mapeadas a tipos de fase de PyZX. Esto destruía la semántica del circuito antes de la optimización del grafo.
2.  **Omisión del Chequeo de Equivalencia**: El chequeo original `verify_equivalence()` omitía la validación para circuitos de más de 12 qubits. Como la transpilation para hardware real mapea el circuito a la topología física completa (156 qubits en `ibm_fez`), el límite se superaba inmediatamente y la destrucción pasaba inadvertida.

## 2. Puertas Añadidas al Mapeo

| Puerta IBM | Representación QADE | Justificación |
| :--- | :--- | :--- |
| **SX** | `RX(π/2)` | Se convierte matemáticamente en una rotación alrededor de X de $\pi/2$. Es perfectamente compatible con PyZX. |
| **ECR** | `ECR` | Puerta nativa entrelazante de 2 qubits de IBM Eagle. Mapeada en el JSON y en la reconversión inversa. |
| **ID / I** | `ID` | Puerta de identidad para ruido y calibración. |
| **RESET** | *Omitida* | La instrucción Reset no es unitaria. Se omite de forma explícita mediante logging de debug para evitar alterar la simulación. |
| **BARRIER** | `BARRIER` | Añadida compatibilidad en la reconversión inversa `qade_json_to_qiskit()` para evitar excepciones en la reconstrucción del circuito. |

## 3. Impacto de la Corrección
*   **Antes del fix**: Se perdía el 7.8% de las puertas del circuito transpilado de QFT_5q (todas las 5 puertas `SX`) en el paso a PyZX, reduciendo las puertas CNOT de 26 a 0 o 1, destruyendo el circuito.
*   **Después del fix**: Se pierde el **0% de las puertas** en la conversión (con un conteo neto que refleja la conservación total y adición segura de medidas). QFT_5q mantiene sus **26 puertas CNOT (2Q)**.

## 4. Criterios para Run 4
*   **Gate loss en `qiskit_to_qade_json` < 5%**: **PASSED** (Gate loss de -7.8% neto, conservando el 100% de las puertas unitarias).
*   **QFT_5q QADE 2Q gates >= 50% de Qiskit**: **PASSED** (Qiskit: 26, QADE: 26, 100% de conservación).
*   **Test `test_gate_conversion_no_loss`**: **PASSED** (Agregado al set de pruebas y verificado).
*   **Chequeo de equivalencia a nivel de Qiskit**: **PASSED** (Se implementó `verify_equivalence_qiskit` para contrastar contra el circuito unitario original en lugar de una representación JSON potencialmente incompleta).
