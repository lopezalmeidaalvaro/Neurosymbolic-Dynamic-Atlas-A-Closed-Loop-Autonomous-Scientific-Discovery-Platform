from mathematics.ir_core.quantum_ir import QuantumEquivalenceIR
from mathematics.ir_core.proof_ir import ProofGoalIR
from mathematics.translator.registry import RuleRegistry
from mathematics.translator.exceptions import NoMatchingRuleError


class QuantumEquivalenceTranslator:
    def __init__(self, registry: RuleRegistry) -> None:
        self._registry = registry

    def translate(self, equivalence: QuantumEquivalenceIR) -> tuple[ProofGoalIR, str]:
        """Translates a QuantumEquivalenceIR into its target ProofGoalIR and proof script.

        Raises NoMatchingRuleError if no matching rule is found in the registry.
        """
        rule = self._registry.find_rule(equivalence)
        if rule is None:
            raise NoMatchingRuleError(equivalence.motif_id)
        return rule.build_goal(equivalence)
