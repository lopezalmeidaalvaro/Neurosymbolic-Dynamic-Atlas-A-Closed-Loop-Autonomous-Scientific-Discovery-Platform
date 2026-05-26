import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import subprocess
import sys
import importlib

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def check_and_install(package, import_name):
    """
    Checks if a package is installed. If not, installs it via pip.
    """
    print(f"Checking package '{package}'...")
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, "__version__", "unknown")
        print(f"  Package '{package}' is already installed (version: {version})")
        return True, version
    except ImportError:
        print(f"  Package '{package}' is not installed. Installing via pip...")
        try:
            # Install package
            cmd = [sys.executable, "-m", "pip", "install", package]
            subprocess.check_call(cmd)
            # Try importing again
            module = importlib.import_module(import_name)
            version = getattr(module, "__version__", "unknown")
            print(f"  Successfully installed '{package}' (version: {version})")
            return True, version
        except Exception as e:
            print(f"  [ERROR] Failed to install '{package}': {e}")
            return False, str(e)


def main():
    print("=" * 60)
    print("STARTING FASE 2 ENVIRONMENT SETUP")
    print("=" * 60)

    dependencies = [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("scipy", "scipy"),
        ("matplotlib", "matplotlib"),
        ("sympy", "sympy"),
        ("pysindy>=1.7", "pysindy"),
        ("pysr>=0.12", "pysr"),
    ]

    success_list = []
    failed_list = []

    for pkg, imp_name in dependencies:
        success, info = check_and_install(pkg, imp_name)
        if success:
            success_list.append((pkg, info))
        else:
            failed_list.append((pkg, info))

    print("\n" + "=" * 60)
    print("INSTALLATION SUMMARY:")
    print("=" * 60)
    for pkg, ver in success_list:
        print(f"  - {pkg}: INSTALLED (version: {ver})")
    for pkg, err in failed_list:
        print(f"  - {pkg}: FAILED ({err})")

    print("\n" + "=" * 60)
    if not failed_list:
        print("Entorno de Fase 2 listo")
    else:
        failed_names = [f[0] for f in failed_list]
        print(f"Algunas dependencias fallaron: {failed_names}")
    print("=" * 60)


if __name__ == "__main__":
    main()
