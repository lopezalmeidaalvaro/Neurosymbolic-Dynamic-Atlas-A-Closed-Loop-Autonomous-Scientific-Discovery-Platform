#!/bin/bash
echo "Installing QADE benchmark dependencies..."
pip install qiskit>=2.0.0 numpy pandas networkx psutil
echo "Installing real compiler dependencies..."
pip install pytket>=1.20.0 && echo "TKET: OK" || echo "TKET: FAILED"
pip install bqskit>=1.0.0 && echo "BQSKit: OK" || echo "BQSKit: FAILED"
pip install cirq>=1.3.0 && echo "Cirq: OK" || echo "Cirq: FAILED"
pip install pyzx>=0.8.0 && echo "PyZX: OK" || echo "PyZX: FAILED"
echo "Checking compiler availability..."
python -c "
import importlib
compilers = {
    'pytket': 'TKET',
    'bqskit': 'BQSKit', 
    'cirq': 'Cirq',
    'pyzx': 'PyZX',
    'qiskit': 'Qiskit'
}
for module, name in compilers.items():
    try:
        mod = importlib.import_module(module)
        version = getattr(mod, '__version__', 'unknown')
        print(f'{name}: AVAILABLE (v{version})')
    except ImportError:
        print(f'{name}: NOT AVAILABLE - will be EXCLUDED from benchmarks')
"
