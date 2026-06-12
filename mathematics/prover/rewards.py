import math
from mathematics.verifier.models import VerificationStatus


def calculate_puct(
    parent_visits: int,
    child_visits: int,
    child_total_value: float,
    prior_prob: float,
    c_puct: float = 1.0,
) -> float:
    """Calculates the PUCT (Prior UCB) value for a child node during selection."""
    if child_visits > 0:
        q_value = child_total_value / child_visits
    else:
        q_value = 0.0

    # Exploration term: c_puct * P(s, a) * sqrt(N_parent) / (1 + N_child)
    exploration_term = (
        c_puct * prior_prob * (math.sqrt(parent_visits) / (1 + child_visits))
    )

    return q_value + exploration_term


def map_status_to_reward(status: VerificationStatus) -> float:
    """Maps Lean 4 VerificationStatus outputs into numerical MCTS rewards.

    - VERIFIED: +1.0
    - UNSOLVED_GOALS: +0.1
    - COMPILATION_ERROR / TIMEOUT / INTERNAL_ERROR: -1.0
    """
    if status == VerificationStatus.VERIFIED:
        return 1.0
    elif status == VerificationStatus.UNSOLVED_GOALS:
        return 0.1
    else:
        # Penalize syntax errors, timeouts, or unexpected crashes
        return -1.0
