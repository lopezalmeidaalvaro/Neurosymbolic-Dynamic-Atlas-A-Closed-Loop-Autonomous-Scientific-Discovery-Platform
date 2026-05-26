"""Reproducibility utilities shared by experiments and tests."""

from __future__ import annotations

import os
import random

import numpy as np


def set_global_seed(seed: int, deterministic_torch: bool = True) -> None:
    """Set all supported random seeds.

    Args:
        seed: Integer seed used by Python, NumPy, and PyTorch if available.
        deterministic_torch: Whether to request deterministic PyTorch kernels
            where the installed PyTorch version supports them.

    Returns:
        None.

    Raises:
        ValueError: If ``seed`` is negative.
    """
    if seed < 0:
        raise ValueError("Seed must be non-negative.")

    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)

    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        if deterministic_torch:
            torch.use_deterministic_algorithms(False)
            torch.backends.cudnn.benchmark = False
    except Exception:
        return
