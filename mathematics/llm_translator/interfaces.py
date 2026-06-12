from typing import Protocol


class FormalizableIR(Protocol):
    @property
    def schema_id(self) -> str:
        """The identifier of the schema representing this contract."""
        ...

    @property
    def schema_version(self) -> str:
        """The version of the schema."""
        ...

    @property
    def source_system(self) -> str:
        """The source system originating this contract."""
        ...

    @property
    def motif_id(self) -> str:
        """The unique identifier of the motifs under analysis."""
        ...
