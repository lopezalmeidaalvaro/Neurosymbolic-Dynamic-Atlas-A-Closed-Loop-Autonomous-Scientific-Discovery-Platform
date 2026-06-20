import os
import uuid
import logging
from fastapi import FastAPI, HTTPException, status, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from quantum.api.models import CompileRequest, CompileResponse, GateCount
from quantum.api.backends import AVAILABLE_BACKENDS, load_backend
from quantum.api.compiler import compile_circuit_with_qade

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize QADE_API_KEY from environment or generate a random one
QADE_API_KEY = os.environ.get("QADE_API_KEY")
if not QADE_API_KEY:
    QADE_API_KEY = str(uuid.uuid4())
    logger.warning("=========================================================================")
    logger.warning("WARNING: QADE_API_KEY environment variable is not set!")
    logger.warning(f"Generated a dynamic key for this session: {QADE_API_KEY}")
    logger.warning("=========================================================================")

app = FastAPI(
    title="QADE REST API",
    description="REST API for QADE (Quantum-Assisted Design and Evolution) compiler pipeline with API Key protection",
    version="0.1.0"
)

# Set up API Key header extraction
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(key: str = Security(api_key_header)):
    """
    Dependency to verify the presence and validity of the X-API-Key header.
    """
    if not key or key != QADE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key"
        )

@app.get("/health")
async def health():
    """
    Returns API health status, version, and the default backend.
    No authentication required.
    """
    return {
        "status": "ok",
        "version": "0.1.0",
        "backend": "ibm_fez"
    }

@app.get("/backends", dependencies=[Depends(verify_api_key)])
async def backends():
    """
    Lists the names of available target backends.
    Requires authentication.
    """
    return {
        "available": AVAILABLE_BACKENDS
    }

@app.post("/compile", response_model=CompileResponse, dependencies=[Depends(verify_api_key)])
async def compile_circuit(request: CompileRequest):
    """
    Compiles an OpenQASM 2.0 quantum circuit using QADE's compiler pipeline.
    Requires authentication.
    """
    # 1. Validate backend_name
    if request.backend_name not in AVAILABLE_BACKENDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid backend_name '{request.backend_name}'. Must be one of: {AVAILABLE_BACKENDS}"
        )
        
    # 2. Validate input QASM syntax
    import qiskit.qasm2
    try:
        qiskit.qasm2.loads(request.circuit_qasm)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid OpenQASM 2.0 circuit: {str(e)}"
        )
        
    # 3. Load backend configuration
    try:
        backend = load_backend(request.backend_name)
    except ValueError as e:
        # e.g., missing API key for ibm_fez
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to load backend {request.backend_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load backend: {str(e)}"
        )
        
    # 4. Compile with QADE
    try:
        compiled_qasm, gate_count, depth, qubits_selected, compile_time_ms, note = compile_circuit_with_qade(
            circuit_qasm=request.circuit_qasm,
            backend=backend,
            optimization_level=request.optimization_level,
            hardware_aware=request.hardware_aware
        )
        
        return CompileResponse(
            compiled_qasm=compiled_qasm,
            gate_count=GateCount(**gate_count),
            depth=depth,
            qubits_selected=qubits_selected,
            compile_time_ms=compile_time_ms,
            note=note
        )
    except Exception as e:
        logger.error(f"Compilation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compilation error: {str(e)}"
        )
