# Phase IX - QADE Adapter Gate Loss Bug Report

## 1. Puertas en el circuito transpilado
En un backend simulado de 127 qubits (`GenericBackendV2`), el circuito QFT de 5 qubits transpilado contiene las siguientes puertas:
*   **Puertas únicas**: `rz`, `cx`, `barrier`, `sx`, `measure`
*   **Conteo de puertas sin medidas (no measure)**:
    *   `RZ`: 32
    *   `CX` (CNOT): 26
    *   `SX` (Square root of X): 5
    *   `BARRIER`: 1
    *   **Total**: 64 puertas

## 2. Puertas en el QADE JSON resultante
Después de pasar por `qiskit_to_qade_json()`:
*   **Puertas únicas**: `SX`, `MEASURE`, `RZ`, `BARRIER`, `CNOT`
*   **Conteo de puertas en QADE JSON**:
    *   `RZ`: 32
    *   `CNOT`: 26
    *   `SX`: 5
    *   `BARRIER`: 1
    *   `MEASURE`: 5
    *   **Total**: 69 puertas

## 3. Puertas perdidas en la conversión
*   **Puertas perdidas en qiskit_to_qade_json()**: **0 puertas** (el ratio de supervivencia es del 101.5% ya que se conservan los tipos y se añaden las medidas).
*   **Puertas perdidas en pyzx_adapter.py**: **5 puertas** (las 5 puertas `SX` se descartan silenciosamente al convertir de QADE JSON a PyZX, ya que `pyzx_adapter.py` no tiene ningún caso `elif g_type == "SX"` en `qade_json_to_pyzx()`).

## 4. Puertas no mapeadas específicamente
Las puertas nativas de IBM que no están formalmente mapeadas en `qiskit_to_qade_json()` son:
1.  `SX` (Square root of X): Se mantiene como `"SX"` en el JSON, lo cual no es procesable por PyZX, causando que sea descartada silenciosamente.
2.  `ECR` (Echoed Cross-Resonance): Puerta nativa entrelazante de IBM Eagle que se mantiene como `"ECR"` pero se descarta silenciosamente en PyZX.
3.  `ID`/`I` (Identity): Se mantiene como `"ID"` pero no se mapea en todos los flujos.
4.  `RESET`: Se pasa como `"RESET"` pero no es unitaria y debería ser omitida.
5.  `BARRIER`: Se conserva como `"BARRIER"`, pero `qade_json_to_qiskit()` carece de soporte para ella, lo que provoca un fallo de ejecución en la reconversión.
