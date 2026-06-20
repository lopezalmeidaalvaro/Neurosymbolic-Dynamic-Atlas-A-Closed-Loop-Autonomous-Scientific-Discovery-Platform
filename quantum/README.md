# QADE — Quantum Algorithm Discovery Engine v0.1.0

QADE (Quantum Algorithm Discovery Engine) is a hardware-aware quantum compiler designed to automatically optimize quantum circuits. It integrates calibration-aware qubit placement (Stage C) and Sabre routing (Stage G) with evolutionary search and symbolic ZX-calculus reductions to maximize gate fidelity on real quantum processing units (QPUs).

## Installation

Extract the `qade` package and install it locally in editable mode:
```bash
pip install -e ".[qade]"
```

For development dependencies (like pytest) or running the REST API, use:
```bash
pip install -e ".[api,dev]"
```

## Quick Start

You can import and run the `QADEOptimizerPass` as a standard Qiskit transpilation pass:

```python
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import PassManager
from quantum import QADEOptimizerPass
from quantum.optimization.calibration_model import get_fake_backend

# 1. Create your quantum circuit
qc = QuantumCircuit(5)
qc.h(0)
for i in range(4):
    qc.cx(i, i+1)
qc.measure_all()

# 2. Retrieve target backend configuration (e.g., FakeFez mock backend)
backend = get_fake_backend("FakeFez")

# 3. Transpile with Qiskit first (Level 1 unrolls gates to basis set)
transpiled = transpile(qc, backend=backend, optimization_level=1)

# 4. Apply QADE optimization pass
qade_pass = QADEOptimizerPass(backend=backend, hardware_aware=True)
pm = PassManager(qade_pass)
optimized = pm.run(transpiled)

print("Optimized circuit depth:", optimized.depth())
```

## Folder Structure

- **`optimization/`**: Core compilation passes (placement, SABRE routing, PyZX adapters).
- **`integration/`**: Qiskit adapter layer.
- **`api/`**: REST API using FastAPI.
- **`benchmarks/`**: Local compiler benchmark scripts.
- **`docs/`**: Consolidated dossiers and reports.
- **`tests/`**: Unit test suites.

## CLI Usage

QADE provides executable scripts defined as project entry points:

### 1. Compile QASM (`qade compile`)
Compile an OpenQASM 2.0 file for a specific backend:
```bash
qade compile path/to/circuit.qasm --backend ibm_fez --output compiled.qasm
```

### 2. Validate QASM (`qade validate`)
Validate the syntax of an OpenQASM 2.0 file:
```bash
qade validate path/to/circuit.qasm
```

### 3. Local Benchmarks (`qade benchmark`)
Run comparisons of standard Qiskit Level 3 vs QADE without needing active IBM credentials:
```bash
qade benchmark --backend fake_fez --circuits ghz,qft,kernel,vqe
```

## Consolidated Dossiers

Refer to the domain documentation under `quantum/docs/`:
- **[Knowledge Index](docs/INDEX.md)**: Navigation hub for the domain.
- **[QADE Technical Dossier](docs/QADE_TECHNICAL_DOSSIER.md)**: Architectural pipeline, qubit mapping, and Sabre routing parameters.
- **[QADE Benchmark Dossier](docs/QADE_BENCHMARK_DOSSIER.md)**: Physical hardware execution results on real processors (`ibm_fez`).
- **[QADE Product Dossier](docs/QADE_PRODUCT_DOSSIER.md)**: Commercial visions, ROI calculation scenarios, and licensing models.
- **[Hardware Validation Report](docs/HARDWARE_VALIDATION_REPORT.md)**: Cumulative physical execution logs on IBM processors.
