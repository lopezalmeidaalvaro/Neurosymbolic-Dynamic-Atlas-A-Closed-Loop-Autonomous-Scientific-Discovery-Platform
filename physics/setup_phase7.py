import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import sys
import subprocess

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def install_and_verify():
    print("======================================================================")
    print("INITIALIZING PHASE 7 DEPENDENCIES INSTALLATION")
    print("======================================================================")
    
    dependencies = ["numpy", "scipy", "matplotlib", "networkx", "sympy", "numba"]
    installed_successfully = []
    failed_dependencies = []

    # 1. Install dependencies via pip
    for dep in dependencies:
        print(f"Installing {dep}...")
        try:
            # Use sys.executable to ensure we use the correct virtual/system Python environment
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True, capture_output=True)
            print(f"Successfully installed {dep}.")
            installed_successfully.append(dep)
        except Exception as e:
            print(f"Failed to install {dep} via pip. Error: {e}")
            failed_dependencies.append(dep)

    print("\n----------------------------------------------------------------------")
    print("AUDITING IMPORT STATUSES")
    print("----------------------------------------------------------------------")
    
    import_errors = []
    
    # 2. Verify imports
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"Import check [OK]: '{dep}' imported successfully.")
        except ImportError as e:
            print(f"Import check [FAIL]: Failed to import '{dep}'. Error: {e}")
            import_errors.append((dep, str(e)))

    print("\n======================================================================")
    print("SUMMARY REPORT")
    print("======================================================================")
    
    if len(import_errors) == 0:
        print("Entorno de Fase 7 listo")
        sys.exit(0)
    else:
        print("PROBLEM DETECTED IN ENVIRONMENT SETUP:")
        for dep, err in import_errors:
            print(f"  - Package '{dep}' failed import check. Error details: {err}")
        sys.exit(1)

if __name__ == "__main__":
    install_and_verify()
