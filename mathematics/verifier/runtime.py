import subprocess
import tempfile
import time
from abc import ABC, abstractmethod
from pathlib import Path
from mathematics.verifier.models import VerificationResult, VerificationStatus
from mathematics.verifier.parser import LeanOutputParser


class LeanRuntime(ABC):
    @abstractmethod
    def execute_script(self, lean_code: str) -> VerificationResult:
        """Executes a Lean script and returns the structured VerificationResult."""
        pass


class LocalLeanRuntime(LeanRuntime):
    def __init__(
        self, lean_executable: str = "lean", timeout_seconds: float = 10.0
    ) -> None:
        self.lean_executable = lean_executable
        self.timeout_seconds = timeout_seconds

    def execute_script(self, lean_code: str) -> VerificationResult:
        start_time = time.perf_counter()

        # Write code to a temporary file
        temp_file = tempfile.NamedTemporaryFile(
            suffix=".lean", mode="w", encoding="utf-8", delete=False
        )
        temp_file_name = temp_file.name

        try:
            temp_file.write(lean_code)
            temp_file.close()

            # Execute Lean compiler
            res = subprocess.run(
                [self.lean_executable, temp_file_name],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )

            elapsed_time_ms = int((time.perf_counter() - start_time) * 1000)

            # Delegate parsing to LeanOutputParser
            status, error_details = LeanOutputParser.parse(
                res.stdout, res.stderr, res.returncode
            )

            proof_state = LeanOutputParser.parse_proof_state(res.stdout, res.stderr)

            return VerificationResult(
                status=status,
                output=res.stdout,
                error_details=error_details,
                execution_time_ms=elapsed_time_ms,
                proof_state=proof_state,
            )

        except subprocess.TimeoutExpired as e:
            elapsed_time_ms = int((time.perf_counter() - start_time) * 1000)
            stdout = (
                e.stdout
                if isinstance(e.stdout, str)
                else (e.stdout.decode("utf-8", errors="ignore") if e.stdout else "")
            )
            stderr = (
                e.stderr
                if isinstance(e.stderr, str)
                else (e.stderr.decode("utf-8", errors="ignore") if e.stderr else "")
            )
            return VerificationResult(
                status=VerificationStatus.TIMEOUT,
                output=stdout,
                error_details=f"Execution timed out after {self.timeout_seconds}s. {str(e)}\n{stderr}",
                execution_time_ms=elapsed_time_ms,
            )

        except FileNotFoundError as e:
            elapsed_time_ms = int((time.perf_counter() - start_time) * 1000)
            return VerificationResult(
                status=VerificationStatus.INTERNAL_ERROR,
                output="",
                error_details=f"Lean executable '{self.lean_executable}' not found. Error: {str(e)}",
                execution_time_ms=elapsed_time_ms,
            )

        except Exception as e:
            elapsed_time_ms = int((time.perf_counter() - start_time) * 1000)
            return VerificationResult(
                status=VerificationStatus.INTERNAL_ERROR,
                output="",
                error_details=f"Unexpected error executing Lean script: {str(e)}",
                execution_time_ms=elapsed_time_ms,
            )

        finally:
            try:
                Path(temp_file_name).unlink(missing_ok=True)
            except Exception:
                pass
