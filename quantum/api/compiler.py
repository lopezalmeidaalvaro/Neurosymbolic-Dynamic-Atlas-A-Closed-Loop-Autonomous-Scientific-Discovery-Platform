import time
import logging
from typing import Dict, Any, List, Tuple, Optional
import qiskit
from qiskit import transpile
from qiskit.transpiler import PassManager
from quantum.optimization.qiskit_plugin import QADEOptimizerPass

logger = logging.getLogger(__name__)

def get_gate_counts(qc) -> Dict[str, int]:
    """
    Counts total, 1-qubit, and 2-qubit gates excluding barriers and measurements.
    """
    total = 0
    one_qubit = 0
    two_qubit = 0
    for inst in qc.data:
        name = inst.operation.name
        if name in ("barrier", "measure"):
            continue
        total += 1
        n_q = len(inst.qubits)
        if n_q == 1:
            one_qubit += 1
        elif n_q == 2:
            two_qubit += 1
    return {
        "total": total,
        "one_qubit": one_qubit,
        "two_qubit": two_qubit
    }

def compile_circuit_with_qade(
    circuit_qasm: str,
    backend,
    optimization_level: int = 1,
    hardware_aware: bool = True
) -> Tuple[str, Dict[str, int], int, List[int], float, Optional[str]]:
    """
    Compiles an OpenQASM 2.0 circuit using the QADE Evolutionary Search
    and PyZX simplification passes.
    Returns: (compiled_qasm, gate_count, depth, qubits_selected, compile_time_ms, note)
    """
    # 1. Parse OpenQASM 2.0
    import qiskit.qasm2
    qc = qiskit.qasm2.loads(circuit_qasm)
    
    # Start timing compile logic
    start_time = time.perf_counter()
    
    # 2. Pre-transpile to target backend
    transpiled = transpile(qc, backend=backend, optimization_level=optimization_level)
    
    # Check active virtual qubits
    active_v_qs = set()
    for inst in transpiled.data:
        if inst.operation.name not in ("measure", "barrier"):
            for q in inst.qubits:
                active_v_qs.add(transpiled.find_bit(q).index)
    num_active = len(active_v_qs)
    
    note = None
    if num_active > 20:
        note = f"Routed circuit has {num_active} active qubits (> 20). Bypassing evolutionary search, applying algebraic simplification only."
        
    if hardware_aware:
        # Run QADE pass
        qade_pass = QADEOptimizerPass(backend=backend, hardware_aware=True)
        pm = PassManager(qade_pass)
        optimized = pm.run(transpiled)
        
        # Get selected physical qubits
        layout = qade_pass._optimal_layout
        if layout:
            qubits_selected = [layout.get(v) for v in sorted(list(active_v_qs)) if v in layout]
        else:
            qubits_selected = sorted(list(active_v_qs))
    else:
        # Standard transpiler only
        optimized = transpiled
        qubits_selected = sorted(list(active_v_qs))
        
    compile_time_ms = (time.perf_counter() - start_time) * 1000.0
    
    # 3. Dump compiled circuit to OpenQASM 2.0
    compiled_qasm = qiskit.qasm2.dumps(optimized)
    
    # Get metrics
    gate_count = get_gate_counts(optimized)
    depth = optimized.depth()
    
    return compiled_qasm, gate_count, depth, qubits_selected, compile_time_ms, note
