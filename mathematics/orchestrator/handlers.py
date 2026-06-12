import uuid
from abc import ABC, abstractmethod
from typing import Optional
from mathematics.ir_core.quantum_ir import QuantumEquivalenceIR
from mathematics.ir_core.proof_ir import ProofGoalIR
from mathematics.llm_translator.interfaces import FormalizableIR
from mathematics.llm_translator.models import Provenance
from mathematics.verifier.models import VerificationResult, VerificationStatus
from mathematics.verifier.evaluator import ProofEvaluator
from mathematics.translator.mapper import QuantumEquivalenceTranslator
from mathematics.translator.exceptions import NoMatchingRuleError, FormalizationFailure
from mathematics.llm_translator.repair_loop import AutoFormalizationLoop
from mathematics.prover.mcts import MonteCarloTreeSearch
from mathematics.knowledge_base.library_manager import FormalKnowledgeBase


class AbstractFormalizationHandler(ABC):
    def __init__(self) -> None:
        self._next_handler: Optional[AbstractFormalizationHandler] = None

    def set_next(
        self, handler: "AbstractFormalizationHandler"
    ) -> "AbstractFormalizationHandler":
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(
        self, ir: FormalizableIR
    ) -> Optional[tuple[VerificationResult, str, Provenance]]:
        """Handles the IR formalization.

        Delegates to the next handler if this handler cannot process it.
        """
        if self._next_handler:
            return self._next_handler.handle(ir)
        return None


class DeterministicHandler(AbstractFormalizationHandler):
    def __init__(
        self, translator: QuantumEquivalenceTranslator, evaluator: ProofEvaluator
    ) -> None:
        super().__init__()
        self.translator = translator
        self.evaluator = evaluator

    def handle(
        self, ir: FormalizableIR
    ) -> Optional[tuple[VerificationResult, str, Provenance]]:
        # This handler expects a QuantumEquivalenceIR to perform pattern rule matching
        if not isinstance(ir, QuantumEquivalenceIR):
            return super().handle(ir)

        try:
            goal, proof_script = self.translator.translate(ir)
            result = self.evaluator.evaluate(goal, proof_script)
            return result, proof_script, Provenance.DETERMINISTIC_RULE
        except NoMatchingRuleError:
            return super().handle(ir)


class LLMHandler(AbstractFormalizationHandler):
    def __init__(self, repair_loop: AutoFormalizationLoop) -> None:
        super().__init__()
        self.repair_loop = repair_loop

    def handle(
        self, ir: FormalizableIR
    ) -> Optional[tuple[VerificationResult, str, Provenance]]:
        try:
            # Fall back to LLM translation and iterative repair loop
            result, proof_script, _attempts = self.repair_loop.run(ir)
            return result, proof_script, Provenance.AUTO_FORMALIZED
        except FormalizationFailure as e:
            # Check if the last attempt succeeded compile-wise but left unresolved goals
            if e.attempts:
                last_attempt = e.attempts[-1]
                if (
                    last_attempt.verification_status
                    == VerificationStatus.UNSOLVED_GOALS
                ):
                    # Pass the control to MCTSHandler
                    return super().handle(ir)
            # If compile errors occurred, do NOT pass control
            return None
        except Exception:
            # For any other hard failure, stop execution
            return None


class MCTSHandler(AbstractFormalizationHandler):
    def __init__(self, mcts: MonteCarloTreeSearch, kb: FormalKnowledgeBase) -> None:
        super().__init__()
        self.mcts = mcts
        self.kb = kb

    def handle(
        self, ir: FormalizableIR
    ) -> Optional[tuple[VerificationResult, str, Provenance]]:
        # Map dynamic IR attributes to ProofGoalIR
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

        res, proof_script, telemetry = self.mcts.search(goal)

        # Log the simulation run details for offline Reinforcement Learning telemetry
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        self.kb.log_mcts_run(
            run_id=run_id,
            theorem_id=goal.source_reference,
            total_simulations=telemetry["total_simulations"],
            success=telemetry["success"],
            nodes_explored=telemetry["nodes_explored"],
        )

        if res.status == VerificationStatus.VERIFIED and proof_script:
            return res, proof_script, Provenance.MCTS_DISCOVERY

        return super().handle(ir)
