import os
import sys
from pathlib import Path
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT

# Set up paths
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.optimization.calibration_model import get_fake_backend
from quantum.integration.qiskit_adapter import qiskit_to_qade_json
from quantum.optimization.qubit_placement import QubitPlacement
from quantum.optimization.routing_engine import AdvancedRouter

def run_diagnosis():
    backend = get_fake_backend("FakeFez")
    
    # 5-qubit QFT circuit
    qc = QuantumCircuit(5)
    qc.compose(QFT(5), inplace=True)
    
    print("=" * 80)
    print("QFT ROUTING DIAGNOSIS - TARGET BACKEND: fake_fez")
    print("=" * 80)
    
    # ---------------------------------------------------------
    # 1. Qiskit L3 Routing Trace
    # ---------------------------------------------------------
    qc_qiskit = qc.copy()
    qc_qiskit.measure_all()
    # Transpile with swap in basis_gates to prevent unrolling
    qiskit_compiled = transpile(
        qc_qiskit,
        backend=backend,
        optimization_level=3,
        basis_gates=['id', 'rz', 'sx', 'x', 'cx', 'cz', 'swap']
    )
    
    # Extract initial layout from Qiskit
    layout = qiskit_compiled.layout.initial_layout
    v_to_p_qis = {}
    p_to_v_qis = {}
    for virt, phys in layout.get_virtual_bits().items():
        if virt in qc_qiskit.qubits:
            virt_idx = qc_qiskit.find_bit(virt).index
        else:
            virt_idx = -100 - phys  # Mark ancilla
        v_to_p_qis[virt_idx] = phys
        p_to_v_qis[phys] = virt_idx
        
    print(f"\nQiskit L3 Initial Layout (Virtual -> Physical) for mapped qubits:")
    mapped_qis_layout = {k: v for k, v in v_to_p_qis.items() if k >= 0}
    print(sorted(mapped_qis_layout.items()))
    
    current_v_to_p = v_to_p_qis.copy()
    current_p_to_v = p_to_v_qis.copy()
    
    qiskit_swaps = []
    swap_idx = 0
    for instr in qiskit_compiled.data:
        op_name = instr.operation.name
        phys_qubits = [qiskit_compiled.find_bit(q).index for q in instr.qubits]
        if op_name == "swap":
            u, v = phys_qubits[0], phys_qubits[1]
            v_u = current_p_to_v.get(u, u)
            v_v = current_p_to_v.get(v, v)
            
            # Format logical qubits representation
            lbl_u = f"q{v_u}" if v_u >= 0 else f"ancilla_{-(v_u + 100)}"
            lbl_v = f"q{v_v}" if v_v >= 0 else f"ancilla_{-(v_v + 100)}"
            
            qiskit_swaps.append({
                "swap_index": swap_idx,
                "logical_qubits_involved": f"({lbl_u}, {lbl_v})",
                "physical_qubits_before": f"({u}, {v})",
                "physical_qubits_after": f"({v}, {u})",
                "inserted_by": "Qiskit L3"
            })
            swap_idx += 1
            # Update layout
            current_v_to_p[v_u] = v
            current_v_to_p[v_v] = u
            current_p_to_v[u] = v_v
            current_p_to_v[v] = v_u
            
    # ---------------------------------------------------------
    # 2. QADE Routing Trace
    # ---------------------------------------------------------
    qc_unrolled = transpile(qc, basis_gates=['h', 'rx', 'ry', 'rz', 'cx', 'cz', 'cp'])
    qade_json = qiskit_to_qade_json(qc_unrolled)
    placer = QubitPlacement(5, list(backend.coupling_map), backend=backend)
    initial_layout_qade = placer.place(qade_json, method="fidelity_aware")
    
    print(f"QADE Initial Layout (Virtual -> Physical): {sorted(initial_layout_qade.items())}")
    
    router = AdvancedRouter(list(backend.coupling_map), backend=backend)
    routed_json, final_layout = router.route(
        qade_json,
        method="coherence_aware_sabre",
        initial_layout=initial_layout_qade
    )
    
    current_v_to_p_qade = initial_layout_qade.copy()
    current_p_to_v_qade = {p: v for v, p in initial_layout_qade.items()}
    
    qade_swaps = []
    swap_idx = 0
    for gate in routed_json.get("gates", []):
        g_type = gate.get("type", "").upper()
        qubits = gate.get("qubits", [])
        if g_type == "SWAP":
            u, v = qubits[0], qubits[1]
            v_u = current_p_to_v_qade.get(u, u)
            v_v = current_p_to_v_qade.get(v, v)
            
            lbl_u = f"q{v_u}" if isinstance(v_u, int) and v_u < 100 else f"phys_{v_u}"
            lbl_v = f"q{v_v}" if isinstance(v_v, int) and v_v < 100 else f"phys_{v_v}"
            
            qade_swaps.append({
                "swap_index": swap_idx,
                "logical_qubits_involved": f"({lbl_u}, {lbl_v})",
                "physical_qubits_before": f"({u}, {v})",
                "physical_qubits_after": f"({v}, {u})",
                "inserted_by": "QADE"
            })
            swap_idx += 1
            # Update layout
            current_v_to_p_qade[v_u] = v
            current_v_to_p_qade[v_v] = u
            current_p_to_v_qade[u] = v_v
            current_p_to_v_qade[v] = v_u

    # ---------------------------------------------------------
    # 3. Print Results Table
    # ---------------------------------------------------------
    print("\n" + "=" * 100)
    print("ROUTING COMPARISON TABLE:")
    print("=" * 100)
    print(f"{'swap_index':<12} | {'logical_qubits_involved':<24} | {'physical_qubits_before':<24} | {'physical_qubits_after':<24} | {'inserted_by':<15}")
    print("-" * 100)
    
    # Print Qiskit swaps first
    for s in qiskit_swaps:
        print(f"{s['swap_index']:<12} | {s['logical_qubits_involved']:<24} | {s['physical_qubits_before']:<24} | {s['physical_qubits_after']:<24} | {s['inserted_by']:<15}")
        
    print("-" * 100)
    # Print QADE swaps
    for s in qade_swaps:
        print(f"{s['swap_index']:<12} | {s['logical_qubits_involved']:<24} | {s['physical_qubits_before']:<24} | {s['physical_qubits_after']:<24} | {s['inserted_by']:<15}")
    print("=" * 100)
    
    print(f"\nTotal SWAPs Qiskit L3: {len(qiskit_swaps)}")
    print(f"Total SWAPs QADE:      {len(qade_swaps)}")

if __name__ == "__main__":
    run_diagnosis()
