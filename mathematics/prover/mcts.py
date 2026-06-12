import hashlib
import json
from mathematics.ir_core.proof_ir import ProofGoalIR
from mathematics.verifier.evaluator import ProofEvaluator
from mathematics.verifier.models import (
    VerificationResult,
    VerificationStatus,
    LeanProofState,
)
from mathematics.llm_translator.client import LLMClient
from mathematics.llm_translator.parser import extract_json_object
from mathematics.llm_translator.prompts import build_mcts_expansion_prompt
from mathematics.prover.tree import ProofTree, ProofStateNode
from mathematics.prover.rewards import calculate_puct, map_status_to_reward


class MonteCarloTreeSearch:
    def __init__(self, client: LLMClient, evaluator: ProofEvaluator) -> None:
        self.client = client
        self.evaluator = evaluator

    def _generate_state_id(self, accumulated_script: tuple[str, ...]) -> str:
        """Helper to generate a unique hash for a state based on its tactic script."""
        script_bytes = "\n".join(accumulated_script).encode("utf-8")
        return hashlib.sha256(script_bytes).hexdigest()

    def search(
        self, goal: ProofGoalIR, max_simulations: int = 50
    ) -> tuple[VerificationResult, str | None, dict]:
        """Runs the MCTS proof search to discover a valid tactic sequence.

        Returns (VerificationResult, proof_script_str, telemetry_dict).
        """
        # 1. Initialize root node by running evaluation with 'sorry' to extract initial goals
        initial_res = self.evaluator.evaluate(goal, "sorry")
        initial_feedback = ""
        if initial_res.proof_state:
            initial_feedback = "\n".join(initial_res.proof_state.goals)
        else:
            initial_feedback = (
                initial_res.error_details
                or initial_res.output
                or goal.theorem_statement
            )

        root_node = ProofStateNode(
            state_id="root",
            parent_id=None,
            tactic_applied=None,
            accumulated_script=(),
            lean_feedback=initial_feedback,
        )

        tree = ProofTree()
        tree.add_node(root_node, prior=1.0)

        # Track best verification result found
        best_res = initial_res
        best_script = None

        for sim_idx in range(1, max_simulations + 1):
            # --- SELECTION ---
            curr_id = "root"
            path = [curr_id]

            while tree.children.get(curr_id):
                parent_stats = tree.stats[curr_id]
                parent_visits = parent_stats.visits

                best_child_id = None
                best_puct_score = -float("inf")

                for child_id in tree.children[curr_id]:
                    child_stats = tree.stats[child_id]
                    score = calculate_puct(
                        parent_visits=parent_visits,
                        child_visits=child_stats.visits,
                        child_total_value=child_stats.total_value,
                        prior_prob=child_stats.prior_probability,
                        c_puct=1.4,
                    )
                    if score > best_puct_score:
                        best_puct_score = score
                        best_child_id = child_id

                if best_child_id is None:
                    break
                curr_id = best_child_id
                path.append(curr_id)

            curr_node = tree.nodes[curr_id]

            # --- EXPANSION ---
            # If the leaf node has been visited before, expand it
            if tree.stats[curr_id].visits > 0 or curr_id == "root":
                # Only expand if it's not verified yet and has active goals in feedback
                is_node_verified = (
                    curr_node.lean_feedback is not None
                    and "no goals" in curr_node.lean_feedback.lower()
                )

                if not is_node_verified and curr_node.lean_feedback:
                    previous_tactics = "\n".join(curr_node.accumulated_script)
                    system_prompt = "You are an AI prover helper. Output next tactics in JSON format."
                    user_prompt = build_mcts_expansion_prompt(
                        curr_node.lean_feedback, previous_tactics
                    )

                    try:
                        raw_resp = self.client.generate(system_prompt, user_prompt)
                        parsed = extract_json_object(raw_resp)
                        tactics = parsed.get("tactics", [])
                        scores = parsed.get("tactic_scores", [])

                        # Ensure alignment between tactics and scores
                        if len(tactics) == len(scores) and tactics:
                            for idx, (tactic, score) in enumerate(zip(tactics, scores)):
                                child_script = curr_node.accumulated_script + (tactic,)
                                child_id = self._generate_state_id(child_script)

                                if child_id not in tree.nodes:
                                    child_node = ProofStateNode(
                                        state_id=child_id,
                                        parent_id=curr_id,
                                        tactic_applied=tactic,
                                        accumulated_script=child_script,
                                        lean_feedback=None,
                                    )
                                    tree.add_node(child_node, prior=score)

                            # Select the best child (highest prior) to simulate
                            best_child_id = None
                            best_score = -1.0
                            for child_id in tree.children[curr_id]:
                                child_stats = tree.stats[child_id]
                                if child_stats.prior_probability > best_score:
                                    best_score = child_stats.prior_probability
                                    best_child_id = child_id

                            if best_child_id:
                                curr_id = best_child_id
                                path.append(curr_id)
                                curr_node = tree.nodes[curr_id]

                    except Exception:
                        # Gracefully skip expansion if parser/LLM fails
                        pass

            # --- SIMULATION ---
            # If node hasn't been simulated yet, run Lean compiler
            if curr_node.lean_feedback is None:
                script_str = "\n".join(curr_node.accumulated_script)
                res = self.evaluator.evaluate(goal, script_str)

                # Parse Lean proof state
                feedback_str = ""
                if res.proof_state:
                    feedback_str = "\n".join(res.proof_state.goals)
                else:
                    feedback_str = res.error_details or res.output or "State complete"

                # Update node with simulation feedback
                updated_node = ProofStateNode(
                    state_id=curr_node.state_id,
                    parent_id=curr_node.parent_id,
                    tactic_applied=curr_node.tactic_applied,
                    accumulated_script=curr_node.accumulated_script,
                    lean_feedback=feedback_str,
                )
                tree.nodes[curr_node.state_id] = updated_node
                curr_node = updated_node

                reward = map_status_to_reward(res.status)

                # Keep track of the best result
                if res.status == VerificationStatus.VERIFIED:
                    best_res = res
                    best_script = script_str
                elif (
                    best_res.status != VerificationStatus.VERIFIED
                    and res.status == VerificationStatus.UNSOLVED_GOALS
                ):
                    best_res = res
                    best_script = script_str
            else:
                # Node was already simulated, use its status
                script_str = "\n".join(curr_node.accumulated_script)
                res = self.evaluator.evaluate(goal, script_str)
                reward = map_status_to_reward(res.status)

            # --- BACKPROPAGATION ---
            for node_id in reversed(path):
                stats = tree.stats[node_id]
                stats.visits += 1
                stats.total_value += reward

            # If we verified the theorem, we can terminate early
            if best_res.status == VerificationStatus.VERIFIED:
                break

        telemetry = {
            "total_simulations": sim_idx,
            "success": best_res.status == VerificationStatus.VERIFIED,
            "nodes_explored": len(tree.nodes),
        }

        return best_res, best_script, telemetry
