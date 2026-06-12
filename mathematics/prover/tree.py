from pydantic import BaseModel, Field, ConfigDict


class ProofStateNode(BaseModel):
    model_config = ConfigDict(frozen=True)

    state_id: str = Field(
        ..., description="Unique hash or string identifying this state"
    )
    parent_id: str | None = Field(
        default=None, description="Identifier of the parent node"
    )
    tactic_applied: str | None = Field(
        default=None,
        description="Tactic applied to transition from parent to this state",
    )
    accumulated_script: tuple[str, ...] = Field(
        default_factory=tuple,
        description="The sequence of tactics applied from the root to this node",
    )
    lean_feedback: str | None = Field(
        default=None,
        description="Raw Lean 4 output (goals, compilation log) associated with this state",
    )


class NodeStatistics(BaseModel):
    visits: int = Field(default=0, description="Number of MCTS visits")
    total_value: float = Field(
        default=0.0, description="Accumulated value/reward from simulations"
    )
    prior_probability: float = Field(
        default=1.0, description="Prior probability (P) suggested by the expander LLM"
    )


class ProofTree:
    def __init__(self) -> None:
        self.nodes: dict[str, ProofStateNode] = {}
        self.stats: dict[str, NodeStatistics] = {}
        self.children: dict[str, list[str]] = {}

    def add_node(self, node: ProofStateNode, prior: float = 1.0) -> None:
        """Adds a node to the search tree, initializing its statistics and parent-child relations."""
        self.nodes[node.state_id] = node
        self.stats[node.state_id] = NodeStatistics(prior_probability=prior)
        self.children[node.state_id] = []

        if node.parent_id:
            if node.parent_id not in self.children:
                self.children[node.parent_id] = []
            self.children[node.parent_id].append(node.state_id)
