from abc import ABC, abstractmethod
from mathematics.ir_core.quantum_ir import QuantumEquivalenceIR, GateType
from mathematics.ir_core.proof_ir import ProofGoalIR


class TranslationRule(ABC):
    @abstractmethod
    def matches(self, ir: QuantumEquivalenceIR) -> bool:
        """Determines if the given QuantumEquivalenceIR matches this rule's pattern."""
        pass

    @abstractmethod
    def build_goal(self, ir: QuantumEquivalenceIR) -> tuple[ProofGoalIR, str]:
        """Translates the QuantumEquivalenceIR into a ProofGoalIR and a tactic proof script."""
        pass


class DoubleHadamardRule(TranslationRule):
    def matches(self, ir: QuantumEquivalenceIR) -> bool:
        """Matches if LHS has exactly two 'H' gates on the same qubit, and RHS is empty."""
        if len(ir.lhs) != 2:
            return False

        g1 = ir.lhs[0]
        g2 = ir.lhs[1]

        if g1.gate_type != GateType.H or g2.gate_type != GateType.H:
            return False

        if g1.qubits != g2.qubits:
            return False

        if len(ir.rhs) != 0:
            return False

        return True

    def build_goal(self, ir: QuantumEquivalenceIR) -> tuple[ProofGoalIR, str]:
        """Translates the double Hadamard pattern into a formal ProofGoalIR in Lean 4.

        Yields proof script 'exact H_squared'.
        """
        goal = ProofGoalIR(
            goal_id=f"proof_{ir.motif_id}",
            domain="quantum",
            theorem_statement="H ⬝ H = I",
            assumptions=[],
            source_reference=ir.motif_id,
        )
        return goal, "exact H_squared"
