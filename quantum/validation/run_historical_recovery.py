import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.law_validation.historical_recovery import HistoricalRecovery

def main():
    benchmark = HistoricalRecovery()
    benchmark.run_benchmark()

if __name__ == "__main__":
    main()
