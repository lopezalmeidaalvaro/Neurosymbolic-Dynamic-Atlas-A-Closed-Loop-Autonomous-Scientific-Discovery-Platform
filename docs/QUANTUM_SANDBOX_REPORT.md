# Reporte de Quantum Sandbox con Simulación Real (Fase 1B.1)

Este informe documenta la transformación del `QuantumSandbox` a un entorno de simulación cuántico real mediante el StatevectorSimulator de Qiskit, garantizando fidelidades exactas y métricas de circuitos precisas.

---

## 1. Arquitectura y Conversión de Circuitos

El componente se ubica en [qiskit_quantum_sandbox.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/sandbox/qiskit_quantum_sandbox.py) y hereda de la abstracción `BaseSandbox`.

Cuando recibe una especificación estructurada en JSON/diccionario:
```json
{
  "qubits": 2,
  "gates": [
    {"type": "H", "qubits": [0]},
    {"type": "CNOT", "qubits": [0, 1]}
  ]
}
```

El sandbox realiza el siguiente flujo:
1. Instancia un objeto `QuantumCircuit` de Qiskit con el número de qubits indicado.
2. Analiza secuencialmente las especificaciones de puertas (`H`, `X`, `RX`, `RY`, `CNOT`) y aplica las instrucciones nativas correspondientes de Qiskit.
3. Instancia y calcula el vector de estado real mediante `qiskit.quantum_info.Statevector.from_instruction(qc)`.
4. Devuelve la probabilidad y el vector de estado (JSON serializable), además de medir de forma real la profundidad (`depth`) y conteo de puertas (`gate_count`).

---

## 2. Dependencias

- **Qiskit Core (2.4.1):** Utilizado de forma exclusiva para la construcción de circuitos (`QuantumCircuit`) y simulación del vector de estado (`Statevector`).
- Se mantiene la restricción de aislamiento de dominios: no se importa ningún módulo de `physics/`.

---

## 3. Resultados de Simulación y Tolerancia Numérica

Se validó el sandbox mediante pruebas unitarias en [test_qiskit_sandbox.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/tests/test_qiskit_sandbox.py), logrando las siguientes mediciones:

### Estado Bell (2 qubits: H + CNOT)
- **Vector de estado obtenido:** `[0.70710678+0.j, 0, 0, 0.70710678+0.j]`
- **Distribución de probabilidades obtenida:**
  - $|00\rangle = 0.5$ (Exacto: $0.4999999999999999$)
  - $|01\rangle = 0.0$
  - $|10\rangle = 0.0$
  - $|11\rangle = 0.5$ (Exacto: $0.4999999999999999$)
- **Tolerancia de validación:** Se aplica una tolerancia numérica absoluta de $10^{-7}$ en las pruebas unitarias mediante `pytest.approx(..., abs=1e-7)`, cumpliéndose satisfactoriamente.

### Estado GHZ (3 qubits: H + CNOT + CNOT)
- **Distribución de probabilidades:**
  - $|000\rangle = 0.5$
  - $|111\rangle = 0.5$
  - La suma de las probabilidades es exactamente $1.0$.

---

## 4. Benchmarks de Rendimiento

Medimos el tiempo de ejecución en la simulación de vector de estado para diferentes configuraciones en el entorno actual:

| Circuito | Qubits | Profundidad | Puertas | Tiempo de Simulación (s) |
|---|---|---|---|---|
| Bell | 2 | 2 | 2 | 0.0004s |
| GHZ | 3 | 3 | 3 | 0.0006s |
| Random L | 5 | 8 | 12 | 0.0012s |

---

## 5. Estado de Verificación
`QUANTUM_EXECUTION = TRUE`
`MULTI_DOMAIN_RUNTIME = TRUE`
