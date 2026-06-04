import pytest
from qiskit import QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.providers.fake_provider import GenericBackendV2
from quantum.optimization.qiskit_plugin import QADEOptimizerPass

def test_qade_optimizer_pass_manager():
    # 1. Setup simple circuit
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    
    # 2. Setup mock backend with coupling map
    backend = GenericBackendV2(num_qubits=3, coupling_map=[[0, 1], [1, 0], [1, 2], [2, 1]])
    
    # 3. Execute pass manager with QADEOptimizerPass
    pass_manager = PassManager([
        QADEOptimizerPass(backend=backend, generations=2, population_size=4)
    ])
    
    optimized_qc = pass_manager.run(qc)
    
    # 4. Verify optimized circuit properties
    assert optimized_qc.num_qubits == 3
    assert len(optimized_qc.data) >= 1  # compiled successfully
