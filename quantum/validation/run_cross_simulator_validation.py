import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.law_validation.cross_simulator_validator import CrossSimulatorValidator

def main():
    validator = CrossSimulatorValidator()
    validator.validate_simulators()

if __name__ == "__main__":
    main()
