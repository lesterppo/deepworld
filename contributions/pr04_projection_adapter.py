"""Projection Adapter Module

This module provides a lightweight framework for training and applying cross‑model
projection adapters (`W_{A->B}`) within the CMTIP bridge.  It is intentionally
minimal so that it can be merged quickly and used by other agents without
requiring heavy dependencies.

Key features:
- ``ProjectionAdapter`` class that stores a source and target family and a
  fidelity score.
- ``train`` method that simulates training by adjusting the fidelity based on
  an investment value.
- ``apply`` method that projects a concept vector from source to target.
- ``blend`` static method to mix two concept embeddings.

The implementation uses NumPy for vector arithmetic; NumPy is already a
dependency of the environment.
"""

import numpy as np
from typing import Tuple


class ProjectionAdapter:
    """Represents a cross‑family projection adapter.

    Attributes
    ----------
    source_family : str
        The source model family (e.g., 'nvidia').
    target_family : str
        The target model family.
    fidelity : float
        Current fidelity score (0.0-1.0).  Higher fidelity means less
        semantic drift.
    """

    def __init__(self, source_family: str, target_family: str, initial_fidelity: float = 0.2):
        self.source_family = source_family
        self.target_family = target_family
        self.fidelity = initial_fidelity

    def train(self, investment: float) -> None:
        """Simulate training of the adapter.

        Parameters
        ----------
        investment : float
            Amount of OT invested.  The fidelity is increased by a
            diminishing‑returns curve:

                new_fidelity = min(1.0, old_fidelity + 0.1 * sqrt(investment))
        """
        increment = 0.1 * np.sqrt(investment)
        self.fidelity = min(1.0, self.fidelity + increment)

    def apply(self, vector: np.ndarray) -> np.ndarray:
        """Project a concept vector from source to target.

        The projection is simulated by adding Gaussian noise inversely
        proportional to the fidelity.

        Parameters
        ----------
        vector : np.ndarray
            The input concept embedding.

        Returns
        -------
        np.ndarray
            The projected embedding.
        """
        noise_scale = 1.0 - self.fidelity
        noise = np.random.normal(scale=noise_scale, size=vector.shape)
        return vector + noise

    @staticmethod
    def blend(a: np.ndarray, b: np.ndarray, ratio: float) -> np.ndarray:
        """Blend two embeddings.

        Parameters
        ----------
        a, b : np.ndarray
            Embeddings to blend.
        ratio : float
            Blend ratio (0.0 => pure ``a``, 1.0 => pure ``b``).

        Returns
        -------
        np.ndarray
            The blended embedding.
        """
        return (1 - ratio) * a + ratio * b

# Example usage (not executed on import):
# adapter = ProjectionAdapter('nvidia', 'gemini')
# adapter.train(100)
# projected = adapter.apply(np.random.rand(512))
# blended = ProjectionAdapter.blend(a, b, 0.7)
""