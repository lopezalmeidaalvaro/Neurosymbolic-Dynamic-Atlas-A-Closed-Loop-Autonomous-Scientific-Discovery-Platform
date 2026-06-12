from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNSOLVED_GOALS = "UNSOLVED_GOALS"
    COMPILATION_ERROR = "COMPILATION_ERROR"
    TIMEOUT = "TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class LeanProofState(BaseModel):
    model_config = ConfigDict(frozen=True)

    goals: list[str] = Field(..., description="List of outstanding proof goals")
    context: str = Field(..., description="Available context hypotheses and variables")
    raw_output: str = Field(..., description="Raw output text from Lean compiler")


class VerificationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: VerificationStatus = Field(
        ..., description="The status code of the verification execution"
    )
    output: str = Field(
        ..., description="Raw standard output from the Lean verification compiler"
    )
    error_details: str | None = Field(
        default=None,
        description="Detailed error message if compilation or verification failed",
    )
    execution_time_ms: int = Field(
        ..., ge=0, description="Execution duration measured in milliseconds"
    )
    proof_state: LeanProofState | None = Field(
        default=None,
        description="Detailed Lean proof state if verification is in progress or unsolved",
    )
