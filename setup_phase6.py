import os
import sys
import subprocess

# Force DeepXDE to use PyTorch backend to avoid TensorFlow dependencies
os.environ["DDE_BACKEND"] = "pytorch"

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
    print("STARTING PHASE 6 SCIENTIFIC DEEP MODELING ENVIRONMENT SETUP")
    print("=" * 70)

    # We prioritize torch, torchdiffeq, and deepxde.
    # SciPy, NumPy, Matplotlib and Pandas are standard dependencies and already present from Phase 2-4 setup.
    packages = [
        ("torch", "torch"),
        ("torchdiffeq", "torchdiffeq"),
        ("deepxde", "deepxde"),
        ("scipy", "scipy"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib"),
        ("pandas", "pandas"),
    ]

    results = {}
    for pkg, imp in packages:
        success = install_and_verify_package(pkg, imp)
        results[pkg] = "INSTALLED" if success else "FAILED"

    print("\n" + "=" * 70)
    print("ACCELERATION HARDWARE AUDIT")
    print("=" * 70)

    try:
        import torch

        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print("  CUDA Hardware Acceleration: AVAILABLE")
            print(f"  Active GPU Device Name    : {torch.cuda.get_device_name(0)}")
            print(f"  Active GPU Device Count   : {torch.cuda.device_count()}")
        else:
            print(
                "  CUDA Hardware Acceleration: UNAVAILABLE (Executing on CPU mode by default)"
            )
    except Exception as e:
        print(f"  [ERROR] Failed to perform CUDA hardware acceleration audit: {e}")

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
        print("Entorno de Fase 6 listo")
    else:
        print(
            "Algunas dependencias fallaron: {}".format(
                [k for k, v in results.items() if v == "FAILED"]
            )
        )
    print("=" * 70)


if __name__ == "__main__":
    main()
