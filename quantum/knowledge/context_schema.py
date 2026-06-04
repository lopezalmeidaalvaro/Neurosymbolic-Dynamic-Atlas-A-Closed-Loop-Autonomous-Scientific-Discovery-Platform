from dataclasses import dataclass

@dataclass(frozen=True)
class Context:
    """
    Immutable representation of the physical and task context for a quantum pattern.
    """
    task_name: str
    qubit_count: int
    converged: bool

    def to_dict(self) -> dict:
        return {
            "task_name": self.task_name,
            "qubit_count": self.qubit_count,
            "converged": self.converged
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Context":
        if not data:
            return cls(task_name="unknown", qubit_count=0, converged=False)
        return cls(
            task_name=data.get("task_name", "unknown"),
            qubit_count=data.get("qubit_count", 0),
            converged=data.get("converged", False)
        )
