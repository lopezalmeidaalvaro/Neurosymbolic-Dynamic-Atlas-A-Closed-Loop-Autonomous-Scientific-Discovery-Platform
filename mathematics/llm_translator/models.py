from enum import Enum
from pydantic import BaseModel, Field
from mathematics.verifier.models import VerificationStatus, LeanProofState


class Provenance(str, Enum):
    DETERMINISTIC_RULE = "DETERMINISTIC_RULE"
    AUTO_FORMALIZED = "AUTO_FORMALIZED"
    MCTS_DISCOVERY = "MCTS_DISCOVERY"


class LLMTranslationResponse(BaseModel):
    proof_script: str = Field(
        ...,
        description="The Lean 4 tactics script to prove the goal, without 'by' prefix",
    )
    reasoning: str | None = Field(
        default=None,
        description="Optional step-by-step description of the proof logic",
    )


class FormalizationAttempt(BaseModel):
    attempt_number: int = Field(
        ..., ge=1, description="Index of this attempt in the loop"
    )
    proof_script: str = Field(
        ..., description="The proof script tactics sent to Lean 4"
    )
    verification_status: VerificationStatus = Field(
        ..., description="The compilation/verification status returned by Lean 4"
    )
    lean_output: str = Field(
        ..., description="The compilation output or error traceback details"
    )


class MCTSExpansionResponse(BaseModel):
    tactics: list[str] = Field(
        ..., description="List of mutually exclusive next tactics to explore"
    )
    tactic_scores: list[float] = Field(
        ...,
        description="Prior probability values (must sum to roughly 1.0 or act as weights)",
    )
