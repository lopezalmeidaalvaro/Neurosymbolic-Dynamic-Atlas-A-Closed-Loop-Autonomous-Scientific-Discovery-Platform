"""Compatibility shim for the QADE benchmark suite.

The benchmark implementation is now owned by ``quantum.benchmarks`` so QADE can
be extracted progressively. This root command is preserved for reproducibility:

    python run_all_benchmarks.py
"""

from quantum.benchmarks.phase_suite import main


if __name__ == "__main__":
    main()

