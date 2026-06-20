import argparse
import sys
import os

def compile_command(args):
    """
    Executes the compilation of a QASM circuit using QADE.
    """
    import qiskit.qasm2
    from qiskit import transpile
    from qiskit.transpiler import PassManager
    from quantum.optimization.qiskit_plugin import QADEOptimizerPass
    from quantum.optimization.calibration_model import get_fake_backend
    
    backend_name = args.backend
    if "fake" in backend_name.lower():
        backend = get_fake_backend(backend_name)
    else:
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService
            token = os.environ.get("IBMQ_API_KEY") or os.environ.get("IBM_QUANTUM_TOKEN")
            service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
            backend = service.backend(backend_name)
        except Exception as e:
            print(f"Warning: Could not connect to real IBM backend '{backend_name}' ({e}). Falling back to fake_fez.")
            backend = get_fake_backend("FakeFez")
            
    try:
        qc = qiskit.qasm2.load(args.circuit_qasm)
    except Exception as e:
        print(f"Error: Invalid OpenQASM 2.0 file: {e}")
        sys.exit(1)
        
    print(f"Loaded circuit '{args.circuit_qasm}' with {qc.num_qubits} qubits.")
    
    # Core compilation
    transpiled = transpile(qc, backend=backend, optimization_level=1)
    
    active_v_qs = set()
    for inst in transpiled.data:
        if inst.operation.name not in ("measure", "barrier"):
            for q in inst.qubits:
                active_v_qs.add(transpiled.find_bit(q).index)
                
    if args.hardware_aware:
        qade_pass = QADEOptimizerPass(backend=backend, hardware_aware=True)
        pm = PassManager(qade_pass)
        optimized = pm.run(transpiled)
        layout = qade_pass._optimal_layout
        if layout:
            selected_qubits = [layout.get(v) for v in sorted(list(active_v_qs)) if v in layout]
        else:
            selected_qubits = sorted(list(active_v_qs))
    else:
        optimized = transpiled
        selected_qubits = sorted(list(active_v_qs))
        
    # Count gates
    total = 0
    one_q = 0
    two_q = 0
    for inst in optimized.data:
        if inst.operation.name in ("barrier", "measure"):
            continue
        total += 1
        if len(inst.qubits) == 1:
            one_q += 1
        elif len(inst.qubits) == 2:
            two_q += 1
            
    print("\nCompilation Results:")
    print(f"  Total Gates: {total} (1Q: {one_q}, 2Q: {two_q})")
    print(f"  Depth: {optimized.depth()}")
    print(f"  Selected Qubits: {selected_qubits}")
    
    if args.output:
        qiskit.qasm2.dump(optimized, args.output)
        print(f"  Saved compiled QASM to: {args.output}")

def validate_command(args):
    """
    Validates QASM file syntax and prints structure info.
    """
    import qiskit.qasm2
    try:
        qc = qiskit.qasm2.load(args.circuit_qasm)
        print("QASM syntax is valid.")
        print(f"Logical qubits: {qc.num_qubits}")
        print(f"Total instructions: {len(qc.data)}")
    except Exception as e:
        print(f"Syntax validation failed: {e}")
        sys.exit(1)

