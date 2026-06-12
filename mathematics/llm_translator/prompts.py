def build_system_prompt() -> str:
    """Returns the system instruction prompt demanding a strict JSON response."""
    return (
        "You are an expert Lean 4 formalizer and AI agent. "
        "Translate the given quantum/physics/mathematics concept into a valid Lean 4 tactic proof script.\n"
        "You MUST respond ONLY with a single JSON object in the following format:\n"
        "{\n"
        '  "proof_script": "exact H_squared",\n'
        '  "reasoning": "Step-by-step description of your formalization rationale"\n'
        "}\n"
        "Do not include any extra text, commentary, or markdown outside of the JSON block. "
        "The 'proof_script' field should contain only the tactics, NOT including the starting 'by' keyword."
    )


def build_correction_prompt(lean_error_output: str) -> str:
    """Returns a repair correction prompt containing the Lean 4 compiler feedback."""
    return (
        f"Your previous proof script failed to verify. Lean 4 compiler returned the following error/output:\n"
        f"```\n{lean_error_output}\n```\n"
        f"Please repair the proof script to resolve this compile error and satisfy all goals. "
        "Ensure your output strictly adheres to the JSON format described."
    )


def build_mcts_expansion_prompt(current_goal: str, previous_tactics: str) -> str:
    """Returns a prompt for generating next tactics to expand in the MCTS proof tree."""
    previous_desc = previous_tactics if previous_tactics else "None (starting state)"
    return (
        f"We are proving a theorem in Lean 4. The current outstanding goal state is:\n"
        f"```\n{current_goal}\n```\n"
        f"The tactics applied so far in this branch are:\n"
        f"```\n{previous_desc}\n```\n"
        f"Please suggest a list of mutually exclusive next tactics to explore, along with a prior probability/score for each.\n"
        f"You MUST respond ONLY with a single JSON object in the following format:\n"
        f"{{\n"
        f'  "tactics": ["exact H_squared", "intro h", "cases h"],\n'
        f'  "tactic_scores": [0.7, 0.2, 0.1]\n'
        f"}}\n"
        f"The tactic scores should represent prior probabilities (must sum to roughly 1.0). "
        f"Do not include any extra text, commentary, or markdown outside of the JSON block."
    )
