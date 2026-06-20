import os
import subprocess
import sys

def test_no_monorepo_imports():
    """Verifica que ningún módulo de QADE importa fuera de su dominio"""
    forbidden_patterns = [
        "from satellite", "from mathematics", "from ia_matematica",
        "import satellite", "import mathematics"
    ]
    
    # Check only QADE core standalone packages
    core_packages = {"optimization", "integration", "sandbox", "critics", "evolution", "hardware"}
    violations = []
    
    for root, dirs, files in os.walk("quantum"):
        parts = root.split(os.sep)
        if len(parts) > 1:
            pkg_name = parts[1]
            if pkg_name not in core_packages:
                continue
        else:
            continue
            
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line_no, line in enumerate(f, 1):
                        clean_line = line.strip()
                        if not clean_line or clean_line.startswith("#"):
                            continue
                        for pattern in forbidden_patterns:
                            if pattern in clean_line:
                                violations.append(f"{filepath}:{line_no} -> {clean_line}")
                                
    assert len(violations) == 0, f"Monorepo imports found in core QADE package:\n" + "\n".join(violations)
    print("[OK] No monorepo imports found in core QADE package")

def test_cli_version():
    """Verifica que el CLI responde"""
    # Execute python -m quantum.cli --version instead of bare 'qade' command to bypass system path delays
    # or test the installed entry point directly. Let's do both or fallback to python -m
    try:
        result = subprocess.run(
            ["qade", "--version"],
            capture_output=True, text=True, shell=True
        )
        output = (result.stdout + result.stderr).strip()
    except Exception:
        output = ""
        
    if "0.1.0" not in output:
        # Fallback to direct python execution in case environment path is not refreshed
        result = subprocess.run(
            [sys.executable, "-m", "quantum.cli", "--version"],
            capture_output=True, text=True
        )
        output = (result.stdout + result.stderr).strip()
        
    assert "0.1.0" in output, f"CLI version test failed. Output was: {output}"
    print("[OK] CLI version OK")

if __name__ == "__main__":
    test_no_monorepo_imports()
    test_cli_version()
    print("\n[OK] Isolation smoke test PASSED")
