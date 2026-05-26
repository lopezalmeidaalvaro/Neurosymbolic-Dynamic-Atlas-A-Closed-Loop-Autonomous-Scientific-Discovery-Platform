import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import os
import sys
import subprocess

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def install_and_verify_package(package_name, import_name=None):
    if import_name is None:
        import_name = package_name

    print(f"Checking package '{package_name}'...")
    try:
        __import__(import_name)
        print(f"  Package '{package_name}' is already installed.")
        return True
    except ImportError:
        print(f"  Package '{package_name}' is not installed. Installing via pip...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name], check=True
            )
            __import__(import_name)
            print(f"  Successfully installed and imported '{package_name}'.")
            return True
        except Exception as e:
            print(f"  [ERROR] Failed to install '{package_name}': {e}")
            return False


def main():
    print("=" * 70)
    print("STARTING PHASE 5 AUTONOMOUS DISCOVERY LOOP ENVIRONMENT SETUP")
    print("=" * 70)

    packages = [
        ("openai", "openai"),
        ("anthropic", "anthropic"),
        ("docker", "docker"),
        ("requests", "requests"),
        ("json5", "json5"),
        ("tenacity", "tenacity"),
    ]

    results = {}
    for pkg, imp in packages:
        success = install_and_verify_package(pkg, imp)
        results[pkg] = "INSTALLED" if success else "FAILED"

    print("\n" + "=" * 70)
    print("ENVIRONMENT VARIABLE CHECK")
    print("=" * 70)

    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    if openai_key:
        print("  OPENAI_API_KEY     : CONFIGURED (Length: {})".format(len(openai_key)))
    else:
        print("  OPENAI_API_KEY     : MISSING (Optional, required for GPT-4/o1/o3)")

    if anthropic_key:
        print(
            "  ANTHROPIC_API_KEY  : CONFIGURED (Length: {})".format(len(anthropic_key))
        )
    else:
        print("  ANTHROPIC_API_KEY  : MISSING (Optional, required for Claude)")

    if not openai_key and not anthropic_key:
        print(
            "\n[WARNING] No API keys detected! Resilient mock simulations will be active by default."
        )
        print("To configure keys, set them in your environment variables:")
        print("  Windows CMD        : set OPENAI_API_KEY=your_key")
        print('  Windows PowerShell : $env:OPENAI_API_KEY="your_key"')
        print('  Linux/macOS Bash   : export OPENAI_API_KEY="your_key"')

    print("\n" + "=" * 70)
    print("DOCKER ENGINE CHECK")
    print("=" * 70)

    docker_available = False
    try:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print("  Docker Engine      : DETECTED & ACCESSIBLE")
            docker_available = True
        else:
            print(
                "  Docker Engine      : INSTALLED BUT ACCESSIBILITY FAILED (Is Docker Desktop running?)"
            )
    except FileNotFoundError:
        print("  Docker Engine      : NOT INSTALLED / NOT ON PATH")
        print(
            "\n[INFO] Docker is highly recommended for safe sandboxed code execution."
        )
        print("To install Docker:")
        print(
            "  1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/"
        )
        print(
            "  2. Complete installation, reboot, and ensure Docker Desktop is running."
        )
        print(
            "  3. Subprocess execution fallback mode will be automatically used in the sandbox."
        )

    print("\n" + "=" * 70)
    print("INSTALLATION SUMMARY:")
    print("=" * 70)
    all_ok = True
    for pkg, status in results.items():
        print(f"  - {pkg:<20}: {status}")
        if status == "FAILED":
            all_ok = False

    print("\n" + "=" * 70)
    if all_ok:
        print("Entorno de Fase 5 listo")
    else:
        print(
            "Algunas dependencias fallaron: {}".format(
                [k for k, v in results.items() if v == "FAILED"]
            )
        )
    print("=" * 70)


if __name__ == "__main__":
    main()
