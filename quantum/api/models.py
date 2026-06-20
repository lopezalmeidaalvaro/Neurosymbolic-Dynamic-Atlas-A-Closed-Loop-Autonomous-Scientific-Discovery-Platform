from pydantic import BaseModel, Field
from typing import List, Optional

class CompileRequest(BaseModel):
    circuit_qasm: str = Field(..., description="OpenQASM 2.0 representation of the circuit to compile")
    backend_name: str = Field("ibm_fez", description="Target backend name (ibm_fez, fake_fez, fake_sherbrooke)")
    optimization_level: int = Field(1, ge=0, le=3, description="Qiskit transpilation optimization level (0-3)")
    hardware_aware: bool = Field(True, description="Whether to apply QADE hardware-aware optimization pass")

class GateCount(BaseModel):
    total: int = Field(..., description="Total gate count (excluding barriers and measurements)")
    one_qubit: int = Field(..., description="Number of 1-qubit gates")
    two_qubit: int = Field(..., description="Number of 2-qubit gates")

class CompileResponse(BaseModel):
    compiled_qasm: str = Field(..., description="Compiled circuit represented in OpenQASM 2.0")
    gate_count: GateCount = Field(..., description="Decomposed gate counts")
    depth: int = Field(..., description="Depth of the compiled circuit")
    qubits_selected: List[int] = Field(..., description="Physical layout qubit mapping (Stage C selection)")
    compile_time_ms: float = Field(..., description="Compile execution time in milliseconds")
    qade_version: str = Field("0.1.0", description="QADE compiler version")
    note: Optional[str] = Field(None, description="Optional notes, e.g. details about evolution bypass")
