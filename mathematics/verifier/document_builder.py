from mathematics.ir_core.proof_ir import ProofGoalIR


class LeanDocumentBuilder:
    def __init__(self) -> None:
        self._comments: list[str] = []
        self._imports: list[str] = []
        self._namespace: str | None = None
        self._goal: ProofGoalIR | None = None

    def add_comment(self, text: str) -> "LeanDocumentBuilder":
        """Appends a comment to the document header."""
        self._comments.append(text)
        return self

    def add_import(self, module: str) -> "LeanDocumentBuilder":
        """Adds a module import declaration to the document."""
        self._imports.append(module)
        return self

    def set_namespace(self, name: str) -> "LeanDocumentBuilder":
        """Sets the namespace namespace scope for the document."""
        self._namespace = name
        return self

    def set_goal(self, goal_ir: ProofGoalIR) -> "LeanDocumentBuilder":
        """Sets the proof goal intermediate representation."""
        self._goal = goal_ir
        return self

    def build_document(self, proof_script: str) -> str:
        """Assembles and returns the full Lean 4 source document as a string."""
        if not self._goal:
            raise ValueError("ProofGoalIR must be set before building the document.")

        lines: list[str] = []

        # 1. Add Imports
        if self._imports:
            for imp in self._imports:
                lines.append(f"import {imp}")
            lines.append("")

        # 2. Add Namespace (Start)
        if self._namespace:
            lines.append(f"namespace {self._namespace}")
            lines.append("")

        # 3. Add Comments
        if self._comments:
            for comment in self._comments:
                for subline in comment.split("\n"):
                    lines.append(f"-- {subline}")
            lines.append("")

        # 4. Add Theorem Declaration
        stmt = self._goal.theorem_statement.strip()
        if stmt.startswith("theorem"):
            theorem_decl = stmt
        else:
            # Construct theorem statement with assumptions
            formatted_asms = []
            for asm in self._goal.assumptions:
                asm_str = asm.strip()
                if not asm_str:
                    continue
                # Wrap in parentheses if not already wrapped
                if not (asm_str.startswith("(") and asm_str.endswith(")")) and not (
                    asm_str.startswith("[") and asm_str.endswith("]")
                ):
                    formatted_asms.append(f"({asm_str})")
                else:
                    formatted_asms.append(asm_str)

            assumptions_str = (" " + " ".join(formatted_asms)) if formatted_asms else ""
            theorem_decl = f"theorem {self._goal.goal_id}{assumptions_str} : {stmt}"

        # 5. Add Proof Script
        lines.append(f"{theorem_decl} := by")
        proof_script_clean = proof_script.strip()
        for p_line in proof_script_clean.split("\n"):
            lines.append(f"  {p_line}")

        # 6. Add Namespace (End)
        if self._namespace:
            lines.append("")
            lines.append(f"end {self._namespace}")

        return "\n".join(lines)
