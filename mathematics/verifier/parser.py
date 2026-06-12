from mathematics.verifier.models import VerificationStatus, LeanProofState


class LeanOutputParser:
    @staticmethod
    def parse(
        stdout: str, stderr: str, return_code: int
    ) -> tuple[VerificationStatus, str | None]:
        """Parses the output of the Lean 4 compiler process to determine verification status.

        It looks for indicators of unsolved goals or 'sorry' statements.
        """
        combined = stdout + "\n" + stderr
        combined_lower = combined.lower()

        # Check for sorry usage or unsolved goals.
        # Lean 4 outputs messages like "unsolved goals" or "declaration uses sorry"
        # during tactic execution.
        has_unsolved = (
            "unsolved goals" in combined_lower
            or "goals remaining" in combined_lower
            or "declaration uses sorry" in combined_lower
            or "sorry" in combined_lower
        )

        if has_unsolved:
            return (
                VerificationStatus.UNSOLVED_GOALS,
                "The proof contains unsolved goals or utilizes 'sorry' placeholders.",
            )

        if return_code != 0:
            error_details = stderr.strip() or stdout.strip()
            return (
                VerificationStatus.COMPILATION_ERROR,
                error_details or "Compilation failed with a non-zero return code.",
            )

        return VerificationStatus.VERIFIED, None

    @staticmethod
    def parse_proof_state(stdout: str, stderr: str) -> LeanProofState | None:
        """Parses standard streams to extract outstanding proof goals and hypotheses context."""
        combined = stdout + "\n" + stderr
        combined_lower = combined.lower()

        # Lean 4 uses the turnstile character '⊢' to prefix outstanding goals
        if (
            "⊢" in combined
            or "unsolved goals" in combined_lower
            or "goals remaining" in combined_lower
        ):
            goals = []
            context_lines = []
            for line in combined.split("\n"):
                line_strip = line.strip()
                if not line_strip:
                    continue
                if "⊢" in line_strip:
                    goals.append(line_strip)
                elif (
                    ":" in line_strip
                    and not line_strip.startswith("state:")
                    and not line_strip.startswith("unsolved goals")
                ):
                    context_lines.append(line_strip)

            return LeanProofState(
                goals=goals,
                context="\n".join(context_lines),
                raw_output=combined,
            )
        return None
