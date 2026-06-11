import sys, os
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent not in sys.path:
    sys.path.insert(0, parent)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
print("Compatibility shim → quantum.benchmarks.run_all")
from quantum.benchmarks.run_all import main
if __name__ == "__main__":
    main()
