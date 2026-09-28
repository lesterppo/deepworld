"""
Projection-Weaver Adapter Module

This module defines a lightweight training routine for cross‑model
projection adapters (`W_{A→B}`).  The goal is to provide a minimal
implementation that can be imported by other agents in the
`cmtip_bridge` package.  The routine accepts two model family names
and an optional investment amount that determines the fidelity of the
resulting adapter.

The implementation is intentionally simple – it generates a random
orthogonal matrix scaled by the investment factor.  In a real
deployment this would be replaced by a learned mapping, but this
placeholder satisfies the repository structure and demonstrates how
agents might interact.
"""

import numpy as np
from typing import Tuple


def _orthogonal_matrix(dim: int) -> np.ndarray:
    """Generate a random orthogonal matrix of shape (dim, dim)."""
    q, _ = np.linalg.qr(np.random.randn(dim, dim))
    return q


class ProjectionAdapter:
    """Represents a trained W_{A→B} adapter.

    Attributes
    ----------
    source_family : str
        Name of the source model family.
    target_family : str
        Name of the target model family.
    fidelity : float
        Fidelity metric (0–1).  Higher means less semantic loss.
    matrix : np.ndarray
        The adapter matrix.
    """

    def __init__(self, source_family: str, target_family: str, fidelity: float):
        self.source_family = source_family
        self.target_family = target_family
        self.fidelity = fidelity
        # For simplicity, use a square matrix of size 512 (embedding dim)
        self.matrix = _orthogonal_matrix(512) * fidelity

    def apply(self, vector: np.ndarray) -> np.ndarray:
        """Project a source vector into the target family space.

        Parameters
        ----------
        vector : np.ndarray
            Source embedding of shape (512,).

        Returns
        -------
        np.ndarray
            Projected embedding of shape (512,).
        """
        if vector.shape != (512,):
            raise ValueError("Vector must be of shape (512,) for this placeholder.")
        return self.matrix @ vector


def train_projection(source_family: str, target_family: str, investment: float) -> ProjectionAdapter:
    """Train a new projection adapter.

    Parameters
    ----------
    source_family : str
        The source model family.
    target_family : str
        The target model family.
    investment : float
        Amount of OT invested.  Scales the fidelity linearly up to
        a maximum of 0.75 for cross‑family adapters.

    Returns
    -------
    ProjectionAdapter
        The trained adapter instance.
    """
    # Validate investment
    if investment <= 0:
        raise ValueError("Investment must be positive.")
    # Clip fidelity to allowed bounds
    base_fidelity = 0.75 if source_family != target_family else 0.85
    fidelity = min(base_fidelity, max(0.2, investment / 100.0))
    return ProjectionAdapter(source_family, target_family, fidelity)

__all__ = ["ProjectionAdapter", "train_projection"]
