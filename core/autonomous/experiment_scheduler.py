import subprocess
import sys
import os
import concurrent.futures
from typing import List, Tuple

def run_noise_sweep(base_experiment: str, noise_levels: List[float]) -> List[str]:
    """
    Run pipeline sweeps for different noise levels.
    Returns a list of generated experiment session IDs.
    Kept for backward compatibility.
    """
    session_ids = []
    for noise in noise_levels:
        session_id = f"{base_experiment}_noise_{noise}"
        print(f"\n[SCHEDULER] Running pipeline for session {session_id} with noise level {noise}...")
        
        cmd = [
            sys.executable,
            "run_pipeline.py",
            "--experiment", session_id,
            "--noise", str(noise)
        ]
        
        result = subprocess.run(cmd)
        if result.returncode == 0:
            session_ids.append(session_id)
            print(f"[SCHEDULER] Session {session_id} completed successfully.")
        else:
            print(f"[SCHEDULER] Error running session {session_id}. Exit code: {result.returncode}")
            
    return session_ids

def run_single_pipeline_task(task_args: Tuple[str, float, int]) -> Tuple[str, int]:
    system, noise, seed = task_args
    session_id = f"{system}_noise_{noise:.4f}_seed_{seed}"
    cmd = [
        sys.executable,
        "run_pipeline.py",
        "--experiment", session_id,
        "--noise", f"{noise:.4f}",
        "--seed", str(seed),
        "--system", system
    ]
    # Capture stdout and stderr to avoid interleaving in console
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return session_id, result.returncode

def run_massive_sweep(
    systems: List[str],
    noise_levels: List[float],
    seeds: List[int],
    max_workers: int = None
) -> List[str]:
    """
    Runs a grid of systems, noise levels, and seeds concurrently.
    """
    tasks = []
    for sys_name in systems:
        for noise in noise_levels:
            for seed in seeds:
                tasks.append((sys_name, noise, seed))
                
    total_tasks = len(tasks)
    print(f"[SCHEDULER] Spawning massive parallel sweep of {total_tasks} runs...")

    if max_workers is None:
        max_workers = min(4, total_tasks, os.cpu_count() or 1)
    print(f"[SCHEDULER] Max parallel workers: {max_workers}")
    
    session_ids = []
    completed_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(run_single_pipeline_task, task): task
            for task in tasks
        }
        
        for future in concurrent.futures.as_completed(future_to_task):
            task = future_to_task[future]
            system, noise, seed = task
            try:
                session_id, returncode = future.result()
                completed_count += 1
                if returncode == 0:
                    session_ids.append(session_id)
                    print(f"[SCHEDULER] [{completed_count}/{total_tasks}] Session {session_id} completed successfully.")
                else:
                    print(f"[SCHEDULER] [{completed_count}/{total_tasks}] ❌ Session {session_id} failed with exit status {returncode}.")
            except Exception as exc:
                completed_count += 1
                session_id = f"{system}_noise_{noise:.4f}_seed_{seed}"
                print(f"[SCHEDULER] [{completed_count}/{total_tasks}] ❌ Session {session_id} raised exception: {exc}")
                
    return session_ids
