from dataclasses import dataclass, asdict
from mathematics.llm_translator.interfaces import FormalizableIR
from mathematics.orchestrator.pipeline import DomainOrchestrator
from mathematics.knowledge_base.library_manager import FormalKnowledgeBase


@dataclass(slots=True)
class VerificationResponse:
    success: bool
    status: str
    provenance: str | None
    proof_script: str | None
    execution_time_ms: int | None
    error: str | None


class MathEngine:
    def __init__(
        self, orchestrator: DomainOrchestrator, kb: FormalKnowledgeBase
    ) -> None:
        self._orchestrator = orchestrator
        self._kb = kb

    def verify_discovery(self, ir: FormalizableIR) -> dict:
        """Verifies a formalizable IR by running it through the handler chain.

        Returns a dictionary representation of VerificationResponse.
        It catches all exceptions to prevent system crashes.
        """
        try:
            res_tuple = self._orchestrator.process(ir)
            if res_tuple is None:
                # The verification chain ran but failed to find a verified proof
                resp = VerificationResponse(
                    success=False,
                    status="UNVERIFIED",
                    provenance=None,
                    proof_script=None,
                    execution_time_ms=None,
                    error="Formalization chain failed to verify the proof goal.",
                )
                return asdict(resp)

            result, proof_script, provenance = res_tuple
            is_verified = result.status.value == "VERIFIED"

            resp = VerificationResponse(
                success=is_verified,
                status=result.status.value,
                provenance=provenance.value,
                proof_script=proof_script,
                execution_time_ms=result.execution_time_ms,
                error=result.error_details,
            )
            return asdict(resp)

        except Exception as e:
            resp = VerificationResponse(
                success=False,
                status="INTERNAL_ERROR",
                provenance=None,
                proof_script=None,
                execution_time_ms=None,
                error=str(e),
            )
            return asdict(resp)

    def get_rlcf_interface(self) -> FormalKnowledgeBase:
        """Exposes the internal database interface for RLCF operations."""
        return self._kb
