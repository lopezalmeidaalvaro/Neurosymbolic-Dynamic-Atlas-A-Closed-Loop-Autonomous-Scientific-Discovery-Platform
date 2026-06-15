from typing import Optional
from mathematics.ir_core.quantum_ir import QuantumEquivalenceIR
from mathematics.llm_translator.interfaces import FormalizableIR
from mathematics.llm_translator.models import Provenance
from mathematics.verifier.models import VerificationResult, VerificationStatus
from mathematics.knowledge_base.library_manager import FormalKnowledgeBase
from mathematics.orchestrator.handlers import AbstractFormalizationHandler


class DomainOrchestrator:
    def __init__(
        self, chain: AbstractFormalizationHandler, kb: FormalKnowledgeBase
    ) -> None:
        self.chain = chain
        self.kb = kb

    def process(
        self, ir: FormalizableIR
    ) -> Optional[tuple[VerificationResult, str, Provenance]]:
        """Processes the formalizable IR through the Chain of Responsibility.

        If verification succeeds, it persists the result in the formal knowledge base.
        """
        import uuid

        run_id = f"run_{uuid.uuid4().hex}"

        res_tuple = self.chain.handle(ir)

        # Extract trajectories from handlers in the chain
        trajectories = []
        curr = self.chain
        while curr:
            if hasattr(curr, "repair_loop") and getattr(curr, "repair_loop"):
                loop = getattr(curr, "repair_loop")
                if hasattr(loop, "trajectories") and loop.trajectories:
                    trajectories.extend(loop.trajectories)
            elif hasattr(curr, "mcts") and getattr(curr, "mcts"):
                mcts_inst = getattr(curr, "mcts")
                if hasattr(mcts_inst, "trajectories") and mcts_inst.trajectories:
                    trajectories.extend(mcts_inst.trajectories)
            curr = getattr(curr, "_next_handler", None)

        # Bulk log trajectories
        ir_metadata = getattr(ir, "metadata", None)
        for traj in trajectories:
            self.kb.log_trajectory(
                run_id=run_id,
                state_context=traj["state_context"],
                tactic_applied=traj["tactic_applied"],
                status=traj["status"],
                reward=traj["reward"],
                metadata=ir_metadata,
            )

        if res_tuple is None:
            return None

        result, proof_script, provenance = res_tuple

        # Check if the result was VERIFIED
        is_verified = result.status == VerificationStatus.VERIFIED

        # If verified, save it to the FormalKnowledgeBase
        if is_verified:
            # Map IR parameters dynamically
            if isinstance(ir, QuantumEquivalenceIR):
                lhs_str = " ⬝ ".join(
                    [
                        (
                            g.gate_type.value
                            if hasattr(g.gate_type, "value")
                            else str(g.gate_type)
                        )
                        for g in ir.lhs
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
                            for g in ir.rhs
                        ]
                    )
                    if ir.rhs
                    else "I"
                )
                statement = f"{lhs_str} = {rhs_str}"
                theorem_id = ir.motif_id
                domain = "quantum"
            else:
                statement = getattr(ir, "theorem_statement", "True")
                theorem_id = getattr(
                    ir, "motif_id", getattr(ir, "goal_id", "generic_id")
                )
                domain = getattr(ir, "domain", "quantum")

            self.kb.add_theorem(
                theorem_id=theorem_id,
                domain=domain,
                schema_version=ir.schema_version,
                statement=statement,
                lean_proof=proof_script,
                verified=is_verified,
                provenance=provenance.value,
                dependencies=[],
            )

        return res_tuple
