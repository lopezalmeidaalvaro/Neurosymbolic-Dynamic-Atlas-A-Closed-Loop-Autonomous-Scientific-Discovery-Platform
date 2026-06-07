import json
import time
from typing import Dict, Any, List
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from quantum.interfaces import BaseSandbox

class QiskitQuantumSandbox(BaseSandbox):
    """
    Ejecutor de circuitos cuánticos reales utilizando el simulador de estados de Qiskit (Statevector).
    """

    def execute(self, circuit_spec: Any, input_data: Any = None) -> Dict[str, Any]:
        """
        Convierte una especificación de circuito en JSON/dict a un QuantumCircuit real de Qiskit,
        ejecuta la simulación de vector de estado y devuelve las probabilidades y la profundidad del circuito.
        """
        start_time = time.time()
        
        try:
            # Intentar parsear el código si viene como cadena JSON
            if isinstance(circuit_spec, str):
                trimmed = circuit_spec.strip()
                # Limpiar markdown backticks si los hay
                if trimmed.startswith("```"):
                    lines = trimmed.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].startswith("```"):
                        lines = lines[:-1]
                    trimmed = "\n".join(lines).strip()

                if trimmed.startswith("{") and trimmed.endswith("}"):
                    data = json.loads(trimmed)
                else:
                    return {
                        "success": False, 
                        "error": "La cadena provista no es un objeto JSON de circuito válido."
                    }
            else:
                data = circuit_spec

            if not isinstance(data, dict):
                return {
                    "success": False, 
                    "error": "Especificación de circuito inválida: debe ser un objeto JSON o diccionario."
                }

            qubits = data.get("qubits", 0)
            gates = data.get("gates", [])

            if qubits <= 0:
                return {
                    "success": False, 
                    "error": "El número de qubits debe ser mayor que 0."
                }

            # 1. Crear el QuantumCircuit
            qc = QuantumCircuit(qubits)

            # 2. Aplicar las puertas
            for idx, gate in enumerate(gates):
                g_type = gate.get("type")
                g_qubits = gate.get("qubits", [])
                
                # Validar índices de qubits
                for q in g_qubits:
                    if q < 0 or q >= qubits:
                        return {
                            "success": False, 
                            "error": f"Índice de qubit {q} fuera de rango [0, {qubits - 1}] en la puerta {idx}."
                        }

                if g_type == "H":
                    if len(g_qubits) != 1:
                        return {"success": False, "error": f"Puerta H requiere exactamente 1 qubit en la puerta {idx}."}
                    qc.h(g_qubits[0])
                elif g_type == "X":
                    if len(g_qubits) != 1:
                        return {"success": False, "error": f"Puerta X requiere exactamente 1 qubit en la puerta {idx}."}
                    qc.x(g_qubits[0])
                elif g_type == "Y":
                    if len(g_qubits) != 1:
                        return {"success": False, "error": f"Puerta Y requiere exactamente 1 qubit en la puerta {idx}."}
                    qc.y(g_qubits[0])
                elif g_type == "Z":
                    if len(g_qubits) != 1:
                        return {"success": False, "error": f"Puerta Z requiere exactamente 1 qubit en la puerta {idx}."}
                    qc.z(g_qubits[0])
                elif g_type == "RX":
                    if len(g_qubits) != 1:
                        return {"success": False, "error": f"Puerta RX requiere exactamente 1 qubit en la puerta {idx}."}
                    theta = gate.get("theta", 0.0)
                    qc.rx(theta, g_qubits[0])
                elif g_type == "RY":
                    if len(g_qubits) != 1:
                        return {"success": False, "error": f"Puerta RY requiere exactamente 1 qubit en la puerta {idx}."}
                    theta = gate.get("theta", 0.0)
                    qc.ry(theta, g_qubits[0])
                elif g_type == "RZ":
                    if len(g_qubits) != 1:
                        return {"success": False, "error": f"Puerta RZ requiere exactamente 1 qubit en la puerta {idx}."}
                    theta = gate.get("theta", 0.0)
                    qc.rz(theta, g_qubits[0])
                elif g_type in ("CNOT", "CX"):
                    if len(g_qubits) != 2:
                        return {"success": False, "error": f"Puerta CNOT/CX requiere exactamente 2 qubits (control, target) en la puerta {idx}."}
                    qc.cx(g_qubits[0], g_qubits[1])
                elif g_type == "CZ":
                    if len(g_qubits) != 2:
                        return {"success": False, "error": f"Puerta CZ requiere exactamente 2 qubits en la puerta {idx}."}
                    qc.cz(g_qubits[0], g_qubits[1])
                elif g_type == "SWAP":
                    if len(g_qubits) != 2:
                        return {"success": False, "error": f"Puerta SWAP requiere exactamente 2 qubits en la puerta {idx}."}
                    qc.swap(g_qubits[0], g_qubits[1])
                else:
                    return {
                        "success": False, 
                        "error": f"Puerta cuántica no soportada '{g_type}' en la puerta {idx}."
                    }

            # 3. Simular usando Statevector de Qiskit
            sv = Statevector.from_instruction(qc)

            # 4. Formatear el vector de estado (JSON serializable)
            statevector_str = [str(z) for z in sv.data]
            statevector_complex = [[float(z.real), float(z.imag)] for z in sv.data]
            probabilities = [float(p) for p in sv.probabilities()]

            execution_time = time.time() - start_time

            return {
                "success": True,
                "result": {
                    "statevector": statevector_str,
                    "statevector_complex": statevector_complex,
                    "probabilities": probabilities,
                    "depth": qc.depth(),
                    "gate_count": len(gates),
                    "qubits": qubits,
                    "status": "compiled_successfully"
                },
                "execution_time": round(execution_time, 4)
            }

        except Exception as e:
            return {
                "success": False, 
                "error": f"Fallo al ejecutar la simulación del circuito cuántico: {str(e)}"
            }
