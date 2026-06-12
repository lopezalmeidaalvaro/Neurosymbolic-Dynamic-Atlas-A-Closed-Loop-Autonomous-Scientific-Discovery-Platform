class TranslationError(Exception):
    """Base exception for all translation errors in the mathematics domain."""

    pass


class NoMatchingRuleError(TranslationError):
    """Exception raised when no translation rule matches the given IR motif."""

    def __init__(self, motif_id: str) -> None:
        super().__init__(
            f"No matching translation rule was found for motif ID: '{motif_id}'"
        )
        self.motif_id = motif_id


class FormalizationFailure(TranslationError):
    """Exception raised when the auto-formalization loop fails to prove a goal."""

    def __init__(self, message: str, attempts: list) -> None:
        super().__init__(message)
        self.attempts = attempts
