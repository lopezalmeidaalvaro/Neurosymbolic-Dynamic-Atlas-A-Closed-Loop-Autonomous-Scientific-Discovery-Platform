import concurrent.futures
import subprocess
import sys
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
        print(
            f"\n[SCHEDULER] Running pipeline for session {session_id} with noise level {noise}..."
        )

        cmd = [
            sys.executable,
            "run_pipeline.py",
            "--experiment",
            session_id,
            "--noise",
            str(noise),
        ]

        result = subprocess.run(cmd)
        if result.returncode == 0:
            session_ids.append(session_id)
            print(f"[SCHEDULER] Session {session_id} completed successfully.")
        else:
            print(
                f"[SCHEDULER] Error running session {session_id}. Exit code: {result.returncode}"
            )

    return session_ids


def run_single_pipeline_task(task_args: Tuple[str, float, int]) -> Tuple[str, int]:
    system, noise, seed = task_args
    session_id = f"{system}_noise_{noise:.4f}_seed_{seed}"
    cmd = [
        sys.executable,
        "run_pipeline.py",
        "--experiment",
        session_id,
        "--noise",
        f"{noise:.4f}",
        "--seed",
        str(seed),
        "--system",
        system,
    ]
    # Capture stdout and stderr to avoid interleaving in console.
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return session_id, result.returncode


def run_massive_sweep(
    systems: List[str],
    noise_levels: List[float],
    seeds: List[int],
    max_workers: int = None,
) -> List[str]:
    """
    Runs a grid of systems, noise levels, and seeds.

    The default is serial execution because each pipeline run writes shared
    SQLite/artifact files. Any failed child run fails the whole sweep instead
    of producing a partial certification report.
    """
    tasks = [
        (sys_name, noise, seed)
        for sys_name in systems
        for noise in noise_levels
        for seed in seeds
    ]

    total_tasks = len(tasks)
    print(f"[SCHEDULER] Spawning massive sweep of {total_tasks} runs...")

    if max_workers is None:
        max_workers = 1
    print(f"[SCHEDULER] Max workers: {max_workers}")

    session_ids = []
    failed_sessions = []
    completed_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(run_single_pipeline_task, task): task for task in tasks
        }

        for future in concurrent.futures.as_completed(future_to_task):
            system, noise, seed = future_to_task[future]
            session_id = f"{system}_noise_{noise:.4f}_seed_{seed}"
            completed_count += 1

            try:
                returned_session_id, returncode = future.result()
            except Exception as exc:
                failed_sessions.append(session_id)
                print(
                    f"[SCHEDULER] [{completed_count}/{total_tasks}] FAILED {session_id}: {exc}"
                )
                continue

            if returncode == 0:
                session_ids.append(returned_session_id)
                print(
                    f"[SCHEDULER] [{completed_count}/{total_tasks}] Session {returned_session_id} completed successfully."
                )
            else:
                failed_sessions.append(returned_session_id)
                print(
                    f"[SCHEDULER] [{completed_count}/{total_tasks}] FAILED {returned_session_id} with exit status {returncode}."
                )

    if failed_sessions:
        failed = ", ".join(failed_sessions)
        raise RuntimeError(
            f"Massive sweep failed for {len(failed_sessions)} session(s): {failed}"
        )

    return session_ids