def benchmark_command(args):
    """
    Compares standard Qiskit L3 against QADE.
    """
    import qiskit.qasm2
    from qiskit import QuantumCircuit, transpile
    from qiskit.transpiler import PassManager
    from qiskit.circuit.library import QFT
    from quantum.optimization.qiskit_plugin import QADEOptimizerPass
    from quantum.optimization.calibration_model import get_fake_backend
    
    print(f"Running benchmarks against backend: {args.backend}...")
    backend = get_fake_backend(args.backend)
    
    circs_to_run = args.circuits.split(",")
    circuits = {}
    
    if "ghz" in circs_to_run:
        ghz = QuantumCircuit(5)
        ghz.h(0)
        for i in range(4):
            ghz.cx(i, i+1)
        circuits["GHZ_5q"] = ghz
        
    if "qft" in circs_to_run:
        qft = QuantumCircuit(5)
        qft.compose(QFT(5), inplace=True)
        circuits["QFT_5q"] = qft
        
    if "kernel" in circs_to_run:
        qk = QuantumCircuit(5)
        for i in range(5):
            qk.h(i)
            qk.rz(0.5, i)
        for i in range(4):
            qk.cx(i, i+1)
            qk.rz(0.3, i+1)
        for i in range(5):
            qk.h(i)
            qk.rz(0.5, i)
        for i in range(4):
            qk.cx(i, i+1)
        circuits["Quantum_Kernel_5q"] = qk
        
    if "vqe" in circs_to_run:
        vqe = QuantumCircuit(5)
        for i in range(5):
            vqe.ry(0.3 * i, i)
        for i in range(4):
            vqe.cx(i, i+1)
        for i in range(5):
            vqe.ry(0.2 * i, i)
        circuits["VQE_5q"] = vqe
        
    print("\n" + "=" * 80)
    print(f"| {'Circuit':<20} | {'Qiskit L3 Gates (2Q)':<22} | {'QADE Gates (2Q)':<18} | {'Reduction':<10} |")
    print("-" * 80)
    
    for name, qc in circuits.items():
        # Standard Qiskit L3
        qiskit_c = transpile(qc, backend=backend, optimization_level=3)
        qiskit_2q = sum(1 for inst in qiskit_c.data if len(inst.qubits) == 2)
        qiskit_gates = len([inst for inst in qiskit_c.data if inst.operation.name not in ("barrier", "measure")])
        
        # QADE compiler
        transpiled = transpile(qc, backend=backend, optimization_level=1)
        qade_pass = QADEOptimizerPass(backend=backend, hardware_aware=True)
        pm = PassManager(qade_pass)
        qade_c = pm.run(transpiled)
        qade_2q = sum(1 for inst in qade_c.data if len(inst.qubits) == 2)
        qade_gates = len([inst for inst in qade_c.data if inst.operation.name not in ("barrier", "measure")])
        
        reduction = (qiskit_2q - qade_2q) / qiskit_2q if qiskit_2q > 0 else 0.0
        reduction_str = f"{reduction:+.1%}" if qiskit_2q > 0 else "0.0%"
        
        print(f"| {name:<20} | {qiskit_gates:<22} ({qiskit_2q}) | {qade_gates:<18} ({qade_2q}) | {reduction_str:<10} |")
        
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="QADE Command Line Interface")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")
    
    compile_parser = subparsers.add_parser("compile", help="Compile QASM circuit using QADE")
    compile_parser.add_argument("circuit_qasm", help="Input OpenQASM 2.0 file")
    compile_parser.add_argument("--backend", default="ibm_fez", help="Target backend name")
    compile_parser.add_argument("--hardware-aware", action="store_true", default=True, help="Apply hardware-aware placement")
    compile_parser.add_argument("--no-hardware-aware", dest="hardware_aware", action="store_false", help="Disable hardware-aware layout")
    compile_parser.add_argument("--output", help="Output OpenQASM 2.0 file")
    
    bench_parser = subparsers.add_parser("benchmark", help="Compare Qiskit L3 and QADE")
    bench_parser.add_argument("--backend", default="fake_fez", help="Backend name")
    bench_parser.add_argument("--shots", type=int, default=8192, help="Number of shots")
    bench_parser.add_argument("--circuits", default="ghz,qft,kernel,vqe", help="Circuits list")
    
    val_parser = subparsers.add_parser("validate", help="Validate QASM file")
    val_parser.add_argument("circuit_qasm", help="Input OpenQASM 2.0 file")
    
    args = parser.parse_args()
    
    if args.version:
        print("QADE 0.1.0")
        sys.exit(0)
        
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    if args.command == "compile":
        compile_command(args)
    elif args.command == "benchmark":
        benchmark_command(args)
    elif args.command == "validate":
        validate_command(args)

def compile_command_entry():
    parser = argparse.ArgumentParser(description="Compile QASM using QADE")
    parser.add_argument("circuit_qasm", help="Input QASM file")
    parser.add_argument("--backend", default="ibm_fez")
    parser.add_argument("--hardware-aware", action="store_true", default=True)
    parser.add_argument("--no-hardware-aware", dest="hardware_aware", action="store_false")
    parser.add_argument("--output")
    args = parser.parse_args()
    compile_command(args)

def benchmark_command_entry():
    parser = argparse.ArgumentParser(description="Run local QADE benchmarks")
    parser.add_argument("--backend", default="fake_fez")
    parser.add_argument("--shots", type=int, default=8192)
    parser.add_argument("--circuits", default="ghz,qft,kernel,vqe")
    args = parser.parse_args()
    benchmark_command(args)

def validate_command_entry():
    parser = argparse.ArgumentParser(description="Validate QASM file")
    parser.add_argument("circuit_qasm", help="Input QASM file")
    args = parser.parse_args()
    validate_command(args)

if __name__ == "__main__":
    main()
