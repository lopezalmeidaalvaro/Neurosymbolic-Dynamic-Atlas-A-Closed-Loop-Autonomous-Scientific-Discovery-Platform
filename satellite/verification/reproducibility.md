# Scientific Reproducibility Checklist — AST-OS

This document details the checklist and system configurations required to execute all verification tests and benchmarks deterministically.

---

## 1. Environment Pinned Constraints
To ensure identical mathematical rounding, verify that your environment matches the pinned version targets:

- **Python Version**: `3.10.x`, `3.11.x`, or `3.12.x`
- **PyTorch**: `>=2.3.0` (Forced deterministic operations via `torch.use_deterministic_algorithms(True)`)
- **NumPy**: `>=1.26.0` (Consistent random seed tracking via `np.random.seed(42)`)
- **SciPy**: `>=1.13.0` (Consistent Runge-Kutta-Fehlberg ODE tolerances)

---

## 2. Step-by-Step Reproduction Checklist

- `[ ]` **1. Clone the Standalone Repository**:
  ```bash
  git clone https://github.com/lopezalmeidaalvaro/autonomous-spacecraft-thermal-os.git
  cd autonomous-spacecraft-thermal-os
  ```
- `[ ]` **2. Install Pinned Dependencies**:
  ```bash
  pip install -r satellite/api/requirements.txt
  ```
- `[ ]` **3. Run pytest Unit & Integration Suite**:
  ```bash
  pytest tests/ -v
  ```
  Ensure all **8 tests pass** inside `test_physics.py`, `test_numerical.py`, and `test_components.py`.
- `[ ]` **4. Execute Standalone Benchmarks**:
  ```bash
  python benchmarks/run_cad_benchmark.py
  python benchmarks/run_pinn_benchmark.py
  python benchmarks/run_tvac_benchmark.py
  ```
- `[ ]` **5. Compare Telemetry CSVs**:
  Compare newly generated CSVs in `/benchmarks/` against target baselines, verifying that standard deviations and speedup scales match.
