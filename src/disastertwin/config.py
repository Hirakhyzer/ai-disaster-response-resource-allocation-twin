"""Configuration helpers for synthetic disaster-response experiments."""

from __future__ import annotations

from pathlib import Path
import random

import numpy as np


def set_seed(seed: int) -> None:
    """Set deterministic seeds for reproducible synthetic experiments."""
    random.seed(seed)
    np.random.seed(seed)


def ensure_output_dirs(base: str | Path) -> dict[str, Path]:
    """Create and return standard output directories."""
    base = Path(base)
    paths = {
        "base": base,
        "results": base / "results",
        "reports": base / "reports",
        "figures": base / "figures",
        "audit": base / "audit",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths
