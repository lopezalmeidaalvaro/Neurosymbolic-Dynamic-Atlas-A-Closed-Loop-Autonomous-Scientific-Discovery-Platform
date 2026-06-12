from mathematics.ir_core.proof_ir import ProofGoalIR
from mathematics.verifier.document_builder import LeanDocumentBuilder
from mathematics.verifier.models import VerificationResult
from mathematics.verifier.runtime import LeanRuntime


class ProofEvaluator:
    def __init__(self, runtime: LeanRuntime) -> None:
        self.runtime = runtime

    def evaluate(self, goal: ProofGoalIR, proof_script: str) -> VerificationResult:
        """Assembles a Lean 4 document and executes it using the configured runtime."""
        # 1. Build the document
        builder = LeanDocumentBuilder()
        builder.add_comment(f"Proof Goal ID: {goal.goal_id}")
        builder.add_comment(f"Source Reference: {goal.source_reference}")
        builder.add_comment(f"Domain: {goal.domain}")

        # Set namespace dynamically based on the domain to isolate proofs
        builder.set_namespace(f"MathDomain.{goal.domain}")
        builder.set_goal(goal)

        lean_code = builder.build_document(proof_script)

        # 2. Run verification script via runtime
        return self.runtime.execute_script(lean_code)
