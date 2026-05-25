import os
import sys
import json
import uuid
import sqlite3
import subprocess
import platform
from datetime import datetime
from functools import wraps

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def get_git_commit_hash():
    """
    Retrieves the short Git commit hash of the current repository.
    Returns "no_git" if git is not initialized or fails.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return "no_git"

def get_system_info():
    """
    Gathers date/time, machine name, python version, and operating system info.
    """
    return {
        "datetime": datetime.now().isoformat(),
        "node": platform.node(),
        "python": platform.python_version(),
        "os": f"{platform.system()} {platform.release()}"
    }

class ExperimentTracker:
    """
    SQLite-backed Experiment Tracker (internal MLflow-like utility) to record
    seeds, parameters, outputs, git hashes, and runtime environments.
    """
    def __init__(self, storage_path="artifacts/experiments.db"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(os.path.abspath(self.storage_path)), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    id VARCHAR(36) PRIMARY KEY,
                    timestamp VARCHAR(50),
                    git_commit VARCHAR(20),
                    system VARCHAR(50),
                    module VARCHAR(50),
                    seed INTEGER,
                    hyperparameters_json TEXT,
                    results_json TEXT,
                    status VARCHAR(20)
                )
            """)
            conn.commit()

    def log_experiment(self, system, module, seed, hyperparameters, results, status="completed"):
        """
        Records an experiment run in the database. Generates a content-hash
        deterministic UUID based on seed and hyperparams.
        """
        git_commit = get_git_commit_hash()
        timestamp = datetime.now().isoformat()
        
        # Deterministic UUIDv5 based on system, module, seed, and hyperparams
        content_str = f"{system}_{module}_{seed}_{json.dumps(hyperparameters, sort_keys=True)}"
        experiment_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, content_str))
        
        hp_json = json.dumps(hyperparameters, indent=2)
        res_json = json.dumps(results, indent=2)
        
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO experiments 
                (id, timestamp, git_commit, system, module, seed, hyperparameters_json, results_json, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (experiment_id, timestamp, git_commit, system, module, seed, hp_json, res_json, status))
            conn.commit()
            
        return experiment_id

    def get_experiment(self, experiment_id):
        """
        Retrieves a single experiment's parameters and results.
        """
        with sqlite3.connect(self.storage_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def query_experiments(self, system=None, module=None, status=None, limit=50):
        """
        Queries all experiments matching the provided filters.
        """
        query = "SELECT * FROM experiments WHERE 1=1"
        params = []
        if system:
            query += " AND system = ?"
            params.append(system)
        if module:
            query += " AND module = ?"
            params.append(module)
        if status:
            query += " AND status = ?"
            params.append(status)
            
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.storage_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def compare_runs(self, experiment_ids):
        """
        Creates a list comparing inputs and metrics across runs.
        """
        comparison = []
        for eid in experiment_ids:
            exp = self.get_experiment(eid)
            if exp:
                comparison.append({
                    "id": exp["id"],
                    "timestamp": exp["timestamp"],
                    "git_commit": exp["git_commit"],
                    "system": exp["system"],
                    "module": exp["module"],
                    "seed": exp["seed"],
                    "hyperparameters": json.loads(exp["hyperparameters_json"]),
                    "results": json.loads(exp["results_json"]),
                    "status": exp["status"]
                })
        return comparison

    def export_to_markdown(self, experiment_ids, output_path):
        """
        Generates a detailed markdown report comparing selected runs.
        """
        runs = self.compare_runs(experiment_ids)
        if not runs:
            return
            
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        md = []
        md.append("# Scientific Experiment Versioning & Provenance Report")
        md.append(f"\n*Report Compiled: {datetime.now().isoformat()}*")
        
        md.append("\n## System Environment Details")
        sys_info = get_system_info()
        md.append(f"- **OS**: `{sys_info['os']}`")
        md.append(f"- **Python**: `{sys_info['python']}`")
        md.append(f"- **Host Node**: `{sys_info['node']}`")
        
        md.append("\n## Audited Run Matrix")
        md.append("| Run ID | Timestamp | System | Module | Git Hash | Seed | Status |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :---: | :---: |")
        for run in runs:
            md.append(
                f"| `{run['id'][:8]}...` | {run['timestamp']} | **{run['system']}** | `{run['module']}` | `{run['git_commit']}` | {run['seed']} | **{run['status'].upper()}** |"
            )
            
        md.append("\n## Detailed Run Parameters & Metrics")
        for idx, run in enumerate(runs):
            md.append(f"\n### [{idx+1}] Run `{run['id']}`")
            md.append(f"- **Git Commit Hash**: `{run['git_commit']}`")
            md.append("- **Hyperparameters**:")
            md.append("```json")
            md.append(json.dumps(run["hyperparameters"], indent=2))
            md.append("```")
            md.append("- **Results / Metrics**:")
            md.append("```json")
            md.append(json.dumps(run["results"], indent=2))
            md.append("```")
            
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))
            
        print(f"✅ Exported comparisons to Markdown report: {output_path}")

def integrate_tracker(pipeline_module):
    """
    Decorator that intercepts function calls and registers their execution,
    parameters, and metrics deterministically into ExperimentTracker.
    """
    tracker = ExperimentTracker()
    
    @wraps(pipeline_module)
    def wrapper(*args, **kwargs):
        # Infer system and module from function metadata
        module_name = pipeline_module.__name__
        system_name = kwargs.get("system_name", "generic_system")
        seed = kwargs.get("seed", 42)
        
        # Serialize arguments as hyperparameters
        serialized_args = {}
        for idx, val in enumerate(args):
            serialized_args[f"arg_{idx}"] = str(val) if not isinstance(val, (int, float, bool, str)) else val
        for k, v in kwargs.items():
            serialized_args[k] = str(v) if not isinstance(v, (int, float, bool, str)) else v
            
        try:
            result = pipeline_module(*args, **kwargs)
            
            # Serialize result metrics
            serialized_res = {}
            if isinstance(result, dict):
                for k, v in result.items():
                    serialized_res[k] = str(v) if not isinstance(v, (int, float, bool, str, list, dict)) else v
            elif isinstance(result, (int, float, bool, str)):
                serialized_res["output"] = result
            else:
                serialized_res["output_type"] = str(type(result))
                
            tracker.log_experiment(
                system=system_name,
                module=module_name,
                seed=seed,
                hyperparameters=serialized_args,
                results=serialized_res,
                status="completed"
            )
            return result
        except Exception as e:
            tracker.log_experiment(
                system=system_name,
                module=module_name,
                seed=seed,
                hyperparameters=serialized_args,
                results={"error": str(e)},
                status="failed"
            )
            raise e
            
    return wrapper
