"""Single-entry reproducible pipeline for neurosymbolic experiments."""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .audit import linear_cka
from .config import load_config
from .neural_ode import NeuralODEModel, generate_harmonic_oscillator
from .reproducibility import set_global_seed
from .symbolic import recover_sindy_coefficients


def configure_logging(log_path: Path) -> logging.Logger:
    """Create a file-backed pipeline logger.

    Args:
        log_path: Destination log file path.

    Returns:
        Configured logger instance.

    Raises:
        OSError: If the log directory cannot be created.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("neurosymbolic.pipeline")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(file_handler)
    return logger


def generate_system_trajectory(
    system: str, config: dict[str, Any]
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    """Generate trajectory and derivative data for a supported system.

    Args:
        system: System name such as ``lorenz``, ``rossler``, ``duffing``, or
            ``harmonic``.
        config: Parsed experiment configuration.

    Returns:
        Tuple ``(t, x, dxdt, variable_names)``.

    Raises:
        ValueError: If ``system`` is unsupported.
    """
    systems = config.get("systems", {})
    params = dict(systems.get(system, {}))
    n_timesteps = int(params.pop("n_timesteps", 400))
    dt = float(params.pop("dt", 0.01))

    if system == "harmonic":
        t, x = generate_harmonic_oscillator(n_timesteps, dt)
        dxdt = np.column_stack([x[:, 1], -x[:, 0]])
        return t, x, dxdt, ["x", "v"]

    import synthetic_systems

    if system == "lorenz":
        data = synthetic_systems.generate_lorenz(
            n_timesteps=n_timesteps, dt=dt, **params
        )
        x = np.column_stack([data["x"], data["y"], data["z"]])
        dxdt = np.column_stack(
            [
                data["derivatives"]["dx"],
                data["derivatives"]["dy"],
                data["derivatives"]["dz"],
            ]
        )
        return data["t"], x, dxdt, ["x", "y", "z"]

    if system == "rossler":
        data = synthetic_systems.generate_rossler(
            n_timesteps=n_timesteps, dt=dt, **params
        )
        x = np.column_stack([data["x"], data["y"], data["z"]])
        dxdt = np.column_stack(
            [
                data["derivatives"]["dx"],
                data["derivatives"]["dy"],
                data["derivatives"]["dz"],
            ]
        )
        return data["t"], x, dxdt, ["x", "y", "z"]

    if system == "duffing":
        data = synthetic_systems.generate_duffing(
            n_timesteps=n_timesteps, dt=dt, **params
        )
        x = np.column_stack([data["x"], data["v"]])
        dxdt = np.column_stack([data["derivatives"]["dx"], data["derivatives"]["dv"]])
        return data["t"], x, dxdt, ["x", "v"]

    raise ValueError(f"Unsupported system: {system}")


def save_trajectory_plot(t: np.ndarray, x: np.ndarray, output_path: Path) -> None:
    """Save a trajectory plot for the first state coordinate.

    Args:
        t: Time grid with shape ``(n_steps,)``.
        x: State matrix with shape ``(n_steps, n_features)``.
        output_path: Destination PNG path.

    Returns:
        None.

    Raises:
        OSError: If the output directory cannot be created.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(t, x[:, 0], color="#10b981", linewidth=1.4)
    ax.set_xlabel("t")
    ax.set_ylabel("x0")
    ax.set_title("System trajectory")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def save_loss_plot(losses: list[float], output_path: Path) -> None:
    """Save a Neural ODE training-loss plot.

    Args:
        losses: Sequence of training losses.
        output_path: Destination PNG path.

    Returns:
        None.

    Raises:
        OSError: If the output directory cannot be created.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(losses, color="#38bdf8", linewidth=1.4)
    ax.set_xlabel("epoch")
    ax.set_ylabel("MSE")
    ax.set_title("Neural ODE loss")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def run_system_pipeline(system: str, config_path: str | Path = "config.yaml") -> Path:
    """Run the end-to-end reproducible pipeline for one dynamical system.

    Args:
        system: Dynamical system name.
        config_path: YAML configuration path.

    Returns:
        Path to the generated system results directory.

    Raises:
        FileNotFoundError: If the configuration file is missing.
        ValueError: If the system or configuration values are invalid.
        OSError: If result artifacts cannot be written.
    """
    config = load_config(config_path)
    seed = int(config.get("seed", 42))
    set_global_seed(seed)

    results_root = Path(config.get("paths", {}).get("results_dir", "results"))
    result_dir = results_root / system
    result_dir.mkdir(parents=True, exist_ok=True)
    logger = configure_logging(result_dir / "pipeline.log")
    logger.info("Starting pipeline for system=%s config=%s", system, config_path)

    t, x, dxdt, variable_names = generate_system_trajectory(system, config)
    save_trajectory_plot(t, x, result_dir / "trajectory.png")
    logger.info("Generated trajectory with shape=%s", x.shape)

    neural_cfg = config.get("neural_ode", {})
    train_steps = min(int(neural_cfg.get("train_steps", 160)), len(t))
    model = NeuralODEModel(
        input_dim=x.shape[1],
        hidden_dim=int(neural_cfg.get("hidden_dim", 32)),
        num_layers=int(neural_cfg.get("num_layers", 2)),
    )
    losses = model.fit(
        t[:train_steps],
        x[:train_steps],
        epochs=int(neural_cfg.get("epochs", 40)),
        lr=float(neural_cfg.get("lr", 0.01)),
    )
    save_loss_plot(losses, result_dir / "neural_ode_loss.png")
    logger.info("Neural ODE initial_loss=%.8f final_loss=%.8f", losses[0], losses[-1])

    symbolic_rows = []
    for idx, variable in enumerate(variable_names):
        coefficients = recover_sindy_coefficients(
            x,
            dxdt[:, idx],
            feature_names=variable_names,
            threshold=float(config.get("symbolic", {}).get("threshold", 1e-6)),
        )
        for term, value in coefficients.items():
            symbolic_rows.append(
                {"target": f"d{variable}/dt", "term": term, "coefficient": value}
            )

    symbolic_path = result_dir / "symbolic_coefficients.csv"
    with symbolic_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["target", "term", "coefficient"])
        writer.writeheader()
        writer.writerows(symbolic_rows)
    logger.info("Saved symbolic coefficients to %s", symbolic_path)

    rng = np.random.default_rng(seed)
    perturbation = x + rng.normal(0.0, 1e-3, size=x.shape)
    cka_value = linear_cka(x, perturbation)

    metrics_path = result_dir / "metrics.csv"
    with metrics_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerows(
            [
                {"metric": "neural_ode_initial_loss", "value": losses[0]},
                {"metric": "neural_ode_final_loss", "value": losses[-1]},
                {"metric": "linear_cka_self_perturbed", "value": cka_value},
                {"metric": "n_samples", "value": len(t)},
            ]
        )
    logger.info("Saved metrics to %s", metrics_path)
    logger.info("Pipeline finished successfully")
    return result_dir
