from typing import Dict, Any
from quantum.simulation.cuquantum_backend import CuQuantumBackend

class SimulationManager:
    """
    Backend Selection Engine. Automatically routes quantum simulations to 
    Statevector or Tensor Network simulators based on qubit count thresholds.
    """

    def __init__(self, use_gpu: bool = True):
        self.backend = CuQuantumBackend(use_gpu=use_gpu)

    def select_backend(self, qubits: int) -> str:
        """
        Determines whether to use Statevector or Tensor Network simulation.
        """
        if qubits <= 25:
            return "STATEVECTOR_SIM"
        else:
            return "TENSOR_NETWORK_SIM"

    def run_simulation(self, circuit_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the appropriate simulation method depending on the qubit count.
        """
        qubits = circuit_spec.get("qubits", 0)
        backend_type = self.select_backend(qubits)
        
        if backend_type == "STATEVECTOR_SIM":
            res = self.backend.simulate_statevector(circuit_spec)
        else:
            res = self.backend.simulate_tensor_network(circuit_spec)
            
        if res.get("success", False):
            res["result"]["backend_selected"] = backend_type
            res["result"]["estimated_memory_mb"] = self.backend.estimate_memory(qubits)
        return res
