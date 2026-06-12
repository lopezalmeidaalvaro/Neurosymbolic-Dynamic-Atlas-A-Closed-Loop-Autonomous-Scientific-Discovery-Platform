from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class ProofGoalIR(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_id: Literal["proof_goal_ir"] = Field(
        default="proof_goal_ir",
        description="Fixed schema identifier",
    )
    schema_version: Literal["1.0"] = Field(
        default="1.0",
        description="Fixed schema version",
    )
    goal_id: str = Field(..., description="Unique identifier for the proof goal")
    domain: Literal["quantum", "physics", "mathematics"] = Field(
        ...,
        description="Logical domain of the theorem statement",
    )
    theorem_statement: str = Field(
        ...,
        description="Logical target representation of the theorem (e.g. in Lean format or prefix logic)",
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="List of proof hypotheses or assumptions",
    )
    source_reference: str = Field(
        ...,
        description="Reference identifier linking to the original quantum or physics IR",
    )
