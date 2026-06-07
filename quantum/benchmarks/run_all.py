"""QADE benchmark CLI wrapper.

This module makes the benchmark suite addressable from the quantum domain:

    python -m quantum.benchmarks.run_all

Root-level runners remain as compatibility shims.
"""

from quantum.benchmarks.phase_suite import main


if __name__ == "__main__":
    main()

