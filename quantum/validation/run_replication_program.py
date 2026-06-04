import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.law_validation.replication_engine import LawReplicationEngine

def main():
    engine = LawReplicationEngine()
    engine.run_replications()

if __name__ == "__main__":
    main()
