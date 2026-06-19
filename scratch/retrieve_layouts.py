import os
import sys
from pathlib import Path
from qiskit_ibm_runtime import QiskitRuntimeService

# Set up paths
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def retrieve_layouts():
    token = "U35_gPZ0AXsUm-xzxlYK5yyyPJfTqmSicVmOsvtICjmr"
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
    
    jobs_to_query = {
        "GHZ_5q_qiskit": "d8pklf6gbcrc73f26p60",
        "GHZ_5q_qade": "d8pklfegbcrc73f26p70",
        "QFT_5q_qiskit": "d8pklj201fac73d1t1m0",
        "QFT_5q_qade": "d8pkljegbcrc73f26peg"
    }
    
    for name, job_id in jobs_to_query.items():
        print(f"\nQuerying job {job_id} for {name}...")
        try:
            job = service.job(job_id)
            circuits = job.inputs.get("pubs", [])
            # In SamplerV2, inputs are stored under "pubs"
            # Each pub is a tuple/object containing the circuit and optional parameter values
            # Let's inspect the structure
            print(f"Pubs count: {len(circuits)}")
            for idx, pub in enumerate(circuits):
                print(f"  Type of pub: {type(pub)}")
                if isinstance(pub, (tuple, list)):
                    circuit = pub[0]
                elif hasattr(pub, "circuit"):
                    circuit = pub.circuit
                else:
                    circuit = pub
                
                print(f"  Type of circuit: {type(circuit)}")
                
                # Print name and physical qubits used
                active_qubits = sorted(list(set(circuit.find_bit(q).index for instr in circuit.data for q in instr.qubits)))
                print(f"  Circuit {idx} Name: {circuit.name}")
                print(f"  Active physical qubits: {active_qubits}")
                
                # Check measurement mapping
                measures = []
                for instr in circuit.data:
                    if instr.operation.name == "measure":
                        q_phys = circuit.find_bit(instr.qubits[0]).index
                        c_idx = circuit.find_bit(instr.clbits[0]).index
                        measures.append((c_idx, q_phys))
                print(f"  Measurements (clbit -> physical qubit): {sorted(measures)}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    retrieve_layouts()
