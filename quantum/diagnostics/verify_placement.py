import sys
import os
import math
from typing import Dict, Any, List, Tuple

from qiskit import QuantumCircuit

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from quantum.optimization.qubit_placement import QubitPlacement
from quantum.optimization.calibration_model import get_fake_backend
from quantum.integration.qiskit_adapter import qiskit_to_qade_json
from quantum.optimization.hardware_cost_model import (
    get_qubit_quality,
    get_gate_properties,
    estimate_swap_error,
    estimate_swap_duration,
)

def make_ghz(num_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits)
    qc.h(0)
    for i in range(num_qubits - 1):
        qc.cx(i, i+1)
    return qc

def find_shortest_path(adj: Dict[int, set], u: int, v: int) -> List[int]:
    if u == v:
        return [u]
    queue = [[u]]
    visited = {u}
    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node == v:
            return path
        for neighbor in adj[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return []

def get_avg_2q_error(backend: Any, adj: Dict[int, set], p: int) -> float:
    errors = []
    for neighbor in adj.get(p, ()):
        two_q_errors = []
        for gate_name in ("cx", "ecr", "cz"):
            try:
                err = get_gate_properties(backend, gate_name, (p, neighbor))["error"]
                two_q_errors.append(err)
            except Exception:
                pass
        if two_q_errors:
            errors.append(min(two_q_errors))
    return sum(errors) / len(errors) if errors else 0.01

def estimate_layout_fidelity(layout: Dict[int, int], qade_json: Dict[str, Any], backend: Any, placement: QubitPlacement) -> float:
    # Track end times for coherence decay
    qubit_end_times = {p: 0.0 for p in layout.values()}
    
    # 1. H gate on virtual 0 (mapped to layout[0])
    p0 = layout[0]
    h_error = get_gate_properties(backend, "x", (p0,))["error"]
    h_duration = get_gate_properties(backend, "x", (p0,))["duration"]
    
    log_gate_fidelity = math.log(max(1e-15, 1.0 - h_error))
    current_time = h_duration
    qubit_end_times[p0] = current_time
    
    # 2. CNOTs
    for i in range(4):
        u = layout[i]
        v = layout[i+1]
        
        path = find_shortest_path(placement.adj, u, v)
        if not path:
            # unconnected, apply penalty
            log_gate_fidelity += math.log(1e-15)
            current_time += 1e-6
            continue
            
        d = len(path) - 1
        if d == 1:
            err = get_gate_properties(backend, "cx", (u, v))["error"]
            dur = get_gate_properties(backend, "cx", (u, v))["duration"]
            log_gate_fidelity += math.log(max(1e-15, 1.0 - err))
            current_time += dur
        else:
            # d - 1 SWAPs + 1 CNOT
            total_err_log = 0.0
            cx_err = get_gate_properties(backend, "cx", (path[-2], path[-1]))["error"]
            total_err_log += math.log(max(1e-15, 1.0 - cx_err))
            dur = get_gate_properties(backend, "cx", (path[-2], path[-1]))["duration"]
            
            for j in range(d - 1):
                swap_err = estimate_swap_error(backend, (path[j], path[j+1]))
                total_err_log += math.log(max(1e-15, 1.0 - swap_err))
                dur += estimate_swap_duration(backend, (path[j], path[j+1]))
                
            log_gate_fidelity += total_err_log
            current_time += dur
            
        # Update end times for all physical qubits involved in this step's path
        for node in path:
            if node in qubit_end_times:
                qubit_end_times[node] = current_time
                
    # 3. Readout and Coherence errors
    log_readout_fidelity = 0.0
    log_coherence_fidelity = 0.0
    for q in layout.values():
        quality = get_qubit_quality(backend, q)
        readout_error = max(0.0, min(1.0, quality["readout_error"]))
        log_readout_fidelity += math.log(max(1e-15, 1.0 - readout_error))
        
        residence_time = qubit_end_times.get(q, 0.0)
        t1 = max(quality["t1"], 1e-15)
        t2 = max(quality["t2"], 1e-15)
        log_coherence_fidelity += -(residence_time / t1) - (residence_time / t2)
        
    F_gate = math.exp(log_gate_fidelity)
    F_readout = math.exp(log_readout_fidelity)
    F_coherence = math.exp(log_coherence_fidelity)
    F_total = F_gate * F_readout * F_coherence
    return F_total

def main():
    backend = get_fake_backend("FakeFez")
    
    qc = make_ghz(5)
    qade_json = qiskit_to_qade_json(qc)
    
    placement = QubitPlacement(5, None, backend=backend)
    
    layout_fa = placement.place(qade_json, method="fidelity_aware")
    layout_tr = {i: i for i in range(5)} # Trivial layout
    
    # Print layouts
    print("=== PLACEMENT INSPECTION REPORT ===")
    
    # 1. Trivial layout details
    print("\nLayout trivial [0,1,2,3,4]:")
    for i in range(5):
        p = layout_tr[i]
        q = get_qubit_quality(backend, p)
        avg_2q = get_avg_2q_error(backend, placement.adj, p)
        print(f"  Qubit {p}: T1={q['t1']*1e6:.1f}us, T2={q['t2']*1e6:.1f}us, readout={q['readout_error']*100:.3f}%, avg_2q_error={avg_2q*100:.3f}%")
    
    fid_tr = estimate_layout_fidelity(layout_tr, qade_json, backend, placement)
    print(f"  Fidelidad teórica estimada: {fid_tr:.6f}")
    
    # 2. Fidelity-aware layout details
    # The layout dictionary layout_fa can map virtual qubits 0..4 in different orders, let's print them ordered by logical qubit 0..4
    fa_phys_list = [layout_fa[i] for i in range(5)]
    print(f"\nLayout fidelity_aware {fa_phys_list}:")
    for i in range(5):
        p = layout_fa[i]
        q = get_qubit_quality(backend, p)
        avg_2q = get_avg_2q_error(backend, placement.adj, p)
        print(f"  Qubit {p}: T1={q['t1']*1e6:.1f}us, T2={q['t2']*1e6:.1f}us, readout={q['readout_error']*100:.3f}%, avg_2q_error={avg_2q*100:.3f}%")
        
    fid_fa = estimate_layout_fidelity(layout_fa, qade_json, backend, placement)
    print(f"  Fidelidad teórica estimada: {fid_fa:.6f}")
    
    # 3. Comparison
    are_different = "YES" if fa_phys_list != [0,1,2,3,4] else "NO"
    is_better = "YES" if fid_fa > fid_tr else "NO"
    delta = fid_fa - fid_tr
    
    print("\n=== SUMMARY ===")
    print(f"¿Son distintos? {are_different}")
    print(f"¿Fidelity_aware es mejor? {is_better} (delta: {delta:.6f})")

    # QubitPlacement.place() Tarea 2 answers printout
    print("\n=== ANSWERS TO TAREA 2 QUESTIONS ===")
    print("1. ¿Qué métrica usa 'fidelity_aware' para puntuar qubits?")
    print("   Usa una combinación lineal ponderada de: T1 normalizado (35%), T2 normalizado (35%), readout_error (15% negativo), avg_gate_error (15% negativo) y degree (1% positivo).")
    print("2. ¿Consulta el backend en tiempo real o usa valores hardcoded?")
    print("   Si backend está disponible, consulta en tiempo real mediante get_qubit_quality() y get_gate_properties() del hardware_cost_model. Si no, usa valores fallback predefinidos.")
    print("3. ¿Hay algún caso donde retorna [0,1,...,N] por defecto?")
    print("   Sí: si la coupling map está vacía, si hay 1 o menos qubits físicos, si el método de placement no es soportado, o si algunos qubits virtuales no pueden ser enrutados y se asignan a sí mismos.")

if __name__ == "__main__":
    main()
