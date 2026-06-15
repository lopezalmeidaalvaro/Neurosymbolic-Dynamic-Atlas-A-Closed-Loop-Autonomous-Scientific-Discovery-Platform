"""
IBM Quantum Account Setup Verification Script

Before running:
1. Create account at quantum.ibm.com
2. Copy your API token from Account Settings
3. Set environment variable: IBM_QUANTUM_TOKEN=your_token_here
   (NEVER hardcode the token in code)

Run: python quantum/hardware/setup_ibm_account.py
"""

import os
from qiskit_ibm_runtime import QiskitRuntimeService

def verify_account():
    token = os.environ.get("IBM_QUANTUM_TOKEN")
    if not token:
        print("ERROR: IBM_QUANTUM_TOKEN environment variable not set.")
        print("Set it with: export IBM_QUANTUM_TOKEN=your_token_here")
        return False
    
    print("Connecting to IBM Quantum...")
    try:
        service = QiskitRuntimeService(
            channel="ibm_quantum_platform",
            token=token
        )
        # Guardar credenciales localmente para uso futuro
        QiskitRuntimeService.save_account(
            channel="ibm_quantum_platform",
            token=token,
            overwrite=True
        )
        print("Connection successful.")
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
    
    # Listar backends disponibles
    print("\nAvailable backends:")
    backends = service.backends()
    
    real_backends = []
    for b in backends:
        status = b.status()
        if status.operational:
            config = b.configuration()
            num_qubits = getattr(config, 'n_qubits', 'unknown')
            queue = status.pending_jobs
            print(f"  {b.name}: {num_qubits} qubits, queue={queue}")
            if hasattr(config, 'simulator') and not config.simulator:
                real_backends.append({
                    "name": b.name,
                    "qubits": num_qubits,
                    "queue": queue
                })
    
    if real_backends:
        # Recomendar el backend con menor cola y suficientes qubits
        best = min(
            [b for b in real_backends if b["qubits"] >= 5],
            key=lambda x: x["queue"],
            default=None
        )
        if best:
            print(f"\nRecommended backend: {best['name']}")
            print(f"  Qubits: {best['qubits']}, Queue: {best['queue']} jobs")
    
    return True

if __name__ == "__main__":
    verify_account()
