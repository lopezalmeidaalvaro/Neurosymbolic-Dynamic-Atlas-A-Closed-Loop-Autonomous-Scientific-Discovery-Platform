import os
from typing import Any, Dict
from mathematics import bootstrap_math_engine


def bootstrap_application(
    db_path: str = "mathematics.db",
    llm_api_url: str = "http://localhost:8000/v1",
    llm_api_key: str = "mock-key",
    llm_model: str = "mock-model",
    lean_executable: str = "lean",
) -> Dict[str, Any]:
    """App-level Composition Root that bootstraps the mathematics engine and

    injects it into the QADE quantum optimizer module.
    """
    # 1. Initialize the formal mathematical verification engine
    math_engine = bootstrap_math_engine(
        db_path=db_path,
        llm_api_url=llm_api_url,
        llm_api_key=llm_api_key,
        llm_model=llm_model,
        lean_executable=lean_executable,
    )

    # 2. Import quantum components
    from quantum.adapters.formal_verifier import FormalVerificationAdapter
    from quantum.pipeline.phase_v_certification import QADEMotifCertifier
    from quantum.factories.quantum_factory import create_quantum_container

    # 3. Instantiate the adapter and certifier wrapping the MathEngine
    verifier_adapter = FormalVerificationAdapter(math_engine)
    motif_certifier = QADEMotifCertifier(verifier_adapter)

    # 4. Bootstrap the quantum optimization container
    quantum_container = create_quantum_container()

    # 5. Inject dependencies into the quantum module's container
    # (Dynamically extending the container with Phase V formal verification elements)
    quantum_container.math_engine = math_engine
    quantum_container.verifier_adapter = verifier_adapter
    quantum_container.motif_certifier = motif_certifier

    # 6. Return the fully assembled application configuration
    return {
        "math_engine": math_engine,
        "quantum_container": quantum_container,
        "verifier_adapter": verifier_adapter,
        "motif_certifier": motif_certifier,
    }
