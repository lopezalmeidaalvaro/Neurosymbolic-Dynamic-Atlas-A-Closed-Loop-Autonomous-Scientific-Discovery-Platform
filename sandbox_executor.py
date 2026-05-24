import os
import sys
import re
import ast
import tempfile
import shutil
import subprocess
import time
import json
import json5

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def create_sandbox_environment():
    """
    Creates a temporary directory for the sandbox and prepares a requirements.txt file.
    Returns the path to the directory.
    """
    temp_dir = tempfile.mkdtemp(prefix="atlas_sandbox_")
    req_path = os.path.join(temp_dir, "requirements.txt")

    # Standard dependencies used by symbolic/topological/geometric methods
    requirements = [
        "numpy",
        "scipy",
        "pandas",
        "sympy",
        "json5",
        "networkx",
        "tenacity",
    ]

    with open(req_path, "w", encoding="utf-8") as f:
        f.write("\n".join(requirements))

    return temp_dir


class SafetyVisitor(ast.NodeVisitor):
    """
    AST visitor to statically scan Python code for safety violations.
    """

    def __init__(self):
        self.warnings = []
        self.is_safe = True

        # Blacklisted modules that shouldn't be imported in the sandbox
        self.blacklisted_modules = {
            "os",
            "subprocess",
            "shutil",
            "socket",
            "urllib",
            "http",
            "ftplib",
            "smtplib",
            "telnetlib",
            "pydoc",
            "webbrowser",
            "ctypes",
        }

        # Blacklisted function names and attribute names
        self.blacklisted_calls = {
            "eval",
            "exec",
            "system",
            "popen",
            "spawn",
            "fork",
            "kill",
            "rmdir",
            "remove",
            "unlink",
            "rmtree",
            "chdir",
            "listdir",
            "walk",
        }

    def visit_Import(self, node):
        for name in node.names:
            base_module = name.name.split(".")[0]
            if base_module in self.blacklisted_modules:
                self.is_safe = False
                self.warnings.append(
                    f"Blocked import of dangerous module: '{name.name}'"
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            base_module = node.module.split(".")[0]
            if base_module in self.blacklisted_modules:
                self.is_safe = False
                self.warnings.append(
                    f"Blocked import from dangerous module: '{node.module}'"
                )
        self.generic_visit(node)

    def visit_Call(self, node):
        # Check direct function calls (e.g. exec(code), eval(expr))
        if isinstance(node.func, ast.Name):
            if node.func.id in self.blacklisted_calls:
                self.is_safe = False
                self.warnings.append(
                    f"Blocked dangerous function call: '{node.func.id}()'"
                )

        # Check method/attribute calls (e.g. os.system("cmd"))
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in self.blacklisted_calls:
                self.is_safe = False
                self.warnings.append(
                    f"Blocked dangerous attribute/method call: '.{node.func.attr}()'"
                )

        self.generic_visit(node)


class SandboxExecutor:
    """
    Executes LLM-generated Python code in a secure sandboxed environment.
    Supports Docker container isolation and falls back gracefully to local subprocess.
    """

    def __init__(self, use_docker=True, timeout=120, memory_limit_mb=512):
        self.use_docker = use_docker
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.docker_available = False

        if self.use_docker:
            try:
                import docker

                self.docker_client = docker.from_env()
                # Run quick ping to verify accessibility
                self.docker_client.ping()
                self.docker_available = True
                print("[INFO] SandboxExecutor: Docker Engine verified and active.")
            except Exception as e:
                print(
                    f"[WARNING] SandboxExecutor: Docker not accessible ({e}). Falling back to local Subprocess mode."
                )
                self.use_docker = False

    def validate_code_safety(self, code):
        """
        Statically scans Python code using AST to check for safety violations.
        Returns a tuple: (is_safe, warnings_list)
        """
        try:
            tree = ast.parse(code)
            visitor = SafetyVisitor()
            visitor.visit(tree)
            return visitor.is_safe, visitor.warnings
        except SyntaxError as e:
            return False, [f"Syntax Error in code: {e}"]
        except Exception as e:
            return False, [f"Error performing static safety scan: {e}"]

    def execute(self, code, input_data=None):
        """
        Validates safety, injects input data, executes code and parses output.
        Returns a structured dictionary with results and logs.
        """
        # 1. Validate Code Safety
        is_safe, warnings = self.validate_code_safety(code)
        if not is_safe:
            return {
                "success": False,
                "stdout": "",
                "stderr": "\n".join(warnings),
                "result": None,
                "execution_time": 0.0,
                "error": f"Security Validation Failed. Code contains unsafe operations: {', '.join(warnings)}",
            }

        # Create temporary sandbox environment
        sandbox_dir = create_sandbox_environment()

        # 2. Inject global input variables
        # We prepend serialization / deserialization setup so that the variables
        # are in the local namespace of the script.
        injection_code = "import json\n"
        if input_data:
            for var_name, var_value in input_data.items():
                serialized_val = json.dumps(var_value)
                injection_code += f"{var_name} = json.loads({repr(serialized_val)})\n"

        full_code = injection_code + "\n" + code
        script_path = os.path.join(sandbox_dir, "experiment.py")

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(full_code)

        start_time = time.time()

        try:
            if self.use_docker and self.docker_available:
                return self._execute_docker(sandbox_dir, "experiment.py", start_time)
            else:
                return self._execute_subprocess(
                    sandbox_dir, "experiment.py", start_time
                )
        finally:
            # Clean up sandbox directory
            try:
                shutil.rmtree(sandbox_dir)
            except Exception:
                pass

    def _execute_subprocess(self, sandbox_dir, script_name, start_time):
        """
        Runs code in a local subprocess. Uses PYTHONPATH to ensure local project modules are accessible.
        """
        script_path = os.path.join(sandbox_dir, script_name)

        # Set environment to include the current project working directory in PYTHONPATH
        env = os.environ.copy()
        current_pwd = os.getcwd()
        env["PYTHONPATH"] = current_pwd + os.pathsep + env.get("PYTHONPATH", "")

        try:
            # Execute python script as subprocess
            proc = subprocess.run(
                [sys.executable, script_path],
                cwd=current_pwd,  # Run relative to project root to allow local file loads/saves
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env,
            )

            execution_time = time.time() - start_time
            stdout = proc.stdout
            stderr = proc.stderr

            # Check exit status
            success = proc.returncode == 0
            error_msg = None
            if not success:
                error_msg = (
                    f"Subprocess exited with non-zero return code: {proc.returncode}"
                )

            # Attempt to extract and parse JSON from stdout
            result_data = None
            if success:
                try:
                    # Find last occurrence of JSON structure in stdout
                    json_match = re.search(r"\{.*\}", stdout, re.DOTALL)
                    if json_match:
                        result_data = json5.loads(json_match.group(0))
                    else:
                        success = False
                        error_msg = "Execution succeeded but stdout did not print a valid JSON object."
                except Exception as e:
                    success = False
                    error_msg = f"Failed to parse JSON result from stdout: {e}"

            return {
                "success": success,
                "stdout": stdout,
                "stderr": stderr,
                "result": result_data,
                "execution_time": execution_time,
                "error": error_msg,
            }

        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "stdout": e.stdout if e.stdout else "",
                "stderr": e.stderr if e.stderr else "",
                "result": None,
                "execution_time": execution_time,
                "error": f"Execution timed out after {self.timeout} seconds.",
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "result": None,
                "execution_time": execution_time,
                "error": f"Execution failed: {e}",
            }

    def _execute_docker(self, sandbox_dir, script_name, start_time):
        """
        Runs code inside an isolated Docker container with memory limits and clean removal.
        """
        # Create Dockerfile
        dockerfile_content = (
            "FROM python:3.11-slim\n"
            "WORKDIR /app\n"
            "COPY . /app\n"
            "RUN pip install --no-cache-dir numpy scipy pandas sympy json5 networkx tenacity\n"
            f'CMD ["python", "{script_name}"]\n'
        )

        with open(os.path.join(sandbox_dir, "Dockerfile"), "w", encoding="utf-8") as f:
            f.write(dockerfile_content)

        # Copy current directory modules into the sandbox to allow imports in the container
        # We only copy .py files from root to avoid copying massive telemetry/dashboard datasets.
        current_pwd = os.getcwd()
        for item in os.listdir(current_pwd):
            item_path = os.path.join(current_pwd, item)
            if (
                os.path.isfile(item_path)
                and item.endswith(".py")
                and item != "setup_phase5.py"
            ):
                shutil.copy2(item_path, sandbox_dir)

        try:
            # Build docker image
            image, _ = self.docker_client.images.build(path=sandbox_dir, rm=True)

            # Start container with memory and network isolation
            container = self.docker_client.containers.create(
                image.id,
                mem_limit=f"{self.memory_limit_mb}m",
                network_disabled=True,
                detach=False,
            )

            # Start container and wait with timeout
            container.start()

            # Wait for exit status
            wait_res = container.wait(timeout=self.timeout)
            exit_code = wait_res.get("StatusCode", 0)

            # Retrieve logs
            logs = container.logs(stdout=True, stderr=True).decode(
                "utf-8", errors="replace"
            )
            container.remove(force=True)
            self.docker_client.images.remove(image=image.id, force=True)

            execution_time = time.time() - start_time
            success = exit_code == 0
            error_msg = (
                None
                if success
                else f"Docker container exited with status code: {exit_code}"
            )

            # Parse output JSON
            result_data = None
            if success:
                try:
                    json_match = re.search(r"\{.*\}", logs, re.DOTALL)
                    if json_match:
                        result_data = json5.loads(json_match.group(0))
                    else:
                        success = False
                        error_msg = "Docker execution succeeded but stdout/logs did not print a valid JSON object."
                except Exception as e:
                    success = False
                    error_msg = f"Failed to parse JSON result from Docker logs: {e}"

            return {
                "success": success,
                "stdout": logs,
                "stderr": "",  # Docker merges or we read all logs
                "result": result_data,
                "execution_time": execution_time,
                "error": error_msg,
            }

        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "result": None,
                "execution_time": execution_time,
                "error": f"Docker sandbox execution encountered an error: {e}",
            }
