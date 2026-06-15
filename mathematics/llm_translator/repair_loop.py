from mathematics.ir_core.proof_ir import ProofGoalIR
from mathematics.verifier.evaluator import ProofEvaluator
from mathematics.verifier.models import VerificationResult, VerificationStatus
from mathematics.llm_translator.interfaces import FormalizableIR
from mathematics.llm_translator.models import FormalizationAttempt
from mathematics.llm_translator.client import LLMClient
from mathematics.llm_translator.parser import extract_json_object
from mathematics.llm_translator.prompts import (
    build_system_prompt,
    build_correction_prompt,
)
from mathematics.translator.exceptions import FormalizationFailure
from mathematics.prover.rewards import map_status_to_reward


class AutoFormalizationLoop:
    def __init__(self, client: LLMClient, evaluator: ProofEvaluator) -> None:
        self.client = client
        self.evaluator = evaluator
        self.trajectories: list[dict] = []

    def run(
        self, ir: FormalizableIR, max_attempts: int = 3
    ) -> tuple[VerificationResult, str, list[FormalizationAttempt]]:
        """Orchestrates the iterative proof-repair loop against the Lean 4 compiler feedback."""
        self.trajectories = []
        # 1. Translate FormalizableIR into ProofGoalIR dynamically if needed
        if hasattr(ir, "lhs") and hasattr(ir, "rhs"):
            lhs_gates = getattr(ir, "lhs")
            rhs_gates = getattr(ir, "rhs")
            lhs_str = " ⬝ ".join(
                [
                    (
                        g.gate_type.value
                        if hasattr(g.gate_type, "value")
                        else str(g.gate_type)
                    )
                    for g in lhs_gates
                ]
            )
            rhs_str = (
                " ⬝ ".join(
                    [
                        (
                            g.gate_type.value
                            if hasattr(g.gate_type, "value")
                            else str(g.gate_type)
                        )
                        for g in rhs_gates
                    ]
                )
                if rhs_gates
                else "I"
            )
            statement = f"{lhs_str} = {rhs_str}"
            goal_id = f"proof_{ir.motif_id}"
            domain = "quantum"
            source_reference = ir.motif_id
            assumptions = getattr(ir, "assumptions", [])
        else:
            statement = getattr(ir, "theorem_statement", "True")
            goal_id = getattr(
                ir, "goal_id", f"proof_{getattr(ir, 'motif_id', 'generic')}"
            )
            domain = getattr(ir, "domain", "quantum")
            source_reference = getattr(
                ir, "motif_id", getattr(ir, "source_reference", "generic")
            )
            assumptions = getattr(ir, "assumptions", [])

        goal = ProofGoalIR(
            goal_id=goal_id,
            domain=domain,
            theorem_statement=statement,
            assumptions=assumptions,
            source_reference=source_reference,
        )

        attempts: list[FormalizationAttempt] = []
        user_prompt = f"Theorem to prove: {goal.theorem_statement}\nAssumptions: {goal.assumptions}"
        system_prompt = build_system_prompt()

        for attempt_idx in range(1, max_attempts + 1):
            # 2. Query LLM Client
            raw_response = self.client.generate(system_prompt, user_prompt)

            # 3. Parse JSON Response
            try:
                parsed = extract_json_object(raw_response)
                proof_script = parsed.get("proof_script", "")
            except Exception as e:
                proof_script = ""
                attempt = FormalizationAttempt(
                    attempt_number=attempt_idx,
                    proof_script="",
                    verification_status=VerificationStatus.INTERNAL_ERROR,
                    lean_output=f"JSON extraction failed: {str(e)}\nRaw Response: {raw_response}",
                )
                attempts.append(attempt)

                # Context before this attempt is either "Initial state" or previous attempt's output
                if attempt_idx == 1:
                    state_context = "Initial state"
                else:
                    state_context = attempts[-2].lean_output or "Initial state"

                self.trajectories.append(
                    {
                        "state_context": state_context,
                        "tactic_applied": "",
                        "status": VerificationStatus.INTERNAL_ERROR.value,
                        "reward": -1.0,
                    }
                )

                user_prompt = build_correction_prompt(attempt.lean_output)
                continue

            # 4. Evaluate in Lean 4
            result = self.evaluator.evaluate(goal, proof_script)

            # 5. Record Attempt
            attempt = FormalizationAttempt(
                attempt_number=attempt_idx,
                proof_script=proof_script,
                verification_status=result.status,
                lean_output=result.error_details or result.output,
            )
            attempts.append(attempt)

            # Record trajectory
            if attempt_idx == 1:
                state_context = "Initial state"
            else:
                state_context = attempts[-2].lean_output or "Initial state"

            reward = map_status_to_reward(result.status)
            self.trajectories.append(
                {
                    "state_context": state_context,
                    "tactic_applied": proof_script,
                    "status": result.status.value,
                    "reward": reward,
                }
            )

            # 6. Check if Verified
            if result.status == VerificationStatus.VERIFIED:
                return result, proof_script, attempts

            # 7. Feed back error to compile prompt for next attempt
            user_prompt = build_correction_prompt(attempt.lean_output)

        raise FormalizationFailure(
            f"Auto-formalization failed to prove goal after {max_attempts} attempts.",
            attempts,
        )
