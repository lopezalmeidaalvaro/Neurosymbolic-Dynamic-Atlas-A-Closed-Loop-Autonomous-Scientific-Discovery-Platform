import json
import argparse
import sys
import io
import shutil
from pathlib import Path

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Create a baseline snapshot from the current massive sweep report")
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Name of the baseline (e.g. phase_3_5_reference)"
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    artifacts_dir = project_root / "dashboard" / "public" / "artifacts"
    discoveries_dir = artifacts_dir / "discoveries"
    baselines_dir = artifacts_dir / "baselines"
    
    current_sweep_path = discoveries_dir / "massive_sweep_report.json"
    
    if not current_sweep_path.exists():
        print(f"❌ Error: Current massive sweep report not found at {current_sweep_path}")
        print("Please run a massive sweep first (e.g., python run_massive_sweep.py)")
        sys.exit(1)
        
    try:
        with open(current_sweep_path, "r", encoding="utf-8") as f:
            sweep_data = json.load(f)
    except Exception as e:
        print(f"❌ Error parsing current sweep JSON: {e}")
        sys.exit(1)
        
    metadata = sweep_data.get("metadata", {})
    timestamp = metadata.get("timestamp")
    
    if not timestamp:
        print("❌ Error: 'metadata.timestamp' is missing in the current sweep report.")
        sys.exit(1)
        
    # Create baselines directory if it does not exist
    baselines_dir.mkdir(parents=True, exist_ok=True)
    
    # Construct copy filename
    safe_timestamp = timestamp.replace(":", "-")
    source_filename = f"massive_sweep_{safe_timestamp}.json"
    baseline_dest_path = baselines_dir / source_filename
    
    # Copy the file
    try:
        shutil.copy2(current_sweep_path, baseline_dest_path)
        print(f"✅ Copied current sweep report to baseline: {baseline_dest_path}")
    except Exception as e:
        print(f"❌ Failed to copy baseline file: {e}")
        sys.exit(1)
        
    # Load or initialize baseline index
    index_path = baselines_dir / "baseline_index.json"
    if index_path.exists():
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                index_data = json.load(f)
        except Exception as e:
            print(f"⚠️ Warning: Could not parse baseline_index.json ({e}). Re-initializing index.")
            index_data = {"baselines": []}
    else:
        index_data = {"baselines": []}
        
    # Update or insert baseline entry
    baselines_list = index_data.setdefault("baselines", [])
    
    new_entry = {
        "name": args.name,
        "timestamp": timestamp,
        "source": source_filename
    }
    
    # Remove existing baseline with the same name to avoid duplicates
    baselines_list = [b for b in baselines_list if b.get("name") != args.name]
    baselines_list.append(new_entry)
    index_data["baselines"] = baselines_list
    
    try:
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)
        print(f"✅ Updated baseline_index.json at {index_path} with baseline '{args.name}'")
    except Exception as e:
        print(f"❌ Failed to write baseline_index.json: {e}")
        sys.exit(1)
        
    print("🎉 Baseline snapshot system update complete!")

if __name__ == "__main__":
    main()
