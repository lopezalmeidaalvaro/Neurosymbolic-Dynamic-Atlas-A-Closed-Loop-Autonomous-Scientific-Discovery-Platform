import os
from qiskit_ibm_runtime import QiskitRuntimeService
from quantum.optimization.calibration_model import get_fake_backend

AVAILABLE_BACKENDS = ["ibm_fez", "fake_fez", "fake_sherbrooke"]

def load_backend(backend_name: str):
    """
    Loads the requested quantum backend by name.
    'fake_fez' and 'fake_sherbrooke' are loaded locally without credentials.
    'ibm_fez' requires credentials in the IBMQ_API_KEY environment variable.
    """
    backend_clean = backend_name.strip().lower()
    
    if backend_clean == "fake_fez":
        return get_fake_backend("FakeFez")
    elif backend_clean == "fake_sherbrooke":
        return get_fake_backend("FakeSherbrooke")
    elif backend_clean == "ibm_fez":
        api_key = os.environ.get("IBMQ_API_KEY")
        if not api_key:
            raise ValueError("Environment variable IBMQ_API_KEY is not set.")
        service = QiskitRuntimeService(channel="ibm_quantum_platform", token=api_key)
        return service.backend("ibm_fez")
    else:
        raise ValueError(f"Backend '{backend_name}' is not available. Choose from {AVAILABLE_BACKENDS}")
