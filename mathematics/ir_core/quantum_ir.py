from datetime import datetime
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class GateType(str, Enum):
    H = "H"
    X = "X"
    Y = "Y"
    Z = "Z"
    CNOT = "CNOT"
    SWAP = "SWAP"
    RX = "RX"
    RY = "RY"
    RZ = "RZ"


class GateNode(BaseModel):
    model_config = ConfigDict(frozen=True)

    gate_type: GateType = Field(..., description="The type of quantum gate")
    qubits: list[int] = Field(
        ..., description="Indices of the qubits affected by this gate"
    )
    parameters: list[float] | None = Field(
        default=None,
        description="Optional list of float parameters (e.g. rotation angles)",
    )


class QuantumEquivalenceIR(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_id: Literal["quantum_equivalence_ir"] = Field(
        default="quantum_equivalence_ir",
        description="Fixed schema identifier",
    )
    schema_version: Literal["1.0"] = Field(
        default="1.0",
        description="Fixed schema version",
    )
    motif_id: str = Field(..., description="Identifier of the equivalent quantum motif")
    source_system: str = Field(..., description="Traceability source system")
    created_at: datetime = Field(..., description="Timestamp when the IR was created")
    lhs: list[GateNode] = Field(..., description="Left-hand side quantum gate sequence")
    rhs: list[GateNode] = Field(
        ..., description="Right-hand side quantum gate sequence"
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="List of logical assumptions for this equivalence",
    )
