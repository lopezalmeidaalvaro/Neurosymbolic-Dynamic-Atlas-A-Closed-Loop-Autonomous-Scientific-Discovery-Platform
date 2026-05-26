import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import argparse
import json
import sys
from experiment_versioning import ExperimentTracker

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(description="Query and list tracked scientific experiments.")
    parser.add_argument("--system", type=str, default=None, help="Filter by test system name")
    parser.add_argument("--module", type=str, default=None, help="Filter by pipeline module name")
    parser.add_argument("--status", type=str, default=None, help="Filter by completion status")
    parser.add_argument("--last", type=int, default=20, help="Number of recent runs to display")
    
    args = parser.parse_args()
    
    tracker = ExperimentTracker()
    runs = tracker.query_experiments(
        system=args.system,
        module=args.module,
        status=args.status,
        limit=args.last
    )
    
    print("=" * 110)
    print(f"📋 LISTING RECENT SCIENTIFIC EXPERIMENT RUNS (Last {args.last})")
    print("=" * 110)
    
    if not runs:
        print("No experiments found matching filters.")
        print("=" * 110)
        return
        
    print(f"{'Run ID':38} | {'Timestamp':25} | {'System':15} | {'Module':15} | {'Status':10}")
    print("-" * 110)
    for r in runs:
        print(f"{r['id']:38} | {r['timestamp'][:25]:25} | {r['system'][:15]:15} | {r['module'][:15]:15} | {r['status'].upper():10}")
        
    print("=" * 110)

if __name__ == "__main__":
    main()
