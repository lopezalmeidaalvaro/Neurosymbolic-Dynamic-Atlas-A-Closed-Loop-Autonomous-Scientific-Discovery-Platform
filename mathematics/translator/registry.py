from mathematics.ir_core.quantum_ir import QuantumEquivalenceIR
from mathematics.translator.rules import TranslationRule


class RuleRegistry:
    def __init__(self) -> None:
        self._rules: list[TranslationRule] = []

    def register(self, rule: TranslationRule) -> None:
        """Registers a translation rule in the registry."""
        self._rules.append(rule)

    def find_rule(self, ir: QuantumEquivalenceIR) -> TranslationRule | None:
        """Finds and returns the first translation rule that matches the given IR.

        Returns None if no matching rule is found.
        """
        for rule in self._rules:
            if rule.matches(ir):
                return rule
        return None
