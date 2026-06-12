from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class ExpressionNode(BaseModel):
    model_config = ConfigDict(frozen=True)

    operator: str | None = Field(
        default=None,
        description="Optional operator name (e.g. '+', '*', 'd/dt')",
    )
    value: str | float | None = Field(
        default=None,
        description="Optional leaf value (constant, variable name, etc.)",
    )
    children: list[ExpressionNode] = Field(
        default_factory=list,
        description="List of child sub-expressions",
    )


# Rebuild the model to resolve self-referential / recursive annotations in Pydantic
ExpressionNode.model_rebuild()


class PhysicsLawIR(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_id: Literal["physics_law_ir"] = Field(
        default="physics_law_ir",
        description="Fixed schema identifier",
    )
    schema_version: Literal["1.0"] = Field(
        default="1.0",
        description="Fixed schema version",
    )
    system_id: str = Field(..., description="Identifier of the physical system")
    source_system: str = Field(..., description="Traceability source system")
    created_at: datetime = Field(..., description="Timestamp when the IR was created")
    differential_equation_ast: ExpressionNode = Field(
        ...,
        description="Abstract Syntax Tree of the differential equation",
    )
    state_variables: list[str] = Field(
        ...,
        description="List of system state variables",
    )
    invariants: list[str] = Field(
        default_factory=list,
        description="List of system conservation laws or invariants",
    )
