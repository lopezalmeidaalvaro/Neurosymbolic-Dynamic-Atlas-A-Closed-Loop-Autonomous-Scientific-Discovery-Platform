import copy
from typing import Dict, Any, List

Gate = Dict[str, Any]
Circuit = Dict[str, Any]

class QuantumCircuitCanonicalizer:
    """
    Canonicalizador de circuitos cuánticos utilizando simplificaciones algebraicas locales.
    Reduce secuencias de compuertas a su forma mínima sin sintetizar matrices de transferencia.
    """

    @staticmethod
    def canonicalize(circuit: Circuit) -> Circuit:
        """
        Reduce el circuito cuántico dado mediante simplificaciones locales y eliminación de redundancias.
        """
        if not circuit or "gates" not in circuit:
            return circuit
        
        gates = circuit.get("gates", [])
        qubits = circuit.get("qubits", 0)
        
        simplified_gates: List[Gate] = []
        
        for gate in gates:
            g_type = gate.get("type")
            g_qubits = gate.get("qubits", [])
            
            # Omitir compuertas sin tipo o qubits
            if not g_type or not g_qubits:
                continue
                
            # Simplificación de ángulos para RX y RY: omitir si theta mod 2*pi es aproximadamente 0
            if g_type in ("RX", "RY"):
                theta = float(gate.get("theta", 0.0))
                # Normalizar a [-pi, pi]
                theta = (theta + 3.141592653589793) % (2 * 3.141592653589793) - 3.141592653589793
                if abs(theta) < 1e-9:
                    continue
            
            # Buscar hacia atrás para simplificar si es conmutativo
            cancelled_or_merged = False
            for i in range(len(simplified_gates) - 1, -1, -1):
                prev_gate = simplified_gates[i]
                prev_type = prev_gate.get("type")
                prev_qubits = prev_gate.get("qubits", [])
                
                # Comprobar traslape de qubits
                overlap = set(g_qubits).intersection(set(prev_qubits))
                if not overlap:
                    # Qubits completamente disjuntos: las compuertas conmutan. Continuar buscando hacia atrás.
                    continue
                
                # Los qubits se traslapan. Sólo podemos simplificar si son exactamente los mismos qubits
                if set(g_qubits) == set(prev_qubits) and g_type == prev_type:
                    if g_type in ("H", "X", "CNOT", "CX"):
                        # Par autoinverso (H H -> I, X X -> I, CNOT CNOT -> I)
                        simplified_gates.pop(i)
                        cancelled_or_merged = True
                        break
                    elif g_type in ("RX", "RY"):
                        # Combinar rotaciones: RX(theta1) RX(theta2) -> RX(theta1 + theta2)
                        theta1 = float(prev_gate.get("theta", 0.0))
                        theta2 = float(gate.get("theta", 0.0))
                        new_theta = theta1 + theta2
                        # Normalizar a [-pi, pi]
                        new_theta = (new_theta + 3.141592653589793) % (2 * 3.141592653589793) - 3.141592653589793
                        
                        if abs(new_theta) < 1e-9:
                            simplified_gates.pop(i)
                        else:
                            simplified_gates[i] = {
                                "type": g_type,
                                "qubits": g_qubits,
                                "theta": new_theta
                            }
                        cancelled_or_merged = True
                        break
                
                # Si hay traslape de qubits pero no podemos cancelar/fusionar,
                # las compuertas no conmutan. Detener la búsqueda hacia atrás.
                break
                
            if not cancelled_or_merged:
                simplified_gates.append(copy.deepcopy(gate))
                
        canonical_circuit = copy.deepcopy(circuit)
        canonical_circuit["gates"] = simplified_gates
        return canonical_circuit
