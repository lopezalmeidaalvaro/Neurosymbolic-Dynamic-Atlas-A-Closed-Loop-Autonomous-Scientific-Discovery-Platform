import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.law_validation.synthetic_world_generator import SyntheticWorldGenerator

def main():
    generator = SyntheticWorldGenerator()
    generator.run_challenge()

if __name__ == "__main__":
    main()
